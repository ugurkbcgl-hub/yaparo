"""Owned setup across stale tabs and consistent in-site summaries."""

import secrets

from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.campaigns.models import (
    CampaignBrandAdChoice,
    CampaignPlanRevision,
    WorkspaceCampaignDraft,
)
from growthtwin.modules.campaigns.test_brand_settings import PlanFixture


class BrandSettingsBrowserTests(PlanFixture, LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.password = secrets.token_urlsafe(32)
        self.owner.set_password(self.password)
        self.owner.save(update_fields=["password"])
        self.before = WorkspaceCampaignDraft.objects.values().get(pk=self.camp.pk)
        self.choice_before = list(CampaignBrandAdChoice.objects.values())

    def fill(self, page, budget="2500,50", audience="Sentetik tasarım meraklıları"):
        page.get_by_label("Kampanyanın amacı").select_option("traffic")
        page.get_by_label("Hedef kitle").fill(audience)
        page.get_by_label("Planlanan bölge").fill("İstanbul")
        page.get_by_label("Toplam medya bütçesi").fill(budget)
        page.get_by_label("Başlangıç tarihi").fill(self.values["start"])
        page.get_by_label("Bitiş tarihi").fill(self.values["end"])
        page.get_by_label("Yalnız sentetik plan kaydediyorum", exact=False).check()

    def test_localized_plan_save_stale_preservation_reopen_and_list_summary(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_context().new_page()
                setup = self.live_server_url + reverse(
                    "campaigns:brand_setup", args=[self.camp.pk]
                )
                page.goto(setup)
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(self.password)
                page.get_by_role("button", name="Giriş yap").click()
                stale = page.context.new_page()
                stale.goto(setup)
                self.fill(page)
                page.get_by_role("button", name="Planı kaydet").click()
                expect(
                    page.get_by_text("Toplam 2.500,50 TRY", exact=False)
                ).to_be_visible()
                self.fill(
                    stale,
                    budget="4000,00",
                    audience="Kaybolmaması gereken sentetik metin",
                )
                stale.get_by_role("button", name="Planı kaydet").click()
                expect(stale.get_by_role("alert")).to_be_visible()
                expect(stale.get_by_label("Hedef kitle")).to_have_value(
                    "Kaybolmaması gereken sentetik metin"
                )
                expect(stale.get_by_label("Toplam medya bütçesi")).to_have_value(
                    "4000,00"
                )
                page.goto(setup)
                expect(page.get_by_label("Toplam medya bütçesi")).to_have_value(
                    "2500,50"
                )
                self.fill(page, budget="3000,25", audience="Ö" * 200)
                page.get_by_role("button", name="Planı kaydet").click()
                expect(
                    page.get_by_text("Toplam 3.000,25 TRY", exact=False)
                ).to_be_visible()
                page.set_viewport_size({"width": 390, "height": 1100})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                page.goto(self.live_server_url + reverse("campaigns:list"))
                expect(
                    page.get_by_text(
                        "3.000,25 TRY toplam medya bütçesi planı", exact=True
                    )
                ).to_be_visible()
                expect(
                    page.get_by_text("Site ziyaretleri · İstanbul", exact=True)
                ).to_be_visible()
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
            finally:
                browser.close()
        self.assertEqual(CampaignPlanRevision.objects.count(), 2)
        self.assertEqual(
            WorkspaceCampaignDraft.objects.values().get(pk=self.camp.pk), self.before
        )
        self.assertEqual(
            list(CampaignBrandAdChoice.objects.values()), self.choice_before
        )
