"""Provider/database-free contract acceptance; not account or form qualification."""

import json
import re
from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from unittest import TestCase
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from growthtwin.modules.campaigns.recommendations.contracts import (
    ROUTES,
    AccountReference,
    Allocation,
    ContractError,
    DeclaredBrief,
    DraftContent,
    DraftRevision,
    EvidenceMetric,
    MetricStatus,
    OwnerScope,
    PlanBounds,
    SourceKind,
    matches_current,
    propose_revision,
)


class RecommendationContractTests(TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
        self.scope = OwnerScope(1, 2, uuid4(), 3)
        self.bounds = PlanBounds(
            "TR",
            None,
            ("TR",),
            "tr",
            "TRY",
            "Europe/Istanbul",
            date(2026, 11, 1),
            date(2026, 11, 7),
            300001,
            "Sentetik bölge",
        )
        self.content = DraftContent(self.brief(), self.bounds, (), 300001)

    def snapshot(self, *, intent="promote", outcome="traffic", delivery="paid"):
        return {
            "version": "yaparo-first-stage-v1",
            "intent": intent,
            "outcome": outcome,
            "answers": {"delivery_mode": delivery, "promote_name": "Sentetik çalışma"},
        }

    def brief(self, **kwargs):
        return DeclaredBrief.from_snapshot(self.snapshot(**kwargs))

    def evidence(self, **kwargs):
        args = dict(
            scope=self.scope,
            evidence_id=uuid4(),
            metric="link_clicks",
            source=SourceKind.AUTHORED_DEMO,
            status=MetricStatus.AVAILABLE,
            value=Decimal(0),
            unit="count",
            currency=None,
            source_as_of=self.now - timedelta(hours=2),
            fetched_at=self.now,
            expires_at=self.now + timedelta(hours=1),
            context_binding=self.content.context_binding,
        )
        args.update(kwargs)
        return EvidenceMetric(**args)

    def save(self, history=(), **kwargs):
        args = dict(
            trusted_scope=self.scope,
            history=history,
            request_id=uuid4(),
            expected_revision=len(history),
            content=self.content,
            now=self.now,
        )
        args.update(kwargs)
        return propose_revision(**args)

    def test_route_list_matches_all_46_current_browser_routes(self):
        path = (
            Path(__file__).resolve().parents[5]
            / "experiments/decision-studio/dist/first-stage-bank.js"
        )
        block = re.search(
            r"const routeOptions = \{(.*?)\n  \};",
            path.read_text(encoding="utf-8"),
            re.S,
        )
        self.assertIsNotNone(block)
        actual = {}
        for line in block.group(1).strip().splitlines():
            intent, options = line.strip().split(":", 1)
            actual[intent] = tuple(re.findall(r"\['([a-z_]+)',", options))
        self.assertEqual(actual, dict(ROUTES))
        self.assertEqual(sum(map(len, actual.values())), 46)
        for intent, outcomes in ROUTES:
            for outcome in outcomes:
                with self.subTest(intent=intent, outcome=outcome):
                    brief = self.brief(intent=intent, outcome=outcome)
                    self.assertEqual(brief.validation_status, "declared_unqualified")

    def test_bounded_closed_envelope_does_not_trust_client_valid_flag(self):
        snapshot = self.snapshot()
        snapshot["valid"] = True
        with self.assertRaises(ContractError):
            DeclaredBrief.from_snapshot(snapshot)
        snapshot.pop("valid")
        snapshot["answers"]["made_up_field"] = "unvalidated declaration"
        # Field semantics are deliberately not qualified by this first slice.
        self.assertEqual(
            DeclaredBrief.from_snapshot(snapshot).validation_status,
            "declared_unqualified",
        )
        for value in ([], None, {}, {"unknown": True}):
            with self.subTest(value=value), self.assertRaises(ContractError):
                DeclaredBrief.from_snapshot(value)

    def test_raw_mutation_cannot_change_stored_snapshot_or_binding(self):
        snapshot = self.snapshot()
        snapshot["answers"]["list"] = ["first", "second"]
        brief = DeclaredBrief.from_snapshot(snapshot)
        binding = brief.binding
        snapshot["answers"]["list"].append("changed")
        self.assertEqual(brief.binding, binding)
        self.assertNotEqual(DeclaredBrief.from_snapshot(snapshot).binding, binding)
        with self.assertRaises(FrozenInstanceError):
            brief.canonical_snapshot = "changed"
        parsed = json.loads(brief.canonical_snapshot)
        reordered = dict(reversed(list(parsed.items())))
        self.assertEqual(DeclaredBrief.from_snapshot(reordered), brief)

    def test_noncanonical_duplicate_future_and_nonfinite_declarations_refuse(self):
        canonical = self.brief().canonical_snapshot
        for raw in (
            canonical + " ",
            canonical.replace('"intent":', '"intent":"sell","intent":'),
            canonical.replace("yaparo-first-stage-v1", "future"),
        ):
            with self.subTest(raw=raw[:30]), self.assertRaises(ContractError):
                DeclaredBrief(raw)
        for bad in (
            float("nan"),
            float("inf"),
            {"nested": 1},
            [None] * 31,
            "x" * 4097,
            "\ud800",
        ):
            snapshot = self.snapshot()
            snapshot["answers"]["bad"] = bad
            with self.subTest(bad=type(bad)), self.assertRaises(ContractError):
                DeclaredBrief.from_snapshot(snapshot)

    def test_incompatible_pair_bad_risk_and_unresolved_mode_cannot_qualify(self):
        with self.assertRaises(ContractError):
            self.brief(intent="promote", outcome="donate")
        for field, value in (
            ("risk", "invented"),
            ("delivery_mode", []),
            ("delivery_mode", "live"),
        ):
            snapshot = self.snapshot()
            snapshot["answers"][field] = value
            with self.assertRaises(ContractError):
                DeclaredBrief.from_snapshot(snapshot)
        self.assertFalse(self.content.publication_enabled)

    def test_risk_absent_not_normal_and_fundraising_retains_declared_risk(self):
        self.assertEqual(self.brief().risks, ())
        snapshot = self.snapshot(intent="fundraise", outcome="donate")
        snapshot["answers"]["risk"] = "health"
        self.assertEqual(
            DeclaredBrief.from_snapshot(snapshot).risks, ("fundraising", "health")
        )

    def test_date_bounds_inclusive_same_day_leap_and_invalid_values(self):
        self.assertEqual(self.bounds.days, 7)
        self.assertEqual(replace(self.bounds, end=self.bounds.start).days, 1)
        leap = replace(self.bounds, start=date(2028, 2, 28), end=date(2028, 3, 1))
        self.assertEqual(leap.days, 3)
        for kwargs in (
            {"end": date(2026, 10, 31)},
            {"end": date(2027, 11, 1)},
            {"start": self.now},
            {"timezone": "not/a/zone"},
            {"target_markets": ["TR"]},
            {"target_markets": ("TR", "TR")},
            {"currency": "JPY"},
            {"business_country": "turkey"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ContractError):
                replace(self.bounds, **kwargs)

    def test_account_country_business_and_target_market_are_distinct(self):
        bounds = replace(self.bounds, account_country="US", target_markets=("TR", "DE"))
        self.assertEqual(
            (bounds.business_country, bounds.account_country), ("TR", "US")
        )
        self.assertEqual(bounds.target_markets, ("TR", "DE"))
        self.assertFalse(replace(self.content, bounds=bounds).publication_enabled)

    def test_exact_integer_money_rejects_bool_float_negative_and_overflow(self):
        for amount in (True, False, 0.5, -1, 1_000_000_000, Decimal(3)):
            with self.subTest(amount=amount), self.assertRaises(ContractError):
                replace(self.bounds, media_budget_minor=amount)
        for amount in (0, -1, True, 1.5):
            with self.assertRaises(ContractError):
                Allocation("google_search", amount)

    def test_zero_organic_content_only_and_unsure_have_no_media_allocations(self):
        for mode in ("organic", "content_only", "unsure"):
            brief = self.brief(delivery=mode)
            content = DraftContent(
                brief, replace(self.bounds, media_budget_minor=0), (), 0
            )
            self.assertFalse(content.publication_enabled)
            with self.assertRaises(ContractError):
                replace(self.content, brief=brief)

    def test_allocations_and_reserve_exact_total_no_duplicate_channels(self):
        allocations = (
            Allocation("google_search", 100001),
            Allocation("meta_social", 100000),
        )
        content = replace(self.content, allocations=allocations, reserve_minor=100000)
        self.assertFalse(content.publication_enabled)
        for reserve in (99999, 100001, -1, True):
            with self.assertRaises(ContractError):
                replace(content, reserve_minor=reserve)
        with self.assertRaises(ContractError):
            replace(content, allocations=(allocations[0], allocations[0]))

    def test_available_zero_distinct_from_all_unavailable_states(self):
        zero = self.evidence()
        self.assertEqual(zero.value, Decimal(0))
        for status in MetricStatus:
            if status is MetricStatus.AVAILABLE:
                continue
            evidence = self.evidence(
                status=status, value=None, reason="not yet qualified"
            )
            self.assertIsNone(evidence.value)
            with self.assertRaises(ContractError):
                replace(evidence, value=Decimal(0))
        for bad in (None, True, 0.0, Decimal("NaN"), Decimal("Infinity"), Decimal(-1)):
            with self.assertRaises(ContractError):
                self.evidence(value=bad)

    def test_source_dates_not_fetch_dates_and_expiry_rechecked(self):
        evidence = self.evidence()
        self.assertEqual(evidence.status_at(self.now), "available")
        self.assertEqual(evidence.status_at(evidence.expires_at), "stale")
        self.assertEqual(
            evidence.status_at(self.now - timedelta(seconds=1)), "not_yet_observed"
        )
        for kwargs in (
            {"source_as_of": self.now + timedelta(seconds=1)},
            {"source_as_of": None},
            {"expires_at": self.now},
            {"fetched_at": self.now.replace(tzinfo=None)},
        ):
            with self.assertRaises(ContractError):
                self.evidence(**kwargs)

    def test_business_money_result_can_be_negative_but_allocation_cannot(self):
        evidence = self.evidence(
            metric="net_contribution",
            unit="money_minor",
            currency="TRY",
            value=Decimal(-100),
            source=SourceKind.BUSINESS_ACTUAL,
        )
        self.assertEqual(evidence.value, Decimal(-100))
        with self.assertRaises(ContractError):
            replace(evidence, value=Decimal("-0.5"))
        with self.assertRaises(ContractError):
            Allocation("google_search", -100)

    def test_evidence_binding_scope_currency_and_reference_integrity(self):
        evidence = self.evidence()
        allocation = Allocation("google_search", 100, (evidence.evidence_id,))
        content = replace(
            self.content,
            evidence=(evidence,),
            allocations=(allocation,),
            reserve_minor=299901,
        )
        record = self.save(content=content)
        self.assertEqual(record.content.evidence[0].source, SourceKind.AUTHORED_DEMO)
        with self.assertRaises(ContractError):
            replace(content, bounds=replace(self.bounds, region_declaration="Changed"))
        for kwargs in (
            {"evidence": (evidence, evidence)},
            {"evidence": ()},
            {"evidence": (replace(evidence, currency="USD", unit="money_minor"),)},
        ):
            with self.assertRaises(ContractError):
                replace(content, **kwargs)
        foreign = replace(evidence, scope=replace(self.scope, workspace_id=9))
        with self.assertRaises(ContractError):
            self.save(content=replace(content, evidence=(foreign,)))

    def test_account_generation_changes_fingerprint_but_not_permission(self):
        account = AccountReference("google_ads", "synthetic-account", uuid4(), uuid4())
        evidence = self.evidence(source=SourceKind.OFFICIAL_FORECAST, account=account)
        content = replace(self.content, evidence=(evidence,))
        changed = replace(evidence, account=replace(account, generation=uuid4()))
        self.assertNotEqual(
            content.binding, replace(content, evidence=(changed,)).binding
        )
        self.assertFalse(content.publication_enabled)
        with self.assertRaises(ContractError):
            replace(evidence, account=None)

    def test_new_revision_requires_current_owner_scope_and_expected_version(self):
        first = self.save()
        second = self.save((first,))
        self.assertEqual(second.revision, 2)
        for kwargs in (
            {"expected_revision": 0},
            {"trusted_scope": replace(self.scope, owner_id=9)},
            {"history": (second,)},
            {"history": (first, first)},
            {"expected_revision": True},
        ):
            args = dict(history=(first,))
            args.update(kwargs)
            with self.assertRaises(ContractError):
                self.save(**args)

    def test_exact_replay_returns_original_without_rolling_back_current(self):
        first = self.save()
        changed = replace(self.content, brief=self.brief(outcome="understand"))
        second = self.save((first,), content=changed)
        history = (first, second)
        replay = self.save(history, request_id=first.request_id, expected_revision=0)
        self.assertIs(replay, first)
        self.assertEqual(history[-1].revision, 2)
        self.assertFalse(
            matches_current(
                replay,
                trusted_scope=self.scope,
                current_revision=2,
                content_binding=changed.binding,
            )
        )
        with self.assertRaises(ContractError):
            self.save(
                history,
                request_id=first.request_id,
                expected_revision=0,
                content=changed,
            )

    def test_historical_replay_allowed_new_backdated_revision_rejected(self):
        first = self.save()
        future = self.now + timedelta(days=60)
        self.assertIs(
            self.save(
                (first,), request_id=first.request_id, expected_revision=0, now=future
            ),
            first,
        )
        with self.assertRaises(ContractError):
            self.save((first,), now=future)

    def test_changed_evidence_bounds_and_brief_invalidate_metadata_match(self):
        record = self.save()
        self.assertTrue(
            matches_current(
                record,
                trusted_scope=self.scope,
                current_revision=1,
                content_binding=self.content.binding,
            )
        )
        for content in (
            replace(self.content, brief=self.brief(outcome="remember")),
            replace(self.content, bounds=replace(self.bounds, language="en")),
            replace(self.content, evidence=(self.evidence(),)),
        ):
            self.assertFalse(
                matches_current(
                    record,
                    trusted_scope=self.scope,
                    current_revision=1,
                    content_binding=content.binding,
                )
            )

    def test_scope_revision_and_uuid_types_are_strict(self):
        for kwargs in (
            {"owner_id": True},
            {"workspace_id": 0},
            {"draft_id": UUID(int=0)},
            {"brand_id": False},
        ):
            with self.assertRaises(ContractError):
                replace(self.scope, **kwargs)
        record = self.save()
        for kwargs in (
            {"revision": True},
            {"recorded_at": self.now.replace(tzinfo=None)},
            {"request_id": "not-a-uuid"},
        ):
            with self.assertRaises(ContractError):
                replace(record, **kwargs)
        self.assertEqual(type(record), DraftRevision)

    def test_timezone_equivalent_evidence_has_stable_binding(self):
        first = self.evidence()
        offset = timezone(timedelta(hours=3))
        second = replace(
            first,
            fetched_at=first.fetched_at.astimezone(offset),
            source_as_of=first.source_as_of.astimezone(offset),
            expires_at=first.expires_at.astimezone(offset),
        )
        self.assertEqual(
            replace(self.content, evidence=(first,)).binding,
            replace(self.content, evidence=(second,)).binding,
        )

    def test_dst_fold_compares_instants_for_evidence_and_revision_history(self):
        zone = ZoneInfo("America/New_York")
        earlier = datetime(2026, 11, 1, 1, 45, fold=0, tzinfo=zone)
        later = datetime(2026, 11, 1, 1, 30, fold=1, tzinfo=zone)
        with self.assertRaises(ContractError):
            self.evidence(
                source_as_of=later,
                fetched_at=earlier,
                expires_at=later + timedelta(hours=2),
            )
        with self.assertRaises(ContractError):
            self.evidence(source_as_of=earlier, fetched_at=later, expires_at=earlier)
        evidence = self.evidence(
            source_as_of=earlier, fetched_at=earlier, expires_at=later
        )
        self.assertEqual(evidence.status_at(later), "stale")
        reverse = self.evidence(
            source_as_of=earlier,
            fetched_at=later,
            expires_at=later + timedelta(hours=2),
        )
        self.assertEqual(reverse.status_at(earlier), "not_yet_observed")
        bounds = replace(self.bounds, start=date(2026, 11, 3), end=date(2026, 11, 7))
        content = replace(self.content, bounds=bounds)
        first = self.save(now=later, content=content)
        with self.assertRaises(ContractError):
            self.save((first,), now=earlier, content=content)
        # A locally increasing wall time is nevertheless a decreasing instant.
        second = DraftRevision(self.scope, 2, uuid4(), content, earlier)
        with self.assertRaises(ContractError):
            self.save((first, second), now=later + timedelta(hours=2), content=content)
