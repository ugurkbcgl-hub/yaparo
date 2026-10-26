"""Site-internal brand creative to campaign plan; no downloads or paid calls."""

import re
import secrets

from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.campaigns.models import (
    CampaignBrandAdChoice,
    WorkspaceCampaignDraft,
)
from growthtwin.modules.campaigns.test_brand_ad_selection import BrandCampaignFixture


class BrandCampaignBrowserTests(BrandCampaignFixture, LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.password = secrets.token_urlsafe(32)
        self.owner.set_password(self.password)
        self.owner.save(update_fields=["password"])

    def test_create_campaign_preview_pins_old_ad_then_explicitly_reselect(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_context().new_page()
                editor = self.live_server_url + reverse(
                    "brands:brand_ad_editor", args=[self.brand.pk, self.ad_record.pk]
                )
                page.goto(editor)
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(self.password)
                page.get_by_role("button", name="Giriş yap").click()
                expect(page.locator("#ad-status")).to_have_text(
                    "Kayıtlı taslak hazır. PNG indirebilirsin."
                )
                start = page.get_by_role(
                    "button", name="Bu reklamla kampanya planı oluştur"
                )
                expect(start).to_be_enabled()
                page.get_by_label("Başlık", exact=False).fill("Kaydedilmemiş başlık")
                expect(start).to_be_disabled()
                page.get_by_label("Başlık", exact=False).fill(
                    self.ad_record.content["title"]
                )
                expect(start).to_be_enabled()
                page.get_by_label(
                    "Yalnız sentetik kampanya planı oluşturuyorum; reklam yayını ve harcama başlamaz."
                ).check()
                page.get_by_role(
                    "button", name="Bu reklamla kampanya planı oluştur"
                ).click()
                choose_url = page.url
                page.get_by_role("link", name="Kampanyada seçilen reklamı gör").click()
                old_url = page.url
                expect(page.locator("#ad-status")).to_have_text(
                    "Kampanyaya seçilen kayıt hazır."
                )
                expect(page.get_by_label("Çağrı metni")).to_have_value("Keşfet")
                self.assertEqual(
                    page.get_by_role("button", name=re.compile("indir", re.I)).count(),
                    0,
                )
                other = page.context.new_page()
                other.goto(editor)
                expect(
                    other.get_by_role("button", name="Taslağı kaydet")
                ).to_be_enabled()
                other.get_by_label("Çağrı metni").fill("Yeni kayıt")
                other.get_by_role("button", name="Taslağı kaydet").click()
                expect(other.locator("#ad-status")).to_have_text(
                    "Kayıtlı taslak hazır. PNG indirebilirsin."
                )
                page.reload()
                expect(page.locator("#ad-status")).to_have_text(
                    "Kampanyaya seçilen kayıt hazır."
                )
                expect(page.get_by_label("Çağrı metni")).to_have_value("Keşfet")
                page.goto(choose_url)
                page.get_by_role("button", name="Bu kaydı kampanyaya seç").click()
                page.get_by_role("link", name="Kampanyada seçilen reklamı gör").click()
                expect(page.locator("#ad-status")).to_have_text(
                    "Kampanyaya seçilen kayıt hazır."
                )
                expect(page.get_by_label("Çağrı metni")).to_have_value("Yeni kayıt")
                self.assertEqual(page.request.get(old_url).status, 409)
                page.set_viewport_size({"width": 390, "height": 1100})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
            finally:
                browser.close()
        self.assertEqual(WorkspaceCampaignDraft.objects.get().brand_id, self.brand.pk)
        self.assertEqual(CampaignBrandAdChoice.objects.count(), 2)
