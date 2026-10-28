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
        self.assertIn("Toplam %100", page.locator("#geo-total").inner_text())
        page.get_by_role("button", name="Planın özetini gör").click()
        self.assertIn("Google Ads %50.0", page.locator("#review-values").inner_text())
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
        self.assertIn("pay ayırmaz", page.locator("#chat-log").inner_text())
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

    def test_radius_bounds_and_geo_budget_filter(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1100})
        page.goto(self.origin)
        page.get_by_role("button", name="Bir işletmeyi tanıt").click()
        page.get_by_role("button", name="Üç yaklaşımı keşfet").click()
        page.locator(".choose").first.click()
        page.locator("#content-next").click()
        page.locator("#geo-mode").select_option("radius")
        self.assertTrue(page.locator("#geo-radius").is_visible())
        self.assertTrue(page.locator("#region").is_disabled())
        for radius in (1, 800, 37):
            page.locator("#radius-number").fill(str(radius))
            self.assertEqual(page.locator("#radius-range").input_value(), str(radius))
            self.assertIn(f"{radius} km", page.locator("#geo-status").inner_text())
            self.assertIn("%100", page.locator("#geo-total").inner_text())
            self.assertEqual(page.locator(".geo-unverified").count(), 12)
            for excluded in page.locator(".geo-unverified").all():
                self.assertEqual(
                    excluded.locator("input[type=number]").input_value(), "0.00"
                )
        for radius in ("0", "801", "1.5", ""):
            page.locator("#radius-number").fill(radius)
            self.assertEqual(page.locator("#radius-number").input_value(), radius)
            self.assertIn("Toplam %0", page.locator("#geo-total").inner_text())
            self.assertEqual(page.locator("#google").input_value(), "0")
        page.locator("#radius-number").fill("37")
        page.locator("#geo-center").select_option("ankara")
        self.assertEqual(page.locator("#latitude").input_value(), "39.9179")
        page.locator("#latitude").fill("99")
        self.assertIn("Toplam %0", page.locator("#geo-total").inner_text())
        page.locator("#geo-center").select_option("istanbul")
        page.locator("#audience").fill("Sentetik örnek yerel kitle")
        page.locator("#destination").fill("Örnek tanıtım sayfası")
        page.screenshot(path=str(self.evidence / "radius-desktop.png"), full_page=True)
        page.locator("#plan-form button[type=submit]").click()
        summary = page.locator("#review-values").inner_text()
        self.assertIn("37 km ∩ Türkiye", summary)
        self.assertIn("29.04000", summary)
        self.assertIn("Meta:", summary)
        self.assertIn("TikTok:", summary)
        page.get_by_role("button", name="Planı düzenle", exact=True).click()
        page.locator("#radius-number").fill("801")
        self.assertTrue(page.get_by_role("button", name="4 Son kontrol").is_disabled())
        self.assertIn("Toplam %0", page.locator("#geo-total").inner_text())
        page.locator("#radius-number").fill("37")
        page.locator("#plan-form button[type=submit]").click()
        page.get_by_role("button", name="Planı düzenle", exact=True).click()
        page.locator("#geo-map").click(position={"x": 100, "y": 100})
        self.assertTrue(page.get_by_role("button", name="4 Son kontrol").is_disabled())
        page.locator("#geo-mode").select_option("country")
        self.assertIn("Türkiye geneli", page.locator("#geo-status").inner_text())
        self.assertTrue(page.locator("#radius-number").is_disabled())
        page.locator("#geo-mode").select_option("radius")
        self.assertEqual(page.locator("#radius-number").input_value(), "37")
        page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(
            page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        )
        page.screenshot(path=str(self.evidence / "radius-mobile.png"), full_page=True)
        page.locator("#geo-mode").select_option("area")
        page.locator("#region").fill(" ")
        self.assertIn("Toplam %0", page.locator("#geo-total").inner_text())
        page.close()

    def test_turkey_intersection_and_scenario_choices(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1100})
        page.goto(self.origin)
        page.get_by_role("button", name="Bir işletmeyi tanıt").click()
        page.get_by_role("button", name="Üç yaklaşımı keşfet").click()
        page.locator(".choose").first.click()
        page.locator("#content-next").click()
        page.locator("#geo-mode").select_option("radius")
        page.locator("#latitude").fill("41.677")
        page.locator("#longitude").fill("26.555")
        page.locator("#radius-number").fill("80")
        proof = page.evaluate("""() => {
            const s=YaparoGeo.snapshot();
            return {has:s!==null,area:s?.areaKm2,raw:s?.rawAreaKm2,
              outside:s?polygonClipping.difference(s.polygons,YaparoTurkey.geometry.coordinates).length:null,
              center:YaparoGeo.inside([26.555,41.677]),
              verified:s?.operationalBoundaryVerified,
              cents:s?.channels.reduce((n,c)=>n+c.amountCents,0)};
        }""")
        self.assertTrue(proof["has"])
        self.assertTrue(proof["center"])
        self.assertGreater(proof["area"], 0)
        self.assertLess(proof["area"], proof["raw"] * 0.9)
        self.assertEqual(proof["outside"], 0)
        self.assertFalse(proof["verified"])
        self.assertEqual(proof["cents"], 300000)
        self.assertEqual(page.locator(".channel-line").count(), 14)
        page.locator('[data-channel="microsoft"] input[type=checkbox]').uncheck()
        self.assertTrue(
            page.locator('[data-channel="microsoft"] input[type=checkbox]').evaluate(
                "el=>el===document.activeElement"
            )
        )
        self.assertEqual(page.locator("#google").input_value(), "100")
        page.locator('[data-channel="google"] input[type=checkbox]').uncheck()
        self.assertIn("Toplam %0", page.locator("#geo-total").inner_text())
        self.assertIsNone(page.evaluate("YaparoGeo.snapshot()"))
        page.locator('[data-channel="google"] input[type=checkbox]').check()
        page.locator('[data-channel="microsoft"] input[type=checkbox]').check()
        page.locator('[data-channel="microsoft"] input[type=number]').fill("90.91")
        shares = page.evaluate("YaparoGeo.snapshot().channels.map(c=>c.amountCents)")
        self.assertEqual(sum(shares), 300000)
        self.assertGreater(shares[1], shares[0] * 9)
        page.locator("#geo-mode").select_option("country")
        first = page.evaluate(
            "YaparoGeo.snapshot().channels.reduce((n,c)=>n+c.impressions,0)"
        )
        page.locator("#budget").fill("6000")
        second = page.evaluate(
            "YaparoGeo.snapshot().channels.reduce((n,c)=>n+c.impressions,0)"
        )
        self.assertAlmostEqual(second, first * 2)
        page.locator(".mixer-help>summary").click()
        page.locator(".scenario-assumptions summary").click()
        page.locator("#scenario-cpm").fill("200")
        third = page.evaluate(
            "YaparoGeo.snapshot().channels.reduce((n,c)=>n+c.impressions,0)"
        )
        self.assertAlmostEqual(third, second / 2)
        page.locator("#geo-mode").select_option("radius")
        page.locator("#latitude").fill("36.2")
        page.locator("#longitude").fill("37.16")
        self.assertIn("Toplam %0", page.locator("#geo-total").inner_text())
        self.assertIsNone(page.evaluate("YaparoGeo.snapshot()"))
        page.locator("#geo-center").select_option("ankara")
        page.locator("#radius-number").fill("80")
        page.locator("#scenario-density").fill("1")
        page.locator("#scenario-frequency").fill("1")
        big = page.evaluate(
            "YaparoGeo.snapshot().channels.reduce((n,c)=>n+c.impressions,0)"
        )
        page.locator("#radius-number").fill("1")
        small = page.evaluate(
            "YaparoGeo.snapshot().channels.reduce((n,c)=>n+c.impressions,0)"
        )
        self.assertLess(small, big)
        page.locator("#radius-number").fill("80")
        page.locator("#geo-center").select_option("custom")
        page.locator("#latitude").fill("41.677")
        page.locator("#longitude").fill("26.555")
        page.screenshot(path=str(self.evidence / "turkey-channels.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(
            page.evaluate("document.documentElement.scrollWidth<=innerWidth")
        )
        page.screenshot(path=str(self.evidence / "turkey-mobile.png"), full_page=True)
        page.close()

    def test_percentage_mixer_rebalance_drag_and_booklet(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1100})
        page.goto(self.origin)
        page.get_by_role("button", name="Bir işletmeyi tanıt").click()
        page.get_by_role("button", name="Üç yaklaşımı keşfet").click()
        page.locator(".choose").first.click()
        page.locator("#content-next").click()
        google = page.locator('[data-channel="google"] input[type=number]')
        microsoft = page.locator('[data-channel="microsoft"] input[type=number]')
        google.fill("70")
        self.assertEqual(microsoft.input_value(), "30.00")
        page.locator("#geo-mode").select_option("radius")
        page.locator("#latitude").fill("")
        self.assertIsNone(page.evaluate("YaparoGeo.snapshot()"))
        self.assertIn("Dağıtılan ₺0", page.locator("#allocation-money").inner_text())
        page.locator("#latitude").fill("41.005")
        self.assertEqual(google.input_value(), "70.00")
        self.assertEqual(microsoft.input_value(), "30.00")
        self.assertEqual(page.locator(".pool-group").count(), 3)
        self.assertEqual(page.locator(".channel-line").count(), 14)
        self.assertEqual(page.locator(".channel-inline-details[open]").count(), 0)
        page.evaluate(
            "window.retainedRange=document.querySelector('[data-channel=google] input[type=range]')"
        )
        bar = page.locator('[data-channel="google"] input[type=range]')
        for value in ("75", "80", "33.33", "100", "0", "50"):
            bar.fill(value)
            bar.dispatch_event("input")
            result = page.evaluate(
                """() => ({same:retainedRange===document.querySelector('[data-channel=google] input[type=range]'),sum:YaparoGeo.snapshot().channels.reduce((n,c)=>n+Math.round(c.share*100),0),cents:YaparoGeo.snapshot().channels.reduce((n,c)=>n+c.amountCents,0)})"""
            )
            self.assertTrue(result["same"])
            self.assertEqual(result["sum"], 10000)
            self.assertEqual(result["cents"], 300000)
        google.fill("101")
        self.assertIsNone(page.evaluate("YaparoGeo.snapshot()"))
        self.assertIn("Geçerli paylar", page.locator("#geo-total").inner_text())
        self.assertIn("Dağıtılan ₺0", page.locator("#allocation-money").inner_text())
        google.fill("33.33")
        self.assertEqual(microsoft.input_value(), "66.67")
        page.locator('[data-channel="google"] .channel-book').click()
        self.assertTrue(page.locator("#channel-guide").is_visible())
        self.assertEqual(
            page.locator("#channel-guide-title").inner_text(), "Google Ads"
        )
        self.assertIn(
            "gerçek platform tahmini değildir",
            page.locator("#channel-guide-content").inner_text(),
        )
        page.get_by_role("button", name="Kanal rehberini kapat").click()
        page.locator("#geo-mode").select_option("country")
        google.fill("33.33")
        total = page.evaluate(
            "YaparoGeo.snapshot().channels.reduce((n,c)=>n+Math.round(c.share*100),0)"
        )
        self.assertEqual(total, 10000)
        page.locator("#audience").fill("Sentetik kitle")
        page.locator("#destination").fill("Örnek sayfa")
        page.locator("#plan-form button[type=submit]").click()
        page.get_by_role("button", name="Planı düzenle", exact=True).click()
        google.fill("44.44")
        self.assertTrue(page.get_by_role("button", name="4 Son kontrol").is_disabled())
        page.locator("#plan-form button[type=submit]").click()
        self.assertIn("Google Ads %44.44", page.locator("#review-values").inner_text())
        page.get_by_role("button", name="Planı düzenle", exact=True).click()
        page.screenshot(
            path=str(self.evidence / "percentage-desktop.png"), full_page=True
        )
        page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(
            page.evaluate("document.documentElement.scrollWidth<=innerWidth")
        )
        page.screenshot(
            path=str(self.evidence / "percentage-mobile.png"), full_page=True
        )
        page.close()

    def test_selected_pool_all_channels_and_fresh_suggestion(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1100})
        unexpected = []
        page.on(
            "request",
            lambda request: (
                unexpected.append(request.url)
                if not request.url.startswith(self.origin + "/")
                else None
            ),
        )
        page.goto(self.origin)
        page.get_by_role("button", name="Bir işletmeyi tanıt").click()
        page.get_by_role("button", name="Üç yaklaşımı keşfet").click()
        page.locator(".choose").first.click()
        page.locator("#content-next").click()
        self.assertEqual(
            page.locator("#selected-channel-rows .channel-line").count(), 2
        )
        self.assertEqual(page.locator(".channel-pool .channel-line").count(), 12)
        self.assertEqual(
            page.locator('input[type=range][aria-label$="pay çubuğu"]:visible').count(),
            2,
        )
        meta = page.locator('[data-channel="meta"] input[type=checkbox]')
        self.assertTrue(meta.is_enabled())
        meta.check()
        self.assertEqual(
            page.locator("#selected-channel-rows [data-channel=meta]").count(), 1
        )
        snap = page.evaluate("YaparoGeo.snapshot()")
        self.assertTrue(snap["manualUnverifiedScenario"])
        self.assertFalse(
            next(c for c in snap["channels"] if c["id"] == "meta")["geoEligible"]
        )
        self.assertEqual(sum(c["amountCents"] for c in snap["channels"]), 300000)
        meta.uncheck()
        self.assertEqual(page.locator(".channel-pool [data-channel=meta]").count(), 1)
        self.assertFalse(
            page.locator("[data-channel=meta] input[type=range]").is_visible()
        )
        for checkbox in page.locator(".channel-line input[type=checkbox]").all():
            checkbox.check()
        self.assertEqual(
            page.locator("#selected-channel-rows .channel-line").count(), 14
        )
        self.assertEqual(page.locator(".channel-pool .channel-line").count(), 0)
        self.assertLess(page.locator(".selected-mix").bounding_box()["height"], 520)
        self.assertEqual(
            sum(
                round(c["share"] * 100)
                for c in page.evaluate("YaparoGeo.snapshot().channels")
            ),
            10000,
        )
        page.locator("#ai-distribution").click()
        first = page.evaluate("YaparoGeo.snapshot().suggestion")
        self.assertEqual(first["revision"], 1)
        self.assertFalse(first["externalQuery"])
        self.assertIsNone(first["provider"])
        self.assertEqual(
            page.locator("#selected-channel-rows .channel-line").count(), 2
        )
        self.assertIn(
            "neden", page.locator("#suggestion-explanation").inner_text().lower()
        )
        page.locator("[data-channel=google] input[type=number]").fill("77")
        self.assertIn("değiştirildi", page.locator("#suggestion-status").inner_text())
        page.locator("#geo-mode").select_option("country")
        page.locator("#goal").select_option("awareness")
        page.locator("#budget").fill("2000")
        page.locator("#ai-distribution").click()
        second = page.evaluate("YaparoGeo.snapshot()")
        self.assertEqual(second["suggestion"]["revision"], 2)
        self.assertNotEqual(first["id"], second["suggestion"]["id"])
        self.assertEqual(second["suggestion"]["context"]["budget"], 2000)
        self.assertEqual(second["suggestion"]["context"]["goal"], "awareness")
        self.assertEqual(second["suggestion"]["context"]["geo"]["mode"], "country")
        self.assertEqual(len(second["channels"]), 3)
        self.assertTrue(all(c["geoEligible"] for c in second["channels"]))
        page.locator("#ai-distribution").click()
        third = page.evaluate("YaparoGeo.snapshot().suggestion")
        self.assertEqual(third["revision"], 3)
        self.assertFalse(third["stale"])
        page.locator("#budget").fill("500")
        page.locator("#ai-distribution").click()
        fourth = page.evaluate("YaparoGeo.snapshot()")
        self.assertEqual(fourth["suggestion"]["revision"], 4)
        self.assertEqual(len(fourth["channels"]), 2)
        self.assertEqual(sum(c["amountCents"] for c in fourth["channels"]), 50000)
        page.locator("#suggestion-explanation").evaluate("el=>el.open=false")
        page.locator("#mixer-view").click()
        frame = page.locator("#plan-form>.plan-grid>.panel").first
        self.assertFalse(frame.is_visible())
        self.assertLess(
            page.locator("#distribution-panel").bounding_box()["height"], 750
        )
        page.locator("#distribution-panel").screenshot(
            path=str(self.evidence / "compact-selection.png")
        )
        page.locator("#plan-form button[type=submit]").click()
        self.assertTrue(frame.is_visible())
        page.locator("#audience").fill("Sentetik örnek kitle")
        page.locator("#destination").fill("Örnek tanıtım sayfası")
        page.locator("#mixer-view").click()
        page.locator("#ai-distribution").click()
        self.assertEqual(
            page.evaluate("YaparoGeo.snapshot().suggestion.context.audience"),
            "Sentetik örnek kitle",
        )
        page.locator("#suggestion-explanation").evaluate("el=>el.open=false")
        page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(
            page.evaluate("document.documentElement.scrollWidth<=innerWidth")
        )
        page.screenshot(path=str(self.evidence / "compact-mobile.png"), full_page=True)
        self.assertEqual(unexpected, [])
        page.close()

    def test_static_asset_integrity(self):
        import hashlib

        hashes = json.loads((ROOT / "asset-hashes.json").read_text())
        for name, expected in hashes.items():
            target = (
                ROOT / "dist" / ("vendor" if name.startswith("polygon-") else "") / name
            )
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), expected)

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
