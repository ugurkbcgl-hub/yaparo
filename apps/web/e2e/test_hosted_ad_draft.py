"""Saved-output draft editing, stale refusal and real PNG export in Chromium."""

import io
import os
import secrets
from hashlib import sha256
from pathlib import Path

from django.test import LiveServerTestCase
from django.urls import reverse
from PIL import Image
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.assets.raster_validation import normalize_raster
from growthtwin.modules.workspaces.models import (
    HostedAdDraft,
    HostedImageTrial,
    HostedTextTrial,
)
from growthtwin.modules.workspaces.test_hosted_ad_drafts import SavedTrialsFixture


class HostedAdBrowserTests(SavedTrialsFixture, LiveServerTestCase):
    def login(self, page, url, password):
        page.goto(self.live_server_url + url)
        page.locator("#id_username").fill(self.owner.username)
        page.locator("#id_password").fill(password)
        page.get_by_role("button", name="Giriş yap").click()

    def test_select_edit_save_reopen_stale_and_png_preserve_sources(self):
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        before_text = HostedTextTrial.objects.values().get()
        before_image = HostedImageTrial.objects.values().get()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1100})
                page = context.new_page()
                self.login(page, reverse("brands:hosted_image_trial"), password)
                page.get_by_role("link", name="Metinle birleştir ve düzenle").click()
                card = page.locator(".narrow-column > section.summary-card").filter(
                    has=page.get_by_role("heading", name="El yapımı seramik kupalar")
                )
                candidate = card.locator("input[name=candidate]").first.input_value()
                source = card.locator("input[name=source]").first.input_value()
                card.get_by_role(
                    "button", name="Bu ölçüyle oluştur — Özgün dikey · 768 × 1376"
                ).click()
                editor_url = page.url
                expect(
                    page.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                ).to_be_enabled()
                with page.expect_download() as event:
                    page.get_by_role("button", name="Kayıtlı taslağı PNG indir").click()
                first_png = Path(event.value.path()).read_bytes()
                self.assertTrue(event.value.suggested_filename.endswith("-v1.png"))
                old = page.context.new_page()
                old.goto(editor_url)
                expect(old.get_by_role("button", name="Taslağı kaydet")).to_be_enabled()
                page.get_by_label("Başlık").fill("Benim reklam başlığım")
                expect(
                    page.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                ).to_be_disabled()
                page.get_by_role("button", name="Taslağı kaydet").click()
                expect(page.locator("#ad-revision")).to_have_text("2")
                expect(
                    page.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                ).to_be_enabled()
                old.get_by_label("Başlık").fill("Eski sekmenin metni")
                old.get_by_role("button", name="Taslağı kaydet").click()
                expect(old.get_by_role("alert")).to_contain_text("Kayıt doğrulanamadı")
                expect(old.get_by_label("Başlık")).to_have_value("Eski sekmenin metni")
                expect(
                    old.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                ).to_be_disabled()
                token = page.locator(
                    "input[name=csrfmiddlewaretoken]"
                ).first.input_value()
                replay = page.request.post(
                    self.live_server_url + reverse("brands:hosted_ad_create"),
                    form={
                        "candidate": candidate,
                        "source": source,
                        "csrfmiddlewaretoken": token,
                    },
                    headers={"Origin": self.live_server_url},
                )
                self.assertEqual(replay.status, 200)
                page.reload()
                expect(page.get_by_label("Başlık")).to_have_value(
                    "Benim reklam başlığım"
                )
                expect(
                    page.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                ).to_be_enabled()
                with page.expect_download() as event:
                    page.get_by_role("button", name="Kayıtlı taslağı PNG indir").click()
                second_png = Path(event.value.path()).read_bytes()
                self.assertTrue(event.value.suggested_filename.endswith("-v2.png"))
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1100})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                    directory = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                    if directory:
                        page.screenshot(
                            path=str(Path(directory) / f"hosted-ad-{width}.png"),
                            full_page=True,
                        )
            finally:
                browser.close()
        self.assertNotEqual(first_png, second_png)
        with Image.open(io.BytesIO(second_png)) as image:
            self.assertEqual(image.size, (768, 1376))
            pixels = image.convert("RGBA")
            self.assertEqual(pixels.getpixel((100, 1200)), (36, 76, 59, 255))
            self.assertEqual(pixels.getpixel((10, 10)), (245, 237, 223, 255))
        draft = HostedAdDraft.objects.get()
        self.assertEqual(draft.revision, 2)
        self.assertEqual(draft.history.count(), 2)
        self.assertEqual(HostedTextTrial.objects.values().get(), before_text)
        self.assertEqual(HostedImageTrial.objects.values().get(), before_image)

    def test_missing_or_altered_image_disables_save_and_export(self):
        draft = self.create()
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        wrong_png = bytes(self.image.original)  # Valid PNG/dimensions, different hash.
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                self.login(
                    page, reverse("brands:hosted_ad_editor", args=[draft.pk]), password
                )
                pattern = "**/ai-trial/drafts/*/image/"
                for status, body in ((403, b"denied"), (200, wrong_png)):
                    page.route(
                        pattern,
                        lambda route, request, s=status, b=body: route.fulfill(
                            status=s, content_type="image/png", body=b
                        ),
                    )
                    page.reload()
                    expect(page.locator("#ad-status")).to_contain_text(
                        "Kaydedilmiş görsel doğrulanamadı"
                    )
                    expect(
                        page.get_by_role("button", name="Taslağı kaydet")
                    ).to_be_disabled()
                    expect(
                        page.get_by_role("button", name="Kayıtlı taslağı PNG indir")
                    ).to_be_disabled()
                    page.unroute(pattern)
            finally:
                browser.close()
        draft.refresh_from_db()
        self.assertEqual(draft.revision, 1)

    def test_explicit_square_and_portrait_export_keep_complete_photo(self):
        legacy = self.create()
        before = HostedAdDraft.objects.values().get(pk=legacy.pk)
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                self.login(page, reverse("brands:hosted_ad_choices"), password)
                for label, height in (
                    ("Kare · 1080 × 1080", 1080),
                    ("Dikey · 1080 × 1350", 1350),
                ):
                    page.goto(
                        self.live_server_url + reverse("brands:hosted_ad_choices")
                    )
                    card = page.locator(".narrow-column > section.summary-card").filter(
                        has=page.get_by_role(
                            "heading", name="El yapımı seramik kupalar"
                        )
                    )
                    card.get_by_role(
                        "button", name="Bu ölçüyle oluştur — " + label
                    ).click()
                    url = page.url
                    expect(
                        page.get_by_text(label + " · Kayıt", exact=False)
                    ).to_be_visible()
                    expect(page.locator("#ad-export")).to_be_enabled()
                    page.get_by_label("Başlık").fill("Bu ölçü için reklam")
                    page.locator("#ad-save").click()
                    expect(page.locator("#ad-revision")).to_have_text("2")
                    expect(page.locator("#ad-export")).to_be_enabled()
                    with page.expect_download() as event:
                        page.locator("#ad-export").click()
                    png = Path(event.value.path()).read_bytes()
                    with Image.open(io.BytesIO(png)) as image:
                        self.assertEqual(image.size, (1080, height))
                        # Entire portrait is fitted, with side space, not stretched/cropped.
                        self.assertEqual(
                            image.getpixel((540, height - 10))[:3], (36, 76, 59)
                        )
                        self.assertEqual(
                            image.getpixel((10, height - 10))[:3], (245, 237, 223)
                        )
                        self.assertEqual(
                            image.getpixel((540, height - 450))[:3], (232, 223, 204)
                        )
                    page.reload()
                    expect(page.get_by_label("Başlık")).to_have_value(
                        "Bu ölçü için reklam"
                    )
                    page.set_viewport_size({"width": 390, "height": 900})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                    self.assertEqual(page.url, url)
            finally:
                browser.close()
        self.assertEqual(HostedAdDraft.objects.values().get(pk=legacy.pk), before)
        self.assertEqual(HostedAdDraft.objects.count(), 3)

    def test_legacy_overlay_preserves_source_alpha_pixels(self):
        with Image.open(io.BytesIO(bytes(self.image.png))) as source:
            rgba = source.convert("RGBA")
            rgba.putpixel((10, 1200), (200, 100, 50, 0))
            rgba.putpixel((11, 1200), (100, 80, 60, 128))
            stream = io.BytesIO()
            rgba.save(stream, format="PNG")
        original = stream.getvalue()
        normalized = normalize_raster(original, declared_media_type="image/png")
        HostedImageTrial.objects.filter(pk=self.image.pk).update(
            original=original,
            png=normalized.png,
            original_sha256=sha256(original).hexdigest(),
            png_sha256=normalized.derivative_sha256,
            normalization_tool=normalized.tool,
        )
        draft = self.create()
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                self.login(
                    page, reverse("brands:hosted_ad_editor", args=[draft.pk]), password
                )
                expect(page.locator("#ad-export")).to_be_enabled()
                with page.expect_download() as event:
                    page.locator("#ad-export").click()
                with Image.open(event.value.path()) as exported:
                    pixels = exported.convert("RGBA")
                    self.assertEqual(pixels.getpixel((10, 1200))[3], 0)
                    self.assertEqual(pixels.getpixel((11, 1200))[3], 128)
                    self.assertEqual(pixels.getpixel((100, 1200)), (36, 76, 59, 255))
            finally:
                browser.close()
