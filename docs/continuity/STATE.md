# Yaparo — current handoff

Verified: 2026-10-29 11:01 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Objective and authorization

Owner approved the recommendation-engine plan on29October2026. Local synthetic
implementation may proceed; actual account/real data/provider/spend/publishing/
production and paid-service gates remain closed. Usage monitoring disabled.
First implementation is deliberately a small WP01 foundation, NOT full accepted
brief analysis, persistent storage or operational recommendation integration.

## Repository

Checkout C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
PR374 MERGED at2026-10-29 11:01 Europe/Istanbul, squashce36b03 on main.
Reviewed headd43214f; required CI40838250522 SUCCESS (exact-head guarded merge).
The earlier c55cccc run was cancelled only after a superseding DST fix; final
head completed all required checks. Researchf534af7/handoff87fa86d included.
Current checkout codex/accepted-brief-analysis, based on origin/maince36b03,
upstream unset. This verified handoff is local only; carry it with the next
meaningful package instead of creating a standalone documentation PR.
Post-merge main CI40839160910 was IN_PROGRESS when checked, no success claimed.

## Completed local package

The four research documents in docs/planning/recommendation-engine are retained.
Owner approval recorded in PROJECT/ROADMAP/implementation plan. ADR0074 records
new pure campaigns/recommendations/contracts.py and all qualifications:

- Immutable canonical browser declarations with exact46 route vocabulary, usage,
  retained explicit/fundraising risks. Always declared_unqualified. Full bank
  required/conditional/hidden-field validator is NOT yet ported server-side.
- Separate business/account countries, markets, language/currency/timezone,
  inclusive1..365day local dates, media budget/allocations/reserve.
- Structural evidence available0 versus nullable unavailable states, separate
  source kind/as-of/fetch/expiry, owner/context and account/generation binding.
- Scope metadata is not authorization. status_at checks declared expiry only,
  not real provider max-age/terms/quality/permissions. No active-generation lookup.
- Pure expected-version/history/request replay decision; exact replay returns
  original revision without restoring current authority. New past plans refuse.
  No persistence, transaction/race guarantee, HTTP, worker, credential or provider.
- publication_enabled always False; organic/content-only/unsure0 media does not
  loosen existing WorkspaceCampaignDraft DB constraints or touch old records.

Existing planning.py descriptive daily average now counts both endpoints,
matching ADR0071/brand_settings; same-day1 and leap dates covered. Publisher
budgets/pacing unchanged. No prototype8014 asset change.

## Verification actually run

23 pure contracts +5 calendar +18 existing metric tests =46 local passes;
Django system check clear. All selected tests are database-free; no DB setup,
migration or provider. Configured Ruff format/check passed355 files.
Independent review found a repeated-DST-hour instant-ordering edge; evidence and
history comparisons now normalize UTC, with a passing regression. Earlier
read-only source review found no blocker in unqualified/unwired scope
and recorded the remaining qualification boundaries above. Documentation updated.
Required CI40838250522 passed all checks: full PostgreSQL suite1194 tests
(4 explicit skips) and45 app browser E2E, plus16 first-stage/6 compact-plan/
19 legacy browser checks and source/editor/packaging/lint/audit checks.
Final temporal re-review found no blocker. No deployment or actual provider claim.
PR artifact UI attachment failed at the app's100-attachment limit; ordinary PR
URL remains usable. Follow-up issue375 records the remaining WP01 validator work.

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

Complete/review the server-owned first-stage field validator and accepted
analysis across46 routes (GitHub issue375) before any durable owner service or
actual forecast integration. Full bank qualification is still pending; do not
consume declared_unqualified answers as accepted analysis.
