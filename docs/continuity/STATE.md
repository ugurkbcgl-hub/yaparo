# Yaparo — current handoff

Verified: 2026-10-29 18:29 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Current request and approval hold

Owner supplied a new business-fit budget-planner decision: optional upfront
budget; economics/shared incremental capacity → candidate scenarios → cash fit
→ separate spend authorization. Four stages/two first questions unchanged.
This task is explicitly research/documentation ONLY. Wait for owner approval
before implementing this new behavior, including the previously queued durable
draft service. Earlier implementation approval does not override this hold.

Local synthetic only; no code, migration, dependency upgrade, account operation,
provider call, ad/spend/deployment/service or runtime change in this update.
Usage monitoring disabled. Existing running8014 was not changed by this task.

## Repository

Checkout C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
Branch codex/business-budget-planning, based on local handoffd8ae2c3 and
origin/mainb75e16b. PR376 merged; issue375 closed. No open PR at live check.
Post-merge main CI40899075957 rechecked COMPLETED/SUCCESS on b75e16b.
This planning update is local for owner review; no new PR/CI triggered.

## Completed planning update

New docs/planning/recommendation-engine/BUDGET_PLANNER_SPEC.md:
- Optional media ceiling; unknown!=0. Proposed discovery envelope separate from
  existing strict PlanBounds and operational authorized budget.
- Minimal short economic/capacity helper questions, four-stage UI copy.
- Starting test/recommended/current planning upper; never force3levels.
- Shared cross-channel/cross-campaign response+delivery resources, typed units/
  period/daily limits; total/free_after_commitments/advertisable_incremental with
  explicit already-applied deductions to avoid double subtraction.
- Lower-outcome economics, higher-load capacity, separate timed cash stress;
  no margin/revenue/capacity guarantees, no implicit incremental-sales claim.
- Finite candidate grid; initial slider snaps to computed candidates, no API/
  LLM/spend per movement; no unsupported extrapolation or smooth price tiers.
- Version-bound cash/scenario/authorization, concurrent resource holds, stale
  sources, after-stop demand and staged growth within explicit consent.
- Three detailed synthetic product/service/B2B examples plus no-number example.
  Product upper5000 is feasible but lower contribution than suggested3000.
  Service cash3300 reduces suggestion to1800media among inspected candidates.
  B2B has no fabricated leads/sales/profit, only a conditional learning candidate.

IMPLEMENTATION_PLAN updates WP01/02/03/05/06/07/08/10 and first3 jobs:
WP01 optional-budget discovery; WP02 economics+shared resources; WP06 candidate
comparison with WP03 fake data. Real adapters/advanced models remain separate.
ACCEPTANCE_TESTS adds B01–B30 plus numerical/cash/capacity/approval gates.
PROVIDER_CAPABILITIES adds officially sourced spend/pacing semantics; Meta current
numeric behavior inaccessible, explicitly unknown. Documentation is not account
proof. AUDIT/PROJECT/ROADMAP distinguish current code from planned behavior.

## Verification actually performed

Read-only source inspections and official document research; no account/API
exercise. Independent integrated review/arithmetic review found no unresolved
material issue after fixing enum naming, upper-candidate/Pareto scope, daily
contact capacity and B2B pilot-cash assumptions.
All9 numeric candidate rows, capacity, cash and delta arithmetic recomputed;
this is document arithmetic, not an application/provider test.
Planning local links/UTF8/fences and B01–B30/four examples checked;
git diff --check passed. No new app, database or browser tests run.
No new visual check claimed; no UI changed.

## Existing implemented state (preserved)

ADR0074 pure unqualified contracts and ADR0075 full46-path server field validator/
normalized analysis are implemented. Prior PR376 CI40843454047 passed1210 tests
(4 skips),45 app browser E2E and prototype/build/source checks. Those are historical
code results, not evidence that the new budget planner works.
Current8014 still requires an explicit budget and uses authored simulations.
Current PlanBounds requires resolved media_budget_minor. Neither changed here.
Protected provider/account/real-data/financial/launch gates remain.

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

Present the budget-planner update for owner approval. Only after approval start
WP01 BudgetDiscoveryDraft with optional media ceiling, scenario/cash/approval
version separation and existing hard execution bounds preserved.
