"""Synthetic pure business cost/capacity acceptance, no ORM or provider use."""

from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest import TestCase

from growthtwin.modules.campaigns.recommendations.contracts import ContractError
from growthtwin.modules.campaigns.recommendations.economics import (
    CampaignCost,
    CapacityBasis,
    CapacityDeduction,
    CapacityEnvelope,
    CapacityObservation,
    CapacityResource,
    CostComponent,
    CostUse,
    DailyDemand,
    DeductionKind,
    ResourceDemand,
    ResourceIdentity,
    TaxBasis,
    UnitEconomics,
)

D = Decimal


class BusinessEconomicsTests(TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
        self.provenance = dict(
            source="synthetic_declaration",
            revision=1,
            observed_at=self.now,
            expires_at=self.now + timedelta(hours=1),
        )
        self.economics = UnitEconomics(
            "completed_order",
            "TRY",
            TaxBasis.EXCLUSIVE,
            10000,
            (
                CostComponent("goods", CostUse.UNIT_DIRECT, 2000),
                CostComponent("shipping", CostUse.UNIT_DIRECT, 1000),
            ),
            **self.provenance,
            costs_complete=True,
        )
        self.cost = CampaignCost(
            "TRY",
            TaxBasis.EXCLUSIVE,
            (
                CostComponent("media", CostUse.MEDIA, 20000),
                CostComponent("design", CostUse.PRODUCTION, 10000),
            ),
            **self.provenance,
            costs_complete=True,
        )

    def test_conditional_contribution_deducts_each_component_once(self):
        self.assertEqual(self.economics.unit_contribution_at(self.now), 7000)
        self.assertEqual(self.cost.total_at(self.now), 30000)
        self.assertEqual(
            self.cost.conditional_contribution_at(self.economics, D(10), self.now),
            40000,
        )

    def test_overlapping_unit_and_campaign_cost_identity_rejected(self):
        cost = replace(
            self.cost, components=(CostComponent("shipping", CostUse.SERVICE, 1000),)
        )
        with self.assertRaises(ContractError):
            cost.conditional_contribution_at(self.economics, D(1), self.now)

    def test_duplicate_component_identity_rejected_even_with_different_use(self):
        with self.assertRaises(ContractError):
            replace(
                self.cost,
                components=(
                    CostComponent("x", CostUse.MEDIA, 1),
                    CostComponent("x", CostUse.SERVICE, 2),
                ),
            )

    def test_missing_costs_and_unknown_tax_are_not_zero(self):
        for econ in (
            replace(self.economics, costs_complete=False),
            replace(self.economics, revenue_minor=None),
            replace(self.economics, tax_basis=TaxBasis.UNKNOWN),
            replace(
                self.economics,
                direct_costs=(CostComponent("x", CostUse.UNIT_DIRECT, None),),
            ),
        ):
            self.assertIsNone(econ.unit_contribution_at(self.now))
        self.assertIsNone(replace(self.cost, costs_complete=False).total_at(self.now))
        self.assertIsNone(
            replace(
                self.cost, components=(CostComponent("x", CostUse.MEDIA, None),)
            ).total_at(self.now)
        )

    def test_currency_and_tax_mismatch_refuse_calculation(self):
        for cost in (
            replace(self.cost, currency="USD"),
            replace(self.cost, tax_basis=TaxBasis.INCLUSIVE),
        ):
            with self.assertRaises(ContractError):
                cost.conditional_contribution_at(self.economics, D(1), self.now)

    def test_known_zero_and_negative_contribution_remain_known(self):
        self.assertEqual(
            replace(self.economics, revenue_minor=0).unit_contribution_at(self.now),
            -3000,
        )
        self.assertEqual(replace(self.cost, components=()).total_at(self.now), 0)

    def test_expiry_and_future_observation_are_unknown(self):
        for now in (self.now - timedelta(seconds=1), self.now + timedelta(hours=1)):
            self.assertIsNone(self.economics.unit_contribution_at(now))
            self.assertIsNone(self.cost.total_at(now))

    def test_strict_numbers_and_types(self):
        for value in (True, 1.5, -1, 1000000000):
            with self.assertRaises(ContractError):
                CostComponent("x", CostUse.MEDIA, value)
        for results in (1, 1.5, D("NaN"), D("Infinity"), D("-1"), D("0.0000001")):
            with self.assertRaises(ContractError):
                self.cost.conditional_contribution_at(self.economics, results, self.now)
        with self.assertRaises(ContractError):
            replace(self.economics, direct_costs=list(self.economics.direct_costs))

    def test_wrong_cost_category_and_unbounded_total_rejected(self):
        with self.assertRaises(ContractError):
            replace(
                self.economics, direct_costs=(CostComponent("x", CostUse.MEDIA, 1),)
            )
        with self.assertRaises(ContractError):
            replace(self.cost, components=(CostComponent("x", CostUse.UNIT_DIRECT, 1),))
        with self.assertRaises(ContractError):
            replace(
                self.cost,
                components=(
                    CostComponent("x", CostUse.MEDIA, 999999999),
                    CostComponent("y", CostUse.MEDIA, 1),
                ),
            )

    def test_bindings_include_revision_and_costs_and_values_are_immutable(self):
        self.assertNotEqual(
            self.economics.binding, replace(self.economics, revision=2).binding
        )
        self.assertNotEqual(
            self.cost.binding, replace(self.cost, components=()).binding
        )
        with self.assertRaises(FrozenInstanceError):
            self.economics.revenue_minor = 1


class SharedCapacityTests(TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
        self.start, self.end = date(2026, 11, 1), date(2026, 11, 2)
        self.identity = ResourceIdentity(
            1, "shop", "delivery_staff", "hours", "Europe/Istanbul"
        )
        self.provenance = dict(
            source="synthetic_declaration",
            revision=1,
            observed_at=self.now,
            expires_at=self.now + timedelta(hours=1),
        )
        self.period = CapacityObservation(
            self.start,
            self.end,
            CapacityBasis.TOTAL,
            D(20),
            (),
            **self.provenance,
            deductions_complete=True,
        )
        self.resource = CapacityResource(
            self.identity,
            self.period,
            (
                replace(self.period, end=self.start, units=D(10)),
                replace(self.period, start=self.end, units=D(10)),
            ),
        )
        self.demand = ResourceDemand(
            self.identity,
            D(12),
            (DailyDemand(self.start, D(6)), DailyDemand(self.end, D(6))),
        )
        self.envelope = CapacityEnvelope(1, (self.resource,))

    def test_total_deducts_unique_loads_once(self):
        deductions = (
            CapacityDeduction("booked", DeductionKind.COMMITMENT, D(3), False),
            CapacityDeduction("organic", DeductionKind.ORGANIC, D(2), False),
            CapacityDeduction("buffer", DeductionKind.SAFETY, D(1), False),
        )
        self.assertEqual(
            replace(self.period, deductions=deductions).available_at(self.now), 14
        )
        with self.assertRaises(ContractError):
            replace(self.period, deductions=deductions + (deductions[0],))

    def test_free_capacity_does_not_rededuct_commitments(self):
        free = replace(
            self.period,
            basis=CapacityBasis.FREE_AFTER_COMMITMENTS,
            units=D(17),
            deductions=(
                CapacityDeduction("booked", DeductionKind.COMMITMENT, D(3), True),
                CapacityDeduction("organic", DeductionKind.ORGANIC, D(2), False),
            ),
        )
        self.assertEqual(free.available_at(self.now), 15)
        with self.assertRaises(ContractError):
            replace(
                free,
                deductions=(
                    CapacityDeduction("booked", DeductionKind.COMMITMENT, D(3), False),
                ),
            )

    def test_incremental_keeps_included_load_and_deducts_only_new_load(self):
        incremental = replace(
            self.period,
            basis=CapacityBasis.ADVERTISABLE_INCREMENTAL,
            units=D(10),
            deductions=(
                CapacityDeduction("old", DeductionKind.OTHER_CAMPAIGN, None, True),
                CapacityDeduction("new", DeductionKind.COMMITMENT, D(2), False),
            ),
        )
        self.assertEqual(incremental.available_at(self.now), 8)

    def test_unknown_and_overloaded_capacity_are_distinct(self):
        self.assertIsNone(replace(self.period, units=None).available_at(self.now))
        self.assertIsNone(
            replace(self.period, deductions_complete=False).available_at(self.now)
        )
        self.assertIsNone(
            replace(
                self.period,
                deductions=(
                    CapacityDeduction("x", DeductionKind.ORGANIC, None, False),
                ),
            ).available_at(self.now)
        )
        self.assertEqual(
            replace(
                self.period,
                deductions=(
                    CapacityDeduction("x", DeductionKind.ORGANIC, D(30), False),
                ),
            ).available_at(self.now),
            0,
        )

    def test_daily_bottleneck_despite_sufficient_period(self):
        demand = replace(
            self.demand,
            daily=(DailyDemand(self.start, D(11)), DailyDemand(self.end, D(1))),
        )
        result = self.envelope.assess((demand,), self.now)
        self.assertEqual(result.status, "exceeded")
        self.assertIn("daily_exceeded", [v.reason for v in result.findings])

    def test_complete_period_and_daily_limits_are_conditional_declarations(self):
        result = self.envelope.assess((self.demand,), self.now)
        self.assertEqual(result.status, "within_declared_limits")
        self.assertEqual(result.resource_bindings, (self.resource.binding,))
        self.assertFalse(hasattr(result, "execution_authorized"))

    def test_missing_daily_distribution_is_unknown_not_equal_split(self):
        result = self.envelope.assess((replace(self.demand, daily=()),), self.now)
        self.assertEqual(result.status, "unknown")
        self.assertIn("unknown_daily", [v.reason for v in result.findings])
        self.assertEqual(
            CapacityEnvelope(1, (replace(self.resource, daily=()),))
            .assess((self.demand,), self.now)
            .status,
            "unknown",
        )

    def test_daily_demand_must_account_for_whole_period(self):
        demand = replace(
            self.demand,
            daily=(DailyDemand(self.start, D(1)), DailyDemand(self.end, D(1))),
        )
        result = self.envelope.assess((demand,), self.now)
        self.assertEqual(result.status, "unknown")
        self.assertIn("incomplete_daily_demand", [v.reason for v in result.findings])
        with self.assertRaises(ContractError):
            replace(demand, period_units=D(1))

    def test_shared_resource_not_duplicated_per_channel_or_brand(self):
        with self.assertRaises(ContractError):
            CapacityEnvelope(1, (self.resource, self.resource))
        with self.assertRaises(ContractError):
            self.envelope.assess((self.demand, self.demand), self.now)

    def test_workspace_unit_and_location_mismatch_rejected(self):
        with self.assertRaises(ContractError):
            CapacityEnvelope(2, (self.resource,))
        for identity in (
            replace(self.identity, workspace_id=2),
            replace(self.identity, unit="slots"),
            replace(self.identity, site_key="other"),
        ):
            with self.assertRaises(ContractError):
                self.envelope.assess(
                    (replace(self.demand, identity=identity),), self.now
                )

    def test_same_physical_resource_cannot_be_cloned_with_another_unit(self):
        cloned = replace(self.resource, identity=replace(self.identity, unit="slots"))
        with self.assertRaises(ContractError):
            CapacityEnvelope(1, (self.resource, cloned))

    def test_stale_missing_or_unknown_demand_is_not_safe(self):
        self.assertEqual(
            self.envelope.assess((self.demand,), self.now + timedelta(hours=1)).status,
            "unknown",
        )
        self.assertEqual(self.envelope.assess((), self.now).status, "unknown")
        self.assertEqual(
            self.envelope.assess(
                (replace(self.demand, period_units=None),), self.now
            ).status,
            "unknown",
        )

    def test_multiple_resources_all_have_to_fit(self):
        stock_id = replace(self.identity, resource_key="stock", unit="items")
        stock = replace(
            self.resource, identity=stock_id, period=replace(self.period, units=D(1))
        )
        stock_demand = replace(self.demand, identity=stock_id)
        result = CapacityEnvelope(1, (self.resource, stock)).assess(
            (self.demand, stock_demand), self.now
        )
        self.assertEqual(result.status, "exceeded")
        self.assertEqual(len(result.resource_bindings), 2)

    def test_binding_fences_resource_revision_and_deduction_changes(self):
        revised = replace(self.resource, period=replace(self.period, revision=2))
        self.assertNotEqual(self.resource.binding, revised.binding)
        self.assertNotEqual(
            self.envelope.binding, CapacityEnvelope(1, (revised,)).binding
        )

    def test_strict_daily_window_duplicate_and_quantity_validation(self):
        with self.assertRaises(ContractError):
            replace(self.resource, daily=(self.period,))
        with self.assertRaises(ContractError):
            replace(
                self.resource, daily=(self.resource.daily[0], self.resource.daily[0])
            )
        with self.assertRaises(ContractError):
            replace(self.period, start=datetime(2026, 11, 1))
        with self.assertRaises(ContractError):
            self.envelope.assess(
                (replace(self.demand, daily=(DailyDemand(date(2026, 11, 3), D(1)),)),),
                self.now,
            )
        for value in (True, 1.5, D("NaN"), D("-1"), D("0.0000001")):
            with self.assertRaises(ContractError):
                replace(self.period, units=value)
