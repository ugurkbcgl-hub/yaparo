"""Browser generation, private image read and download, mocked provider only."""

import os
import secrets
from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.ai_gateway.brand_sample import REQUEST
from growthtwin.modules.workspaces import hosted_image_trial as service
from growthtwin.modules.workspaces.hosted_trial import PROFILE as TEXT_PROFILE
from growthtwin.modules.workspaces.models import (
    HostedImageTrial,
    HostedTextTrial,
    Workspace,
)
from growthtwin.modules.workspaces.test_hosted_image_trial import sample_png


class HostedImageBrowserTests(LiveServerTestCase):
    def test_one_image_refresh_download_and_text_job_preserved(self):
        password = secrets.token_urlsafe(32)
        owner = get_user_model().objects.create_user(
            username="image-browser", password=password
        )
        workspace = Workspace.objects.create(owner=owner, name="Synthetic")
        HostedTextTrial.objects.create(
            workspace=workspace,
            owner=owner,
            profile=TEXT_PROFILE,
            source_hash=REQUEST.source_hash,
            reserved_usd="0.001",
        )
        text_before = HostedTextTrial.objects.values().get()
        with (
            override_settings(
                DEBUG=True,
                LOCAL_HOSTED_TEXT_TRIAL_ENABLED=True,
                LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID=workspace.pk,
                LOCAL_HOSTED_IMAGE_TRIAL_ENABLED=True,
            ),
            mock.patch.dict(
                os.environ,
                {
                    "OPENROUTER_API_KEY": "test-only-key",
                    "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED": "1",
                },
            ),
            mock.patch.object(
                service, "generate_image", return_value=(sample_png(), ".png", 0.033625)
            ) as generator,
            mock.patch.object(
                service, "reserve_evaluation_cost", return_value=Path("test-ledger")
            ),
            mock.patch.object(service, "settle_evaluation_cost"),
            sync_playwright() as p,
        ):
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto(self.live_server_url + reverse("brands:hosted_trial"))
                page.locator("#id_username").fill(owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                page.get_by_role("link", name="AI görsel üretimini aç").click()
                expect(
                    page.get_by_role("button", name="AI görseli üret")
                ).to_be_visible()
                generator.assert_not_called()
                page.get_by_role("button", name="AI görseli üret").click()
                image = page.get_by_role(
                    "img",
                    name="Duru Studio için AI ile üretilen kurgusal seramik kupa görseli",
                )
                expect(image).to_be_visible()
                self.assertTrue(
                    image.evaluate("i => i.complete && i.naturalWidth === 64")
                )
                with page.expect_download() as event:
                    page.get_by_role("link", name="Görseli indir").click()
                downloaded = Path(event.value.path()).read_bytes()
                page.reload()
                expect(
                    page.get_by_role("button", name="AI görseli üret")
                ).to_have_count(0)
                page.get_by_text("Görsel ve maliyet bilgileri", exact=True).click()
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1000})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                    directory = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                    if directory:
                        page.screenshot(
                            path=str(Path(directory) / f"hosted-image-{width}.png"),
                            full_page=True,
                        )
                generator.assert_called_once()
            finally:
                browser.close()
        job = HostedImageTrial.objects.get()
        self.assertEqual(job.status, "completed")
        self.assertEqual(downloaded, bytes(job.png))
        self.assertEqual(HostedTextTrial.objects.values().get(), text_before)
