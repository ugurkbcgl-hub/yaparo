"""Explicit choice → editor → campaign, with revision pin and stale-form denial."""

import os
import secrets
from pathlib import Path
from uuid import uuid4

from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.campaigns.models import CampaignDesignChoice
from growthtwin.modules.campaigns.test_design_selection import SelectionFixture
from growthtwin.modules.workspaces.creative_documents import create_document


@override_settings(DEBUG=True, SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True)
class CampaignDesignBrowserTests(SelectionFixture, LiveServerTestCase):
    def test_select_edit_reselect_without_silent_following_and_stale_overwrite(self):
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        document = create_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            expected_identity_version=1,
            request_id=uuid4(),
            design_format="portrait",
        )
        url = self.live_server_url + reverse("campaigns:design", args=[self.draft.pk])
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                page = context.new_page()
                page.goto(
                    self.live_server_url
                    + reverse("campaigns:detail", args=[self.draft.pk])
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                expect(
                    page.get_by_text("Henüz marka ve tasarım seçilmedi.")
                ).to_be_visible()
                page.get_by_role("link", name="Marka ve tasarım seç").click()
                stale = page.context.new_page()
                stale.goto(url)
                row = (
                    page.locator("section.summary-card")
                    .filter(has_text="800 × 1000")
                    .filter(
                        has=page.get_by_role("button", name="Bu tasarım kaydını seç")
                    )
                )
                row.get_by_role("button", name="Bu tasarım kaydını seç").click()
                expect(
                    page.get_by_text("Seçili tasarım kaydı 1", exact=False)
                ).to_be_visible()
                old = (
                    stale.locator("section.summary-card")
                    .filter(has_text="800 × 1000")
                    .filter(
                        has=stale.get_by_role("button", name="Bu tasarım kaydını seç")
                    )
                )
                old.get_by_role("button", name="Bu tasarım kaydını seç").click()
                expect(stale.get_by_role("alert")).to_contain_text(
                    "Seçim kaydedilemedi"
                )
                stale.close()
                page.get_by_role("link", name="Güncel tasarımı düzenle").click()
                expect(page.locator("#save")).to_be_enabled()
                expect(
                    page.get_by_role("link", name="Kampanyanın tasarım seçimine dön")
                ).to_be_visible()
                page.locator("#copy").fill("Kampanya için yeni kurgusal başlık")
                page.locator("#save").click()
                expect(page.locator("#revision")).to_have_text("2")
                page.get_by_role(
                    "link", name="Kampanyanın tasarım seçimine dön"
                ).click()
                expect(
                    page.get_by_text("Tasarımın daha yeni bir kaydı var.", exact=False)
                ).to_be_visible()
                expect(
                    page.get_by_text("Seçili tasarım kaydı 1", exact=False)
                ).to_be_visible()
                output = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                if output:
                    page.screenshot(
                        path=str(Path(output) / "campaign-design-desktop.png"),
                        full_page=True,
                    )
                page.set_viewport_size({"width": 390, "height": 844})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                if output:
                    page.screenshot(
                        path=str(Path(output) / "campaign-design-mobile.png"),
                        full_page=True,
                    )
                row = (
                    page.locator("section.summary-card")
                    .filter(has_text="800 × 1000")
                    .filter(
                        has=page.get_by_role("button", name="Bu tasarım kaydını seç")
                    )
                )
                row.get_by_role("button", name="Bu tasarım kaydını seç").click()
                expect(
                    page.get_by_text("Seçili tasarım kaydı 2", exact=False)
                ).to_be_visible()
                page.get_by_role("link", name="Kampanyaya dön", exact=False).click()
                expect(
                    page.get_by_text("Seçili tasarım kaydı 2", exact=False)
                ).to_be_visible()
            finally:
                browser.close()
        self.assertEqual(
            CampaignDesignChoice.objects.filter(draft=self.draft).count(), 2
        )
        self.assertEqual(
            self.draft.design_choices.first().snapshot.document_id, document.pk
        )
        self.assertEqual(self.draft.design_choices.last().snapshot.revision, 1)
