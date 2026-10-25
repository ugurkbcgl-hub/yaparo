"""Real editor actions, bounded local history and failed-save preservation."""

import os
import secrets
from pathlib import Path
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.assets.durable_rasters import create_palette_material
from growthtwin.modules.workspaces.creative_documents import create_document
from growthtwin.modules.workspaces.creative_scenes import seed_scene
from growthtwin.modules.workspaces.models import BrandCreativeDocument, Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
class EditorUndoBrowserTests(LiveServerTestCase):
    def setUp(self):
        self.password = secrets.token_urlsafe(32)
        self.owner = get_user_model().objects.create_user(
            username="undo-fixture", password=self.password
        )
        workspace = Workspace.objects.create(owner=self.owner, name="Synthetic undo")
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=workspace.pk, fixture="product"
        )

    def document(self, schema=2):
        if schema == 1:
            identity = self.brand.current_identity
            return BrandCreativeDocument.objects.create(
                id=uuid4(),
                identity=identity,
                scene=seed_scene(
                    fixture="product",
                    tagline_text=identity.tagline_text,
                    primary_color=identity.primary_color,
                    logo_key=identity.logo_key,
                ),
            )
        palette = (
            create_palette_material(owner=self.owner, brand_id=self.brand.pk)
            if schema == 3
            else None
        )
        return create_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            expected_identity_version=1,
            request_id=uuid4(),
            palette_material_id=palette.version.material_id if palette else None,
        )

    def open(self, browser, document):
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(
            self.live_server_url
            + reverse("brand_documents:editor", args=[self.brand.pk, document.pk])
        )
        page.locator("#id_username").fill(self.owner.username)
        page.locator("#id_password").fill(self.password)
        page.get_by_role("button", name="Giriş yap").click()
        expect(page.locator("#save")).to_be_enabled()
        return page

    def test_buttons_keyboard_native_fields_failed_and_successful_save(self):
        document = self.document()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = self.open(browser, document)
                expect(page.locator("#undo")).to_be_disabled()
                expect(page.locator("#redo")).to_be_disabled()
                page.locator("#copy").fill("Özgün başlık")
                page.locator("#x").fill("72")
                page.locator("#color").fill("#9a3f2d")
                page.locator("#undo").click()
                expect(page.locator("#color")).to_have_value("#244c3b")
                page.locator("#undo").click()
                expect(page.locator("#x")).to_have_value("55")
                page.locator("#undo").focus()
                page.keyboard.press("Control+z")
                expect(page.locator("#copy")).to_have_value(
                    "Gününe küçük bir güzellik."
                )
                page.keyboard.press("Control+Shift+z")
                expect(page.locator("#copy")).to_have_value("Özgün başlık")
                page.keyboard.press("Control+y")
                expect(page.locator("#x")).to_have_value("72")
                page.locator("#undo").click()
                page.locator("#x").fill("90")
                expect(page.locator("#redo")).to_be_disabled()
                # Input fields retain the browser's native undo event.
                page.evaluate(
                    "document.addEventListener('keydown',e=>{window.undoKeyPrevented=e.defaultPrevented;})"
                )
                page.locator("#copy").press("Control+z")
                self.assertFalse(page.evaluate("window.undoKeyPrevented"))
                page.locator("#copy").fill("Başarısız kayıtta korunur")
                attempted = []
                pending = []

                def deny(route):
                    attempted.append(route.request.post_data_json)
                    pending.append(route)

                page.route("**/scene/", deny)
                page.locator("#save").click()
                expect(page.locator("#undo")).to_be_disabled()
                expect(page.locator("#redo")).to_be_disabled()
                page.locator(".stage").focus()
                page.keyboard.press("Control+z")
                expect(page.locator("#copy")).to_have_value("Başarısız kayıtta korunur")
                self.assertEqual(len(pending), 1)
                pending[0].fulfill(
                    status=409, content_type="application/json", body="{}"
                )
                expect(page.locator("#status")).to_contain_text("Kayıt doğrulanamadı")
                expect(page.locator("#copy")).to_have_value("Başarısız kayıtta korunur")
                expect(page.locator("#undo")).to_be_enabled()
                page.locator("#undo").click()
                page.locator("#redo").click()
                expect(page.locator("#copy")).to_have_value("Başarısız kayıtta korunur")
                self.assertEqual(len(attempted), 1)
                page.unroute("**/scene/")
                page.locator("#save").click()
                expect(page.locator("#revision")).to_have_text("2")
                expect(page.locator("#undo")).to_be_disabled()
                expect(page.locator("#redo")).to_be_disabled()
                page.reload()
                expect(page.locator("#save")).to_be_enabled()
                expect(page.locator("#copy")).to_have_value("Başarısız kayıtta korunur")
                page.locator("#x").fill("110")
                page.get_by_role("button", name="Örnek görsel", exact=True).click()
                page.locator("#history").select_option("1")
                page.on("dialog", lambda dialog: dialog.accept())
                page.locator("#restore").click()
                expect(page.locator("#revision")).to_have_text("3")
                expect(page.locator("#undo")).to_be_disabled()
                expect(page.locator("#redo")).to_be_disabled()
                expect(page.locator("#selected-name")).to_have_text("Başlık")
                expect(page.locator("#copy")).to_have_value(
                    "Gününe küçük bir güzellik."
                )
                expect(page.locator("#x")).to_have_value("55")
                page.locator("#copy").fill("Geri dönüşten sonra doğru katman")
                page.locator("#undo").click()
                expect(page.locator("#copy")).to_have_value(
                    "Gününe küçük bir güzellik."
                )
                screenshot = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                if screenshot:
                    page.screenshot(
                        path=str(Path(screenshot) / "undo-desktop.png"), full_page=True
                    )
                page.set_viewport_size({"width": 390, "height": 844})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                if screenshot:
                    page.screenshot(
                        path=str(Path(screenshot) / "undo-mobile.png"), full_page=True
                    )
            finally:
                browser.close()
        document.refresh_from_db()
        self.assertEqual(document.revision, 3)
        self.assertEqual(document.history.count(), 3)

    def test_fifty_step_cap_noop_and_new_branch_without_network_writes(self):
        document = self.document()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = self.open(browser, document)
                posts = []
                page.on(
                    "request",
                    lambda request: (
                        posts.append(request.url) if request.method == "POST" else None
                    ),
                )
                for value in range(100, 151):
                    page.locator("#x").fill(str(value))
                for _ in range(50):
                    page.locator("#undo").click()
                expect(page.locator("#x")).to_have_value("100")
                expect(page.locator("#undo")).to_be_disabled()
                page.locator("#x").fill("100")
                expect(page.locator("#redo")).to_be_enabled()
                for _ in range(50):
                    page.locator("#redo").click()
                expect(page.locator("#x")).to_have_value("150")
                expect(page.locator("#redo")).to_be_disabled()
                self.assertEqual(posts, [])
            finally:
                browser.close()
        document.refresh_from_db()
        self.assertEqual(document.revision, 1)

    def test_drag_after_undo_keeps_current_scene_in_v1_and_v3(self):
        documents = [(schema, self.document(schema)) for schema in (1, 3)]
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                for schema, document in documents:
                    page = self.open(browser, document)
                    page.get_by_role("button", name="Örnek görsel", exact=True).click()
                    box = page.locator(".upper-canvas").bounding_box()
                    # Use the actual visible image body, avoiding control handles.
                    offset_x, offset_y = (290, 200) if schema == 1 else (160, 100)
                    x = box["x"] + (115 + offset_x) * box["width"] / 800
                    y = box["y"] + (310 + offset_y) * box["height"] / 800
                    for delta in (40, 30):
                        page.mouse.move(x, y)
                        page.mouse.down()
                        page.mouse.move(x + delta * box["width"] / 800, y, steps=5)
                        page.mouse.up()
                        self.assertAlmostEqual(
                            float(page.locator("#x").input_value()),
                            115 + delta,
                            delta=2,
                        )
                        page.locator("#undo").click()
                        expect(page.locator("#x")).to_have_value("115")
                    page.locator("#redo").click()
                    page.locator("#save").click()
                    expect(page.locator("#revision")).to_have_text("2")
                    page.close()
            finally:
                browser.close()
        for schema, document in documents:
            document.refresh_from_db()
            self.assertAlmostEqual(document.scene["layers"][0]["x"], 145, delta=2)
            self.assertEqual(document.scene["schema_version"], schema)
