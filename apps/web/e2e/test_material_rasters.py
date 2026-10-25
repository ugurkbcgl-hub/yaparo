"""Browser proof for an owner creating, reopening and viewing a fixed raster."""

import os
import secrets
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.assets.models import MaterialRasterPair
from growthtwin.modules.workspaces.models import Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
class MaterialRasterBrowserTests(LiveServerTestCase):
    def test_generate_reopen_and_repeat_preserves_one_private_image(self):
        password = secrets.token_urlsafe(32)
        owner = get_user_model().objects.create_user(
            username="raster-browser", password=password
        )
        workspace = Workspace.objects.create(owner=owner, name="Sentetik görsel alanı")
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
                        "button", name="Örnek palet görselini hazırla"
                    ).click()
                image = page.get_by_role(
                    "img",
                    name="Bu marka kimliğinin renklerinden üretilen sentetik palet örneği",
                )
                expect(image).to_be_visible()
                self.assertEqual(
                    [320, 200],
                    image.evaluate("image => [image.naturalWidth,image.naturalHeight]"),
                )
                source = image.get_attribute("src")
                page.reload()
                expect(image).to_have_attribute("src", source)
                with page.expect_navigation(wait_until="load"):
                    page.get_by_role(
                        "button", name="Örnek palet görselini hazırla"
                    ).click()
                expect(image).to_have_attribute("src", source)
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                screenshot_dir = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                if screenshot_dir:
                    directory = Path(screenshot_dir)
                    directory.mkdir(parents=True, exist_ok=True)
                    page.screenshot(
                        path=str(directory / "material-raster-mobile.png"),
                        full_page=True,
                    )
                    page.set_viewport_size({"width": 1440, "height": 1000})
                    page.screenshot(
                        path=str(directory / "material-raster-desktop.png"),
                        full_page=True,
                    )
            finally:
                browser.close()
        self.assertEqual(1, MaterialRasterPair.objects.count())
