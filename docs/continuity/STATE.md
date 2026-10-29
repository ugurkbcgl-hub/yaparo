# Yaparo — current handoff

Verified: 2026-10-29 09:40 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Current objective and boundary

Owner supplied a detailed recommendation/budget-engine research brief. This task
is research, audit and implementation planning ONLY. Four-stage journey remains:
clarify request → build plan → create content → review/publish. Owner explicitly
requires approval BEFORE application coding. No new migration, dependency upgrade,
account read, OAuth, ad object, publishing, spending or deployment was performed.
Local synthetic product work remains gated as before. Usage monitoring disabled.

## Repository and evidence

Checkout C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
Current feature branch codex/recommendation-engine-research, from local87fa86d
handoff on maincba8fba. No open PR at initial live check.
PR373 merge and required CI40789784874 remain historical success; main
CI40790844945 has now been rechecked COMPLETED/SUCCESS for cba8fba.
Research package is local for owner review; no PR/new CI triggered this task.
Do not mistake the earlier handoff's in-progress main CI for current status.

## Completed planning deliverable

docs/planning/recommendation-engine/:
- AUDIT.md: actual code/function/data/test inventory; working vs authored vs
  designed/unverified, reference-package defects, preserved boundaries.
- PROVIDER_CAPABILITIES.md: official sources checked29Oct; Google Search/YouTube,
  Meta, LinkedIn, TikTok, Microsoft, Yandex; access/version/mutation/metric limits,
  unknown costs/retention and account/pazar validation; no live account evidence.
- IMPLEMENTATION_PLAN.md: proposed owned contracts, metric/event/evidence models,
  cache/approval invalidation, per-purpose marginal allocation,11 work packages
  with dependencies/acceptance/effort/rollback, costs and approval gates.
- ACCEPTANCE_TESTS.md:36 scenarios, mathematical invariants, frozen forecast
  evaluation, maturity/dedup/attribution vs incrementality, G0–G4 and visual gates.

PROJECT/ROADMAP point to research and record implementation approval hold.
This proposal does not select a new provider/stack/database/budget or approve
production/real data. First proposed work: WP01 versioned owned draft/evidence,
WP02 business outcomes/metric semantics, WP03 capabilities/freshness.

## Material findings

8014 still uses authored Simulation.forecast and score-squared allocation.
Public FX is not an account forecast. Django draft only Google Search/lead and
positive media budget; organic/46routes require a separate versioned contract.
Existing report_metrics ownership/completeness/zero/freshness patterns are reusable.
planning.py date difference vs brand_settings inclusive+1 is a real source
inconsistency; resolve/test in WP01 before real pacing, no code fix done here.

Official current Google docs differ from old token/v23 assumptions: Cloud-project
access and v24+ strategy-dependent forecast fields must be qualified. Meta
SDK gives audience size, not a proven paid result curve. Some Meta references
were inaccessible; current Graph version/change date remain unverified.
Yandex report creation is not strictly read-only. All current account/production
forecast access remains unverified; protected TEST work is not permission proof.

## Verification this task

Independent read-only integrated reviews corrected inaccurate symbol names and
clarified spend invariant/cache scope wording. No unresolved material review issue.
Agent actually ran pure brief-analysis, owned-recommendation and V2 importer
--check successfully; source workbook/hash matched. No generated source change.
Four document deliverables/local links/UTF8/fence checks and git diff --check passed.
No new application/DB/browser/provider suite was run; no UI change or new visual
verification claimed. Prior PR373 desktop/mobile evidence remains historical.
Source research and case studies explicitly distinguish provider claims, model
projections, inaccessible evidence and actual measured outcomes.

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

Present the completed research plan for owner approval. Wait for that approval
before implementing WP01's synthetic owned draft/evidence contract. No real
provider/account operation is part of that first development package.
