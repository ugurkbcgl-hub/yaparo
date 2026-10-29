# Yaparo — current handoff

Verified: 2026-10-29 23:23 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Objective and authorization

Owner approved business-fit budget-planner implementation. First small WP01 slice
now implements pure budget-optional discovery/context and synthetic selection/cash
metadata only. Local synthetic; no real data/account/provider/AI/ad/spend/release
or new service. Usage monitoring disabled. No prototype UI/DB/runtime change.

## Repository

Checkout C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
Branch codex/shared-business-resources, based on origin/main c834d5e.
PR377 merged 2026-10-29 18:54:41 Europe/Istanbul; squash commit
c834d5e80686e4e4adeca8f2571928b737945033. Reviewed head
5c90031c94b9bc3d3a38407c78cd41cc720262af passed required CI40904479147.
Post-merge main CI40906309933 also completed SUCCESS on the squash commit.
This handoff/ADR completion note is a local commit carried into the next meaningful
feature package; no standalone documentation PR. No WP02 code started.
PR link: https://github.com/ugurkbcgl-hub/yaparo/pull/377
App attachment failed because the thread reached its100-attachment limit;
the normal GitHub PR link remains usable.

## Completed first discovery contract slice (ADR0076)

New campaigns/recommendations/discovery.py:
- DiscoveryContext without budget; optional result deadline/flight/region and
  separate business/account/market/currency/timezone. Incomplete context valid.
- BudgetDiscoveryDraft None=unknown,0=no-paid, positive=media ceiling. Existing
  PlanBounds and operational hard limits unchanged, no dummy0/sample amount.
- Exact accepted-analysis/scope/context/version binding. Context revision changes
  clear selection/cash. Separate monotonic state_revision stops stale/ABA requests
  after selection/cash/withdrawal without changing candidate context binding.
- SyntheticScenario closed fixture with total media/production/service costs,
  unknown-or-known peak cash and explicit synthetic-upfront-campaign-v1 cash model.
  Known peak >= campaign cost is a deliberately narrow fixture assumption, not
  actual cash-flow math or full candidate engine.
- Paid/hybrid current fixture selection only, within declared media ceiling;
  no organic/content-only/unsure paid selection. New selections need complete
  metadata/current not-yet-started flight; exact current repeat is no-op.
- CashFit user-declared fixture binds full selected scenario/context/currency.
  Lower/unknown/insufficient cash can be recorded without confirmation. Renew,
  withdraw and strict sufficient-fit helper; older/equal-but-different declarations
  reject. Expiry and flights rechecked, UTC instant comparisons include DST.
- Stage derived at supplied time, never input ready flag. cash_confirmed is
  not financial proof/consent. publication_enabled/execution_authorized alwaysFalse.
  No separately_spend_authorized transition or automatic PlanBounds conversion.

## Verification actually run

27 new pure tests plus prior62 accepted-bank/contracts/calendar/metric tests:
89 local passes, no DB setup/migration/provider. Ruff format/check passed361 files.
Independent read-only review found semantic-version binding, cash withdrawal/
renewal, stale declaration and ABA gaps; fixed with targeted regressions and
re-reviewed without blocker. No UI change/manual visual claim.
Required PR CI40904479147 passed on the reviewed head:1237 application tests
with4 explicit skips,45 application browser E2E checks; prototype19 legacy,
16 first-stage and6 compact-plan browser checks plus source/editor checks passed.
Required formatting/lint/dependency/build/migration-drift checks passed.
Post-merge main CI40906309933 SUCCESS verified. This is not a real-ready planner.

## Planning preserved and updated

BUDGET_PLANNER_SPEC and source/acceptance/implementation research remain included.
Owner approval recorded; currentimplemented boundary clear in PROJECT/ROADMAP.
30budget acceptance scenarios are future full-planner tests, not all implemented.
Numerical recommendations, shared capacity/economics, actual cash timing, durable
owner service and UI are still pending. Existing8014 uses mandatory-budget authored
demo; this pure backend foundation does not yet alter that screen.

## Preserved capabilities and protected work

Paid/organic/combined authored20-channel plan, public TCMB/ECB freshness/cache,
shared ideas/editor and placement adaptations remain. No actual LLM/ad forecast,
price quote/video generation or publishing. Prior ECB readback success/TCMB timeout
are historical, not fresh observations. Prior8013/Django8002 remain separate.

Python %USERPROFILE%\.yaparo\.venv; secrets/databases outside OneDrive.
Private preview %TEMP%\yaparo-public-preview-q2ql3pkq/preview.sqlite3; preserve
campaigns, brands, plans, holds and AI sources. Login READ helper
%USERPROFILE%\.yaparo\prepare_preview_login.py read; never print its password.
Google candidate quarantined %TEMP%\gwt-scoped-preparation-_jafwrsl; never repeat
completed PREPARE/APPLY/reset/refresh or restore over consumed history. ADR0068
unresolved holds and ADR0067–0071 ownership/replay/financial contracts retained.

## Next action

WP02: typed economics and shared response/delivery resources, cost-component
identities and total/free/incremental deduction semantics with synthetic examples.
Track https://github.com/ugurkbcgl-hub/yaparo/issues/378; bind revisions to discovery
and prevent double deductions. Finite budget candidates and WP07 UI follow;
no real provider/account rollout.
