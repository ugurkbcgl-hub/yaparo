"""Browser proof for an owner creating, reopening and viewing a fixed raster."""

import base64
import json
import os
import secrets
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from PIL import Image
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
                external = []

                def only_local(route):
                    if route.request.url.startswith(self.live_server_url + "/"):
                        route.continue_()
                    else:
                        external.append(route.request.url)
                        route.abort()

                page.context.route("**/*", only_local)
                page.get_by_role("button", name="Bu görselle yeni tasarım aç").click()
                page.wait_for_url("**/documents/*/")
                with page.expect_download() as bundle_event:
                    page.get_by_role(
                        "link", name="Tasarım paketini indir (ZIP)"
                    ).click()
                with ZipFile(bundle_event.value.path()) as archive:
                    manifest = json.loads(archive.read("manifest.json"))
                    self.assertEqual(
                        json.loads(archive.read("scene.json"))["schema_version"], 4
                    )
                    self.assertEqual(manifest["document"]["revision"], 1)
                    image_data = archive.read("assets/hero-normalized.png")
                    self.assertEqual(
                        sha256(image_data).hexdigest(),
                        manifest["files"]["assets/hero-normalized.png"]["sha256"],
                    )
                    self.assertIn(
                        "Uyumlu Yaparo",
                        archive.read("README.txt").decode(),
                    )
                if screenshot_dir:
                    page.screenshot(
                        path=str(directory / "bundle-detail-desktop.png"),
                        full_page=True,
                    )
                    page.set_viewport_size({"width": 390, "height": 844})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                    page.screenshot(
                        path=str(directory / "bundle-detail-mobile.png"), full_page=True
                    )
                    page.set_viewport_size({"width": 1440, "height": 1000})
                page.get_by_role("link", name="Görsel editörü aç").click()
                expect(page.locator("#download")).to_be_enabled()
                editor_url = page.url
                page.get_by_role("button", name="Örnek görsel", exact=True).click()
                page.locator("#x").fill("160")
                page.locator("#save").click()
                expect(page.locator("#revision")).to_have_text("2")
                page.reload()
                expect(page.locator("#download")).to_be_enabled()
                with page.expect_download() as event:
                    page.locator("#download").click()
                encoded = base64.b64encode(
                    Path(event.value.path()).read_bytes()
                ).decode("ascii")
                pixels = page.evaluate(
                    """data => new Promise(resolve=>{const i=new Image();i.onload=()=>{const c=document.createElement('canvas');c.width=c.height=800;const x=c.getContext('2d');x.drawImage(i,0,0);resolve([Array.from(x.getImageData(230,380,1,1).data),Array.from(x.getImageData(170,320,1,1).data)]);};i.src='data:image/png;base64,'+data;})""",
                    encoded,
                )
                self.assertEqual(pixels, [[36, 76, 59, 255], [245, 237, 223, 255]])
                if screenshot_dir:
                    page.screenshot(
                        path=str(directory / "palette-editor-desktop.png"),
                        full_page=True,
                    )
                page.set_viewport_size({"width": 390, "height": 844})
                self.assertFalse(
                    page.evaluate("document.documentElement.scrollWidth > innerWidth")
                )
                if screenshot_dir:
                    page.screenshot(
                        path=str(directory / "palette-editor-mobile.png"),
                        full_page=True,
                    )
                page.locator("#history").select_option("1")
                page.locator("#restore").click()
                expect(page.locator("#revision")).to_have_text("3")
                expect(page.locator("#download")).to_be_enabled()
                self.assertEqual([], external)
                # Fail the private image read. The editor must never fall back
                # to a built-in illustration and export an incomplete design.
                wrong_size = BytesIO()
                with Image.new("RGB", (1, 1)) as wrong_image:
                    wrong_image.save(wrong_size, format="PNG")
                failures = [
                    dict(status=403, body="denied"),
                    dict(status=404, body="missing"),
                    dict(status=200, content_type="image/png", body=b"bad PNG"),
                    dict(
                        status=200, content_type="image/png", body=b"\x89PNG\r\n\x1a\n"
                    ),
                    dict(
                        status=200, content_type="image/png", body=wrong_size.getvalue()
                    ),
                    dict(status=200, content_type="image/png", body=b"x" * 8388609),
                    dict(
                        status=200, content_type="text/html", body="<p>not an image</p>"
                    ),
                    dict(
                        status=302,
                        headers={"Location": "https://example.invalid/private-image"},
                    ),
                ]
                for failure in failures:
                    with self.subTest(
                        response=failure.get("status"), kind=failure.get("content_type")
                    ):
                        page.route(
                            "**" + source, lambda route: route.fulfill(**failure)
                        )
                        page.goto(editor_url)
                        expect(page.locator("#status")).to_contain_text(
                            "Eksik görselle kaydetme ve indirme kapalı"
                        )
                        expect(page.locator("#download")).to_be_disabled()
                        expect(page.locator("#save")).to_be_disabled()
                        page.unroute("**" + source)
                self.assertEqual([], external)
            finally:
                browser.close()
        self.assertEqual(1, MaterialRasterPair.objects.count())
