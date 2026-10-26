"""Website paid-intent path with mocked provider and budget, no live API."""

import io
import secrets
from unittest import mock

from django.test import LiveServerTestCase
from django.urls import reverse
from PIL import Image
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.workspaces import brand_generation as service
from growthtwin.modules.workspaces.test_brand_generation import GenerationFixture


class BrandGenerationBrowserTests(GenerationFixture, LiveServerTestCase):
    def test_saved_image_is_decoded_and_fits_mobile_card(self):
        from django.conf import settings

        plan = self.make(
            expected_version=1, brief={**self.brief, "deliverable": "image"}
        )
        settings.LOCAL_BRAND_AI_APPROVED_REQUESTS[str(plan.pk)] = plan.fingerprint
        stream = io.BytesIO()
        Image.new("RGB", (768, 1376), "#254d9b").save(stream, format="JPEG")
        with mock.patch.object(
            service, "generate_image", return_value=(stream.getvalue(), ".jpg", 0.03)
        ):
            self.assertEqual(self.run_job(plan).status, "completed")
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 1100})
                page.goto(
                    self.live_server_url
                    + reverse(
                        "brands:production_request", args=[self.brand.pk, plan.pk]
                    )
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                image = page.get_by_role(
                    "img", name="Bu marka talebi ve renklerine göre üretilen AI görseli"
                )
                expect(image).to_be_visible()
                self.assertEqual(image.evaluate("el => el.naturalWidth"), 768)
                self.assertTrue(
                    image.evaluate(
                        "el => el.clientWidth <= el.parentElement.clientWidth - 40"
                    )
                )
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                page.reload()
                expect(image).to_be_visible()
            finally:
                browser.close()

    def test_request_page_generates_saved_copy_once_and_refresh_keeps_it(self):
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(
                    self.live_server_url
                    + reverse(
                        "brands:production_request", args=[self.brand.pk, self.plan.pk]
                    )
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                token = page.locator(
                    "#main-content input[name=csrfmiddlewaretoken]"
                ).input_value()
                page.get_by_role("button", name="Bu marka talebinden AI üret").click()
                expect(
                    page.get_by_role("heading", name="Markaya özel AI üretimi")
                ).to_be_visible()
                expect(
                    page.get_by_text("Gerçek AI çıktısı", exact=False)
                ).to_be_visible()
                expect(
                    page.get_by_role("button", name="Bu marka talebinden AI üret")
                ).not_to_be_visible()
                response = page.request.post(
                    self.live_server_url
                    + reverse(
                        "brands:production_generate", args=[self.brand.pk, self.plan.pk]
                    ),
                    form={
                        "csrfmiddlewaretoken": token,
                        "fingerprint": self.plan.fingerprint,
                    },
                    headers={"Origin": self.live_server_url},
                )
                self.assertEqual(response.status, 200)
                page.reload()
                expect(
                    page.get_by_text("Gerçek AI çıktısı", exact=False)
                ).to_be_visible()
                page.set_viewport_size({"width": 390, "height": 1100})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
            finally:
                browser.close()
        self.generator.generate.assert_called_once()
        self.settlement.assert_called_once()
