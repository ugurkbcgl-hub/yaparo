"""Choose, pin, edit elsewhere and explicitly reselect through the actual UI."""

import secrets
from hashlib import sha256
from pathlib import Path

from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.campaigns.models import (
    CampaignHostedAdChoice,
    WorkspaceCampaignDraft,
)
from growthtwin.modules.campaigns.test_hosted_ad_selection import CampaignAdFixture


class CampaignHostedAdBrowserTests(CampaignAdFixture, LiveServerTestCase):
    def test_explicit_choice_pinned_preview_and_reselection(self):
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        before = WorkspaceCampaignDraft.objects.values().get(pk=self.plan.pk)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1100})
                page = context.new_page()
                page.goto(
                    self.live_server_url
                    + reverse("campaigns:detail", args=[self.plan.pk])
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                page.get_by_role(
                    "link", name="AI reklam görselini seç veya önizle"
                ).click()
                page.get_by_role("button", name="Bu kaydı kampanyaya seç").click()
                page.get_by_role("link", name="Seçili kaydı önizle").click()
                preview_url = page.url
                expect(page.get_by_label("Başlık", exact=True)).to_have_value(
                    "El yapımı seramik kupalar"
                )
                expect(page.get_by_label("Başlık", exact=True)).not_to_be_editable()
                expect(page.locator("#ad-save")).not_to_be_visible()
                expect(page.locator("#ad-package")).to_be_disabled()
                expect(page.locator("#ad-export")).to_be_enabled()
                with page.expect_download() as event:
                    page.locator("#ad-export").click()
                first = Path(event.value.path()).read_bytes()
                edit = context.new_page()
                edit.goto(
                    self.live_server_url
                    + reverse("brands:hosted_ad_editor", args=[self.ad.pk])
                )
                expect(edit.locator("#ad-save")).to_be_enabled()
                edit.get_by_label("Başlık").fill("Sonraki kayıt")
                edit.locator("#ad-save").click()
                expect(edit.locator("#ad-revision")).to_have_text("2")
                page.reload()
                expect(page.get_by_label("Başlık", exact=True)).to_have_value(
                    "El yapımı seramik kupalar"
                )
                expect(page.locator("#ad-export")).to_be_enabled()
                with page.expect_download() as event:
                    page.locator("#ad-export").click()
                self.assertEqual(
                    sha256(Path(event.value.path()).read_bytes()).hexdigest(),
                    sha256(first).hexdigest(),
                )
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1100})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                page.get_by_role("link", name="← Kampanya görsel seçimine dön").click()
                page.get_by_role("button", name="Bu kaydı kampanyaya seç").click()
                page.get_by_role("link", name="Seçili kaydı önizle").click()
                expect(page.get_by_label("Başlık", exact=True)).to_have_value(
                    "Sonraki kayıt"
                )
                page.goto(preview_url)
                expect(
                    page.get_by_text("Görsel seçimi doğrulanamadı.", exact=False)
                ).to_be_visible()
            finally:
                browser.close()
        self.assertEqual(CampaignHostedAdChoice.objects.count(), 2)
        self.assertEqual(
            WorkspaceCampaignDraft.objects.values().get(pk=self.plan.pk), before
        )
