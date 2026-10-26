"""Real browser flow with mocked provider; refresh and repeat never redispatch."""

import os
import secrets
from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.workspaces import hosted_trial
from growthtwin.modules.workspaces.models import HostedTextTrial, Workspace
from growthtwin.modules.workspaces.test_hosted_trial import fake_generator


class HostedTrialBrowserTests(LiveServerTestCase):
    def test_generate_reopen_and_mobile_without_second_call(self):
        password = secrets.token_urlsafe(32)
        owner = get_user_model().objects.create_user(
            username="hosted-browser", password=password
        )
        workspace = Workspace.objects.create(owner=owner, name="Synthetic browser")
        generator = fake_generator()
        with (
            override_settings(
                DEBUG=True,
                LOCAL_HOSTED_TEXT_TRIAL_ENABLED=True,
                LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID=workspace.pk,
            ),
            mock.patch.dict(
                os.environ,
                {
                    "OPENROUTER_API_KEY": "test-only-key",
                    "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED": "1",
                },
            ),
            mock.patch.object(
                hosted_trial, "OpenRouterCreativeGenerator", return_value=generator
            ),
            mock.patch.object(
                hosted_trial,
                "reserve_evaluation_cost",
                return_value=Path("test-ledger"),
            ),
            mock.patch.object(hosted_trial, "settle_evaluation_cost"),
            sync_playwright() as playwright,
        ):
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto(self.live_server_url + reverse("brands:list"))
                page.locator("#id_username").fill(owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                page.get_by_role("link", name="Gerçek AI üretimini aç →").click()
                expect(
                    page.get_by_role("heading", name="Gerçek AI üretimi")
                ).to_be_visible()
                expect(
                    page.get_by_role("button", name="AI metinleri üret")
                ).to_be_visible()
                generator.generate.assert_not_called()
                page.get_by_role("button", name="AI metinleri üret").click()
                expect(
                    page.get_by_role("heading", name="Seramik kupalar")
                ).to_be_visible()
                expect(
                    page.get_by_role("button", name="AI metinleri üret")
                ).to_have_count(0)
                page.reload()
                expect(
                    page.get_by_role("heading", name="Seramik kupalar")
                ).to_be_visible()
                page.get_by_text("Üretim ve maliyet bilgileri", exact=True).click()
                expect(page.get_by_text("Model:", exact=False)).to_contain_text("Azure")
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1000})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                    output = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                    if output:
                        page.screenshot(
                            path=str(Path(output) / f"hosted-trial-{width}.png"),
                            full_page=True,
                        )
            finally:
                browser.close()
        self.assertEqual(HostedTextTrial.objects.count(), 1)
        self.assertEqual(HostedTextTrial.objects.get().status, "completed")
        generator.generate.assert_called_once()
