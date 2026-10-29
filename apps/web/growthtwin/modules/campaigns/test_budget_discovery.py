"""Pure synthetic discovery metadata acceptance; no account or database work."""

import json
from copy import deepcopy
from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4
from zoneinfo import ZoneInfo

from growthtwin.modules.campaigns.recommendations.analysis import AcceptedAnalysis
from growthtwin.modules.campaigns.recommendations.contracts import (
    ContractError,
    DeclaredBrief,
    OwnerScope,
    PlanBounds,
)
from growthtwin.modules.campaigns.recommendations.discovery import (
    BudgetDiscoveryDraft,
    CashFit,
    DiscoveryContext,
    SyntheticScenario,
    clear_cash_fit,
    confirm_cash_fit,
    record_cash_availability,
    revise_discovery,
    select_scenario,
)
from growthtwin.modules.campaigns.recommendations.validation import AcceptedBrief


class BudgetDiscoveryTests(TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[5]
        corpus = json.loads(
            (root / "experiments/decision-studio/server-bank-fixtures.json").read_text(
                encoding="utf-8"
            )
        )
        cls.base = next(
            case["snapshot"]
            for case in corpus["cases"]
            if case["name"] == "promote/traffic:base"
        )

    def setUp(self):
        self.now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
        self.scope = OwnerScope(1, 2, uuid4(), 3)
        self.context = DiscoveryContext(
            business_country="TR",
            account_country=None,
            target_markets=("TR",),
            language="tr",
            currency="TRY",
            timezone="Europe/Istanbul",
            result_deadline=date(2026, 12, 1),
            flight_start=date(2026, 11, 1),
            flight_end=date(2026, 11, 14),
            region_declaration="Sentetik bölge",
        )
        self.draft = BudgetDiscoveryDraft(self.scope, self.analysis(), self.context)

    def analysis(self, delivery="paid", name="Sentetik ürün"):
        snapshot = deepcopy(self.base)
        snapshot["answers"]["delivery_mode"] = delivery
        snapshot["answers"]["promote_name"] = name
        return AcceptedAnalysis(AcceptedBrief.from_snapshot(snapshot))

    def scenario(self, draft=None, **overrides):
        draft = draft or self.draft
        values = dict(
            candidate_id=uuid4(),
            context_binding=draft.context_binding,
            currency=draft.context.currency,
            media_budget_minor=200_000,
            production_cost_minor=20_000,
            service_cost_minor=0,
            peak_cash_need_minor=250_000,
            created_at=self.now - timedelta(minutes=1),
            expires_at=self.now + timedelta(hours=1),
        )
        values.update(overrides)
        return SyntheticScenario(**values)

    def selected(self, draft=None, scenario=None, **overrides):
        draft = draft or self.draft
        values = dict(
            trusted_scope=draft.scope, expected_binding=draft.binding, now=self.now
        )
        values.update(overrides)
        return select_scenario(draft, scenario or self.scenario(draft), **values)

    def cash(self, draft, **overrides):
        values = dict(
            context_binding=draft.context_binding,
            scenario_binding=draft.selection.binding,
            currency=draft.context.currency,
            available_cash_minor=250_000,
            declared_at=self.now + timedelta(minutes=1),
            expires_at=self.now + timedelta(minutes=30),
        )
        values.update(overrides)
        return CashFit(**values)

    def confirmed(self, draft=None, cash=None, **overrides):
        draft = draft or self.selected()
        values = dict(
            trusted_scope=draft.scope,
            expected_binding=draft.binding,
            now=self.now + timedelta(minutes=2),
        )
        values.update(overrides)
        return confirm_cash_fit(draft, cash or self.cash(draft), **values)

    def revised(self, draft, **overrides):
        values = dict(
            trusted_scope=draft.scope,
            expected_binding=draft.binding,
            analysis=draft.analysis,
            context=draft.context,
            optional_ceiling_minor=draft.optional_ceiling_minor,
        )
        values.update(overrides)
        return revise_discovery(draft, **values)

    def test_unknown_zero_positive_ceiling_remain_distinct(self):
        unknown = self.draft
        zero = replace(unknown, optional_ceiling_minor=0)
        positive = replace(unknown, optional_ceiling_minor=200_000)
        self.assertEqual(unknown.ceiling_status, "unknown")
        self.assertEqual(zero.ceiling_status, "no_paid_media")
        self.assertEqual(positive.ceiling_status, "declared_ceiling")
        self.assertEqual(len({d.context_binding for d in (unknown, zero, positive)}), 3)
        self.assertEqual(unknown.stage_at(self.now), "discovery")
        with self.assertRaises(ContractError):
            self.selected(zero)

    def test_unresolved_period_and_region_are_valid_discovery_not_selectable(self):
        context = replace(
            self.context,
            result_deadline=None,
            flight_start=None,
            flight_end=None,
            region_declaration=None,
        )
        draft = replace(self.draft, context=context)
        self.assertEqual(
            context.missing_requirements, ("result_deadline", "flight_period", "region")
        )
        self.assertIsNone(context.flight_days)
        self.assertEqual(draft.stage_at(self.now), "discovery")
        with self.assertRaises(ContractError):
            self.selected(draft)
        for missing in ("result_deadline", "region_declaration"):
            with self.assertRaises(ContractError):
                self.selected(
                    replace(
                        self.draft, context=replace(self.context, **{missing: None})
                    )
                )

    def test_context_date_type_inclusive_period_and_result_deadline_separate(self):
        self.assertEqual(self.context.flight_days, 14)
        self.assertEqual(
            replace(self.context, flight_end=self.context.flight_start).flight_days, 1
        )
        self.assertGreater(self.context.result_deadline, self.context.flight_end)
        for changes in (
            {"flight_start": None},
            {"flight_end": date(2026, 10, 30)},
            {"flight_start": self.now},
            {"result_deadline": date(2026, 10, 31)},
            {"timezone": "not/a/timezone"},
            {"target_markets": ["TR"]},
            {"target_markets": ("TR", "TR")},
        ):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                replace(self.context, **changes)

    def test_only_accepted_analysis_and_strict_scope_are_admitted(self):
        declaration = DeclaredBrief.from_snapshot(deepcopy(self.base))
        for changes in (
            {"analysis": declaration},
            {"analysis": {"valid": True}},
            {"scope": {"owner_id": 1}},
        ):
            with self.assertRaises(ContractError):
                replace(self.draft, **changes)

    def test_bindings_immutable_and_change_for_each_context_dimension(self):
        binding = self.draft.context_binding
        self.assertEqual(self.draft.context_binding, binding)
        changes = (
            {"scope": replace(self.scope, owner_id=4)},
            {"scope": replace(self.scope, workspace_id=4)},
            {"scope": replace(self.scope, brand_id=4)},
            {"analysis": self.analysis(name="Başka sentetik ürün")},
            {"optional_ceiling_minor": 1},
            {"context_revision": 2},
        )
        for change in changes:
            with self.subTest(change=tuple(change)):
                self.assertNotEqual(
                    replace(self.draft, **change).context_binding, binding
                )
        for change in (
            {"business_country": "DE"},
            {"account_country": "US"},
            {"target_markets": ("TR", "DE")},
            {"currency": "EUR"},
            {"language": "en"},
            {"timezone": "UTC"},
            {"region_declaration": "Başka bölge"},
            {"flight_end": date(2026, 11, 15)},
            {"result_deadline": date(2026, 12, 2)},
        ):
            with self.subTest(change=change):
                changed = replace(self.draft, context=replace(self.context, **change))
                self.assertNotEqual(changed.context_binding, binding)
        with self.assertRaises(FrozenInstanceError):
            self.draft.optional_ceiling_minor = 123

    def test_semantic_versions_change_draft_binding_and_reject_old_expected_state(self):
        binding = self.draft.binding
        context_binding = self.draft.context_binding
        for target in (
            "growthtwin.modules.campaigns.recommendations.analysis.VERSION",
            "growthtwin.modules.campaigns.recommendations.validation.VALIDATOR_VERSION",
            "growthtwin.modules.campaigns.recommendations.validation.BANK_VERSION",
        ):
            with self.subTest(target=target), patch(target, "synthetic-future-version"):
                self.assertNotEqual(self.draft.context_binding, context_binding)
                self.assertNotEqual(self.draft.binding, binding)
                with self.assertRaises(ContractError):
                    self.revised(self.draft, expected_binding=binding)

    def test_positive_media_ceiling_does_not_include_production_or_cash(self):
        draft = replace(self.draft, optional_ceiling_minor=200_000)
        selected = self.selected(draft)
        self.assertEqual(selected.selection.campaign_cost_minor, 220_000)
        self.assertEqual(selected.selection.peak_cash_need_minor, 250_000)
        self.assertEqual(selected.optional_ceiling_minor, 200_000)
        with self.assertRaises(ContractError):
            self.selected(draft, self.scenario(draft, media_budget_minor=200_001))
        with self.assertRaises(ContractError):
            self.confirmed(selected, self.cash(selected, available_cash_minor=220_000))

    def test_all_money_inputs_are_integer_minor_units_not_bool_or_float(self):
        for bad in (True, False, -1, 1.0, 1_000_000_000):
            with self.assertRaises(ContractError):
                replace(self.draft, optional_ceiling_minor=bad)
            for key in (
                "production_cost_minor",
                "service_cost_minor",
                "peak_cash_need_minor",
            ):
                with self.subTest(key=key, bad=bad), self.assertRaises(ContractError):
                    self.scenario(**{key: bad})
        for bad in (0, True, 1.5):
            with self.assertRaises(ContractError):
                self.scenario(media_budget_minor=bad)
        with self.assertRaises(ContractError):
            self.scenario(media_budget_minor=999_999_999, production_cost_minor=1)
        with self.assertRaises(ContractError):
            self.scenario(peak_cash_need_minor=219_999)

    def test_expired_future_wrong_context_and_currency_scenarios_refuse(self):
        for changes in (
            {"created_at": self.now + timedelta(seconds=1)},
            {"created_at": self.now - timedelta(hours=2), "expires_at": self.now},
            {"context_binding": "0" * 64},
            {"currency": "EUR"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                self.selected(scenario=self.scenario(**changes))

    def test_paid_selection_for_organic_content_only_unsure_is_rejected(self):
        for delivery in ("organic", "content_only", "unsure"):
            draft = replace(self.draft, analysis=self.analysis(delivery=delivery))
            self.assertEqual(draft.stage_at(self.now), "discovery")
            with self.assertRaises(ContractError):
                self.selected(draft)
        self.assertEqual(
            self.selected(
                replace(self.draft, analysis=self.analysis(delivery="hybrid"))
            ).stage_at(self.now),
            "scenario_selected",
        )

    def test_unknown_peak_cash_cannot_be_confirmed(self):
        selected = self.selected(scenario=self.scenario(peak_cash_need_minor=None))
        self.assertEqual(selected.stage_at(self.now), "scenario_selected")
        with self.assertRaises(ContractError):
            self.confirmed(selected)

    def test_cash_confirmation_is_exact_context_scenario_currency_bound(self):
        selected = self.selected()
        confirmed = self.confirmed(selected)
        self.assertEqual(
            confirmed.stage_at(self.now + timedelta(minutes=2)), "cash_confirmed"
        )
        for changes in (
            {"context_binding": "0" * 64},
            {"scenario_binding": "0" * 64},
            {"currency": "EUR"},
            {"available_cash_minor": 249_999},
            {"declared_at": self.now - timedelta(seconds=1)},
            {"declared_at": self.now + timedelta(minutes=3)},
            {"expires_at": self.now + timedelta(minutes=2)},
        ):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                self.confirmed(selected, self.cash(selected, **changes))

    def test_cash_confirmation_never_authorizes_spend_or_publishing(self):
        for draft in (self.draft, self.selected(), self.confirmed()):
            self.assertFalse(draft.publication_enabled)
            self.assertFalse(draft.execution_authorized)
        with self.assertRaises(TypeError):
            BudgetDiscoveryDraft(
                self.scope, self.analysis(), self.context, stage="cash_confirmed"
            )

    def test_context_revisions_clear_selected_scenario_and_cash(self):
        confirmed = self.confirmed()
        for changes in (
            {"optional_ceiling_minor": 100_000},
            {"analysis": self.analysis(name="Yeni konu")},
            {"context": replace(self.context, region_declaration="Yeni bölge")},
            {"context": replace(self.context, currency="EUR")},
            {"context": replace(self.context, flight_end=date(2026, 11, 15))},
        ):
            with self.subTest(changes=tuple(changes)):
                revised = self.revised(confirmed, **changes)
                self.assertEqual(
                    revised.context_revision, confirmed.context_revision + 1
                )
                self.assertIsNone(revised.selection)
                self.assertIsNone(revised.cash_fit)
                self.assertIsNone(revised.selected_at)
                self.assertEqual(revised.stage_at(self.now), "discovery")
                self.assertFalse(revised.execution_authorized)
        self.assertIs(self.revised(confirmed), confirmed)

    def test_attached_old_selection_or_cash_cannot_survive_direct_context_changes(self):
        confirmed = self.confirmed()
        for changes in (
            {"scope": replace(self.scope, owner_id=8)},
            {"analysis": self.analysis(name="Yeni konu")},
            {"context_revision": 2},
            {"optional_ceiling_minor": 300_000},
            {"context": replace(self.context, region_declaration="Yeni bölge")},
        ):
            with self.assertRaises(ContractError):
                replace(confirmed, **changes)

    def test_new_scenario_clears_cash_and_cannot_rewrite_same_candidate_id(self):
        confirmed = self.confirmed()
        next_scenario = self.scenario(media_budget_minor=180_000)
        selected = self.selected(
            confirmed, next_scenario, now=self.now + timedelta(minutes=3)
        )
        self.assertIsNone(selected.cash_fit)
        self.assertEqual(
            selected.stage_at(self.now + timedelta(minutes=3)), "scenario_selected"
        )
        changed = replace(confirmed.selection, media_budget_minor=180_000)
        with self.assertRaises(ContractError):
            self.selected(confirmed, changed)

    def test_expected_binding_and_scope_must_match_current_metadata(self):
        selected = self.selected()
        for kwargs in (
            {"trusted_scope": replace(self.scope, owner_id=7)},
            {"expected_binding": self.draft.binding},
        ):
            with self.assertRaises(ContractError):
                self.confirmed(selected, **kwargs)
            with self.assertRaises(ContractError):
                self.revised(selected, **kwargs)
        with self.assertRaises(ContractError):
            self.selected(
                selected, self.scenario(), expected_binding=self.draft.binding
            )

    def test_expired_records_remain_historical_and_stage_becomes_stale(self):
        confirmed = self.confirmed()
        self.assertEqual(
            confirmed.stage_at(confirmed.cash_fit.expires_at), "stale_review"
        )
        self.assertEqual(
            confirmed.stage_at(confirmed.selection.expires_at), "stale_review"
        )
        self.assertEqual(
            confirmed.stage_at(self.now - timedelta(seconds=1)), "stale_review"
        )
        self.assertIsNotNone(confirmed.selection)
        self.assertIsNotNone(confirmed.cash_fit)
        with self.assertRaises(ContractError):
            self.confirmed(self.selected(), now=self.now + timedelta(hours=2))

    def test_dst_fold_temporal_comparisons_use_instants(self):
        zone = ZoneInfo("America/New_York")
        earlier = datetime(2026, 11, 1, 1, 45, tzinfo=zone, fold=0)
        later = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)
        draft = replace(
            self.draft, context=replace(self.context, timezone="America/New_York")
        )
        scenario = self.scenario(draft, created_at=earlier, expires_at=later)
        selected_at = datetime(2026, 11, 1, 1, 50, tzinfo=zone, fold=0)
        selected = self.selected(draft, scenario, now=selected_at)
        self.assertEqual(selected.stage_at(selected_at), "scenario_selected")
        self.assertEqual(selected.stage_at(later), "stale_review")
        with self.assertRaises(ContractError):
            replace(scenario, created_at=later, expires_at=earlier)

    def test_past_flight_cannot_receive_new_selection_and_naive_time_refuses(self):
        with self.assertRaises(ContractError):
            self.selected(now=self.now + timedelta(days=5))
        with self.assertRaises(ContractError):
            self.selected(now=self.now.replace(tzinfo=None))
        with self.assertRaises(ContractError):
            self.draft.stage_at(self.now.replace(tzinfo=None))

    def test_old_resolved_planbounds_still_requires_budget(self):
        budget = next(
            field for field in fields(PlanBounds) if field.name == "media_budget_minor"
        )
        self.assertIs(budget.default, MISSING)
        with self.assertRaises(TypeError):
            PlanBounds(
                business_country="TR",
                account_country=None,
                target_markets=("TR",),
                language="tr",
                currency="TRY",
                timezone="Europe/Istanbul",
                start=date(2026, 11, 1),
                end=date(2026, 11, 7),
                region_declaration="Sentetik",
            )
        with self.assertRaises(ContractError):
            PlanBounds(
                business_country="TR",
                account_country=None,
                target_markets=("TR",),
                language="tr",
                currency="TRY",
                timezone="Europe/Istanbul",
                start=date(2026, 11, 1),
                end=date(2026, 11, 7),
                region_declaration="Sentetik",
                media_budget_minor=None,
            )

    def test_lower_cash_declaration_replaces_old_fit_without_authorization(self):
        confirmed = self.confirmed()
        lower = self.cash(
            confirmed,
            available_cash_minor=0,
            declared_at=self.now + timedelta(minutes=3),
        )
        now = self.now + timedelta(minutes=4)
        updated = record_cash_availability(
            confirmed,
            lower,
            trusted_scope=self.scope,
            expected_binding=confirmed.binding,
            now=now,
        )
        self.assertEqual(updated.cash_fit.available_cash_minor, 0)
        self.assertEqual(updated.cash_status_at(now), "insufficient")
        self.assertEqual(updated.stage_at(now), "scenario_selected")
        self.assertNotEqual(updated.binding, confirmed.binding)
        self.assertEqual(confirmed.cash_status_at(now), "sufficient_declared")
        self.assertFalse(updated.execution_authorized)
        self.assertFalse(updated.publication_enabled)
        with self.assertRaises(ContractError):
            record_cash_availability(
                updated,
                self.cash(updated),
                trusted_scope=self.scope,
                expected_binding=confirmed.binding,
                now=now,
            )

    def test_unknown_peak_cash_can_be_recorded_but_not_confirmed(self):
        selected = self.selected(scenario=self.scenario(peak_cash_need_minor=None))
        now = self.now + timedelta(minutes=2)
        cash = self.cash(selected)
        updated = record_cash_availability(
            selected,
            cash,
            trusted_scope=self.scope,
            expected_binding=selected.binding,
            now=now,
        )
        self.assertEqual(updated.cash_status_at(now), "unknown_requirement")
        self.assertEqual(updated.stage_at(now), "scenario_selected")
        self.assertFalse(updated.execution_authorized)
        with self.assertRaises(ContractError):
            confirm_cash_fit(
                selected,
                cash,
                trusted_scope=self.scope,
                expected_binding=selected.binding,
                now=now,
            )

    def test_expired_cash_can_be_renewed_or_withdrawn_without_restoring_spend(self):
        confirmed = self.confirmed()
        now = self.now + timedelta(minutes=40)
        self.assertEqual(confirmed.stage_at(now), "stale_review")
        renewed = record_cash_availability(
            confirmed,
            self.cash(
                confirmed,
                declared_at=self.now + timedelta(minutes=39),
                expires_at=self.now + timedelta(minutes=55),
            ),
            trusted_scope=self.scope,
            expected_binding=confirmed.binding,
            now=now,
        )
        self.assertEqual(renewed.stage_at(now), "cash_confirmed")
        self.assertEqual(renewed.cash_status_at(now), "sufficient_declared")
        withdrawn = clear_cash_fit(
            renewed,
            trusted_scope=self.scope,
            expected_binding=renewed.binding,
        )
        self.assertIsNone(withdrawn.cash_fit)
        self.assertIs(withdrawn.selection, renewed.selection)
        self.assertEqual(withdrawn.stage_at(now), "scenario_selected")
        self.assertEqual(withdrawn.cash_status_at(now), "not_declared")
        late = self.now + timedelta(hours=2)
        expired_withdrawal = clear_cash_fit(
            confirmed,
            trusted_scope=self.scope,
            expected_binding=confirmed.binding,
        )
        self.assertEqual(expired_withdrawal.stage_at(late), "stale_review")
        self.assertFalse(expired_withdrawal.execution_authorized)

    def test_same_scenario_metadata_reselection_after_flight_start_is_no_new_action(
        self,
    ):
        scenario = self.scenario(expires_at=self.now + timedelta(days=6))
        selected = self.selected(scenario=scenario)
        day_two = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
        unchanged = self.selected(selected, scenario, now=day_two)
        self.assertIs(unchanged, selected)
        self.assertEqual(unchanged.selected_at, self.now)
        self.assertEqual(unchanged.stage_at(day_two), "scenario_selected")
        self.assertFalse(unchanged.execution_authorized)
        with self.assertRaises(ContractError):
            self.selected(
                selected, replace(scenario, candidate_id=uuid4()), now=day_two
            )

    def test_cash_confirm_then_withdraw_does_not_recreate_old_selected_state(self):
        selected = self.selected()
        confirmed = self.confirmed(selected)
        withdrawn = clear_cash_fit(
            confirmed,
            trusted_scope=self.scope,
            expected_binding=confirmed.binding,
        )
        self.assertEqual(selected.context_binding, withdrawn.context_binding)
        self.assertEqual(selected.context_revision, withdrawn.context_revision)
        self.assertEqual(withdrawn.state_revision, selected.state_revision + 2)
        self.assertNotEqual(withdrawn.binding, selected.binding)
        self.assertIsNone(withdrawn.cash_fit)
        with self.assertRaises(ContractError):
            confirm_cash_fit(
                withdrawn,
                self.cash(withdrawn),
                trusted_scope=self.scope,
                expected_binding=selected.binding,
                now=self.now + timedelta(minutes=2),
            )
        self.assertIs(
            clear_cash_fit(
                withdrawn,
                trusted_scope=self.scope,
                expected_binding=withdrawn.binding,
            ),
            withdrawn,
        )
        self.assertFalse(withdrawn.execution_authorized)

    def test_older_or_equal_time_changed_cash_cannot_replace_newer_lower_declaration(
        self,
    ):
        confirmed = self.confirmed()
        lower = self.cash(
            confirmed,
            available_cash_minor=100_000,
            declared_at=self.now + timedelta(minutes=3),
        )
        now = self.now + timedelta(minutes=4)
        current = record_cash_availability(
            confirmed,
            lower,
            trusted_scope=self.scope,
            expected_binding=confirmed.binding,
            now=now,
        )
        for cash in (confirmed.cash_fit, replace(lower, available_cash_minor=250_000)):
            with self.assertRaises(ContractError):
                record_cash_availability(
                    current,
                    cash,
                    trusted_scope=self.scope,
                    expected_binding=current.binding,
                    now=now,
                )
        self.assertIs(
            record_cash_availability(
                current,
                lower,
                trusted_scope=self.scope,
                expected_binding=current.binding,
                now=now,
            ),
            current,
        )
        self.assertEqual(current.cash_status_at(now), "insufficient")
        self.assertFalse(current.execution_authorized)
