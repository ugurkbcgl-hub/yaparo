"""Measured automated synthetic rehearsal; no human completion-rate claim."""

import json
import os
import secrets
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from zipfile import ZipFile

from django.test import LiveServerTestCase, override_settings
from django.urls import reverse
from PIL import Image
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.campaigns.test_design_selection import SelectionFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True,
)
class DesignJourneyBrowserTests(SelectionFixture, LiveServerTestCase):
    def exercise(self, width):
        self.document.delete()  # This test's fresh synthetic unbound fixture only.
        password = secrets.token_urlsafe(32)
        self.owner.set_password(password)
        self.owner.save(update_fields=["password"])
        steps = []
        with TemporaryDirectory() as temp, sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": width, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(
                    self.live_server_url
                    + reverse("campaigns:detail", args=[self.draft.pk])
                )
                page.locator("#id_username").fill(self.owner.username)
                page.locator("#id_password").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                expect(
                    page.get_by_role("link", name="Marka ve tasarım seç", exact=True)
                ).to_be_visible()
                started = perf_counter()

                def record(name):
                    steps.append(
                        {
                            "step": name,
                            "elapsed_seconds": round(perf_counter() - started, 3),
                        }
                    )
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )

                page.get_by_role(
                    "link", name="Marka ve tasarım seç", exact=True
                ).click()
                record("campaign chooser")
                page.get_by_role(
                    "link", name=self.brand.name + " için tasarım oluştur", exact=True
                ).click()
                expect(
                    page.get_by_role("link", name="Kampanyanın tasarım seçimine dön")
                ).to_be_visible()
                record("owned same-workspace brand")
                page.get_by_role(
                    "button", name="Örnek çalışma oluştur", exact=True
                ).click()
                expect(
                    page.get_by_role("link", name="Kampanyanın tasarım seçimine dön")
                ).to_be_visible()
                record("create saved design")
                page.get_by_role("link", name="Görsel editörü aç").click()
                expect(page.locator("#save")).to_be_enabled()
                page.locator("#copy").fill("Kampanyaya dönen örnek başlık")
                page.locator("#save").click()
                expect(page.locator("#revision")).to_have_text("2")
                record("edit and save")
                page.get_by_role(
                    "link", name="Kampanyanın tasarım seçimine dön"
                ).click()
                expect(
                    page.get_by_text("Henüz marka ve tasarım seçilmedi.")
                ).to_be_visible()
                record("return without automatic selection")
                page.get_by_role("button", name="Bu tasarım kaydını seç").click()
                expect(
                    page.get_by_text("Seçili tasarım kaydı 2", exact=False)
                ).to_be_visible()
                record("explicit selection")
                page.get_by_role(
                    "link", name="Seçili tasarımı görüntüle ve indir"
                ).click()
                expect(page.get_by_role("button", name="PNG indir")).to_be_enabled()
                record("readonly preview")
                with page.expect_download() as item:
                    page.get_by_role("button", name="PNG indir").click()
                png = Path(temp) / "journey.png"
                item.value.save_as(png)
                with Image.open(png) as image:
                    self.assertEqual(image.size, (800, 800))
                record("PNG download")
                with page.expect_download() as item:
                    page.get_by_role(
                        "link", name="Kaynak bilgileriyle ZIP indir"
                    ).click()
                archive_path = Path(temp) / "journey.zip"
                item.value.save_as(archive_path)
                with ZipFile(BytesIO(archive_path.read_bytes())) as archive:
                    manifest = json.loads(archive.read("manifest.json"))
                    scene = json.loads(archive.read("scene.json"))
                    self.assertEqual(manifest["document"]["revision"], 2)
                    self.assertEqual(
                        scene["layers"][2]["text"], "Kampanyaya dönen örnek başlık"
                    )
                record("selected ZIP download")
                report = {
                    "kind": "automated synthetic rehearsal",
                    "width": width,
                    "elapsed_seconds": round(perf_counter() - started, 3),
                    "outcome": "completed",
                    "steps": steps,
                    "browser_errors": errors,
                    "human_observations": 0,
                }
                self.assertEqual(errors, [])
                output = os.environ.get("YAPARO_JOURNEY_REPORT_DIR")
                if output:
                    Path(output, "journey-" + str(width) + ".json").write_text(
                        json.dumps(report, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    page.screenshot(
                        path=str(Path(output) / ("journey-" + str(width) + ".png")),
                        full_page=True,
                    )
                print(json.dumps(report, ensure_ascii=True))
            finally:
                browser.close()
        self.assertEqual(self.draft.design_choices.count(), 1)
        self.assertEqual(self.draft.design_choices.first().snapshot.revision, 2)

    def test_desktop_journey(self):
        self.exercise(1440)

    def test_mobile_journey(self):
        self.exercise(390)
