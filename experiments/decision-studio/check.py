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

    def settle_plan(self, page):
        page.get_by_text(
            "ECB çapraz referans USD/TRY · Güncel kayıt", exact=True
        ).wait_for()
        page.locator("#recommend").click()

    def complete_brief(
        self,
        page,
        *,
        communication="product_service_intro",
        business="local_retail",
        sector="fashion_beauty_lifestyle",
        destination="physical_store",
        action="visit_store",
        mode="paid",
        description=None,
        submit=True,
    ):
        """Choose intent/response first, then fill the revealed context form."""
        family = {
            "launch": "product_service_intro",
            "education": "membership",
            "celebration": "announcement",
            "public_issue": "reputation",
        }.get(communication, communication)
        page.locator(f'[data-purpose="{family}"]').click()
        # The subtype control is contextual; choose a valid initial response to reveal it.
        if family != communication:
            page.locator("#action-choices button").first.click()
            page.locator("#work-kind").select_option(communication)
        page.locator(f'[data-action="{action}"]').click()
        page.locator("#business").select_option(business)
        page.locator("#sector").select_option(sector)
        if page.locator("#q-S1_B02").is_visible():
            page.locator("#q-S1_B02").select_option(destination)
        self.fill_destination(page)
        page.locator("#journey-mode").select_option(mode)
        if description is not None:
            page.locator("#brief").fill(description)
        if submit:
            page.locator("#brief-submit").click()

    def fill_destination(self, page):
        for selector, value in [
            ("#destination-url", "https://ornek.example/kampanya"),
            ("#destination-phone", "+90 555 000 00 00"),
            ("#destination-address", "Sentetik Örnek Mahallesi, Örnek Sokak No: 1"),
        ]:
            if page.locator(selector).is_visible():
                page.locator(selector).fill(value)

    def start_plan(self, page):
        page.goto(self.origin)
        self.complete_brief(page)
        self.settle_plan(page)

    def open_creatives(self, page):
        page.get_by_role("button", name="Yaratıcı fikirleri keşfet").click()
        self.assertTrue(page.locator("#step-2").is_visible())
        self.assertEqual(page.locator(".concept-card").count(), 3)

    def adapt_and_review(self, page):
        page.locator(".choose").nth(0).click()
        page.locator("#adapt-content").click()
        page.locator("#content-next").click()
        self.assertTrue(page.locator("#step-3").is_visible())

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
        self.start_plan(page)
        self.assertEqual(page.locator(".concept-card").count(), 0)
        self.assertTrue(page.locator("#step-1").is_visible())
        page.locator(".economics > summary").click()
        page.locator("#fixture").select_option("demo")
        page.locator("#start").fill("2026-10-27")
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.allocated"), 300000
        )
        self.assertEqual(page.locator("#recommended .channel-row").count(), 2)
        page.screenshot(
            path=str(self.evidence / "plan-first-desktop.png"), full_page=True
        )
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
        page.get_by_role("button", name="Yaratıcı fikirleri keşfet").click()
        self.assertTrue(page.locator("#step-1").is_visible())
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.unallocated"), 680000
        )
        self.open_creatives(page)
        card = page.locator(".concept-card").nth(1)
        card.get_by_role("button", name="Düzenle", exact=True).click()
        page.locator("#edit-title").fill("Sana özel bir tasarım anı")
        page.locator("#edit-x").fill("20")
        page.get_by_role("button", name="Uygula ve geri dön").click()
        self.assertIn("Sana özel", card.inner_text())
        card.get_by_role("button", name="Bu yönü seç").click()
        self.assertTrue(page.locator("#content-next").is_disabled())
        page.locator("#adapt-content").click()
        self.assertFalse(page.evaluate("YaparoStudio.getSnapshot().stale"))
        self.assertGreater(page.locator(".platform-preview").count(), 0)
        page.screenshot(
            path=str(self.evidence / "creative-platform-desktop.png"), full_page=True
        )
        page.locator("#content-next").click()
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
        self.complete_brief(
            page,
            communication="fundraising",
            business="nonprofit_fundraising",
            sector="nonprofit_social_cause",
            action="donate",
            submit=False,
        )
        self.assertTrue(
            page.get_by_label("İzin veya muafiyet belgesi mevcut mu?").is_visible()
        )
        page.locator("#q-S1_F01").select_option("association")
        page.locator("#brief-submit").click()
        self.settle_plan(page)
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.allocated"), 0)
        self.assertIn("incelemesi", page.locator("#recommended").inner_text())
        page.get_by_role("button", name="Yaratıcı fikirleri keşfet").click()
        self.assertTrue(page.locator("#step-1").is_visible())
        self.assertEqual(page.locator(".concept-card").count(), 0)
        page.locator('#step-nav [data-step="0"]').click()
        self.complete_brief(page)
        self.assertEqual(page.locator("#q-S1_F01").count(), 0)
        self.assertNotIn(
            "S1_F01", page.evaluate("YaparoStudio.getSnapshot().brief.branch")
        )
        page.locator("#region").fill("Ankara")
        page.locator(".economics > summary").click()
        page.locator("#fixture").select_option("unknown")
        page.locator("#recommend").click()
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.allocated"), 0)
        page.close()

    def test_mobile_literal_text_and_boundaries(self):
        page = self.browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(self.origin)
        self.complete_brief(
            page,
            description='<img src="https://example.invalid/x" onerror="alert(1)"> sentetik tasarım',
        )
        self.settle_plan(page)
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
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(self.origin)
        page.get_by_role("button", name="◈ Butik koleksiyonu", exact=True).click()
        self.assertEqual(page.locator("#q-S1_B02").input_value(), "physical_store")
        page.get_by_role("button", name="▤ B2B yazılım", exact=True).click()
        self.assertEqual(page.locator("#q-S1_B02").input_value(), "lead_form")
        self.assertEqual(page.locator("#action").input_value(), "fill_form")
        page.get_by_role("button", name="☕ Kafe açılışı", exact=True).click()
        self.complete_brief(page, sector="food_hospitality")
        self.settle_plan(page)
        self.assertEqual(page.locator(".concept-card").count(), 0)
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
        page.locator("#chat-input").fill("Bütçe 6000")
        page.get_by_role("button", name="Mesajı gönder").click()
        page.locator("#duration").fill("15")
        page.locator("#chat-log").get_by_role(
            "button", name="Öneriyi uygula", exact=True
        ).click()
        self.assertEqual(page.locator("#budget").input_value(), "5000")
        self.assertIn("Koşullar değişti", page.locator("#chat-log").inner_text())
        page.locator("#duration").fill("14")
        page.locator("#helper-toggle").click()
        page.locator("#recommend").click()
        self.open_creatives(page)
        self.assertIn("kahve", page.locator("#concepts").inner_text().lower())
        page.locator(".choose").nth(0).click()
        page.locator("#adapt-content").click()
        selected = page.evaluate("YaparoStudio.getSnapshot().creative.id")
        if page.locator("#helper-toggle").is_visible():
            page.locator("#helper-toggle").click()
        page.locator("#chat-input").fill("Daha sade olsun")
        page.get_by_role("button", name="Mesajı gönder").click()
        page.locator("#chat-log").get_by_role(
            "button", name="Öneriyi uygula", exact=True
        ).click()
        self.assertFalse(page.evaluate("YaparoStudio.getSnapshot().stale"))
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().adaptations"))
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().creative.id"), selected
        )
        if page.locator("#helper-toggle").is_visible():
            page.locator("#helper-toggle").click()
        old_title = page.locator(".art-title").nth(0).inner_text()
        page.locator("#regenerate").click()
        self.assertNotEqual(page.locator(".art-title").nth(0).inner_text(), old_title)
        page.locator("#previous-trio").click()
        self.assertEqual(page.locator(".art-title").nth(0).inner_text(), old_title)
        page.locator("#adapt-content").click()
        page.screenshot(
            path=str(self.evidence / "dynamic-cafe-desktop.png"), full_page=True
        )
        self.assertEqual(errors, [])
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().plan.model"))
        page.close()

    def test_source_refresh_provenance_and_live_fx_recompute(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1100})
        self.start_plan(page)
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.fx.rate"), 50)
        self.server.source_services["ecb"].transport = lambda: self.ecb_body.replace(
            b'rate="100"', b'rate="104"'
        )
        self.server.source_services["ecb"].last_attempt = None
        page.locator("#source-refresh").click()
        page.get_by_text(
            "Son kayıt: 1 USD = 52,0000 TRY · ECB çapraz referans", exact=True
        ).wait_for()
        self.assertTrue(page.evaluate("YaparoStudio.getSnapshot().stale"))
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.fx.source"), "ecb"
        )
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.fx.rate"), 52)
        self.assertFalse(page.evaluate("YaparoStudio.getSnapshot().plan.publishable"))
        page.locator("#budget").fill("6000")
        page.locator("#recommend").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().plan.fx.source"), "ecb"
        )
        expected_context = digest(page.evaluate("sourceContext()"))
        page.locator(
            f'#source-panel[data-context-hash="{expected_context}"]'
        ).wait_for()
        page.locator("#recommend").click()
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
        self.open_creatives(page)
        self.adapt_and_review(page)
        self.assertIn("TCMB gösterge satış", page.locator("#review").inner_text())
        page.close()

    def test_organic_only_bypasses_media_and_mixed_requirements(self):
        page = self.browser.new_page()
        page.goto(self.origin)
        self.complete_brief(page, mode="organic")
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().plan"))
        self.assertTrue(page.locator("#budget").is_disabled())
        self.assertFalse(page.locator("#budget").is_visible())
        self.open_creatives(page)
        self.adapt_and_review(page)
        self.assertIn("Yalnız organik paylaşım", page.locator("#review").inner_text())
        self.assertEqual(
            page.evaluate(
                "YaparoStudio.getSnapshot().production.requirements.map(r=>r.usage)"
            ),
            ["organic"],
        )
        page.goto(self.origin)
        self.complete_brief(page, mode="both")
        self.settle_plan(page)
        self.open_creatives(page)
        requirements = page.evaluate(
            "YaparoStudio.getSnapshot().production.requirements"
        )
        self.assertEqual({r["usage"] for r in requirements}, {"paid", "organic"})
        page.close()

    def test_search_only_adaptation_edit_and_replan_guards(self):
        page = self.browser.new_page()
        self.start_plan(page)
        # Remove every funded non-Search product through normal allocation controls.
        others = page.evaluate(
            "YaparoStudio.getSnapshot().plan.rows.filter(r=>r.amount && r.channel.id!=='google_search_maps').map(r=>r.channel.id)"
        )
        for channel in others:
            amount = page.locator(f'[data-channel="{channel}"] input[type=number]')
            amount.fill("0")
            amount.press("Tab")
        self.assertGreater(
            page.evaluate(
                "YaparoStudio.getSnapshot().plan.rows.find(r=>r.channel.id==='google_search_maps').amount"
            ),
            0,
        )
        self.open_creatives(page)
        page.locator(".choose").nth(0).click()
        page.locator("#adapt-content").click()
        self.assertEqual(
            page.locator('.platform-preview[data-medium="image"]').count(), 0
        )
        self.assertEqual(
            page.locator('.platform-preview[data-medium="text"]').count(), 1
        )
        original = page.evaluate("YaparoStudio.getSnapshot().creative")
        page.locator(".concept-card").nth(0).get_by_role(
            "button", name="Düzenle", exact=True
        ).click()
        page.locator("#edit-title").fill("Arama için güncel örnek başlık")
        page.get_by_role("button", name="Uygula ve geri dön").click()
        self.assertFalse(page.evaluate("YaparoStudio.getSnapshot().stale"))
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().adaptations"))
        self.assertTrue(page.locator("#content-next").is_disabled())
        page.locator("#adapt-content").click()
        current = page.evaluate("YaparoStudio.getSnapshot()")
        self.assertGreater(current["creative"]["revision"], original["revision"])
        self.assertTrue(
            all(
                p["coreRevision"] == current["creative"]["revision"]
                for p in current["adaptations"]
            )
        )
        page.locator('#step-nav [data-step="1"]').click()
        page.locator("#video-allowed").check()
        self.assertTrue(page.evaluate("YaparoStudio.getSnapshot().stale"))
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().contentBinding"))
        self.assertTrue(page.locator('#step-nav [data-step="2"]').is_disabled())
        page.locator("#recommend").click()
        self.open_creatives(page)
        self.assertFalse(page.evaluate("YaparoStudio.getSnapshot().stale"))
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().adaptations"))
        page.close()

    def test_organic_video_pending_and_stale_assistant(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(self.origin)
        self.complete_brief(page, mode="organic")
        page.locator('[name="organic-platform"][value="instagram"]').uncheck()
        page.locator('[name="organic-platform"][value="tiktok"]').check()
        page.locator("#helper-toggle").click()
        page.locator("#chat-input").fill("Bütçe 6000")
        page.get_by_role("button", name="Mesajı gönder").click()
        page.locator('[name="organic-platform"][value="youtube"]').check()
        page.locator("#chat-log").get_by_role(
            "button", name="Öneriyi uygula", exact=True
        ).click()
        self.assertEqual(page.locator("#budget").input_value(), "3000")
        self.assertIn("Koşullar değişti", page.locator("#chat-log").inner_text())
        page.locator("#helper-toggle").click()
        self.open_creatives(page)
        page.locator(".choose").nth(0).click()
        page.locator("#adapt-content").click()
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().adaptations"), [])
        self.assertEqual(
            page.locator('.platform-preview[data-medium="image"]').count(), 0
        )
        self.assertIn("0 kanala özel", page.locator("#production-status").inner_text())
        self.assertIn("eksik", page.locator("#platform-previews").inner_text())
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().plan"))
        page.close()

    def test_helper_cannot_skip_unconfirmed_brief(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(self.origin)
        page.locator("#chat-input").fill("Bütçe 6000")
        page.get_by_role("button", name="Mesajı gönder").click()
        page.locator("#chat-log").get_by_role(
            "button", name="Öneriyi uygula", exact=True
        ).click()
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().brief"))
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().plan"))
        self.assertTrue(page.locator('#step-nav [data-step="1"]').is_disabled())
        self.complete_brief(page)
        page.locator('#step-nav [data-step="0"]').click()
        self.complete_brief(
            page,
            description="Sentetik yeni istek: önce bu bilgileri kontrol etmeliyiz.",
            submit=False,
        )
        page.locator("#chat-input").fill("Bütçe 5000")
        page.get_by_role("button", name="Mesajı gönder").click()
        page.locator("#chat-log").get_by_role(
            "button", name="Öneriyi uygula", exact=True
        ).click()
        self.assertTrue(page.locator('#step-nav [data-step="1"]').is_disabled())
        self.assertTrue(page.evaluate("YaparoStudio.getSnapshot().stale"))
        page.close()

    def test_single_screen_narrowing_and_parent_change_pruning(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(self.origin)
        self.assertEqual(
            page.locator(
                "#brief-next, #brief-back, #communication-family, #business-family, #sector-family"
            ).count(),
            0,
        )
        self.assertFalse(page.locator("#brief").is_visible())
        self.assertFalse(page.locator("#communication").is_visible())
        self.assertFalse(page.locator("#journey-mode").is_visible())
        self.assertTrue(page.locator("#brief-submit").is_disabled())
        self.assertNotIn("Diğer", page.locator("#purpose-choices").inner_text())
        self.assertNotIn("Emin değilim", page.locator("#purpose-choices").inner_text())
        self.assertTrue(page.locator("#scenario-examples").is_visible())
        self.complete_brief(
            page,
            communication="fundraising",
            business="nonprofit_fundraising",
            sector="nonprofit_social_cause",
            action="donate",
            submit=False,
        )
        businesses = page.locator("#business option").evaluate_all(
            "ns=>ns.map(n=>n.value).filter(Boolean)"
        )
        sectors = page.locator("#sector option").evaluate_all(
            "ns=>ns.map(n=>n.value).filter(Boolean)"
        )
        self.assertNotIn("mobile_app", businesses)
        self.assertNotIn("fashion_beauty_lifestyle", sectors)
        page.locator("#q-S1_F01").select_option("association")
        risk_details = page.locator("#brief-form .optional-details").filter(
            has=page.locator("#risk")
        )
        if not page.locator("#risk").is_visible():
            risk_details.locator("summary").click()
        page.locator("#risk").select_option("health")
        self.complete_brief(page, submit=False)
        self.assertEqual(page.locator("#q-S1_F01").count(), 0)
        self.assertEqual(page.locator("#risk").input_value(), "health")
        actions = page.locator("#action option").evaluate_all(
            "ns=>ns.map(n=>n.value).filter(Boolean)"
        )
        self.assertIn("visit_store", actions)
        self.assertNotIn("donate", actions)
        self.assertNotIn("apply_job", actions)
        self.assertIn("download_app", actions)
        self.assertLess(len(actions), 16)
        page.locator('[data-action="visit_website"]').click()
        page.locator("#q-S1_B02").select_option("own_website")
        self.fill_destination(page)
        self.assertEqual(page.locator("#action").input_value(), "visit_website")
        self.assertTrue(page.locator("#context-form").is_visible())
        page.screenshot(
            path=str(self.evidence / "brief-single-screen-desktop.png"), full_page=True
        )
        page.locator("#brief-submit").click()
        brief = page.evaluate("YaparoStudio.getSnapshot().brief")
        self.assertEqual(brief["business"], "local_retail")
        self.assertEqual(brief["action"], "visit_website")
        self.assertEqual(brief["branch"]["S1_B02"], "own_website")
        self.assertNotIn("S1_F01", brief["branch"])
        self.assertEqual(brief["risk"], "health")
        page.close()

    def test_manual_sector_other_validation_literal_and_return_to_canonical(self):
        page = self.browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(self.origin)
        self.complete_brief(page, submit=False)
        page.locator("#sector").select_option("other")
        manual = page.locator("#sector-other")
        self.assertTrue(manual.is_visible())
        self.assertTrue(manual.get_attribute("required") is not None)
        self.assertEqual(manual.get_attribute("maxlength"), "200")
        manual.fill("   ")
        page.locator("#brief-submit").click()
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().brief"))
        literal = '<img src="https://example.invalid/manual" onerror="alert(1)"> sentetik özel alan'
        manual.fill(literal)
        page.locator("#brief-submit").click()
        self.settle_plan(page)
        brief = page.evaluate("YaparoStudio.getSnapshot().brief")
        self.assertEqual(brief["sector"], "other")
        self.assertEqual(brief["custom"]["sector"], literal)
        self.assertEqual(page.evaluate("YaparoStudio.getSnapshot().plan.allocated"), 0)
        self.assertEqual(page.locator('img[src*="example.invalid"]').count(), 0)
        page.locator('#step-nav [data-step="0"]').click()
        page.locator("#sector").select_option("fashion_beauty_lifestyle")
        self.assertFalse(manual.is_visible())
        self.assertFalse(manual.get_attribute("required") is not None)
        page.locator("#brief-submit").click()
        self.assertNotIn(
            "sector", page.evaluate("YaparoStudio.getSnapshot().brief.custom")
        )
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
        page.close()

    def test_paired_intent_subtypes_and_plan_invalidation(self):
        page = self.browser.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(self.origin)
        first_purpose = page.locator("#purpose-choices button").first
        first_purpose.focus()
        first_purpose.press("ArrowRight")
        self.assertEqual(
            page.locator("#purpose-choices button:focus").get_attribute("data-purpose"),
            "sale_promotion",
        )
        page.locator("#purpose-choices button:focus").press("ArrowRight")
        self.assertEqual(
            page.locator("#purpose-choices button:focus").get_attribute("data-purpose"),
            "event",
        )
        self.complete_brief(page, mode="organic")
        self.open_creatives(page)
        page.locator('#step-nav [data-step="0"]').click()
        page.locator('[data-action="understand"]').click()
        self.assertTrue(page.locator('#step-nav [data-step="2"]').is_disabled())
        page.locator("#business").select_option("local_service")
        self.assertTrue(page.locator("#context-form").is_visible())
        self.assertEqual(page.locator("#action").input_value(), "understand")
        self.complete_brief(
            page, communication="education", action="understand", submit=False
        )
        self.assertEqual(page.locator("#communication").input_value(), "education")
        self.assertEqual(page.locator("#q-S1_ED01").count(), 1)
        self.assertEqual(page.locator("#q-S1_M01").count(), 0)
        page.locator("#work-kind").select_option("membership")
        self.assertEqual(page.locator("#q-S1_ED01").count(), 0)
        self.assertEqual(page.locator("#q-S1_M01").count(), 1)
        self.assertEqual(errors, [])
        page.close()

    def test_manual_other_fields_stay_explicit_and_organic_unqualified(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(self.origin)
        for select, manual in [
            ("business", "business"),
            ("q-S1_B02", "destination"),
        ]:
            self.complete_brief(page, submit=False)
            page.locator(f"#{select}").select_option("__other__")
            field = page.locator(f"#{manual}-other")
            self.assertTrue(field.is_visible(), manual)
            self.assertTrue(field.get_attribute("required") is not None, manual)
            self.assertEqual(field.get_attribute("maxlength"), "200")
            field.fill("Sentetik özel " + manual)
        # A manually described sector is retained in an organic-only draft;
        # it does not become a qualified paid objective or trigger provider access.
        self.complete_brief(page, mode="organic", submit=False)
        page.locator("#sector").select_option("other")
        page.locator("#sector-other").fill("Sentetik özel bir çalışma alanı")
        page.locator("#brief-submit").click()
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().plan"))
        brief = page.evaluate("YaparoStudio.getSnapshot().brief")
        self.assertEqual(brief["action"], "visit_store")
        self.assertEqual(brief["custom"], {"sector": "Sentetik özel bir çalışma alanı"})
        self.open_creatives(page)
        self.adapt_and_review(page)
        self.assertIn(
            "Sentetik özel bir çalışma alanı", page.locator("#review").inner_text()
        )
        page.locator('#step-nav [data-step="2"]').click()
        page.locator("#regenerate").click()
        page.locator("#previous-trio").click()
        self.assertEqual(
            page.locator("#sector-other").input_value(),
            "Sentetik özel bir çalışma alanı",
        )
        self.assertTrue(page.locator("#sector-other").is_enabled())
        self.assertFalse(
            page.evaluate("YaparoStudio.getSnapshot().production.publishable")
        )
        self.assertEqual(page.locator('img[src*="example.invalid"]').count(), 0)
        page.close()

    def test_destination_required_validation_review_and_type_change(self):
        page = self.browser.new_page()
        outbound = []
        page.on(
            "request",
            lambda request: (
                outbound.append(request.url)
                if not request.url.startswith(self.origin)
                else None
            ),
        )
        page.goto(self.origin)
        self.complete_brief(
            page,
            communication="sale_promotion",
            action="buy_online",
            destination="own_website",
            mode="organic",
            submit=False,
        )
        page.locator("#destination-url").fill("")
        page.locator("#brief-submit").click()
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().brief"))
        page.locator("#destination-url").fill("javascript:alert(1)")
        page.locator("#brief-submit").click()
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().brief"))
        url = "https://ornek.example/urun?renk=mavi"
        page.locator("#destination-url").fill(url)
        page.locator("#brief-submit").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().brief.destination.values"),
            {"url": url},
        )
        self.open_creatives(page)
        self.adapt_and_review(page)
        self.assertIn(url, page.locator("#review").inner_text())
        page.locator('#step-nav [data-step="2"]').click()
        page.locator("#regenerate").click()
        page.locator("#previous-trio").click()
        self.assertEqual(page.locator("#destination-url").input_value(), url)
        page.locator('#step-nav [data-step="0"]').click()
        page.locator('[data-action="visit_store"]').click()
        page.locator("#q-S1_B02").select_option("physical_store")
        self.assertEqual(page.locator("#destination-url").count(), 0)
        self.assertEqual(page.locator("#destination-address").input_value(), "")
        page.locator("#brief-submit").click()
        self.assertTrue(page.locator("#step-0").is_visible())
        page.locator("#destination-mapUrl").fill("https://harita.example/konum")
        page.locator("#brief-submit").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().brief.destination.values"),
            {"mapUrl": "https://harita.example/konum"},
        )
        self.assertEqual(outbound, [])
        page.close()

    def test_event_registration_collects_destination_and_phone(self):
        page = self.browser.new_page()
        page.goto(self.origin)
        self.complete_brief(
            page,
            communication="event",
            business="event",
            sector="entertainment_events",
            action="register_event",
            destination="lead_form",
            mode="organic",
            submit=False,
        )
        self.assertTrue(page.locator("#destination-url").is_visible())
        page.locator("#brief-submit").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().brief.destination.type"),
            "lead_form",
        )
        # The owned destination is retained even where source S1_B02 does not apply.
        self.assertNotIn(
            "S1_B02", page.evaluate("YaparoStudio.getSnapshot().brief.branch")
        )
        page.locator('#step-nav [data-step="0"]').click()
        self.complete_brief(
            page,
            communication="lead_request",
            business="local_service",
            sector="professional_services",
            action="call",
            destination="whatsapp_phone",
            mode="organic",
            submit=False,
        )
        page.locator("#destination-phone").fill("123")
        page.locator("#brief-submit").click()
        self.assertTrue(page.locator("#step-0").is_visible())
        page.locator("#destination-phone").fill("+90 555 000 00 00")
        page.locator("#brief-submit").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().brief.destination.values.phone"),
            "+90 555 000 00 00",
        )
        page.close()

    def test_structured_dates_and_non_cash_fundraising(self):
        page = self.browser.new_page()
        page.goto(self.origin)
        self.complete_brief(
            page,
            communication="sale_promotion",
            action="buy_online",
            destination="own_website",
            mode="organic",
            submit=False,
        )
        page.locator("#q-S1_P03-start").fill("2026-11-01")
        page.locator("#q-S1_P03-end").fill("2026-10-31")
        page.locator("#brief-submit").click()
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().brief"))
        page.locator("#q-S1_P03-end").fill("2026-11-07")
        page.locator("#brief-submit").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().brief.branch.S1_P03"),
            {"start": "2026-11-01", "end": "2026-11-07"},
        )
        page.locator('#step-nav [data-step="0"]').click()
        self.complete_brief(
            page,
            communication="fundraising",
            business="nonprofit_fundraising",
            sector="nonprofit_social_cause",
            action="donate",
            mode="organic",
            submit=False,
        )
        page.locator("#q-S1_F04-kind").select_option("money")
        page.locator("#q-S1_F04-channel").select_option("official_account")
        page.locator("#q-S1_F04-target").fill("1000")
        # Changing to volunteer support removes a now-irrelevant monetary target/channel.
        page.locator("#q-S1_F04-kind").select_option("volunteer")
        self.assertTrue(page.locator("#q-S1_F04-target").is_disabled())
        self.assertFalse(page.locator("#q-S1_F04-target").is_visible())
        self.assertEqual(page.locator("#q-S1_F04-channel").input_value(), "")
        page.locator("#q-S1_F04-channel").select_option("in_person")
        page.locator("#brief-submit").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().brief.branch.S1_F04"),
            {"kind": "volunteer", "channel": "in_person"},
        )
        self.assertNotIn(
            "S1_P03", page.evaluate("YaparoStudio.getSnapshot().brief.branch")
        )
        page.close()

    def test_conditional_other_description_is_saved_and_pruned(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(self.origin)
        self.complete_brief(
            page,
            communication="announcement",
            action="understand",
            mode="organic",
            submit=False,
        )
        page.locator("#branch-fields > details > summary").click()
        page.locator("#q-S1_A01").select_option("other")
        manual = page.locator("#q-S1_A01-other")
        self.assertTrue(manual.is_visible())
        manual.fill("   ")
        page.locator("#brief-submit").click()
        self.assertIsNone(page.evaluate("YaparoStudio.getSnapshot().brief"))
        manual.fill("Sentetik yeni çalışma saatleri duyurusu")
        page.locator("#brief-submit").click()
        self.assertEqual(
            page.evaluate("YaparoStudio.getSnapshot().brief.custom.S1_A01"),
            "Sentetik yeni çalışma saatleri duyurusu",
        )
        self.open_creatives(page)
        self.adapt_and_review(page)
        self.assertIn(
            "Sentetik yeni çalışma saatleri duyurusu",
            page.locator("#review").inner_text(),
        )
        page.locator('#step-nav [data-step="0"]').click()
        self.complete_brief(page)
        self.assertNotIn(
            "S1_A01", page.evaluate("YaparoStudio.getSnapshot().brief.custom")
        )
        self.assertNotIn(
            "S1_A01", page.evaluate("YaparoStudio.getSnapshot().brief.branch")
        )
        page.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
