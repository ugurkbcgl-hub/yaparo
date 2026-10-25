"""Browser proof for owned, identity-pinned synthetic saved work."""

import json
import os
import secrets
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.workspaces.models import Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner


class BrandDocumentBrowserTests(LiveServerTestCase):
    def test_create_edit_reopen_download_and_preserve_old_identity(self):
        password = secrets.token_urlsafe(32)
        owner = get_user_model().objects.create_user(
            username="document-browser-owner", password=password
        )
        workspace = Workspace.objects.create(owner=owner, name="Sentetik çalışma")
        brand = create_brand_for_owner(
            owner=owner, workspace_id=workspace.pk, fixture="product"
        )
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(
                    self.live_server_url + reverse("brands:detail", args=[brand.pk])
                )
                page.locator("#id_username").fill(owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                with page.expect_navigation(wait_until="load"):
                    page.get_by_role(
                        "button", name="Sentetik materyal kitini hazırla"
                    ).click()
                expect(page.get_by_text("Dosya boyutu ölçülmedi")).to_have_count(2)
                expect(
                    page.get_by_text("Yaparo sabit sentetik çizim", exact=False)
                ).to_be_visible()
                page.get_by_role("button", name="Örnek çalışma oluştur").click()
                page.wait_for_url("**/documents/*/")
                document_url = page.url
                page.locator("#id_title").fill("Özgün sentetik çalışma")
                with page.expect_navigation(wait_until="load"):
                    page.get_by_role("button", name="Çalışmayı kaydet").click()
                page.reload()
                expect(page.locator("#id_title")).to_have_value(
                    "Özgün sentetik çalışma"
                )
                with page.expect_download() as download_info:
                    page.get_by_role("link", name="Sahne JSON dosyasını indir").click()
                scene = json.loads(
                    Path(download_info.value.path()).read_text(encoding="utf-8")
                )
                self.assertEqual("Özgün sentetik çalışma", scene["layers"][2]["text"])
                self.assertEqual("product:logo:v1", scene["layers"][1]["asset"])
                page.goto(
                    self.live_server_url + reverse("brands:edit", args=[brand.pk])
                )
                page.locator("#id_primary_color").select_option("#9A3F2D")
                page.get_by_role("button", name="Kimliği kaydet").click()
                page.goto(document_url)
                expect(page.locator("#id_title")).to_have_value(
                    "Özgün sentetik çalışma"
                )
                expect(page.locator("#id_title_color")).to_have_value("#244c3b")
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                screenshot_root = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                if screenshot_root:
                    directory = Path(screenshot_root)
                    directory.mkdir(parents=True, exist_ok=True)
                    page.screenshot(
                        path=str(directory / "document-mobile.png"), full_page=True
                    )
                    page.set_viewport_size({"width": 1440, "height": 1000})
                    page.screenshot(
                        path=str(directory / "document-desktop.png"), full_page=True
                    )
            finally:
                browser.close()
