"""Focused local studio UX checks; isolated browser/server, no app DB or API."""

import importlib.util
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright
from sources import SourceService, digest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("studio_server", ROOT / "serve.py")
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


class StudioCheck(unittest.TestCase):
    def setUp(self):
        cache = Path(tempfile.mkdtemp(prefix="yaparo-source-test-"))
        today = datetime.now(timezone.utc).date()
        tcmb = f'<Tarih_Date Tarih="{today.strftime("%d.%m.%Y")}"><Currency CurrencyCode="USD"><Unit>1</Unit><ForexSelling>50.0000</ForexSelling></Currency></Tarih_Date>'.encode()
        ecb = f'<Envelope xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref"><Cube><Cube time="{today.isoformat()}"><Cube currency="USD" rate="2"/><Cube currency="TRY" rate="100"/></Cube></Cube></Envelope>'.encode()
        self.ecb_body = ecb
        self.server.source_services = {
            "tcmb": SourceService(
                cache_path=cache / "tcmb.json", transport=lambda: tcmb, provider="tcmb"
            ),
            "ecb": SourceService(
                cache_path=cache / "ecb.json", transport=lambda: ecb, provider="ecb"
            ),
        }

    @classmethod
    def setUpClass(cls):
        cls.server = server_module.make_server()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.runtime = sync_playwright().start()
        cls.browser = cls.runtime.chromium.launch()
        cls.evidence = Path(tempfile.mkdtemp(prefix="yaparo-decision-"))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.runtime.stop()
        cls.server.shutdown()
        cls.server.server_close()
        print(f"Evidence: {cls.evidence}")

    def start_plan(self, page):
        page.goto(self.origin)
        page.get_by_role("button", name="Üç yaratıcı yönü keşfet").click()
        page.locator(".concept-card").nth(0).get_by_role(
            "button", name="Bu yönü seç"
        ).click()
        page.locator("#content-next").click()

    def test_full_flow_editor_reasons_and_fresh_reset(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        errors, outbound = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on(
            "request",
            lambda r: (
                outbound.append(r.url) if not r.url.startswith(self.origin) else None
            ),
        )
        page.goto(self.origin)
        page.screenshot(path=str(self.evidence / "start-desktop.png"), full_page=True)
        page.get_by_role("button", name="Üç yaratıcı yönü keşfet").click()
        self.assertEqual(page.locator(".concept-card").count(), 3)
        page.locator(".concept-card").nth(1).get_by_role(
            "button", name="Düzenle", exact=True
        ).click()
        page.locator("#edit-title").fill("Sana özel bir tasarım anı")
        page.locator("#edit-x").fill("20")
        page.get_by_role("button", name="Uygula ve geri dön").click()
        card = page.locator(".concept-card").nth(1)
        self.assertIn("Sana özel", card.inner_text())
        card.get_by_role("button", name="Bu yönü seç").click()
        page.screenshot(
            path=str(self.evidence / "creative-desktop.png"), full_page=True
        )
        page.locator("#content-next").click()
        page.locator(".economics > summary").click()
        page.locator("#fixture").select_option("demo")
        page.locator("#start").fill("2026-10-27")
        page.locator("#recommend").click()
        snap = page.evaluate("YaparoStudio.getSnapshot()")
        self.assertEqual(snap["plan"]["allocated"], 300000)
        self.assertEqual(page.locator("#recommended .channel-row").count(), 2)
        page.screenshot(path=str(self.evidence / "plan-desktop.png"), full_page=True)
        page.locator(".other-channels-box > summary").click()
        page.get_by_role(
            "button", name="TikTok Ads neden ve koşullar", exact=True
        ).click()
        self.assertIn("teknik minimum", page.locator("#guide-body").inner_text())
        page.locator("#guide-close").click()
        page.locator('[data-channel="meta_social"] input[type=number]').fill("1000")
        page.locator('[data-channel="meta_social"] input[type=number]').press("Tab")
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.unallocated"), 80000
        )
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.unallocated"), 0
        )
        page.locator("#budget").fill("10000")
        page.get_by_role("button", name="Planın tamamını gör").click()
        self.assertTrue(page.locator("#step-2").is_visible())
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.unallocated"), 680000
        )
        page.get_by_role("button", name="Planın tamamını gör").click()
        self.assertIn("Sana özel", page.locator("#review").inner_text())
        page.locator("#finish").click()
        self.assertIn("yapılmadı", page.locator("#finish-status").inner_text())
        self.assertEqual(errors, [])
        self.assertEqual(outbound, [])
        self.assertEqual(
            page.evaluate("localStorage.length + sessionStorage.length"), 0
        )
        page.close()

    def test_unknown_context_policy_and_conditional_questions(self):
        page = self.browser.new_page()
        page.goto(self.origin)
        page.locator("#communication").select_option("fundraising")
        self.assertTrue(
            page.get_by_label("İzin veya muafiyet belgesi mevcut mu?").is_visible()
        )
        page.get_by_role("button", name="Üç yaratıcı yönü keşfet").click()
        page.locator(".choose").nth(0).click()
        page.locator("#content-next").click()
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.allocated"), 0)
        self.assertIn("incelemesi", page.locator("#recommended").inner_text())
        page.locator('[data-step="0"]').nth(0).click()
        page.locator("#communication").select_option("product_service_intro")
        self.assertEqual(page.locator("#q-S1_F01").count(), 0)
        page.get_by_role("button", name="Üç yaratıcı yönü keşfet").click()
        page.locator(".choose").nth(0).click()
        page.locator("#content-next").click()
        page.locator("#region").fill("Ankara")
        page.locator(".economics > summary").click()
        page.locator("#fixture").select_option("unknown")
        page.locator("#recommend").click()
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.allocated"), 0)
        page.close()

    def test_mobile_literal_text_and_boundaries(self):
        page = self.browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(self.origin)
        page.locator("#brief").fill(
            '<img src="https://example.invalid/x" onerror="alert(1)"> sentetik tasarım'
        )
        page.get_by_role("button", name="Üç yaratıcı yönü keşfet").click()
        page.locator(".choose").nth(0).click()
        page.locator("#content-next").click()
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
        page.screenshot(path=str(self.evidence / "plan-mobile.png"), full_page=True)
        page.locator("#helper-toggle").click()
        self.assertTrue(page.locator("#chat-input").is_visible())
        page.locator("#chat-input").fill("Bütçe neden böyle?")
        page.get_by_role("button", name="Mesajı gönder").click()
        self.assertIn("ayrılmadı", page.locator("#chat-log").inner_text())
        self.assertEqual(page.locator('img[src*="example.invalid"]').count(), 0)
        page.reload()
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().brief"))
        page.close()
        with self.assertRaises(HTTPError) as denied:
            urlopen(self.origin + "/../../PROJECT.md")
        self.assertEqual(denied.exception.code, 404)
        with self.assertRaises(HTTPError) as host:
            urlopen(Request(self.origin, headers={"Host": "invalid.example"}))
        self.assertEqual(host.exception.code, 403)

    def test_interactive_brief_assistant_and_context_history(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        errors, outbound = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on(
            "request",
            lambda r: (
                outbound.append(r.url) if not r.url.startswith(self.origin) else None
            ),
        )
        page.goto(self.origin)
        page.get_by_role("button", name="☕ Kafe açılışı", exact=True).click()
        page.get_by_role("button", name="Üç yaratıcı yönü keşfet").click()
        self.assertIn("kahve", page.locator("#concepts").inner_text().lower())
        self.assertEqual(page.locator(".demo-illustration svg").count(), 3)
        page.locator(".choose").nth(0).click()
        page.locator("#content-next").click()
        initial = page.evaluate("YaparoStudio.getSnapshot()")
        self.assertTrue(initial["plan"]["interactive"])
        self.assertEqual(initial["plan"]["input"]["region"], "İzmir")
        self.assertGreater(initial["plan"]["allocated"], 0)
        page.locator("#helper-toggle").click()
        page.locator("#chat-input").fill("Bütçe 5000, 14 gün")
        page.get_by_role("button", name="Mesajı gönder").click()
        self.assertEqual(page.locator("#budget").input_value(), "3000")
        page.locator("#chat-log").get_by_role(
            "button", name="Öneriyi uygula", exact=True
        ).click()
        self.assertEqual(page.locator("#budget").input_value(), "5000")
        self.assertEqual(page.locator("#duration").input_value(), "14")
        current = page.evaluate("YaparoStudio.getSnapshot()")
        self.assertFalse(current["stale"])
        self.assertGreater(current["revision"], initial["revision"])
        self.assertEqual(current["creative"]["id"], initial["creative"]["id"])
        page.locator("#chat-input").fill("Bütçe 6000")
        page.get_by_role("button", name="Mesajı gönder").click()
        page.locator("#duration").fill("15")
        page.locator("#chat-log").get_by_role(
            "button", name="Öneriyi uygula", exact=True
        ).click()
        self.assertEqual(page.locator("#budget").input_value(), "5000")
        self.assertIn("Koşullar değişti", page.locator("#chat-log").inner_text())
        page.locator("#duration").fill("14")
        page.locator("#chat-input").fill("Daha sade olsun")
        page.get_by_role("button", name="Mesajı gönder").click()
        page.locator("#chat-log").get_by_role(
            "button", name="Öneriyi uygula", exact=True
        ).click()
        self.assertTrue(page.evaluate("YaparoStudio.getSnapshot().stale"))
        page.locator("#helper-toggle").click()
        page.locator('[data-step="1"]').nth(0).click()
        old_title = page.locator(".art-title").nth(0).inner_text()
        page.locator("#regenerate").click()
        self.assertNotEqual(page.locator(".art-title").nth(0).inner_text(), old_title)
        page.locator("#previous-trio").click()
        self.assertEqual(page.locator(".art-title").nth(0).inner_text(), old_title)
        page.locator("#content-next").click()
        page.screenshot(
            path=str(self.evidence / "dynamic-cafe-desktop.png"), full_page=True
        )
        self.assertEqual(errors, [])
        self.assertEqual(outbound, [])
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.model"), None)
        page.close()

    def test_source_refresh_provenance_and_live_fx_recompute(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1100})
        self.start_plan(page)
        page.get_by_text(
            "ECB çapraz referans USD/TRY · Güncel kayıt", exact=True
        ).wait_for()
        page.locator("#recommend").click()
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.fx.rate"), 50)
        self.server.source_services["ecb"].transport = lambda: self.ecb_body.replace(
            b'rate="100"', b'rate="104"'
        )
        self.server.source_services["ecb"].last_attempt = None
        page.locator("#source-refresh").click()
        page.get_by_text(
            "Son kayıt: 1 USD = 52,0000 TRY · ECB çapraz referans", exact=True
        ).wait_for()
        self.assertIn("52,0000", page.locator("#source-panel").inner_text())
        self.assertTrue(page.evaluate("YaparoStudio.getSnapshot().stale"))
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.fx.source"), "ecb"
        )
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.fx.rate"), 52)
        self.assertFalse(page.evaluate("YaparoStudio.getSnapshot().plan.publishable"))
        page.locator("#budget").fill("6000")
        page.locator("#recommend").click()
        # Public currency quotes are safely reusable; account forecasts cannot be.
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.fx.source"), "ecb"
        )
        expected_context = digest(page.evaluate("sourceContext()"))
        page.locator(
            f'#source-panel[data-context-hash="{expected_context}"]'
        ).wait_for()
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.fx.source"), "ecb"
        )
        page.locator("#fx-provider").select_option("tcmb")
        page.get_by_text(
            "TCMB gösterge satış USD/TRY · Güncel kayıt", exact=True
        ).wait_for()
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.fx.source"), "tcmb"
        )
        page.screenshot(
            path=str(self.evidence / "source-layer-desktop.png"), full_page=True
        )
        page.get_by_role("button", name="Planın tamamını gör").click()
        self.assertIn("TCMB gösterge satış", page.locator("#review").inner_text())
        page.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
