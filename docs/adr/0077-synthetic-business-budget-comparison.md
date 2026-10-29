# ADR0077 — Business-fit budget comparison in the local studio

Status: accepted for local synthetic implementation, 29 October 2026.

## Decision

Preserve the two-question first stage, four-stage journey, selected-channel share
controls and all launch/ownership/spending gates. The8014 Plan screen now accepts
an optional media ceiling: blank means unknown,0 means no paid media, positive
means a ceiling. The existing hidden operational budget receives a positive
amount only after an explicit scenario selection. PlanBounds is unchanged.

Reuse the accepted first-stage summary, ask for missing geography/flight and a
separate result deadline, plus incremental capacity for the whole period. Only
purchase/ticket paths collect completed-result contribution; visits, clicks,
messages and applications cannot silently become sales. Costs remain user
declarations, unknown is not zero. Production and service are shown separately;
known totals require both, with matching declared tax/currency scope.

## Comparison boundary

budget-planner.js is an isolated, immutable browser-local fixture calculator.
It does not call the Python contracts, an AI model, account or forecast provider.
Default evidence is none: no numeric scenarios without explicit sample choice.
The selected sample uses fabricated100–200TL per target action and a finite
1000/2000/3000/5000/8000/12000/20000TL media grid. All assumptions and non-market
labels are visible. It filters by high sample demand against declared period
incremental capacity, optional media/cash ceilings and, if comparable costs are
known, positive low-sample contribution. It deduplicates test/recommended/upper
examples instead of forcing three cards. Ranking is only within those fabricated
candidates; no global optimum, real result, daily feasibility or sales claim.
Unknown production/service means no total, contribution or cash-fit confirmation.

The upfront campaign-only cash model excludes delivery funding and collection
timing. Cash declaration/withdrawal/lower-cash filtering remain distinct from
selection; all plans are conditional. Changed dates, first-stage answers,
geography, materials or economics invalidate selection/cash. Allocation changes
withdraw cash confirmation. Invalid numbers and stale contexts cannot confirm.
No publish/spend action is introduced; existing final launch hold remains.

## Separate application foundation

Pure economics.py implements immutable version-bound UnitEconomics, CampaignCost,
CapacityResource and CapacityEnvelope declarations. Shared resources have stable
workspace/site/resource identities, explicit unique load deductions and
 total/free-after-commitments/incremental meanings. Included loads are not deducted
twice. Cost identities cannot appear in both direct unit and campaign costs.
Currency/tax/expiry/completeness checks refuse unknown arithmetic. Daily demand
and observations are required for daily capacity assessment: no equal split is
invented. This is not inventory reservation, accounting profit or proof of funds.

These richer Python contracts are separate from the simple UI period declaration.
There is no Django persistence, trusted owner service, real forecast adapter,
atomic reservation or actual timing model. Connecting those is subsequent work;
this local preview is not customer-beta or production readiness.

## Verification

Focused pure tests and browser acceptance checks cover unknown/zero/ceiling,
explicit fixture choice, costs/capacity/cash filtering, stale selections, original
channel share constraints, geography, first-stage reuse and organic paths. Desktop
and mobile screenshots are reviewed before merge. Required CI must pass on the
reviewed head; the milestone handoff records actual results.
