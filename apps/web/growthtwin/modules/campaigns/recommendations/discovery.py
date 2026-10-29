"""Budget-optional synthetic discovery metadata; never financial authorization.

No I/O, persistence, candidate calculation or automatic PlanBounds conversion.
Trusted scope/state must eventually be resolved under a transactional owner service.
The synthetic scenario/cash records below are fixtures, not platform forecasts.
"""

from dataclasses import dataclass, replace
from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .analysis import AcceptedAnalysis
from .contracts import (
    MAX_MONEY,
    OwnerScope,
    _aware,
    _country,
    _currency,
    _digest,
    _integer,
    _require,
    _text,
    _utc,
    _uuid,
)

SCHEMA = "yaparo-budget-discovery-v1"
CASH_MODEL = "synthetic-upfront-campaign-v1"


def _binding(value):
    _require(type(value) is str and len(value) == 64)
    _require(all(c in "0123456789abcdef" for c in value))


def _current(created, expires, now):
    return _utc(created) <= _utc(now) < _utc(expires)


@dataclass(frozen=True, slots=True)
class DiscoveryContext:
    """Unresolved planning metadata, deliberately without a media budget."""

    business_country: str
    account_country: str | None
    target_markets: tuple[str, ...]
    language: str
    currency: str
    timezone: str
    result_deadline: date | None = None
    flight_start: date | None = None
    flight_end: date | None = None
    region_declaration: str | None = None

    def __post_init__(self):
        _country(self.business_country)
        if self.account_country is not None:
            _country(self.account_country)
        _require(
            type(self.target_markets) is tuple and 1 <= len(self.target_markets) <= 10
        )
        for market in self.target_markets:
            _country(market)
        _require(len(set(self.target_markets)) == len(self.target_markets))
        _text(self.language, 35)
        _currency(self.currency)
        _text(self.timezone, 80)
        try:
            ZoneInfo(self.timezone)
        except (ValueError, ZoneInfoNotFoundError):
            _require(False)
        for value in (self.result_deadline, self.flight_start, self.flight_end):
            _require(value is None or type(value) is date)
        _require((self.flight_start is None) == (self.flight_end is None))
        if self.flight_start is not None:
            _require(1 <= self.flight_days <= 365)
            if self.result_deadline is not None:
                _require(self.result_deadline >= self.flight_start)
        if self.region_declaration is not None:
            _text(self.region_declaration, 500)

    @property
    def flight_days(self):
        if self.flight_start is None:
            return None
        return (self.flight_end - self.flight_start).days + 1

    @property
    def missing_requirements(self):
        return tuple(
            key
            for key, missing in (
                ("result_deadline", self.result_deadline is None),
                ("flight_period", self.flight_start is None),
                ("region", self.region_declaration is None),
            )
            if missing
        )


@dataclass(frozen=True, slots=True)
class SyntheticScenario:
    """Bound fixture only; no ranking, actual forecast or cash-flow calculation.

    This first slice models full campaign costs funded up front. Therefore a
    declared peak cannot be below campaign cost; richer cash timing is separate.
    """

    candidate_id: UUID
    context_binding: str
    currency: str
    media_budget_minor: int
    production_cost_minor: int
    service_cost_minor: int
    peak_cash_need_minor: int | None
    created_at: datetime
    expires_at: datetime

    def __post_init__(self):
        _uuid(self.candidate_id)
        _binding(self.context_binding)
        _currency(self.currency)
        _integer(self.media_budget_minor, 1)
        _integer(self.production_cost_minor)
        _integer(self.service_cost_minor)
        _integer(self.campaign_cost_minor, 1)
        if self.peak_cash_need_minor is not None:
            _integer(self.peak_cash_need_minor)
            _require(self.peak_cash_need_minor >= self.campaign_cost_minor)
        _aware(self.created_at)
        _aware(self.expires_at)
        _require(_utc(self.expires_at) > _utc(self.created_at))

    @property
    def campaign_cost_minor(self):
        return (
            self.media_budget_minor
            + self.production_cost_minor
            + self.service_cost_minor
        )

    @property
    def binding(self):
        return _digest(
            {
                "schema": SCHEMA,
                "kind": "synthetic_fixture",
                "cash_model": CASH_MODEL,
                "scenario": self,
            }
        )


@dataclass(frozen=True, slots=True)
class CashFit:
    """User-declared synthetic cash availability, never payment/spend consent."""

    context_binding: str
    scenario_binding: str
    currency: str
    available_cash_minor: int
    declared_at: datetime
    expires_at: datetime

    def __post_init__(self):
        _binding(self.context_binding)
        _binding(self.scenario_binding)
        _currency(self.currency)
        _integer(self.available_cash_minor)
        _aware(self.declared_at)
        _aware(self.expires_at)
        _require(_utc(self.expires_at) > _utc(self.declared_at))


@dataclass(frozen=True, slots=True)
class BudgetDiscoveryDraft:
    scope: OwnerScope
    analysis: AcceptedAnalysis
    context: DiscoveryContext
    optional_ceiling_minor: int | None = None
    context_revision: int = 1
    state_revision: int = 1
    selection: SyntheticScenario | None = None
    selected_at: datetime | None = None
    cash_fit: CashFit | None = None

    def __post_init__(self):
        _require(
            type(self.scope) is OwnerScope and type(self.analysis) is AcceptedAnalysis
        )
        _require(type(self.context) is DiscoveryContext)
        _integer(self.context_revision, 1)
        _integer(self.state_revision, 1)
        if self.optional_ceiling_minor is not None:
            _integer(self.optional_ceiling_minor)
        _require((self.selection is None) == (self.selected_at is None))
        if self.selection is not None:
            _require(type(self.selection) is SyntheticScenario)
            _require(self.analysis.to_dict()["delivery"] in {"paid", "hybrid"})
            _require(not self.context.missing_requirements)
            _require(self.selection.context_binding == self.context_binding)
            _require(self.selection.currency == self.context.currency)
            if self.optional_ceiling_minor is not None:
                _require(
                    self.selection.media_budget_minor <= self.optional_ceiling_minor
                )
            _aware(self.selected_at)
            _require(
                _current(
                    self.selection.created_at,
                    self.selection.expires_at,
                    self.selected_at,
                )
            )
        if self.cash_fit is not None:
            _require(type(self.cash_fit) is CashFit and self.selection is not None)
            _require(self.cash_fit.context_binding == self.context_binding)
            _require(self.cash_fit.scenario_binding == self.selection.binding)
            _require(self.cash_fit.currency == self.context.currency)
            _require(_utc(self.cash_fit.declared_at) >= _utc(self.selected_at))
            _require(
                _current(
                    self.selection.created_at,
                    self.selection.expires_at,
                    self.cash_fit.declared_at,
                )
            )

    @property
    def context_binding(self):
        return _digest(
            {
                "schema": SCHEMA,
                "scope": self.scope,
                "analysis": self.analysis.binding,
                "context": self.context,
                "ceiling": self.optional_ceiling_minor,
                "revision": self.context_revision,
            }
        )

    @property
    def binding(self):
        return _digest(
            {"schema": SCHEMA, "context_binding": self.context_binding, "draft": self}
        )

    @property
    def ceiling_status(self):
        return (
            "unknown"
            if self.optional_ceiling_minor is None
            else (
                "no_paid_media"
                if self.optional_ceiling_minor == 0
                else "declared_ceiling"
            )
        )

    def stage_at(self, now):
        _aware(now)
        if self.selection is None:
            return "discovery"
        if (
            not _current(self.selected_at, self.selection.expires_at, now)
            or now.astimezone(ZoneInfo(self.context.timezone)).date()
            > self.context.flight_end
        ):
            return "stale_review"
        if self.cash_fit is None:
            return "scenario_selected"
        cash_status = self.cash_status_at(now)
        if cash_status == "stale":
            return "stale_review"
        return (
            "cash_confirmed"
            if cash_status == "sufficient_declared"
            else "scenario_selected"
        )

    def cash_status_at(self, now):
        _aware(now)
        if self.cash_fit is None:
            return "not_declared"
        if (
            not _current(self.selected_at, self.selection.expires_at, now)
            or not _current(self.cash_fit.declared_at, self.cash_fit.expires_at, now)
            or now.astimezone(ZoneInfo(self.context.timezone)).date()
            > self.context.flight_end
        ):
            return "stale"
        if self.selection.peak_cash_need_minor is None:
            return "unknown_requirement"
        return (
            "sufficient_declared"
            if self.cash_fit.available_cash_minor >= self.selection.peak_cash_need_minor
            else "insufficient"
        )

    @property
    def publication_enabled(self):
        return False

    @property
    def execution_authorized(self):
        return False


def _check_current(draft, scope, expected_binding):
    _require(type(draft) is BudgetDiscoveryDraft and type(scope) is OwnerScope)
    _binding(expected_binding)
    _require(draft.scope == scope and draft.binding == expected_binding)


def _advance(draft, **changes):
    _require(draft.state_revision < MAX_MONEY)
    return replace(draft, state_revision=draft.state_revision + 1, **changes)


def revise_discovery(
    draft, *, trusted_scope, expected_binding, analysis, context, optional_ceiling_minor
):
    """Pure replacement, not a database compare-and-swap or durable revision."""
    _check_current(draft, trusted_scope, expected_binding)
    if (
        analysis == draft.analysis
        and context == draft.context
        and optional_ceiling_minor == draft.optional_ceiling_minor
    ):
        # Validate types even on equality (True compares equal to integer1).
        BudgetDiscoveryDraft(draft.scope, analysis, context, optional_ceiling_minor)
        return draft
    _require(draft.context_revision < MAX_MONEY)
    return _advance(
        draft,
        analysis=analysis,
        context=context,
        optional_ceiling_minor=optional_ceiling_minor,
        context_revision=draft.context_revision + 1,
        selection=None,
        selected_at=None,
        cash_fit=None,
    )


def select_scenario(draft, scenario, *, trusted_scope, expected_binding, now):
    _check_current(draft, trusted_scope, expected_binding)
    _require(type(scenario) is SyntheticScenario)
    _aware(now)
    _require(_current(scenario.created_at, scenario.expires_at, now))
    _require(draft.context.flight_start is not None)
    if (
        draft.selection is not None
        and draft.selection.candidate_id == scenario.candidate_id
    ):
        _require(draft.selection.binding == scenario.binding)
        return draft
    _require(
        draft.context.flight_start
        >= now.astimezone(ZoneInfo(draft.context.timezone)).date()
    )
    return _advance(draft, selection=scenario, selected_at=now, cash_fit=None)


def record_cash_availability(draft, cash_fit, *, trusted_scope, expected_binding, now):
    """Replace a declaration, even if lower/insufficient; never retain old fit."""
    _check_current(draft, trusted_scope, expected_binding)
    _require(type(cash_fit) is CashFit)
    _aware(now)
    _require(draft.selection is not None)
    _require(_current(draft.selected_at, draft.selection.expires_at, now))
    _require(
        now.astimezone(ZoneInfo(draft.context.timezone)).date()
        <= draft.context.flight_end
    )
    _require(_current(cash_fit.declared_at, cash_fit.expires_at, now))
    if draft.cash_fit is not None:
        _require(_utc(cash_fit.declared_at) >= _utc(draft.cash_fit.declared_at))
        if _utc(cash_fit.declared_at) == _utc(draft.cash_fit.declared_at):
            _require(_digest(cash_fit) == _digest(draft.cash_fit))
            return draft
    return _advance(draft, cash_fit=cash_fit)


def clear_cash_fit(draft, *, trusted_scope, expected_binding):
    """Withdraw even an expired declaration; no provider/permission operation."""
    _check_current(draft, trusted_scope, expected_binding)
    return draft if draft.cash_fit is None else _advance(draft, cash_fit=None)


def confirm_cash_fit(draft, cash_fit, *, trusted_scope, expected_binding, now):
    """Strict sufficient-fit helper; cash updates use record_cash_availability."""
    updated = record_cash_availability(
        draft,
        cash_fit,
        trusted_scope=trusted_scope,
        expected_binding=expected_binding,
        now=now,
    )
    _require(updated.stage_at(now) == "cash_confirmed")
    return updated
