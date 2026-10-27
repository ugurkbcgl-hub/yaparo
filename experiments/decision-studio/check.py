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
        """Exercise visible narrowing controls; never patch application state."""
        for _ in range(4):
            if page.locator("#brief-back").is_visible():
                page.locator("#brief-back").click()
        groups = {
            "communication": {
                "offer": [
                    "product_service_intro",
                    "launch",
                    "sale_promotion",
                    "lead_request",
                ],
                "news": ["announcement", "event", "celebration"],
                "knowledge": ["education", "membership"],
                "people": ["recruitment", "fundraising"],
                "public": ["reputation", "public_issue", "unsure"],
            },
            "business": {
                "shop": ["local_retail", "ecommerce_dtc", "marketplace_seller"],
                "service": ["local_service", "b2b_leadgen"],
                "digital": ["saas_subscription", "mobile_app", "media_creator"],
                "participation": ["event", "nonprofit_fundraising"],
                "team": ["employer_recruitment"],
            },
            "sector": {
                "products": [
                    "fashion_beauty_lifestyle",
                    "retail_ecommerce",
                    "automotive",
                ],
                "experience": [
                    "food_hospitality",
                    "travel_tourism",
                    "entertainment_events",
                ],
                "services": [
                    "professional_services",
                    "local_home_services",
                    "real_estate",
                ],
                "tech": ["technology_saas", "industrial_b2b"],
                "expert": ["education_training", "health_medical", "finance_insurance"],
                "community": [
                    "nonprofit_social_cause",
                    "recruitment",
                    "public_political",
                    "other",
                ],
            },
        }
        for kind, value in [
            ("communication", communication),
            ("business", business),
            ("sector", sector),
        ]:
            group = next(k for k, values in groups[kind].items() if value in values)
            page.locator(f"#{kind}-family").select_option(group)
            page.locator(f"#{kind}").select_option(value)
            page.locator("#brief-next").click()
        if page.locator("#q-S1_B02").is_visible():
            page.locator("#q-S1_B02").select_option(destination)
        page.locator("#action").select_option(action)
        page.locator("#brief-next").click()
        page.locator("#journey-mode").select_option(mode)
        if description is not None:
            page.locator("#brief").fill(description)
        if submit:
            page.locator("#brief-submit").click()

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
        page.locator(".brief-examples > summary").click()
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

    def test_brief_cascade_visible_load_and_parent_changes(self):
        page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(self.origin)
        self.assertLessEqual(page.locator("#brief-form select:visible").count(), 2)
        self.assertFalse(page.locator("#brief").is_visible())
        self.assertFalse(page.locator("#brief-submit").is_visible())
        page.locator("#communication-family").select_option("people")
        self.assertEqual(
            page.locator("#communication option").evaluate_all(
                "ns=>ns.map(n=>n.value).filter(Boolean)"
            ),
            ["recruitment", "fundraising"],
        )
        page.locator("#communication").select_option("fundraising")
        page.locator("#communication-family").select_option("offer")
        self.assertEqual(page.locator("#communication").input_value(), "")
        self.assertFalse(
            page.locator("#communication option[value=fundraising]").count()
        )
        page.screenshot(
            path=str(self.evidence / "brief-start-desktop.png"), full_page=True
        )
        page.locator("#communication").select_option("product_service_intro")
        page.locator("#brief-next").click()
        page.locator("#brief-back").focus()
        page.locator("#brief-back").press("Enter")
        self.assertTrue(page.locator("#communication-family").is_visible())
        self.assertFalse(page.locator("#business-family").is_visible())
        self.complete_brief(page, submit=False)
        page.locator("#brief-back").click()
        actions = page.locator("#action option").evaluate_all(
            "ns=>ns.map(n=>n.value).filter(Boolean)"
        )
        self.assertIn("visit_store", actions)
        self.assertNotIn("donate", actions)
        self.assertNotIn("apply_job", actions)
        self.assertNotIn("download_app", actions)
        self.assertLess(len(actions), 16)
        page.locator("#q-S1_B02").select_option("own_website")
        self.assertEqual(page.locator("#action").input_value(), "")
        self.assertIn(
            "buy_online",
            page.locator("#action option").evaluate_all("ns=>ns.map(n=>n.value)"),
        )
        page.locator("#action").select_option("buy_online")
        page.locator("#brief-next").click()
        page.locator("#brief-submit").click()
        brief = page.evaluate("YaparoStudio.getSnapshot().brief")
        self.assertEqual(brief["business"], "local_retail")
        self.assertEqual(brief["action"], "buy_online")
        self.assertEqual(brief["branch"]["S1_B02"], "own_website")
        page.close()

    def test_brief_hidden_notes_pruned_and_risk_preserved(self):
        page = self.browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(self.origin)
        self.complete_brief(
            page,
            communication="fundraising",
            business="nonprofit_fundraising",
            sector="nonprofit_social_cause",
            action="donate",
            submit=False,
        )
        page.locator("#q-S1_F01").select_option("association")
        page.locator("#brief-form .optional-details").filter(
            has=page.locator("#risk")
        ).locator("summary").click()
        page.locator("#risk").select_option("health")
        self.complete_brief(page, submit=False)
        self.assertEqual(page.locator("#q-S1_F01").count(), 0)
        self.assertEqual(page.locator("#risk").input_value(), "health")
        page.locator("#brief-back").click()
        page.locator("#brief-back").click()
        page.locator("#sector-family").select_option("tech")
        sectors = page.locator("#sector option").evaluate_all(
            "ns=>ns.map(n=>n.value).filter(Boolean)"
        )
        self.assertEqual(set(sectors), {"technology_saas", "industrial_b2b"})
        self.assertEqual(page.locator("#sector").input_value(), "")
        page.locator("#sector").select_option("technology_saas")
        page.locator("#brief-back").click()
        page.locator("#business-family").select_option("digital")
        self.assertEqual(page.locator("#business").input_value(), "")
        self.assertNotIn(
            "local_retail",
            page.locator("#business option").evaluate_all("ns=>ns.map(n=>n.value)"),
        )
        self.assertEqual(page.locator("#action").input_value(), "")
        self.complete_brief(page)
        brief = page.evaluate("YaparoStudio.getSnapshot().brief")
        self.assertNotIn("S1_F01", brief["branch"])
        self.assertEqual(brief["risk"], "health")
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
        page.locator('#step-nav [data-step="0"]').click()
        page.locator(".brief-examples > summary").click()
        page.get_by_role("button", name="☕ Kafe açılışı", exact=True).click()
        self.assertEqual(page.locator("#risk").input_value(), "health")
        page.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
