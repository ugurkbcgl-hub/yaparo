"""Normal brand source selection/edit/reopen/PNG and failure boundaries."""

import io
import secrets
from pathlib import Path

from django.test import LiveServerTestCase
from django.urls import reverse
from PIL import Image
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.workspaces.models import BrandAdDraft
from growthtwin.modules.workspaces.test_brand_ad_drafts import BrandAdFixture


class BrandAdBrowserTests(BrandAdFixture, LiveServerTestCase):
    composition_brand_name = "Özenli Seramik ve Tasarım Atölyesi " * 3

    def setUp(self):
        super().setUp()
        self.password = secrets.token_urlsafe(32)
        self.owner.set_password(self.password)
        self.owner.save(update_fields=["password"])

    def login(self, page, path):
        page.goto(self.live_server_url + path)
        page.locator("#id_username").fill(self.owner.username)
        page.locator("#id_password").fill(self.password)
        page.get_by_role("button", name="Giriş yap").click()

    def test_select_edit_save_reopen_replay_stale_and_png(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_context().new_page()
                choices = reverse("brands:brand_ad_choices", args=[self.brand.pk])
                self.login(page, choices)
                page.get_by_label("Kaydedilmiş reklam metni").select_option(
                    f"{self.plan.pk}|{self.key}"
                )
                page.get_by_label("Kaydedilmiş AI görseli").select_option(
                    str(self.image_plan.pk)
                )
                page.get_by_role("button", name="Seçimi incele").click()
                review = page.url
                page.get_by_role(
                    "button", name="Seçimden düzenlenebilir taslak aç"
                ).click()
                editor = page.url
                export = page.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                expect(export).to_be_enabled()
                stale = page.context.new_page()
                stale.goto(editor)
                expect(
                    stale.get_by_role("button", name="Taslağı kaydet")
                ).to_be_enabled()
                page.get_by_label("Çağrı metni").fill("Markayı keşfet")
                expect(export).to_be_disabled()
                page.get_by_role("button", name="Taslağı kaydet").click()
                expect(export).to_be_enabled()
                expect(page.get_by_label("Çağrı metni")).to_have_value("Markayı keşfet")
                stale.get_by_label("Çağrı metni").fill("Eski sekme")
                stale.get_by_role("button", name="Taslağı kaydet").click()
                expect(stale.get_by_role("alert")).to_be_visible()
                expect(stale.get_by_label("Çağrı metni")).to_have_value("Eski sekme")
                expect(
                    stale.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                ).to_be_disabled()
                # Wait for the stale page's private-image request to finish before
                # another DB-backed navigation (shared SQLite live-test database).
                expect(stale.locator("#ad-status")).to_have_text(
                    "Düzenleme ekranda. PNG indirmek için önce kaydet."
                )
                page.goto(review)
                page.get_by_role(
                    "button", name="Seçimden düzenlenebilir taslak aç"
                ).click()
                self.assertEqual(page.url, editor)
                expect(page.get_by_label("Çağrı metni")).to_have_value("Markayı keşfet")
                expect(export).to_be_enabled()
                with page.expect_download() as download:
                    export.click()
                data = Path(download.value.path()).read_bytes()
                with Image.open(io.BytesIO(data)) as image:
                    self.assertEqual(image.size, (768, 1376))
                    self.assertEqual(
                        image.convert("RGB").getpixel((400, 1200)), (37, 77, 155)
                    )
                page.set_viewport_size({"width": 390, "height": 1100})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                page.reload()
                expect(export).to_be_enabled()
            finally:
                browser.close()
        self.assertEqual(BrandAdDraft.objects.get().revision, 2)

    def test_changed_private_image_disables_save_and_export(self):
        draft = self.ad()
        changed = io.BytesIO()
        Image.new("RGB", (768, 1376), "red").save(changed, format="PNG")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.route(
                    "**/ads/*/image/",
                    lambda route: route.fulfill(
                        status=200, content_type="image/png", body=changed.getvalue()
                    ),
                )
                self.login(
                    page,
                    reverse("brands:brand_ad_editor", args=[self.brand.pk, draft.pk]),
                )
                expect(
                    page.get_by_text("Kaydedilmiş görsel doğrulanamadı.", exact=False)
                ).to_be_visible()
                expect(
                    page.get_by_role("button", name="Taslağı kaydet")
                ).to_be_disabled()
                expect(
                    page.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                ).to_be_disabled()
            finally:
                browser.close()
