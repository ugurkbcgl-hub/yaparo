"""Exercise prototype continuity, mobile access and network/file boundaries offline."""

import importlib.util
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("journey_server", ROOT / "serve.py")
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


class JourneyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = server_module.make_server()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.runtime = sync_playwright().start()
        cls.browser = cls.runtime.chromium.launch()
        cls.evidence = Path(tempfile.mkdtemp(prefix="yaparo-journey-"))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.runtime.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def test_flow_retains_editor_and_brief_history(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        errors, unexpected = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "request",
            lambda request: (
                unexpected.append(request.url)
                if not request.url.startswith(self.origin + "/")
                else None
            ),
        )
        page.goto(self.origin)
        page.screenshot(path=str(self.evidence / "start.png"), full_page=True)
        page.get_by_role("button", name="Bir işletmeyi tanıt").click()
        original_brief = page.locator("#brief").input_value()
        page.get_by_role("button", name="Üç yaklaşımı keşfet").click()
        self.assertEqual(page.locator(".concept-card").count(), 3)
        page.locator(".concept-card").nth(1).get_by_role(
            "button", name="Düzenle", exact=True
        ).click()
        page.locator("#edit-title").fill("Bana özel sakin bir mola")
        page.locator("#edit-x").fill("20")
        page.locator("#edit-x").dispatch_event("input")
        page.get_by_role("button", name="Uygula ve içeriğe dön").click()
        card = page.locator(".concept-card").nth(1)
        self.assertIn("Bana özel", card.inner_text())
        card.get_by_role("button", name="Benzerini gör").click()
        card.get_by_role("button", name="Son düzenlemeyi geri al").click()
        self.assertIn("Bana özel", card.inner_text())
        page.screenshot(path=str(self.evidence / "concepts.png"), full_page=True)
        page.get_by_role("button", name="Yeni üçlü gör").click()
        page.get_by_role("button", name="Önceki üçlü").click()
        self.assertIn("Bana özel", page.locator(".concept-card").nth(1).inner_text())
        page.get_by_role("button", name="Reklamını planla →", exact=True).click()
        page.locator("#audience").fill("Sentetik yerel kahveseverler")
        page.locator("#destination").fill("Örnek tanıtım sayfasını ziyaret edecek")
        page.locator("#google").fill("75")
        page.locator("#google").dispatch_event("input")
        self.assertEqual(page.locator("#meta-label").inner_text(), "%25")
        page.get_by_role("button", name="Planın özetini gör").click()
        self.assertIn("Google Ads %75", page.locator("#review-values").inner_text())
        self.assertIn("Bana özel", page.locator("#final-creative").inner_text())
        page.get_by_role("button", name="Taslak deneyimini tamamla").click()
        self.assertIn("yayını yapılmadı", page.locator("#finish-status").inner_text())
        page.screenshot(path=str(self.evidence / "summary.png"), full_page=True)
        page.get_by_role("button", name="1 İsteğini anlat").click()
        page.locator("#brief").fill(
            "Yeni bir seramik koleksiyonu için sentetik tanıtım istiyorum."
        )
        page.get_by_role("button", name="Üç yaklaşımı keşfet").click()
        page.get_by_role("button", name="Önceki üçlü").click()
        self.assertEqual(page.locator("#brief-summary").inner_text(), original_brief)
        self.assertIn("Bana özel", page.locator(".concept-card").nth(1).inner_text())
        page.reload()
        self.assertEqual(page.locator("#brief").input_value(), "")
        self.assertEqual(
            page.evaluate("localStorage.length + sessionStorage.length"), 0
        )
        self.assertEqual(errors, [])
        self.assertEqual(unexpected, [])
        page.close()

    def test_mobile_helper_and_no_overflow(self):
        page = self.browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(self.origin)
        page.locator("#helper-toggle").click()
        self.assertTrue(page.locator("#chat-input").is_visible())
        page.locator("#chat-input").fill("Neden bu kanallar?")
        page.get_by_role("button", name="Mesajı gönder").click()
        self.assertIn("%100", page.locator("#chat-log").inner_text())
        page.get_by_role("button", name="Yardımcıyı kapat").click()
        page.locator("#brief").fill(
            "<img src=x onerror=alert(1)> sentetik bir tanıtım örneği istiyorum."
        )
        page.get_by_role("button", name="Üç yaklaşımı keşfet").click()
        self.assertEqual(page.locator("#brief-summary img").count(), 0)
        self.assertTrue(
            page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        )
        page.screenshot(path=str(self.evidence / "mobile.png"), full_page=True)
        page.close()

    def test_server_exposes_only_allowlisted_gets(self):
        with urlopen(self.origin) as response:
            self.assertIn(
                "connect-src 'none'", response.headers["Content-Security-Policy"]
            )
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        for path in ("/serve.py", "/../../PROJECT.md", "/.env"):
            with self.assertRaises(HTTPError) as raised:
                urlopen(self.origin + path)
            self.assertEqual(raised.exception.code, 404)
        for request, code in (
            (Request(self.origin, data=b"synthetic"), 501),
            (Request(self.origin, headers={"Host": "untrusted.example"}), 403),
        ):
            with self.assertRaises(HTTPError) as raised:
                urlopen(request)
            self.assertEqual(raised.exception.code, code)


if __name__ == "__main__":
    result = unittest.main(exit=False)
    print(
        json.dumps(
            {
                "evidence": str(JourneyTest.evidence),
                "passed": result.result.wasSuccessful(),
            }
        )
    )
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
