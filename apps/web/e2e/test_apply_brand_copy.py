"""Actual CSRF-safe form apply and stale refusal, preserving pinned history."""

import os
import secrets
from copy import deepcopy
from pathlib import Path

from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.campaigns.test_apply_brand_copy import ApplyFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED=True,
    SYNTHETIC_BRAND_COPY_APPLY_ENABLED=True,
)
class ApplyBrowserTests(ApplyFixture, LiveServerTestCase):
    def test_stale_refusal_then_explicit_title_and_body_new_revisions(self):
        original = deepcopy(self.document.scene)
        changed = deepcopy(original)
        changed["layers"][2]["text"] = "User saved title"
        self.save(changed)
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        copy_url = self.live_server_url + reverse(
            "campaigns:brand_copy", args=[self.draft.pk, 1]
        )
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                page = context.new_page()
                page.goto(copy_url)
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                cards = page.locator(".brand-copy-options section")
                expect(
                    cards.nth(1).get_by_role(
                        "button",
                        name="Başlık ve açıklamayı yeni kayda uygula",
                        exact=True,
                    )
                ).to_be_disabled()
                editor = context.new_page()
                editor.goto(
                    self.live_server_url
                    + reverse(
                        "brand_documents:editor", args=[self.brand.pk, self.document.pk]
                    )
                )
                expect(editor.locator("#save")).to_be_enabled()
                editor.locator("#copy").fill("Concurrent user title")
                editor.locator("#save").click()
                expect(editor.locator("#revision")).to_have_text("3")
                cards.first.get_by_role(
                    "button", name="Yalnız başlığı yeni kayda uygula", exact=True
                ).click()
                expect(page.get_by_role("alert")).to_contain_text(
                    "Tasarımın değiştirilmedi"
                )
                editor.reload()
                expect(editor.locator("#copy")).to_have_value("Concurrent user title")
                page.goto(copy_url)
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
                            path=str(Path(output) / f"apply-copy-{width}.png"),
                            full_page=True,
                        )
                page.locator(".brand-copy-options section").first.get_by_role(
                    "button", name="Yalnız başlığı yeni kayda uygula", exact=True
                ).click()
                expect(page.locator("#revision")).to_have_text("4")
                expect(page.locator("#copy")).to_have_value(self.candidate.headline)
                page.goto(copy_url)
                page.locator(".brand-copy-options section").first.get_by_role(
                    "button", name="Başlık ve açıklamayı yeni kayda uygula", exact=True
                ).click()
                expect(page.locator("#revision")).to_have_text("5")
                page.get_by_role("button", name="Açıklama", exact=True).click()
                expect(page.locator("#copy")).to_have_value(self.candidate.body)
            finally:
                browser.close()
        self.document.refresh_from_db()
        self.assertEqual(self.document.history.count(), 5)
        self.assertEqual(self.document.history.get(revision=1).scene, original)
        self.assertEqual(
            self.document.history.get(revision=4).scene["layers"][3],
            original["layers"][3],
        )
        self.assertEqual(self.draft.design_choices.count(), 1)
        self.assertEqual(self.draft.design_choices.first().snapshot.revision, 1)
