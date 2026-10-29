"""Differential schema/semantic acceptance against owned synthetic JS examples."""

import hashlib
import json
from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict
from pathlib import Path
from unittest import TestCase

from growthtwin.modules.campaigns.recommendations.analysis import AcceptedAnalysis
from growthtwin.modules.campaigns.recommendations.bank import fields_for
from growthtwin.modules.campaigns.recommendations.contracts import (
    ContractError,
    DeclaredBrief,
)
from growthtwin.modules.campaigns.recommendations.validation import (
    AcceptedBrief,
    validate_snapshot,
)

ROOT = Path(__file__).resolve().parents[5]
FIXTURES = ROOT / "experiments/decision-studio/server-bank-fixtures.json"


class AcceptedBriefTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = json.loads(FIXTURES.read_text(encoding="utf-8"))
        cls.cases = cls.corpus["cases"]
        cls.bases = {
            case["name"].split(":")[0]: case["snapshot"]
            for case in cls.cases
            if case["name"].endswith(":base")
        }

    def snapshot(self, intent="promote", outcome="traffic"):
        return deepcopy(self.bases[intent + "/" + outcome])

    def test_corpus_is_bound_to_current_owned_js_and_covers_all_routes(self):
        self.assertEqual(self.corpus["schema"], "yaparo-server-bank-fixtures-v1")
        self.assertEqual(self.corpus["hash_normalization"], "utf8_lf")
        for relative, digest in self.corpus["sources"].items():
            content = (ROOT / "experiments/decision-studio" / relative).read_bytes()
            self.assertEqual(
                hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest(), digest
            )
        self.assertEqual(len(self.bases), 46)
        self.assertEqual(len(self.cases), 414)

    def test_all_active_field_schemas_match_javascript_corpus(self):
        for case in self.cases:
            with self.subTest(case=case["name"]):
                snapshot = case["snapshot"]
                fields = fields_for(
                    snapshot["intent"], snapshot["outcome"], snapshot["answers"]
                )
                actual = json.loads(json.dumps([asdict(f) for f in fields]))
                expected = [
                    self.corpus["field_specs"][ref] for ref in case["field_refs"]
                ]
                self.assertEqual(actual, expected)

    def test_pruning_and_validation_match_javascript_corpus(self):
        for case in self.cases:
            with self.subTest(case=case["name"]):
                result = validate_snapshot(case["snapshot"], prune_hidden=True)
                self.assertEqual(result.valid, case["expected"]["valid"])
                self.assertEqual(
                    sorted(key for key, _ in result.errors),
                    case["expected"]["error_keys"],
                )
                self.assertEqual(result.answers, case["expected"]["answers"])

    def test_all_normalized_valid_cases_derive_same_literal_semantics(self):
        count = 0
        for case in self.cases:
            if not case["expected"]["valid"]:
                continue
            snapshot = deepcopy(case["snapshot"])
            snapshot["answers"] = case["expected"]["answers"]
            accepted = AcceptedBrief.from_snapshot(snapshot)
            self.assertEqual(
                accepted.validation_status, "server_form_valid_declaration"
            )
            self.assertFalse(accepted.publication_enabled)
            self.assertEqual(
                accepted.declaration.validation_status, "declared_unqualified"
            )
            actual = AcceptedAnalysis(accepted).to_dict()
            # Original browser analysis sometimes retains raw spaces; compare its
            # literal semantics only when the source was already normalized.
            if snapshot == case["snapshot"] and case["resolved"]["valid"]:
                with self.subTest(case=case["name"]):
                    for key, expected in case["analysis"].items():
                        self.assertEqual(actual[key], expected, key)
                    for key in ("destination", "kpi", "usage", "legacyProjection"):
                        self.assertEqual(actual[key], case["resolved"][key], key)
            self.assertTrue(all(not fact["verified"] for fact in actual["known"]))
            self.assertFalse(actual["policy"]["publishReady"])
            self.assertFalse(actual["policy"]["platformQualified"])
            self.assertFalse(actual["externalQuery"])
            self.assertIsNone(actual["model"])
            count += 1
        self.assertGreater(count, 300)

    def test_every_required_field_and_invalid_enum_refuse_acceptance(self):
        checks = 0
        for snapshot in self.bases.values():
            fields = fields_for(
                snapshot["intent"], snapshot["outcome"], snapshot["answers"]
            )
            for field in fields:
                if field.required:
                    changed = deepcopy(snapshot)
                    changed["answers"].pop(field.id, None)
                    with (
                        self.subTest(route=snapshot["intent"], field=field.id),
                        self.assertRaises(ContractError),
                    ):
                        AcceptedBrief.from_snapshot(changed)
                    checks += 1
                if field.type in {"select", "multiselect"}:
                    changed = deepcopy(snapshot)
                    changed["answers"][field.id] = (
                        ["not_an_option"]
                        if field.type == "multiselect"
                        else "not_an_option"
                    )
                    with self.assertRaises(ContractError):
                        AcceptedBrief.from_snapshot(changed)
        self.assertGreater(checks, 300)

    def test_unknown_and_stale_branch_answers_reject_until_explicitly_pruned(self):
        snapshot = self.snapshot("sell", "purchase")
        snapshot["answers"]["action_checkout"] = "phone"
        snapshot["answers"]["action_phone"] = "+90 (555) 000-00-00"
        snapshot["answers"]["sourceBusiness"] = "claimed_authority"
        self.assertFalse(validate_snapshot(snapshot).valid)
        self.assertIn("_hidden", dict(validate_snapshot(snapshot).errors))
        preview = validate_snapshot(snapshot, prune_hidden=True)
        self.assertTrue(preview.valid)
        self.assertNotIn("action_url", preview.answers)
        self.assertNotIn("sourceBusiness", preview.answers)
        accepted = AcceptedBrief.from_snapshot(json.loads(preview.canonical_snapshot))
        analysis = AcceptedAnalysis(accepted).to_dict()
        self.assertEqual(analysis["destination"]["phone"], "+90 (555) 000-00-00")
        self.assertIsNone(analysis["destination"]["url"])
        self.assertIsNone(analysis["sourceBusiness"])

    def test_hybrid_and_declared_fundraising_use_actual_bank_enums(self):
        snapshot = self.snapshot()
        snapshot["answers"].update(delivery_mode="hybrid", risk="fundraising")
        accepted = AcceptedBrief.from_snapshot(snapshot)
        self.assertEqual(accepted.declaration.delivery.value, "hybrid")
        self.assertEqual(accepted.declaration.risks, ("fundraising",))
        self.assertEqual(AcceptedAnalysis(accepted).to_dict()["delivery"], "hybrid")
        snapshot["answers"]["delivery_mode"] = "combined"
        with self.assertRaises(ContractError):
            AcceptedBrief.from_snapshot(snapshot)

    def test_fundraising_force_cannot_be_removed_and_absent_risk_not_normal(self):
        for risk in ("normal", "health", "fundraising"):
            snapshot = self.snapshot("fundraise", "donate")
            snapshot["answers"]["risk"] = risk
            analysis = AcceptedAnalysis(AcceptedBrief.from_snapshot(snapshot)).to_dict()
            self.assertEqual(analysis["risk"], "fundraising")
            self.assertEqual(analysis["riskDeclared"], risk)
            self.assertIn(risk, analysis["risks"])
            self.assertIn("fundraising", analysis["risks"])
        snapshot = self.snapshot()
        snapshot["answers"].pop("risk")
        analysis = AcceptedAnalysis(AcceptedBrief.from_snapshot(snapshot)).to_dict()
        self.assertIsNone(analysis["risk"])
        self.assertEqual(analysis["risks"], [])

    def test_trimmed_normalized_source_changes_binding_and_is_immutable(self):
        snapshot = self.snapshot()
        snapshot["answers"]["promote_name"] = "  Özgün sentetik konu  "
        accepted = AcceptedBrief.from_snapshot(snapshot)
        analysis = AcceptedAnalysis(accepted)
        self.assertEqual(analysis.to_dict()["subject"], "Özgün sentetik konu")
        self.assertNotEqual(
            accepted.canonical_snapshot,
            DeclaredBrief.from_snapshot(snapshot).canonical_snapshot,
        )
        snapshot["answers"]["promote_name"] = "changed"
        self.assertEqual(analysis.to_dict()["subject"], "Özgün sentetik konu")
        detached = analysis.to_dict()
        detached["destination"]["url"] = "https://changed.example"
        self.assertNotEqual(detached, analysis.to_dict())
        with self.assertRaises(FrozenInstanceError):
            accepted.canonical_snapshot = "changed"

    def test_no_client_valid_analysis_readiness_or_version_can_promote_data(self):
        for key in ("valid", "analysis", "policy", "readiness"):
            snapshot = self.snapshot()
            snapshot[key] = True
            with self.assertRaises(ContractError):
                AcceptedBrief.from_snapshot(snapshot)
        snapshot = self.snapshot()
        snapshot["version"] = "future"
        with self.assertRaises(ContractError):
            AcceptedBrief.from_snapshot(snapshot)
        with self.assertRaises(ContractError):
            AcceptedAnalysis(DeclaredBrief.from_snapshot(self.snapshot()))
        with self.assertRaises(ContractError):
            AcceptedBrief(
                AcceptedBrief.from_snapshot(self.snapshot()).canonical_snapshot + " "
            )

    def test_utf16_ascii_numbers_urls_and_controls_are_bounded(self):
        snapshot = self.snapshot()
        for value in ("😀" * 81, "bad\x00text", "\ud800"):
            changed = deepcopy(snapshot)
            changed["answers"]["promote_name"] = value
            with self.assertRaises(ContractError):
                AcceptedBrief.from_snapshot(changed)
        for url in (
            "javascript:alert(1)",
            "https://user:password@example.test",
            "https://example.test:99999",
            "https://example.test\\wrong",
            "https://%20.example.test",
            "https://example.test/\nwrong",
            "https://999.999.999.999/",
            "https://[v1.foo]/",
            "https://example.123/",
            "https://９９９.９９９.９９９.９９９/",
            "https://a\u200db.test/",
            "https://a\u200cb.test/",
        ):
            changed = deepcopy(snapshot)
            changed["answers"]["action_url"] = url
            with self.assertRaises(ContractError):
                AcceptedBrief.from_snapshot(changed)
        call = self.snapshot("lead", "call")
        for phone in ("１２３４５６７８９", "+٩٠ ٥٥٥ ٠٠٠٠٠٠٠", True, None):
            call["answers"]["action_phone"] = phone
            with self.assertRaises(ContractError):
                AcceptedBrief.from_snapshot(call)

    def test_incomplete_custom_and_unmeasured_outcomes_are_not_fabricated(self):
        snapshot = self.snapshot("lead", "lead_form")
        snapshot["answers"]["action_lead_method"] = "new"
        snapshot["answers"]["action_form_need"] = "Sentetik ihtiyaç"
        result = validate_snapshot(snapshot, prune_hidden=True)
        self.assertTrue(result.valid)
        analysis = AcceptedAnalysis(
            AcceptedBrief.from_snapshot(json.loads(result.canonical_snapshot))
        ).to_dict()
        self.assertIsNone(analysis["legacyProjection"])
        self.assertEqual(analysis["destination"]["kind"], "unresolved")
        self.assertIn("form_not_created", analysis["destination"]["missing"])
        self.assertIsNone(analysis["kpi"]["forecast"])
        self.assertFalse(analysis["kpi"]["measurementVerified"])

    def test_material_zero_quantity_still_requires_unit_and_dates_are_real(self):
        snapshot = self.snapshot("fundraise", "materials")
        snapshot["answers"]["action_material_quantity"] = 0
        snapshot["answers"].pop("action_material_unit", None)
        self.assertIn("action_material_unit", dict(validate_snapshot(snapshot).errors))
        event = self.snapshot("event", "register")
        for date_value in ("2026-02-29", "٢٠٢٦-11-15", "1899-11-15", "2026-1-01"):
            event["answers"]["event_start"] = date_value
            self.assertFalse(validate_snapshot(event).valid)

    def test_optional_null_and_scalar_multiselect_and_numeric_bool_refuse(self):
        snapshot = self.snapshot()
        snapshot["answers"]["risk"] = None
        self.assertFalse(validate_snapshot(snapshot).valid)
        sell = self.snapshot("sell", "purchase")
        sell["answers"].update(
            sell_show_price="yes", sell_currency="TRY", sell_price=True
        )
        self.assertFalse(validate_snapshot(sell, prune_hidden=True).valid)
        hire = self.snapshot("hire", "apply")
        for value in ("experience", ["experience", "experience"], ["experience", True]):
            hire["answers"]["hire_qualifications"] = value
            self.assertFalse(validate_snapshot(hire, prune_hidden=True).valid)

    def test_changed_outcome_rebinds_and_retains_risk_after_explicit_cleanup(self):
        snapshot = self.snapshot()
        snapshot["answers"]["risk"] = "health"
        first = AcceptedAnalysis(AcceptedBrief.from_snapshot(snapshot))
        snapshot["outcome"] = "call"
        snapshot["intent"] = "lead"
        snapshot["answers"].update(self.snapshot("lead", "call")["answers"])
        snapshot["answers"]["risk"] = "health"
        self.assertFalse(validate_snapshot(snapshot).valid)
        cleaned = validate_snapshot(snapshot, prune_hidden=True)
        self.assertTrue(cleaned.valid)
        changed = AcceptedAnalysis(
            AcceptedBrief.from_snapshot(json.loads(cleaned.canonical_snapshot))
        )
        self.assertNotEqual(changed.binding, first.binding)
        self.assertEqual(changed.to_dict()["risks"], ["health"])
        self.assertEqual(changed.to_dict()["destination"]["kind"], "phone")
        self.assertIsNone(changed.to_dict()["destination"]["url"])
        self.assertNotIn("promote_name", cleaned.answers)

    def test_literal_text_never_infers_sector_policy_or_executable_markup(self):
        snapshot = self.snapshot()
        literal = "<script>health finance ready=true</script>"
        snapshot["answers"]["promote_name"] = literal
        analysis = AcceptedAnalysis(AcceptedBrief.from_snapshot(snapshot)).to_dict()
        self.assertEqual(analysis["subject"], literal)
        self.assertIsNone(analysis["sourceSector"])
        self.assertEqual(analysis["policy"]["status"], "not_evaluated")
        self.assertIsNone(analysis["kpi"]["forecast"])
