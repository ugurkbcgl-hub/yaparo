"""Pure declared economics and shared capacity; never proof or a reservation.

All values are local synthetic/declaration metadata. No clock reads, I/O, database,
provider qualification, accounting profit, cash-flow or spending authorization.
Resource identities are workspace-wide, independent of draft/brand/channel.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .contracts import (
    MAX_MONEY,
    _aware,
    _currency,
    _digest,
    _integer,
    _require,
    _text,
    _utc,
)

SCHEMA = "yaparo-declared-business-economics-v1"
MAX_UNITS = Decimal("999999999")


def _quantity(value):
    _require(type(value) is Decimal and value.is_finite())
    _require(Decimal(0) <= value <= MAX_UNITS and value.as_tuple().exponent >= -6)


def _period(start, end):
    _require(type(start) is date and type(end) is date)
    _require(1 <= (end - start).days + 1 <= 365)


def _provenance(source, revision, observed_at, expires_at):
    _text(source, 100)
    _integer(revision, 1)
    _aware(observed_at)
    _aware(expires_at)
    _require(_utc(observed_at) < _utc(expires_at))


def _current(observed, expires, now):
    return _utc(observed) <= _utc(now) < _utc(expires)


def _tuple_of(values, cls, maximum=100):
    _require(type(values) is tuple and len(values) <= maximum)
    _require(all(type(value) is cls for value in values))


class TaxBasis(StrEnum):
    EXCLUSIVE = "exclusive"
    INCLUSIVE = "inclusive"
    UNKNOWN = "unknown"


class CostUse(StrEnum):
    UNIT_DIRECT = "unit_direct"
    MEDIA = "media"
    PRODUCTION = "production"
    SERVICE = "service"


@dataclass(frozen=True, slots=True)
class CostComponent:
    component_id: str
    use: CostUse
    amount_minor: int | None

    def __post_init__(self):
        _text(self.component_id, 100)
        _require(type(self.use) is CostUse)
        if self.amount_minor is not None:
            _integer(self.amount_minor)


def _components(values):
    _tuple_of(values, CostComponent)
    _require(len({v.component_id for v in values}) == len(values))
    _require(sum(v.amount_minor or 0 for v in values) <= MAX_MONEY)


@dataclass(frozen=True, slots=True)
class UnitEconomics:
    """One explicitly named completed-result unit; no guessed margin or LTV."""

    result_unit: str
    currency: str
    tax_basis: TaxBasis
    revenue_minor: int | None
    direct_costs: tuple[CostComponent, ...]
    source: str
    revision: int
    observed_at: datetime
    expires_at: datetime
    costs_complete: bool = False

    def __post_init__(self):
        _text(self.result_unit, 100)
        _currency(self.currency)
        _require(type(self.tax_basis) is TaxBasis)
        if self.revenue_minor is not None:
            _integer(self.revenue_minor)
        _components(self.direct_costs)
        _require(all(v.use is CostUse.UNIT_DIRECT for v in self.direct_costs))
        _require(type(self.costs_complete) is bool)
        _provenance(self.source, self.revision, self.observed_at, self.expires_at)

    @property
    def binding(self):
        return _digest((SCHEMA, self))

    def unit_contribution_at(self, now):
        """Minor-unit declared contribution, including negative; unknown is None."""
        if (
            not _current(self.observed_at, self.expires_at, now)
            or not self.costs_complete
            or self.tax_basis is TaxBasis.UNKNOWN
            or self.revenue_minor is None
            or any(v.amount_minor is None for v in self.direct_costs)
        ):
            return None
        return self.revenue_minor - sum(v.amount_minor for v in self.direct_costs)


@dataclass(frozen=True, slots=True)
class CampaignCost:
    """Media/production/service only; delivery costs belong in unit contribution."""

    currency: str
    tax_basis: TaxBasis
    components: tuple[CostComponent, ...]
    source: str
    revision: int
    observed_at: datetime
    expires_at: datetime
    costs_complete: bool = False

    def __post_init__(self):
        _currency(self.currency)
        _require(type(self.tax_basis) is TaxBasis)
        _components(self.components)
        _require(all(v.use is not CostUse.UNIT_DIRECT for v in self.components))
        _require(type(self.costs_complete) is bool)
        _provenance(self.source, self.revision, self.observed_at, self.expires_at)

    @property
    def binding(self):
        return _digest((SCHEMA, self))

    def total_at(self, now):
        if (
            not _current(self.observed_at, self.expires_at, now)
            or not self.costs_complete
            or self.tax_basis is TaxBasis.UNKNOWN
            or any(v.amount_minor is None for v in self.components)
        ):
            return None
        return sum(v.amount_minor for v in self.components)

    def conditional_contribution_at(self, economics, incremental_results, now):
        """Arithmetic under supplied incrementality; no causal or profit claim."""
        _require(type(economics) is UnitEconomics)
        _quantity(incremental_results)
        _require(self.currency == economics.currency)
        _require(self.tax_basis == economics.tax_basis)
        _require(
            not {v.component_id for v in self.components}
            & {v.component_id for v in economics.direct_costs}
        )
        unit = economics.unit_contribution_at(now)
        total = self.total_at(now)
        if unit is None or total is None:
            return None
        return incremental_results * unit - total


class CapacityBasis(StrEnum):
    TOTAL = "total"
    FREE_AFTER_COMMITMENTS = "free_after_commitments"
    ADVERTISABLE_INCREMENTAL = "advertisable_incremental"


class DeductionKind(StrEnum):
    COMMITMENT = "commitment"
    ORGANIC = "organic"
    OTHER_CAMPAIGN = "other_campaign"
    SAFETY = "safety"


@dataclass(frozen=True, slots=True)
class ResourceIdentity:
    workspace_id: int
    site_key: str
    resource_key: str
    unit: str
    timezone: str

    def __post_init__(self):
        _integer(self.workspace_id, 1)
        for value in (self.site_key, self.resource_key, self.unit, self.timezone):
            _text(value, 100)
        try:
            ZoneInfo(self.timezone)
        except (ValueError, ZoneInfoNotFoundError):
            _require(False)


@dataclass(frozen=True, slots=True)
class CapacityDeduction:
    """Unique load identity in one resource/window, already included or pending."""

    load_id: str
    kind: DeductionKind
    units: Decimal | None
    already_included: bool

    def __post_init__(self):
        _text(self.load_id, 100)
        _require(type(self.kind) is DeductionKind)
        if self.units is not None:
            _quantity(self.units)
        _require(type(self.already_included) is bool)


@dataclass(frozen=True, slots=True)
class CapacityObservation:
    start: date
    end: date
    basis: CapacityBasis
    units: Decimal | None
    deductions: tuple[CapacityDeduction, ...]
    source: str
    revision: int
    observed_at: datetime
    expires_at: datetime
    deductions_complete: bool = False

    def __post_init__(self):
        _period(self.start, self.end)
        _require(type(self.basis) is CapacityBasis)
        if self.units is not None:
            _quantity(self.units)
        _tuple_of(self.deductions, CapacityDeduction)
        _require(len({v.load_id for v in self.deductions}) == len(self.deductions))
        _require(type(self.deductions_complete) is bool)
        if self.basis is CapacityBasis.TOTAL:
            _require(not any(v.already_included for v in self.deductions))
        if self.basis is CapacityBasis.FREE_AFTER_COMMITMENTS:
            _require(
                all(
                    v.already_included
                    for v in self.deductions
                    if v.kind is DeductionKind.COMMITMENT
                )
            )
        _provenance(self.source, self.revision, self.observed_at, self.expires_at)

    def available_at(self, now):
        if (
            not _current(self.observed_at, self.expires_at, now)
            or self.units is None
            or not self.deductions_complete
            or any(v.units is None and not v.already_included for v in self.deductions)
        ):
            return None
        # Included load identities are retained, never deducted a second time.
        remaining = self.units - sum(
            (v.units for v in self.deductions if not v.already_included), Decimal(0)
        )
        return max(Decimal(0), remaining)


@dataclass(frozen=True, slots=True)
class CapacityResource:
    identity: ResourceIdentity
    period: CapacityObservation
    daily: tuple[CapacityObservation, ...] = ()

    def __post_init__(self):
        _require(type(self.identity) is ResourceIdentity)
        _require(type(self.period) is CapacityObservation)
        _tuple_of(self.daily, CapacityObservation, 365)
        _require(len({v.start for v in self.daily}) == len(self.daily))
        for observation in self.daily:
            _require(observation.start == observation.end)
            _require(self.period.start <= observation.start <= self.period.end)

    @property
    def binding(self):
        return _digest((SCHEMA, self))


@dataclass(frozen=True, slots=True)
class DailyDemand:
    day: date
    units: Decimal | None

    def __post_init__(self):
        _require(type(self.day) is date)
        if self.units is not None:
            _quantity(self.units)


@dataclass(frozen=True, slots=True)
class ResourceDemand:
    """Aggregated high-demand load across all channels, same physical unit."""

    identity: ResourceIdentity
    period_units: Decimal | None
    daily: tuple[DailyDemand, ...] = ()

    def __post_init__(self):
        _require(type(self.identity) is ResourceIdentity)
        if self.period_units is not None:
            _quantity(self.period_units)
        _tuple_of(self.daily, DailyDemand, 365)
        _require(len({v.day for v in self.daily}) == len(self.daily))
        if self.period_units is not None:
            _require(
                sum((v.units or Decimal(0) for v in self.daily), Decimal(0))
                <= self.period_units
            )


@dataclass(frozen=True, slots=True)
class CapacityFinding:
    identity: ResourceIdentity
    day: date | None
    reason: str


@dataclass(frozen=True, slots=True)
class CapacityAssessment:
    status: str
    findings: tuple[CapacityFinding, ...]
    resource_bindings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CapacityEnvelope:
    """Declared shared resource snapshots; no lock, reservation or permission."""

    workspace_id: int
    resources: tuple[CapacityResource, ...]

    def __post_init__(self):
        _integer(self.workspace_id, 1)
        _tuple_of(self.resources, CapacityResource)
        _require(1 <= len(self.resources))
        _require(
            len(
                {(v.identity.site_key, v.identity.resource_key) for v in self.resources}
            )
            == len(self.resources)
        )
        _require(
            all(v.identity.workspace_id == self.workspace_id for v in self.resources)
        )
        windows = {(v.period.start, v.period.end) for v in self.resources}
        _require(len(windows) == 1)

    @property
    def binding(self):
        return _digest((SCHEMA, self))

    def assess(self, demands, now):
        _tuple_of(demands, ResourceDemand)
        _aware(now)
        _require(len({v.identity for v in demands}) == len(demands))
        _require({v.identity for v in demands} <= {v.identity for v in self.resources})
        demand_by_id = {v.identity: v for v in demands}
        findings = []
        for resource in self.resources:
            identity = resource.identity
            demand = demand_by_id.get(identity)
            if demand is None:
                findings.append(CapacityFinding(identity, None, "missing_demand"))
                continue
            _require(
                all(
                    resource.period.start <= v.day <= resource.period.end
                    for v in demand.daily
                )
            )
            available = resource.period.available_at(now)
            if available is None or demand.period_units is None:
                findings.append(CapacityFinding(identity, None, "unknown_period"))
            elif demand.period_units > available:
                findings.append(CapacityFinding(identity, None, "period_exceeded"))
            if (
                demand.period_units is not None
                and all(v.units is not None for v in demand.daily)
                and sum((v.units for v in demand.daily), Decimal(0))
                != demand.period_units
            ):
                findings.append(
                    CapacityFinding(identity, None, "incomplete_daily_demand")
                )
            daily_capacity = {v.start: v for v in resource.daily}
            daily_demand = {v.day: v.units for v in demand.daily}
            # No equal split of a period total: every calendar day needs an explicit
            # observation and high-demand amount, even if that amount is zero.
            for offset in range((resource.period.end - resource.period.start).days + 1):
                day = resource.period.start.fromordinal(
                    resource.period.start.toordinal() + offset
                )
                capacity = daily_capacity.get(day)
                units = daily_demand.get(day)
                free = capacity.available_at(now) if capacity is not None else None
                if units is None or free is None:
                    findings.append(CapacityFinding(identity, day, "unknown_daily"))
                elif units > free:
                    findings.append(CapacityFinding(identity, day, "daily_exceeded"))
        reasons = {v.reason for v in findings}
        if reasons & {"period_exceeded", "daily_exceeded"}:
            status = "exceeded"
        elif findings:
            status = "unknown"
        else:
            status = "within_declared_limits"
        return CapacityAssessment(
            status, tuple(findings), tuple(v.binding for v in self.resources)
        )
