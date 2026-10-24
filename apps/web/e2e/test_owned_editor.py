"""Owned canvas save/reopen/conflict and decoded PNG verification."""

import base64
import os
import secrets
from pathlib import Path
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.workspaces.creative_documents import create_document
from growthtwin.modules.workspaces.creative_scenes import seed_scene
from growthtwin.modules.workspaces.models import BrandCreativeDocument, Workspace
from growthtwin.modules.workspaces.services import (
    create_brand_for_owner,
    update_brand_identity_for_owner,
)


class OwnedEditorBrowserTests(LiveServerTestCase):
    def test_save_reopen_stale_tab_and_png(self):
        password = secrets.token_urlsafe(32)
        owner = get_user_model().objects.create_user(
            username="canvas-owner", password=password
        )
        workspace = Workspace.objects.create(owner=owner, name="Sentetik")
        brand = create_brand_for_owner(
            owner=owner, workspace_id=workspace.pk, fixture="product"
        )
        initial = brand.current_identity
        legacy = BrandCreativeDocument.objects.create(
            id=uuid4(),
            identity=initial,
            scene=seed_scene(
                fixture="product",
                tagline_text=initial.tagline_text,
                primary_color=initial.primary_color,
                logo_key=initial.logo_key,
            ),
        )
        update_brand_identity_for_owner(
            owner=owner,
            brand_id=brand.pk,
            expected_version=1,
            primary_color="#254D9B",
            secondary_color="#EAF0FF",
            tone="calm",
            tagline_key="small_beauty",
        )
        document = create_document(
            owner=owner,
            brand_id=brand.pk,
            expected_identity_version=2,
            request_id=uuid4(),
        )
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                external = []

                def route_local(route):
                    if route.request.url.startswith(self.live_server_url + "/"):
                        route.continue_()
                    else:
                        external.append(route.request.url)
                        route.abort()

                context.route("**/*", route_local)
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                url = self.live_server_url + reverse(
                    "brand_documents:editor", args=[brand.pk, document.pk]
                )
                page.goto(url)
                page.locator("#id_username").fill(owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                expect(page.locator("#save")).to_be_enabled()
                stale = context.new_page()
                stale.goto(url)
                expect(stale.locator("#save")).to_be_enabled()
                page.locator("#copy").fill("Özgün örnek · Şığ çömlek")
                page.locator("#x").fill("72")
                page.locator("#save").click()
                expect(page.locator("#revision")).to_have_text("2")
                page.reload()
                expect(page.locator("#copy")).to_have_value("Özgün örnek · Şığ çömlek")
                expect(page.locator("#x")).to_have_value("72")
                page.locator("#history").select_option("1")
                page.locator("#restore").click()
                expect(page.locator("#revision")).to_have_text("3")
                expect(page.locator("#copy")).to_have_value(
                    "Gününe küçük bir güzellik."
                )
                page.locator("#history").select_option("2")
                page.locator("#restore").click()
                expect(page.locator("#revision")).to_have_text("4")
                expect(page.locator("#copy")).to_have_value("Özgün örnek · Şığ çömlek")
                stale.locator("#copy").fill("Eski sekme")
                stale.locator("#save").click()
                expect(stale.locator("#status")).to_contain_text("Kayıt doğrulanamadı")
                stale.close()
                with page.expect_download() as event:
                    page.locator("#download").click()
                data = Path(event.value.path()).read_bytes()
                encoded = base64.b64encode(data).decode("ascii")
                size = page.evaluate(
                    "data => new Promise((resolve,reject) => {const image=new Image(); image.onload=()=>resolve([image.naturalWidth,image.naturalHeight]); image.onerror=reject; image.src='data:image/png;base64,'+data;})",
                    encoded,
                )
                self.assertEqual([800, 800], size)
                palette = page.evaluate(
                    "data => new Promise(resolve => {const image=new Image(); image.onload=()=>{const c=document.createElement('canvas');c.width=c.height=800;const x=c.getContext('2d');x.drawImage(image,0,0);resolve([Array.from(x.getImageData(0,0,1,1).data),Array.from(x.getImageData(65,68,1,1).data)]);};image.src='data:image/png;base64,'+data;})",
                    encoded,
                )
                self.assertEqual([[234, 240, 255, 255], [37, 77, 155, 255]], palette)

                self.assertEqual([], external)
                self.assertEqual([], errors)
                output = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                if output:
                    page.screenshot(
                        path=str(Path(output) / "owned-editor-desktop.png"),
                        full_page=True,
                    )
                page.set_viewport_size({"width": 390, "height": 844})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                if output:
                    page.screenshot(
                        path=str(Path(output) / "owned-editor-mobile.png"),
                        full_page=True,
                    )
                self.assertEqual(0, page.evaluate("localStorage.length"))
                page.goto(
                    self.live_server_url
                    + reverse("brand_documents:editor", args=[brand.pk, legacy.pk])
                )
                expect(page.locator("#save")).to_be_enabled()
                with page.expect_download() as old_event:
                    page.locator("#download").click()
                old_data = base64.b64encode(
                    Path(old_event.value.path()).read_bytes()
                ).decode("ascii")
                old_background = page.evaluate(
                    "data => new Promise(resolve => {const image=new Image();image.onload=()=>{const c=document.createElement('canvas');c.width=c.height=800;const x=c.getContext('2d');x.drawImage(image,0,0);resolve(Array.from(x.getImageData(0,0,1,1).data));};image.src='data:image/png;base64,'+data;})",
                    old_data,
                )
                self.assertEqual([245, 237, 223, 255], old_background)

            finally:
                browser.close()
