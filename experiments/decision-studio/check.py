"""Focused local studio UX checks; isolated browser/server, no app DB or API."""

import importlib.util
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("studio_server", ROOT / "serve.py")
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


class StudioCheck(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
