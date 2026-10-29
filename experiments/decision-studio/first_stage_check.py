"""Owned first-stage UI and existing local plan integration; synthetic and offline."""

import importlib.util
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright
from sources import SourceService

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("owned_studio_server", ROOT / "serve.py")
SERVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SERVER)


class FirstStageCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = SERVER.make_server()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.runtime = sync_playwright().start()
        cls.browser = cls.runtime.chromium.launch()
        cls.evidence = Path(tempfile.mkdtemp(prefix="yaparo-first-stage-"))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.runtime.stop()
        cls.server.shutdown()
        cls.server.server_close()
        print(f"Evidence: {cls.evidence}")

    def setUp(self):
        cache = Path(tempfile.mkdtemp(prefix="yaparo-owned-source-"))
        today = datetime.now(timezone.utc).date()
        tcmb = f'<Tarih_Date Tarih="{today.strftime("%d.%m.%Y")}"><Currency CurrencyCode="USD"><Unit>1</Unit><ForexSelling>50.0000</ForexSelling></Currency></Tarih_Date>'.encode()
        ecb = f'<Envelope xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref"><Cube><Cube time="{today.isoformat()}"><Cube currency="USD" rate="2"/><Cube currency="TRY" rate="100"/></Cube></Cube></Envelope>'.encode()
        self.server.source_services = {
            "tcmb": SourceService(
                cache_path=cache / "tcmb.json", transport=lambda: tcmb, provider="tcmb"
            ),
            "ecb": SourceService(
                cache_path=cache / "ecb.json", transport=lambda: ecb, provider="ecb"
            ),
        }
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        self.errors = []
        self.outbound = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on(
            "request",
            lambda request: (
                self.outbound.append(request.url)
                if not request.url.startswith(self.origin + "/")
                else None
            ),
        )
        self.page.goto(self.origin)
        self.page.locator("#first-stage-root").wait_for(state="visible")

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.errors, [])
        self.assertEqual(self.outbound, [])

    def snapshot(self):
        return self.page.evaluate("YaparoStudio.getSnapshot()")

    def select_pair(self, intent, outcome):
        if self.page.locator("#first-stage-change").is_visible():
            self.page.locator("#first-stage-change").click()
        self.page.locator(f'[data-first-intent="{intent}"]').click()
        self.page.locator(f'[data-first-outcome="{outcome}"]').click()

    def field(self, field_id):
        return self.page.locator(f"#first-stage-{field_id}")

    def fill_remaining(self, mode="organic", overrides=None):
        """Read the schema, but enter every fixture answer through visible controls."""
        overrides = dict(overrides or {})
        for _ in range(80):
            current = self.snapshot()["firstStage"]
            fields = self.page.evaluate(
                "s=>YaparoFirstStage.fields(s.intent,s.outcome,s.answers)", current
            )
            outstanding = [
                field
                for field in fields
                if (field["required"] or field.get("essential"))
                and field["id"] not in current["answers"]
            ]
            if not outstanding:
                break
            field = outstanding[0]
            control = self.field(field["id"])
            kind = field["type"]
            override = overrides.get(field["id"])
            if field["id"] == "delivery_mode":
                control.select_option(mode)
            elif kind == "select":
                control.select_option(override or field["options"][0]["value"])
            elif kind == "multiselect":
                values = override or [field["options"][0]["value"]]
                for value in values:
                    control.locator(f'input[value="{value}"]').check()
            elif kind == "number":
                control.fill(str(override or max(field.get("min", 0), 1)))
            elif kind == "date":
                control.fill(override or "2026-11-15")
            elif kind == "time":
                control.fill(
                    override or ("11:00" if field["id"].endswith("_end") else "10:00")
                )
            elif kind == "url":
                control.fill(override or "https://ornek.example/sentetik")
            elif kind == "tel":
                control.fill(override or "+90 (555) 000-00-00")
            elif kind == "email":
                control.fill(override or "sentetik@example.test")
            else:
                control.fill(override or "Somut sentetik açıklama")
        else:
            self.fail("Fixture did not converge to the visible required fields")
        self.field("delivery_mode").select_option(mode)

    def submit(self):
        self.page.locator("#first-stage-submit").click()

    def test_owned_examples_fill_five_forms_and_reach_content(self):
        pairs = {
            "cafe": ("promote", "visit"),
            "fashion": ("promote", "visit"),
            "saas": ("lead", "lead_form"),
            "home": ("lead", "call"),
            "event": ("event", "register"),
        }
        for key, pair in pairs.items():
            self.page.locator(f'[data-scenario="{key}"]').click()
            current = self.snapshot()["firstStage"]
            self.assertEqual((current["intent"], current["outcome"]), pair)
            errors = self.page.evaluate(
                "s=>YaparoFirstStage.validate(s.intent,s.outcome,s.answers).errors",
                current,
            )
            self.assertEqual(list(errors), ["delivery_mode"])
            self.assertIn(
                "kurgusaldır", self.page.locator("#owned-example-status").inner_text()
            )
            self.assertEqual(
                self.page.locator(f'[data-scenario="{key}"]').get_attribute(
                    "aria-pressed"
                ),
                "true",
            )
            self.assertIsNone(self.snapshot()["plan"])
            self.assertIsNone(self.snapshot()["adaptations"])
            for field in ["budget", "region", "start", "plan-end"]:
                self.assertEqual(self.page.locator(f"#{field}").input_value(), "")
            if key == "cafe":
                self.submit()
                self.assertTrue(self.page.locator("#step-0").is_visible())
                self.assertEqual(
                    self.field("delivery_mode").get_attribute("aria-invalid"), "true"
                )
                self.page.evaluate("window.scrollTo(0,0)")
                self.page.screenshot(
                    path=str(self.evidence / "owned-cafe-example-desktop.png"),
                    full_page=True,
                )
            self.field("delivery_mode").select_option("content_only")
            self.submit()
            self.page.locator("#step-1").wait_for(state="visible")
            self.assertTrue(self.page.locator("#plan-bounds").is_hidden())
            self.page.get_by_role("button", name="İçeriklere devam et").click()
            self.page.locator("#step-2").wait_for(state="visible")
            self.assertEqual(self.page.locator(".concept-card").count(), 3)
            self.page.locator(".choose").first.click()
            self.assertEqual(self.snapshot()["creative"]["outcome"], pair[1])
            self.page.locator("#adapt-content").click()
            self.page.locator("#content-next").click()
            self.page.locator("#step-3").wait_for(state="visible")
            self.assertIn("Sentetik Örnek", self.page.locator("#review").inner_text())
            self.page.locator('#step-nav [data-step="0"]').click()

        self.select_pair("fundraise", "volunteer")
        self.assertTrue(self.page.locator("#owned-example-status").is_hidden())
        self.assertEqual(
            self.page.locator('[data-scenario][aria-pressed="true"]').count(), 0
        )

    def test_example_switch_clears_old_plan_but_preserves_declared_risk(self):
        self.page.locator('[data-scenario="cafe"]').click()
        self.field("delivery_mode").select_option("paid")
        self.submit()
        self.plan_basics()
        self.page.get_by_text(
            "ECB çapraz referans USD/TRY · Güncel kayıt", exact=True
        ).wait_for(state="attached")
        self.page.locator("#recommend").click()
        self.assertGreater(self.snapshot()["plan"]["allocated"], 0)
        self.page.locator('#step-nav [data-step="0"]').click()
        self.field("risk").evaluate(
            "el=>{const detail=el.closest('details');if(detail)detail.open=true;}"
        )
        self.field("risk").select_option("health")
        self.page.locator('[data-scenario="fashion"]').click()
        current = self.snapshot()["firstStage"]
        self.assertEqual(current["answers"]["risk"], "health")
        self.assertNotIn("promote_strength_other", current["answers"])
        self.assertNotIn("İzmir", current["answers"]["action_location_address"])
        self.assertNotIn("delivery_mode", current["answers"])
        self.assertIsNone(self.snapshot()["plan"])
        self.assertIsNone(self.snapshot()["contentBinding"])
        for field in [
            "budget",
            "region",
            "radius",
            "start",
            "plan-end",
            "business",
            "sector",
        ]:
            self.assertEqual(self.page.locator(f"#{field}").input_value(), "")
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "owned-fashion-example-mobile.png"), full_page=True
        )
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"), 390
        )

    def test_helper_brief_does_not_insert_synthetic_example_facts(self):
        text = "Kafe açılışı için komşuları davet etmek istiyorum"
        self.page.locator("#chat-input").fill(text)
        self.page.locator("#chat-form").evaluate("form=>form.requestSubmit()")
        self.page.locator("#chat-log .assistant-message").last.get_by_role(
            "button", name="İsteğime yerleştir"
        ).click()
        answers = self.snapshot()["firstStage"]["answers"]
        self.assertEqual(answers, {"promote_name": text})
        self.assertIn(
            "eklenmedi", self.page.locator("#owned-example-status").inner_text()
        )

    def test_recommendation_uses_brief_without_repeated_classification(self):
        self.page.locator('[data-scenario="cafe"]').click()
        self.field("delivery_mode").select_option("paid")
        self.submit()
        self.assertEqual(self.page.locator("#plan-advanced").count(), 0)
        self.assertEqual(
            self.page.get_by_text("Öneri için ek bilgiler", exact=True).count(), 0
        )
        for field in [
            "business",
            "sector",
            "audience",
            "measurement",
            "fixture",
            "demo-readiness",
        ]:
            self.assertTrue(self.page.locator(f"#{field}").is_hidden())
            self.assertTrue(self.page.locator(f"#{field}").is_disabled())
        self.plan_basics()
        self.page.get_by_text(
            "ECB çapraz referans USD/TRY · Güncel kayıt", exact=True
        ).wait_for(state="attached")
        self.page.locator("#recommend").click()
        plan = self.snapshot()["plan"]
        self.assertGreater(plan["allocated"], 0)
        self.assertEqual(
            plan["analysis"]["subject"],
            self.snapshot()["firstStage"]["answers"]["promote_name"],
        )
        self.assertIn(
            "Sentetik Örnek Kafe", self.page.locator("#why-plan").inner_text()
        )
        self.assertIn("Bireyler", self.page.locator("#why-plan").inner_text())
        self.assertEqual(plan["analysis"]["sourceSector"], None)
        self.assertEqual(plan["analysis"]["risk"], None)
        self.assertEqual(self.snapshot()["brief"]["risk"], "not_declared")
        self.assertEqual(plan["qualification"]["publishReady"], False)
        self.page.locator("#business").evaluate("el=>el.value='b2b_leadgen'")
        self.page.locator("#sector").evaluate("el=>el.value='food_hospitality'")
        self.page.locator("#recommend").click()
        self.assertEqual(
            [r["amount"] for r in self.snapshot()["plan"]["rows"]],
            [r["amount"] for r in plan["rows"]],
        )
        self.assertEqual(
            self.snapshot()["plan"]["input"]["business"], "owned_unspecified"
        )
        self.page.locator("#plan-data-details > summary").click()
        self.assertIn(
            "Henüz doğrulanmayanlar",
            self.page.locator("#plan-data-details").inner_text(),
        )
        self.assertEqual(self.page.locator("#plan-data-details select").count(), 0)

    def test_recommendation_rebinds_changed_outcome_and_preserves_risk_gate(self):
        self.page.locator('[data-scenario="cafe"]').click()
        self.field("delivery_mode").select_option("paid")
        self.submit()
        self.plan_basics()
        self.page.locator("#recommend").click()
        previous = self.snapshot()["plan"]["analysis"]["signature"]
        self.page.locator('#step-nav [data-step="0"]').click()
        self.select_pair("promote", "traffic")
        self.fill_remaining(mode="paid")
        self.field("action_url").fill("https://ornek.example/ziyaret")
        self.submit()
        self.plan_basics()
        self.page.locator("#recommend").click()
        current = self.snapshot()["plan"]
        self.assertEqual(current["input"]["goal"], "traffic")
        self.assertEqual(current["analysis"]["outcome"], "traffic")
        self.assertNotEqual(current["analysis"]["signature"], previous)
        self.assertIsNone(self.snapshot()["contentBinding"])
        self.page.locator('#step-nav [data-step="0"]').click()
        self.field("risk").evaluate(
            "el=>{const d=el.closest('details');if(d)d.open=true;}"
        )
        self.field("risk").select_option("health")
        self.submit()
        self.plan_basics()
        self.page.locator("#recommend").click()
        self.assertEqual(self.snapshot()["plan"]["allocated"], 0)
        self.assertIn("health", self.snapshot()["plan"]["analysis"]["risks"])
        self.assertTrue(self.snapshot()["plan"]["blocked"])

    def plan_basics(self):
        self.page.locator("#geo-mode").select_option("country")
        self.page.locator("#start").fill("2026-11-01")
        self.page.locator("#plan-end").fill("2026-11-07")
        self.page.locator("#plan-result-deadline").fill("2026-11-14")
        self.page.locator("#plan-media-ceiling").fill("3000")
        self.page.locator("#plan-period-capacity").fill("100")
        if self.page.locator("#plan-contribution").is_visible():
            self.page.locator("#plan-contribution").fill("500")
        if not self.page.locator("#plan-production-cost").is_visible():
            self.page.get_by_text(
                "Üretim ve hizmet maliyetleri · biliyorsan ekle", exact=True
            ).click()
        self.page.locator("#plan-production-cost").fill("0")
        self.page.locator("#plan-service-cost").fill("0")
        self.page.locator("#plan-evidence").select_option("synthetic")
        self.page.locator("#budget-compare").click()
        self.page.locator('[data-media-minor="300000"]').click()

    def test_every_pair_has_own_form_and_no_cross_bank_fields(self):
        intents = self.page.evaluate("YaparoFirstStage.intents()")
        self.assertEqual(len(intents), 9)
        self.assertEqual(self.page.locator("[data-first-intent]").count(), 9)
        self.assertTrue(self.page.locator("#brief-form").is_hidden())
        routes = 0
        bank_prefixes = {
            "promote_",
            "sell_",
            "event_",
            "lead_",
            "hire_",
            "fundraise_",
            "announce_",
            "community_",
            "reputation_",
        }
        for intent in intents:
            outcomes = self.page.evaluate(
                "intent=>YaparoFirstStage.outcomes(intent)", intent["id"]
            )
            for outcome in outcomes:
                self.select_pair(intent["id"], outcome["id"])
                routes += 1
                current = self.snapshot()["firstStage"]
                self.assertEqual(current["intent"], intent["id"])
                self.assertEqual(current["outcome"], outcome["id"])
                self.assertTrue(self.page.locator("#first-stage-context").is_visible())
                self.assertEqual(
                    self.page.locator("#first-stage-outcomes > button").count(),
                    len(outcomes),
                )
                actual = self.page.locator("[data-first-field]").evaluate_all(
                    "nodes=>nodes.map(n=>n.dataset.firstField)"
                )
                for field_id in actual:
                    if any(field_id.startswith(prefix) for prefix in bank_prefixes):
                        self.assertTrue(field_id.startswith(intent["id"] + "_"))
                if intent["id"] == "fundraise":
                    text = self.page.locator("#first-stage-fields").inner_text()
                    self.assertNotIn("Şirketlere ürün", text)
                    self.assertNotIn("Mağazamdan", text)
                    self.assertEqual(self.page.locator("#business:visible").count(), 0)
        self.assertGreaterEqual(routes, 46)

    def test_required_and_donation_targets_prune_on_outcome_change(self):
        self.select_pair("fundraise", "donate")
        self.submit()
        self.assertTrue(self.page.locator("#first-stage-errors").is_visible())
        self.assertIsNone(self.snapshot()["brief"])
        self.assertEqual(
            self.page.evaluate("document.activeElement.id"),
            "first-stage-fundraise_organizer_type",
        )
        self.field("fundraise_target_status").select_option("set")
        self.field("fundraise_target").fill("1000")
        self.field("fundraise_currency").select_option("TRY")
        self.field("action_donation_method").select_option("official_page")
        self.field("action_url").fill("https://ornek.example/bagis")
        self.page.locator("#first-stage-fields > details > summary").click()
        self.field("risk").focus()
        self.field("risk").select_option("health")
        self.assertEqual(
            self.page.evaluate("document.activeElement.id"), "first-stage-risk"
        )
        self.select_pair("fundraise", "volunteer")
        answers = self.snapshot()["firstStage"]["answers"]
        self.assertEqual(answers.get("risk"), "health")
        for field_id in [
            "fundraise_target",
            "fundraise_currency",
            "action_donation_method",
            "action_url",
        ]:
            self.assertNotIn(field_id, answers)
            self.assertEqual(self.field(field_id).count(), 0)
        self.assertTrue(self.field("action_volunteer_task").is_visible())
        self.select_pair("fundraise", "materials")
        self.assertTrue(self.field("action_materials").is_visible())
        self.assertEqual(self.field("fundraise_target").count(), 0)
        self.select_pair("fundraise", "understand")
        self.assertEqual(self.field("action_donation_method").count(), 0)
        self.assertEqual(self.field("fundraise_permit").count(), 0)
        self.assertTrue(self.field("fundraise_goal").is_visible())

    def test_event_location_date_errors_and_independent_hiring_controls(self):
        self.select_pair("event", "register")
        self.field("event_mode").select_option("physical")
        self.assertTrue(self.field("event_location_address").is_visible())
        self.assertTrue(self.field("event_location_map_url").is_visible())
        self.field("event_timing").select_option("range")
        self.field("event_start").fill("2026-11-20")
        self.field("event_end").fill("2026-11-19")
        self.submit()
        self.assertEqual(self.field("event_end").get_attribute("aria-invalid"), "true")
        self.assertEqual(
            self.field("event_location_address").get_attribute("aria-invalid"), "true"
        )
        self.field("event_location_address").fill("Sentetik Örnek Salon, İzmir")
        self.field("event_mode").select_option("online")
        self.assertEqual(self.field("event_location_address").count(), 0)
        self.assertNotIn(
            "event_location_address", self.snapshot()["firstStage"]["answers"]
        )
        self.assertTrue(self.field("event_online_method").is_visible())
        self.select_pair("hire", "apply")
        self.assertTrue(self.field("hire_role").is_visible())
        self.assertEqual(self.field("hire_role").get_attribute("type"), "text")
        self.field("hire_type").select_option("intern")
        self.field("hire_model").select_option("remote")
        self.assertEqual(self.field("hire_location_address").count(), 0)
        self.field("hire_model").select_option("hybrid")
        self.assertTrue(self.field("hire_location_address").is_visible())
        self.assertEqual(self.field("event_start").count(), 0)

    def test_urls_custom_answer_and_paid_classification_gate(self):
        self.select_pair("promote", "traffic")
        self.fill_remaining(mode="paid")
        self.field("action_url").fill("javascript:alert(1)")
        self.submit()
        self.assertEqual(self.field("action_url").get_attribute("aria-invalid"), "true")
        self.assertIsNone(self.snapshot()["brief"])
        self.field("action_url").fill("https://user:secret@ornek.example/path")
        self.submit()
        self.assertEqual(self.field("action_url").get_attribute("aria-invalid"), "true")
        self.field("action_url").fill("https://ornek.example/sentetik")
        self.field("promote_kind").select_option("other")
        custom = self.field("promote_kind_other")
        self.assertTrue(custom.is_visible())
        custom.fill(" ")
        self.submit()
        self.assertEqual(custom.get_attribute("aria-invalid"), "true")
        custom.fill("Sentetik özgün proje")
        self.submit()
        self.page.locator("#step-1").wait_for(state="visible")
        self.assertEqual(self.page.locator("#business").input_value(), "")
        self.assertEqual(self.page.locator("#sector").input_value(), "")
        self.assertIsNone(self.snapshot()["plan"])
        self.assertIn(
            "bölgesini seç", self.page.locator("#decision-status").inner_text()
        )
        self.assertFalse(self.snapshot()["brief"]["planContext"]["verified"])
        self.assertEqual(
            self.snapshot()["brief"]["firstStage"]["answers"]["promote_kind_other"],
            "Sentetik özgün proje",
        )

    def test_organic_full_flow_literal_summary_history_and_invalidation(self):
        self.select_pair("promote", "understand")
        self.fill_remaining(mode="organic")
        literal = '<img src="x" onerror="alert(1)"> Sentetik çalışma'
        self.field("promote_name").fill(literal)
        self.submit()
        self.page.locator("#step-1").wait_for(state="visible")
        self.assertIsNone(self.snapshot()["plan"])
        self.assertTrue(self.page.locator("#owned-plan-context").is_hidden())
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.page.locator("#step-2").wait_for(state="visible")
        self.assertEqual(self.page.locator(".concept-card").count(), 3)
        old_name = self.snapshot()["brief"]["firstStage"]["answers"]["promote_name"]
        self.page.locator("#regenerate").click()
        self.page.locator("#previous-trio").click()
        self.assertEqual(
            self.snapshot()["firstStage"]["answers"]["promote_name"], old_name
        )
        self.page.locator(".choose").first.click()
        self.page.locator("#adapt-content").click()
        self.page.locator("#content-next").click()
        self.page.locator("#step-3").wait_for(state="visible")
        self.assertIn(literal, self.page.locator("#review").inner_text())
        self.assertEqual(self.page.locator('#review img[src="x"]').count(), 0)
        self.page.locator('#step-nav [data-step="0"]').click()
        self.assertEqual(self.field("promote_name").input_value(), literal)
        self.field("promote_name").fill("Sentetik güncel çalışma")
        self.assertTrue(self.page.locator('#step-nav [data-step="2"]').is_disabled())
        self.assertTrue(self.snapshot()["stale"])
        self.select_pair("event", "register")
        self.assertNotIn("promote_name", self.snapshot()["firstStage"]["answers"])

    def test_paid_brief_analysis_and_later_edit_invalidation(self):
        self.select_pair("promote", "visit")
        self.fill_remaining(mode="paid")
        self.submit()
        self.page.locator("#step-1").wait_for(state="visible")
        self.assertIsNone(self.snapshot()["plan"])
        self.assertEqual(self.page.locator("#business").input_value(), "")
        self.plan_basics()
        self.page.get_by_text(
            "ECB çapraz referans USD/TRY · Güncel kayıt", exact=True
        ).wait_for(state="attached")
        self.page.locator("#recommend").click()
        self.assertEqual(self.page.locator("#action").input_value(), "visit_store")
        self.assertGreater(self.snapshot()["plan"]["allocated"], 0)
        self.assertFalse(self.snapshot()["plan"]["publishable"])
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.page.locator("#step-2").wait_for(state="visible")
        self.page.locator('#step-nav [data-step="0"]').click()
        self.field("promote_name").fill("Sentetik değişen mağaza çalışması")
        self.assertTrue(self.snapshot()["stale"])
        self.assertTrue(self.page.locator('#step-nav [data-step="2"]').is_disabled())
        self.assertIsNone(self.snapshot()["adaptations"])

    def test_unmapped_email_and_volunteering_do_not_use_fallback_actions(self):
        self.select_pair("promote", "contact")
        self.field("action_contact").select_option("message")
        self.field("action_message_method").select_option("email")
        self.fill_remaining(mode="paid")
        self.submit()
        self.page.locator("#step-1").wait_for(state="visible")
        self.plan_basics()
        self.page.locator("#recommend").click()
        self.assertEqual(self.page.locator("#action").input_value(), "")
        self.assertIsNone(self.snapshot()["plan"])
        self.assertIn(
            "henüz bağlı değil", self.page.locator("#decision-status").inner_text()
        )
        self.page.locator('#step-nav [data-step="0"]').click()
        self.select_pair("fundraise", "volunteer")
        self.fill_remaining(mode="organic")
        self.submit()
        self.page.locator("#step-1").wait_for(state="visible")
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.page.locator("#step-2").wait_for(state="visible")
        self.assertEqual(self.page.locator(".concept-card").count(), 3)
        self.assertEqual(self.snapshot()["brief"]["firstStage"]["outcome"], "volunteer")
        self.assertEqual(self.snapshot()["brief"]["action"], "")
        self.page.locator(".choose").first.click()
        self.assertEqual(self.snapshot()["creative"]["outcome"], "volunteer")
        self.assertNotIn("WhatsApp", self.snapshot()["creative"]["cta"])

    def test_community_registration_is_not_paid_event_registration(self):
        self.select_pair("community", "register")
        self.fill_remaining(mode="paid")
        self.submit()
        self.page.locator("#step-1").wait_for(state="visible")
        self.assertEqual(self.page.locator("#action").input_value(), "")
        self.assertIsNone(self.snapshot()["plan"])
        self.assertIsNone(
            self.snapshot()["brief"]["outcomeContract"]["legacyProjection"]
        )
        self.plan_basics()
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.assertTrue(self.page.locator("#step-1").is_visible())
        self.assertIn(
            "ücretli kanal eşleştirmesi",
            self.page.locator("#plan-next-status").inner_text(),
        )

    def test_owned_content_only_formats_destination_and_binding(self):
        self.select_pair("fundraise", "materials")
        self.fill_remaining(mode="content_only")
        self.submit()
        self.page.locator("#step-1").wait_for(state="visible")
        self.assertTrue(self.page.locator("#owned-content-formats").is_visible())
        self.assertTrue(self.page.locator("#organic-controls").is_hidden())
        self.assertIsNone(self.snapshot()["plan"])
        self.page.locator('[name="owned-format"][value="image"]').uncheck()
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.page.locator("#step-2").wait_for(state="visible")
        self.assertEqual(self.page.locator(".concept-card").count(), 3)
        self.page.locator(".choose").first.click()
        creative = self.snapshot()["creative"]
        self.assertEqual(creative["outcome"], "materials")
        self.assertEqual(len(self.snapshot()["production"]["requirements"]), 1)
        self.assertEqual(
            self.snapshot()["production"]["requirements"][0]["medium"], "text"
        )
        self.page.locator("#adapt-content").click()
        preview = self.snapshot()["adaptations"][0]
        self.assertEqual(preview["outcomeSignature"], creative["outcomeSignature"])
        self.assertEqual(preview["destination"], creative["destination"])
        self.assertFalse(preview["publishable"])
        self.page.locator("#content-next").click()
        self.page.locator("#step-3").wait_for(state="visible")
        self.assertIn(
            creative["kpi"]["label"], self.page.locator("#review").inner_text()
        )
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "owned-materials-review-desktop.png"),
            full_page=True,
        )
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"), 390
        )
        self.page.screenshot(
            path=str(self.evidence / "owned-materials-review-mobile.png"),
            full_page=True,
        )
        self.page.locator('#step-nav [data-step="1"]').click()
        self.page.locator('[name="owned-format"][value="image"]').check()
        self.assertTrue(self.snapshot()["stale"] is False)
        self.assertIsNone(self.snapshot()["contentBinding"])
        self.assertTrue(self.page.locator('#step-nav [data-step="2"]').is_disabled())

    def test_unsure_requires_explicit_use_then_email_stays_email(self):
        self.select_pair("promote", "contact")
        self.field("action_contact").select_option("message")
        self.field("action_message_method").select_option("email")
        self.fill_remaining(mode="unsure")
        self.submit()
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.assertTrue(self.page.locator("#step-1").is_visible())
        self.page.locator("#owned-mode").select_option("content_only")
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.page.locator("#step-2").wait_for(state="visible")
        self.page.locator(".choose").first.click()
        first = self.snapshot()["creative"]
        self.assertEqual(first["destination"]["email"], "sentetik@example.test")
        self.page.locator(".concept-card").first.get_by_role(
            "button", name="Benzerini gör"
        ).click()
        self.assertEqual(self.snapshot()["creative"]["cta"], first["cta"])
        self.assertEqual(
            self.snapshot()["creative"]["destination"], first["destination"]
        )
        self.page.locator("#regenerate").click()
        self.page.locator(".choose").first.click()
        self.assertEqual(
            self.snapshot()["creative"]["destination"], first["destination"]
        )
        self.page.locator('#step-nav [data-step="0"]').click()
        self.field("promote_name").fill("")
        before = self.snapshot()["creative"]
        self.page.locator("#chat-input").fill("Daha sade olsun")
        self.page.locator("#chat-form").evaluate("form=>form.requestSubmit()")
        self.assertEqual(
            self.page.locator("#chat-log .assistant-message")
            .last.get_by_role("button")
            .count(),
            0,
        )
        self.assertEqual(self.snapshot()["creative"], before)

    def test_mobile_layout_keyboard_focus_and_evidence(self):
        self.page.set_viewport_size({"width": 1100, "height": 900})
        self.select_pair("fundraise", "donate")
        self.field("fundraise_organizer_type").select_option("association")
        self.field("fundraise_organizer_name").fill("Sentetik Örnek Dernek")
        self.field("fundraise_purpose").focus()
        self.field("fundraise_purpose").select_option("other")
        self.assertEqual(
            self.page.evaluate("document.activeElement.id"),
            "first-stage-fundraise_purpose",
        )
        self.field("fundraise_purpose_other").fill("Sentetik kitap desteği")
        self.field("fundraise_purpose").select_option("education")
        self.assertNotIn(
            "fundraise_purpose_other", self.snapshot()["firstStage"]["answers"]
        )
        self.field("fundraise_target_status").select_option("set")
        self.field("fundraise_target").fill("1500")
        self.field("fundraise_currency").select_option("TRY")
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "owned-donation-desktop.png"), full_page=True
        )
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"), 390
        )
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "owned-donation-mobile.png"), full_page=True
        )
        self.select_pair("hire", "apply")
        self.field("hire_model").select_option("hybrid")
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"), 390
        )
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "owned-hiring-mobile.png"), full_page=True
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
