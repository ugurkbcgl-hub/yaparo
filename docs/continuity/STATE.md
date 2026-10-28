# Yaparo — current handoff

Verified: 2026-10-28 20:04 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Objective and constraints

Owner explicitly authorized ALL first-stage question banks from the reviewed
9-page Word/JSON design: two choices → purpose/outcome-specific typed short form.
Default8014 now implements9 intents and46 compatible paths. Owned-core ADR0040
and plan-first ADR0072 remain. Local synthetic only; real customer/account/spend/
publishing/production gates closed. Usage monitoring disabled. Reviewed green PRs
may merge; no direct main push. Owner manages OpenRouter balance; no new paid
service/recharge. Download/export remains undecided.

## Repository

Checkout C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
Branch codex/unified-journey-prototype; PR369 OPEN at verification.
Predecessor72c89c5 full CI40707898330 SUCCESS verified live. This complete-bank
package needs new CI after push. No deployment, DB migration or account action.

Complete-bank commit9710dc1 CI40732927463: owned-form checks SUCCESS; later Django
step failed on an existing oversized-package browser fixture. Its intentional
stream cancellation made response.body() unavailable to Playwright. Test-only
follow-up witnesses fulfilled byte length/hash headers for that oversized fixture;
small fixtures retain full-body hashing and every rejection/download assertion.
Production JS and size guard unchanged. Focused test passed3.361s in a fresh
in-memory SQLite rehearsal; no local app/PostgreSQL data accessed. Fresh full
PostgreSQL CI remains required after the follow-up push; do not bypass or merge
on the failed run.

## Completed first-stage package

Owned schema first-stage-bank.js, UI first-stage-ui.js/CSS, integration bridge.
All9 accepted design intents/outcomes retained; source data.js and fingerprinted
V2 catalogs unchanged. Separate typed fields cover:
- event mode/date/time/timezone/location, ticket/registration and participation;
- job role/type/model/location/skills/application and deadlines;
- fundraising organizer/purpose/permit declaration, money/currency/target,
  materials/delivery and volunteer task/time/application;
- all other design banks and14 outcome additions with relevant endpoint types.

Parent changes prune hidden values to fixed point; explicit risk stays across pair
changes. Required/date/calendar/order/time/number/currency/URL/phone/email/address-
or-map/manual-answer validation is enforced. Unknown pairs/enums/snapshot versions
fail closed. No real document upload or bank-account intake. Permit/risk answers
are declarations, never verification. State remains in tab memory.

Main home8014 mounts the owned first stage. Pair collapses to editable summary;
optional questions disclose separately. Full snapshot is brief.firstStage, with
literal summary and history/editor re-entry; edits invalidate old plan/content.
Examples/helper proposals now enter owned snapshots rather than hidden legacy form.
Legacy prototype retained at /legacy.html for checks; /v2.html remains separate.

Paid plan business/sector is explicitly selected in step2, never inferred. Mapping
holds refuse unmapped email/social messaging, offline purchase→visit substitution,
unbound outcomes and fallback CTAs. Source hidden action list is refilled before
projection. Positive paid authored allocation and organic full flow both tested.
All46 FIRST-stage paths work; not every new outcome has a later plan/content
adapter. Content-only production and undecided usage resolution remain later work.
This is not completion of AI/platform/production or launch readiness.

## Verification actually run

Pure model tests: all9 banks/46 compatible typed fixture completions, canonical
design coverage, blank/unknown refusal, hidden pruning, zero, malformed multi,
date/end ordering, URLcredentials/protocol/whitespace, phone/email and location
constraints passed. Syntax, configured Ruff format/lint and diff checks passed.

Default full-app8 browser tests passed13.530s:
%TEMP%/yaparo-first-stage-4csmamjb. Includes all46 pair routes/domain exclusions,
required/errors/focus, risk persistence, donation endpoint/target pruning,
event date/location, independent hiring controls, literal review/history,
organic full flow, positive paid classification+allocation and edit invalidation,
unmapped email/volunteer hold. No page errors/outbound calls in the isolated runs.

Legacy19 journeys passed27.714s (%TEMP%/yaparo-decision-nji2q4t1). Focused mobile/
keyboard visual rerun passed1.569s, %TEMP%/yaparo-first-stage-ere3rz1w. Desktop and
390px donation/hiring images viewed, no horizontal overflow/cut fields found.
Normalized screenshots scroll to top to avoid full-page sticky-position artifacts.
IAB tool still unavailable; these are actual isolated test-browser images.
Independent cross-review found mapping/hidden-action-list issues; fixed and
regressions passed in parent verification.

Actual8014 server restarted after checking its exact command. HTTP / and all4new
assets returned200. Source Word/research files unchanged this turn. Initial design
Word remains in Yaparo Araştırma/Yaparo_Ilk_Asama_Soru_Bankasi.docx; current runtime
status is in PROJECT/ROADMAP/progressive-brief.md and design JSON runtime metadata.

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

Verify current PR CI; then map the newly captured stage1 outcomes into the later
plan/content contract explicitly, starting with donation/material/volunteer
semantics and preserving source/account/forecast/production gates.
