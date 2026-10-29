# ADR-0076: Budget-optional synthetic discovery foundation

Accepted29October2026 after owner approval of the business-fit budget-planner
update. This is the first WP01 implementation slice, not the full planner or UI.
ADR0074/0075 and existing provider/spend/recovery/launch gates remain.

## Decision

Add pure `campaigns/recommendations/discovery.py`, with no ORM, transport,
credentials, clock reads, provider, AI, pricing/forecast engine or UI integration.
It reuses OwnerScope and AcceptedAnalysis; trusted ownership/current state must
eventually be supplied by an authorized transactional owner service. These pure
metadata comparisons are neither authentication nor durable concurrency proof.

DiscoveryContext separates result deadline from optional ad-flight dates,
business/account countries, markets, language, currency, timezone and optional
literal region. Incomplete context is a valid discovery, never auto-completed
with a sample budget/date/location. Known dates are inclusive1..365 local days;
date-only fields reject datetime subclasses. Country syntax is not capability.

BudgetDiscoveryDraft has an optional media ceiling: None=unknown,0=explicit
no-paid-media, positive=strict integer minor-unit ceiling. No placeholder amount
is assigned. Existing PlanBounds.media_budget_minor remains required and unchanged.
There is no automatic conversion into PlanBounds, existing campaign fields,
publisher approval or financial limits.

Context binding covers scope, version-bound accepted analysis, context, optional
ceiling and context_revision. Draft binding also explicitly includes this context
binding, plus state_revision and all selected/cash metadata. This prevents a
semantic validator/bank/analysis version change from preserving an old expected
state merely because its source dataclass fields happen to compare equal.

revise_discovery requires current scope/expected binding; changed context increments
both context/state revisions and clears selection/cash. Exact unchanged inputs
are type-checked and remain no-op. Selection/cash changes advance only state_revision,
so the candidate's context remains stable while stale state requests refuse.
Selection→cash confirmation→withdrawal cannot restore the original binding (ABA).
This is an in-memory transition contract; no permanent replay history is created.

## Deliberately synthetic selection and cash path

SyntheticScenario is a closed fixture value, never an actual candidate generator
or platform forecast. Its binding includes candidate ID, context, currency, all
amounts, time bounds and the synthetic-upfront-campaign-v1 cash model identifier.
Media is positive; production/service nonnegative; sum is bounded. This first
fixture model funds the full campaign up front, so a known peak cash requirement
cannot be below campaign cost. Unknown peak is None, not0. Real cash timing,
capacity/economics and candidate ranking remain future WP02/WP06 work.

Selection requires paid/hybrid usage, complete declared planning context, matching
currency/context, ceiling and a current fixture window. Organic/content_only/
unsure cannot select a paid fixture; unknown/zero/positive ceiling never creates
spend authority. New selections cannot silently adopt an already-started flight.
Exact current fixture reselection is no-op even later in the flight; it is metadata
readback, not a restart. Expired fixtures cannot be selected/confirmed.

CashFit is a user-declared synthetic availability record, not bank verification,
payment or spending consent. It binds the exact context and complete selected
scenario, including costs. Media ceiling is not total-cash ceiling. Unknown peak
or insufficient cash cannot derive cash_confirmed.

record_cash_availability replaces the current declaration, including a lower or
insufficient one; old confirmation never survives that replacement. It may also
renew an expired cash declaration while its selected scenario is still current.
Older declarations cannot overwrite newer ones; equal-time only exact digest is
no-op. clear_cash_fit withdraws even expired cash and advances state if changed.
confirm_cash_fit is a strict helper returning only a sufficient current declaration;
use the general record transition for lower/unknown availability. No-op equality
never extends expiry. Future persistence must keep actual transition receipts.

stage_at(now) derives discovery/scenario_selected/cash_confirmed/stale_review
from bound records; no caller ready/stage flag exists. cash_status_at distinguishes
not_declared, stale, unknown_requirement, insufficient and sufficient_declared.
Instant comparisons use UTC (including DST-fold hours); flight days use the
declared timezone. publication_enabled and execution_authorized are always False,
including after cash_confirmed. No separately_spend_authorized transition exists.
The conditional_candidates stage belongs to the later scenario engine.

## Verification and remaining work

27 new pure tests cover unknown/zero/ceiling, unresolved context, strict numeric/
date/scope types, analysis-version binding, all context changes/invalidation,
selection/cash currency and amounts, expiry/DST, lower/unknown/renewed/withdrawn
cash, stale/ABA/older-declaration refusal, immutable output and unchanged PlanBounds.
With prior bank/contracts/calendar/metrics tests:89 local passes, no DB setup,
migration or provider operation. Ruff formatting/lint passed361 files.
Independent review's version binding, cash update/withdrawal and ABA findings
were fixed and regression tested; final targeted review found no blocker.
Required PR CI remains the merge gate.

No browser asset changed; no new manual visual check claimed. Existing8014 still
has the old explicit-budget UI; none of the numeric budget recommendations are
implemented by this contract. No shared physical capacity reservation or durable
owner service exists yet. The next bounded work is WP02 shared response/delivery
resources and economic-cost semantics, followed by finite synthetic candidates
and WP07 UI; all before real provider/account/spend rollout.
