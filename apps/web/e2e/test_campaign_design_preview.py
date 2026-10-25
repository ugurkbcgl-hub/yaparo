"""Actual read-only snapshot PNGs remain pixel-identical after live edits."""

import json
import os
import secrets
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from zipfile import ZipFile

from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from PIL import Image
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.assets.durable_rasters import create_palette_material
from growthtwin.modules.campaigns.test_design_selection import SelectionFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True,
)
class CampaignPreviewBrowserTests(SelectionFixture, LiveServerTestCase):
    def exercise(self, palette=False):
        pair = (
            create_palette_material(owner=self.owner, brand_id=self.brand.pk)
            if palette
            else None
        )
        document = self.create(
            request_id=uuid4(),
            design_format="portrait",
            palette_material_id=pair.version.material_id if pair else None,
        )
        self.select(document_id=document.pk)
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        url = self.live_server_url + reverse(
            "campaigns:design_preview", args=[self.draft.pk, 1]
        )
        with TemporaryDirectory() as temp, sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1100})
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(url)
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                button = page.get_by_role("button", name="PNG indir")
                expect(button).to_be_enabled()
                self.assertEqual(
                    page.locator("input,textarea,form,#save,#restore").count(), 0
                )

                def download(name):
                    with page.expect_download() as item:
                        button.click()
                    path = Path(temp) / name
                    item.value.save_as(path)
                    with Image.open(path) as image:
                        self.assertEqual(image.size, (800, 1000))
                        return image.convert("RGBA").tobytes()

                original = download("before.png")

                def archive_download(name):
                    with page.expect_download() as item:
                        page.get_by_role(
                            "link", name="Kaynak bilgileriyle ZIP indir"
                        ).click()
                    path = Path(temp) / name
                    item.value.save_as(path)
                    return path.read_bytes()

                original_zip = archive_download("before.zip")
                with ZipFile(BytesIO(original_zip)) as archive:
                    manifest = json.loads(archive.read("manifest.json"))
                    self.assertEqual(
                        manifest["campaign_selection"]["selection_version"], 1
                    )
                    self.assertEqual(manifest["document"]["revision"], 1)
                    self.assertEqual(
                        json.loads(archive.read("scene.json")), document.scene
                    )
                    if pair:
                        self.assertEqual(
                            archive.read("assets/hero-normalized.png"),
                            bytes(pair.derivative),
                        )
                editor = context.new_page()
                editor.goto(
                    self.live_server_url
                    + reverse(
                        "brand_documents:editor", args=[self.brand.pk, document.pk]
                    )
                )
                expect(editor.locator("#save")).to_be_enabled()
                editor.locator("#copy").fill("Bu yeni başlık seçilmedi")
                editor.locator("#save").click()
                expect(editor.locator("#revision")).to_have_text("2")
                editor.close()
                page.reload()
                expect(button).to_be_enabled()
                self.assertEqual(download("after.png"), original)
                self.assertEqual(archive_download("after.zip"), original_zip)
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                page.set_viewport_size({"width": 390, "height": 844})
                self.assertEqual(download("mobile.png"), original)
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                output = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                if output:
                    page.screenshot(
                        path=str(
                            Path(output)
                            / (
                                "campaign-preview-palette.png"
                                if palette
                                else "campaign-preview.png"
                            )
                        ),
                        full_page=True,
                    )
                if palette:
                    page.route("**/design/1/image/", lambda route: route.abort())
                    page.reload()
                    expect(page.locator("#status")).to_contain_text(
                        "Eksik görselle indirme kapalı"
                    )
                    expect(button).to_be_disabled()
                self.assertEqual(errors, [])
            finally:
                browser.close()
        self.assertEqual(self.draft.design_choices.count(), 1)
        self.assertEqual(document.history.count(), 2)

    def test_fixed_portrait_pinned_png(self):
        self.exercise()

    def test_palette_portrait_pinned_png_and_failed_source(self):
        self.exercise(palette=True)
