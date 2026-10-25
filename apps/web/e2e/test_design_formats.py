"""New format choice and actual PNG dimensions across responsive viewports."""

import json
import os
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from PIL import Image
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.assets.durable_rasters import create_palette_material
from growthtwin.modules.workspaces.creative_documents import create_document
from growthtwin.modules.workspaces.creative_scenes import seed_scene
from growthtwin.modules.workspaces.models import BrandCreativeDocument

from . import test_editor_undo


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
class DesignFormatBrowserTests(LiveServerTestCase):
    setUp = test_editor_undo.EditorUndoBrowserTests.setUp
    open = test_editor_undo.EditorUndoBrowserTests.open

    def png(self, page, height, palette_y=None):
        with page.expect_download() as event:
            page.locator("#download").click()
        with Image.open(BytesIO(Path(event.value.path()).read_bytes())) as image:
            image.load()
            self.assertEqual(image.size, (800, height))
            self.assertEqual(image.getpixel((0, height - 1)), (245, 237, 223, 255))
            if palette_y is not None:
                self.assertEqual(image.getpixel((200, palette_y)), (36, 76, 59, 255))

    def test_actual_portrait_form_edit_history_export_and_mobile(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto(
                    self.live_server_url
                    + reverse("brands:detail", args=[self.brand.pk])
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(self.password)
                page.get_by_role("button", name="Giriş yap").click()
                button = page.get_by_role("button", name="Örnek çalışma oluştur")
                button.locator("..").locator(
                    "select[name=design_format]"
                ).select_option("portrait")
                button.click()
                page.wait_for_url("**/documents/*/")
                with page.expect_download() as package:
                    page.get_by_role(
                        "link", name="Tasarım paketini indir (ZIP)"
                    ).click()
                with ZipFile(package.value.path()) as archive:
                    scene = json.loads(archive.read("scene.json"))
                    self.assertEqual(
                        (scene["schema_version"], scene["width"], scene["height"]),
                        (4, 800, 1000),
                    )
                    self.assertEqual(
                        json.loads(archive.read("manifest.json"))["renderer_contract"],
                        "yaparo-scene-v1-v4",
                    )
                page.get_by_role("link", name="Görsel editörü aç").click()
                expect(page.locator("#save")).to_be_enabled()
                expect(page.locator(".stage-heading")).to_contain_text("800 × 1000")
                expect(page.locator("#y")).to_have_attribute("max", "900")
                output = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                if output:
                    page.screenshot(
                        path=str(Path(output) / "portrait-desktop.png"), full_page=True
                    )
                page.locator("#y").fill("880")
                page.locator("#undo").click()
                expect(page.locator("#y")).to_have_value("135")
                page.locator("#redo").click()
                for width in (999, 390):
                    page.set_viewport_size({"width": width, "height": 844})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                    self.png(page, 1000)
                    expect(page.locator("#y")).to_have_value("880")
                    expect(page.locator("#undo")).to_be_enabled()
                page.locator("#save").click()
                expect(page.locator("#revision")).to_have_text("2")
                page.reload()
                expect(page.locator("#save")).to_be_enabled()
                expect(page.locator("#y")).to_have_value("880")
                page.locator("#history").select_option("1")
                page.locator("#restore").click()
                expect(page.locator("#revision")).to_have_text("3")
                expect(page.locator("#y")).to_have_value("135")
                self.png(page, 1000)
                if output:
                    page.screenshot(
                        path=str(Path(output) / "portrait-mobile.png"), full_page=True
                    )
                # A transform after exporting must still use the restored viewport.
                page.get_by_role("button", name="Örnek görsel", exact=True).click()
                page.locator(".upper-canvas").scroll_into_view_if_needed()
                box = page.locator(".upper-canvas").bounding_box()
                x = box["x"] + 405 * box["width"] / 800
                y = box["y"] + 610 * box["height"] / 1000
                page.mouse.move(x, y)
                page.mouse.down()
                page.mouse.move(x + 30 * box["width"] / 800, y, steps=5)
                page.mouse.up()
                self.assertAlmostEqual(
                    float(page.locator("#x").input_value()), 145, delta=2
                )
                page.locator("#undo").click()
                expect(page.locator("#x")).to_have_value("115")
            finally:
                browser.close()

    def test_palette_formats_and_all_legacy_pngs_remain_correct(self):
        pair = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        identity = self.brand.current_identity
        legacy = BrandCreativeDocument.objects.create(
            id=uuid4(),
            identity=identity,
            scene=seed_scene(
                fixture="product",
                tagline_text=identity.tagline_text,
                primary_color=identity.primary_color,
                logo_key=identity.logo_key,
            ),
        )
        documents = [(legacy, 800, None)]
        for format_name, palette in (
            (None, False),
            (None, True),
            ("square", True),
            ("portrait", True),
        ):
            doc = create_document(
                owner=self.owner,
                brand_id=self.brand.pk,
                expected_identity_version=1,
                request_id=uuid4(),
                design_format=format_name,
                palette_material_id=pair.version.material_id if palette else None,
            )
            documents.append(
                (
                    doc,
                    doc.scene["height"],
                    doc.scene["layers"][0]["y"] + 70 if palette else None,
                )
            )
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                for doc, height, palette_y in documents:
                    page = self.open(browser, doc)
                    page.set_viewport_size({"width": 390, "height": 844})
                    self.png(page, height, palette_y)
                    page.close()
            finally:
                browser.close()
