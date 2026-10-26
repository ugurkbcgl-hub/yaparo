"""Visible brand brief capture with stale form preservation and version history."""

import secrets

from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.workspaces.models import BrandProductionRequest
from growthtwin.modules.workspaces.test_production_briefs import ProductionBriefFixture


class ProductionBriefBrowserTests(ProductionBriefFixture, LiveServerTestCase):
    def test_brand_navigation_capture_stale_form_and_new_request_version(self):
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1100})
                page = context.new_page()
                page.goto(
                    self.live_server_url
                    + reverse("brands:detail", args=[self.brand.pk])
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                page.get_by_role(
                    "link", name="Markaya özel üretim talebi hazırla"
                ).click()
                page.set_viewport_size({"width": 390, "height": 1100})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                page.set_viewport_size({"width": 1440, "height": 1100})
                old = context.new_page()
                old.goto(page.url)
                page.get_by_label("Ne üretelim?").fill(self.brief["description"])
                page.get_by_label("Kime hitap edecek?").fill(self.brief["audience"])
                page.get_by_role(
                    "button", name="Talebi markaya bağla ve kaydet"
                ).click()
                expect(
                    page.get_by_role("heading", name="Üretim talebi kaydedildi")
                ).to_be_visible()
                expect(
                    page.get_by_text(self.brief["description"], exact=True)
                ).to_be_visible()
                first_url = page.url
                old.get_by_label("Ne üretelim?").fill("Eski formun talebi")
                old.get_by_label("Kime hitap edecek?").fill("Sentetik kitle")
                old.get_by_role("button", name="Talebi markaya bağla ve kaydet").click()
                expect(old.get_by_role("alert")).to_be_visible()
                expect(old.get_by_label("Ne üretelim?")).to_have_value(
                    "Eski formun talebi"
                )
                page.get_by_role("link", name="← Yeni talep ve geçmiş").click()
                page.get_by_label("Ne üretelim?").fill("İkinci sürümde görsel talebi")
                page.get_by_label("Kime hitap edecek?").fill("Sentetik ikinci kitle")
                page.get_by_label("İçerik türü").select_option("image")
                page.get_by_role(
                    "button", name="Talebi markaya bağla ve kaydet"
                ).click()
                expect(
                    page.get_by_text("İkinci sürümde görsel talebi", exact=True)
                ).to_be_visible()
                page.goto(first_url)
                expect(
                    page.get_by_text(self.brief["description"], exact=True)
                ).to_be_visible()
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1100})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
            finally:
                browser.close()
        self.assertEqual(BrandProductionRequest.objects.count(), 2)
        self.assertEqual(
            list(
                BrandProductionRequest.objects.order_by("version").values_list(
                    "version", flat=True
                )
            ),
            [1, 2],
        )
