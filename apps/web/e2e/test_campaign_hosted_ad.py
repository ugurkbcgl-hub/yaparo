"""Choose, pin, edit elsewhere and explicitly reselect through the actual UI."""

import json
import secrets
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.campaigns import hosted_ad_selection as selection
from growthtwin.modules.campaigns.models import (
    CampaignHostedAdChoice,
    WorkspaceCampaignDraft,
)
from growthtwin.modules.campaigns.test_hosted_ad_selection import CampaignAdFixture


class CampaignHostedAdBrowserTests(CampaignAdFixture, LiveServerTestCase):
    def test_explicit_choice_pinned_preview_and_reselection(self):
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        before = WorkspaceCampaignDraft.objects.values().get(pk=self.plan.pk)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1100})
                page = context.new_page()
                page.goto(
                    self.live_server_url
                    + reverse("campaigns:detail", args=[self.plan.pk])
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                page.get_by_role(
                    "link", name="AI reklam görselini seç veya önizle"
                ).click()
                page.get_by_role("button", name="Bu kaydı kampanyaya seç").click()
                page.get_by_role("link", name="Seçili kaydı önizle").click()
                preview_url = page.url
                expect(page.get_by_label("Başlık", exact=True)).to_have_value(
                    "El yapımı seramik kupalar"
                )
                expect(page.get_by_label("Başlık", exact=True)).not_to_be_editable()
                expect(page.locator("#ad-save")).not_to_be_visible()
                expect(page.locator("#ad-package")).to_be_enabled()
                expect(page.locator("#ad-export")).to_be_enabled()
                with page.expect_download() as event:
                    page.locator("#ad-export").click()
                first = Path(event.value.path()).read_bytes()
                edit = context.new_page()
                edit.goto(
                    self.live_server_url
                    + reverse("brands:hosted_ad_editor", args=[self.ad.pk])
                )
                expect(edit.locator("#ad-save")).to_be_enabled()
                edit.get_by_label("Başlık").fill("Sonraki kayıt")
                edit.locator("#ad-save").click()
                expect(edit.locator("#ad-revision")).to_have_text("2")
                page.reload()
                expect(page.get_by_label("Başlık", exact=True)).to_have_value(
                    "El yapımı seramik kupalar"
                )
                expect(page.locator("#ad-export")).to_be_enabled()
                with page.expect_download() as event:
                    page.locator("#ad-export").click()
                self.assertEqual(
                    sha256(Path(event.value.path()).read_bytes()).hexdigest(),
                    sha256(first).hexdigest(),
                )
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1100})
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                page.get_by_role("link", name="← Kampanya görsel seçimine dön").click()
                page.get_by_role("button", name="Bu kaydı kampanyaya seç").click()
                page.get_by_role("link", name="Seçili kaydı önizle").click()
                expect(page.get_by_label("Başlık", exact=True)).to_have_value(
                    "Sonraki kayıt"
                )
                page.goto(preview_url)
                expect(
                    page.get_by_text("Görsel seçimi doğrulanamadı.", exact=False)
                ).to_be_visible()
            finally:
                browser.close()
        self.assertEqual(CampaignHostedAdChoice.objects.count(), 2)
        self.assertEqual(
            WorkspaceCampaignDraft.objects.values().get(pk=self.plan.pk), before
        )

    def package_login(self, page, password):
        page.goto(
            self.live_server_url
            + reverse("campaigns:hosted_ad_preview", args=[self.plan.pk, 1])
        )
        page.locator("#id_username").fill(self.owner.username)
        page.locator("#id_password").fill(password)
        page.get_by_role("button", name="Giriş yap").click()

    def test_six_file_package_pins_old_revision_then_denies_reselection(self):
        self.choose()
        self.ad = self.save(self.ad, title="Sonraki düzenleme")
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context()
                page = context.new_page()
                self.package_login(page, password)
                expect(page.locator("#ad-package")).to_be_enabled()
                with page.expect_download() as event:
                    page.locator("#ad-export").click()
                png = Path(event.value.path()).read_bytes()
                with page.expect_download() as event:
                    page.locator("#ad-package").click()
                self.assertEqual(
                    event.value.suggested_filename,
                    f"yaparo-campaign-{self.plan.pk}-selection-1.zip",
                )
                with ZipFile(event.value.path()) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(
                        set(archive.namelist()),
                        {
                            "ad.png",
                            "source.png",
                            "draft.json",
                            "manifest.json",
                            "README.txt",
                            "campaign.json",
                        },
                    )
                    self.assertEqual(archive.read("ad.png"), png)
                    self.assertEqual(archive.read("source.png"), bytes(self.image.png))
                    manifest = json.loads(archive.read("manifest.json"))
                    campaign = json.loads(archive.read("campaign.json"))
                    self.assertEqual(
                        manifest["schema"], "yaparo-campaign-ai-package-v1"
                    )
                    self.assertEqual(manifest["campaign_selection"], campaign)
                    self.assertEqual(campaign["campaign_id"], str(self.plan.pk))
                    self.assertEqual(
                        campaign["snapshot_sha256"],
                        sha256(archive.read("draft.json")).hexdigest(),
                    )
                    snapshot = json.loads(archive.read("draft.json"))
                    self.assertEqual(snapshot["revision"], 1)
                    self.assertEqual(
                        snapshot["content"]["title"], "El yapımı seramik kupalar"
                    )
                    self.assertEqual(
                        set(manifest["files"]),
                        set(archive.namelist()) - {"manifest.json"},
                    )
                    for name, meta in manifest["files"].items():
                        data = archive.read(name)
                        self.assertEqual(
                            meta,
                            {"bytes": len(data), "sha256": sha256(data).hexdigest()},
                        )
                other = context.new_page()
                other.goto(
                    self.live_server_url
                    + reverse("campaigns:hosted_ad_choose", args=[self.plan.pk])
                )
                other.get_by_role("button", name="Bu kaydı kampanyaya seç").click()
                downloads = []
                page.on("download", lambda event: downloads.append(event))
                page.locator("#ad-package").click()
                expect(page.locator("#package-status")).to_contain_text(
                    "Paket doğrulanamadı"
                )
                self.assertEqual(downloads, [])
            finally:
                browser.close()

    def test_campaign_package_denies_changed_context_and_snapshot_bytes(self):
        choice = self.choose()
        data = selection.package_snapshot(
            owner=self.owner, campaign_id=self.plan.pk, version=choice.version
        )
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        altered = json.loads(data["ad_json"])
        altered["source_manifest"]["text"]["usage"] = {"forged": 1}
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                self.package_login(page, password)
                downloads = []
                page.on("download", lambda event: downloads.append(event))
                pattern = "**/ai-visual/1/package.json"
                for payload in (
                    {
                        **data,
                        "campaign_selection": {
                            **data["campaign_selection"],
                            "campaign_id": "99999",
                        },
                    },
                    {**data, "ad_json": json.dumps(altered, ensure_ascii=False)},
                ):
                    page.route(
                        pattern,
                        lambda route, request, body=json.dumps(payload): route.fulfill(
                            status=200, content_type="application/json", body=body
                        ),
                    )
                    expect(page.locator("#ad-package")).to_be_enabled()
                    page.locator("#ad-package").click()
                    expect(page.locator("#package-status")).to_contain_text(
                        "Paket doğrulanamadı"
                    )
                    self.assertEqual(downloads, [])
                    page.unroute(pattern)
                    page.reload()
            finally:
                browser.close()
