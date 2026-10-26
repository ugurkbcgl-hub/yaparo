"""Owned candidate link and responsive no-write preview in a real browser."""

import os
import secrets
from copy import deepcopy
from pathlib import Path

from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.campaigns.test_design_selection import SelectionFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED=True,
)
class BrandCopyBrowserTests(SelectionFixture, LiveServerTestCase):
    def test_preview_does_not_replace_user_scene(self):
        self.select()
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["text"] = "Benim korunacak başlığım"
        self.save(scene)
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto(
                    self.live_server_url
                    + reverse("campaigns:design", args=[self.draft.pk])
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                page.get_by_role(
                    "link", name="Markaya bağlı örnek metinleri gör"
                ).click()
                expect(
                    page.get_by_role("heading", name="Markana bağlı örnek metinler")
                ).to_be_visible()
                self.assertEqual(page.locator("section.summary-card").count(), 3)
                self.assertEqual(
                    page.locator("main").locator("form,input,textarea").count(), 0
                )
                expect(
                    page.get_by_text("Adaylar kaydedilmedi", exact=False)
                ).to_be_visible()
                output = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1000})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                    if output:
                        page.screenshot(
                            path=str(Path(output) / f"brand-copy-{width}.png"),
                            full_page=True,
                        )
                page.get_by_role(
                    "link", name="Tasarımın güncel kaydını düzenle"
                ).click()
                expect(page.locator("#copy")).to_have_value("Benim korunacak başlığım")
                expect(page.locator("#revision")).to_have_text("2")
            finally:
                browser.close()
        self.document.refresh_from_db()
        self.assertEqual(self.document.scene, scene)
        self.assertEqual(self.document.history.count(), 2)
        self.assertEqual(self.draft.design_choices.count(), 1)
