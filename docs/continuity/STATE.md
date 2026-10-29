# Yaparo — current handoff

Verified: 2026-10-29 11:36 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Objective and constraints

Owner requested completing the next WP01 step: full server-owned46-route form
validation and normalized literal analysis. Approved recommendation plan remains.
Local synthetic only; no real account/data/provider/AI/spend/publishing/deployment
or new service. Usage monitoring disabled. Export remains undecided.

## Repository

Checkout C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
Branch codex/accepted-brief-analysis, from local handoffc09cd3c on maince36b03.
Prior PR374 merged; its main CI40839160910 was rechecked SUCCESS.
Issue375 records current validator work. New PR/required CI pending at this note.
Protected Google/AI/DB/consumption history not opened, changed or replayed.

## Implemented server form slice (ADR0075)

Pure bank.py ports current9 intent banks/46 routes and conditional field IDs,
options/labels/roles/required/numeric/UTF16 limits. validation.py normalizes and
validates bounded flat answers, visibility, scalar/multi enums and cross-field
date/location/physical-visit/price/qualification/overnight conditions.
Default rejects unknown/inactive keys; explicit prune_hidden returns a separate
preview, accepted constructor revalidates the clean canonical snapshot.

AcceptedBrief means server_form_valid_declaration ONLY, never verified truth,
policy/account readiness or consent. Binding includes validator/bank versions.
Old DeclaredBrief remains unqualified and DraftContent exact-type stays unchanged.
Corrected source enum gaps: hybrid (not combined) and selectable fundraising.
No actual stored record used these pure contracts; no data/schema migration.

AcceptedAnalysis re-derives exact literal subject/identity/message/audience,
destination, CTA/KPI, forced+explicit risks and known/unknowns. Unsupported paid
mapping null; missing forms/custom destinations unresolved. No keyword guessing.
Policy/platform/measurement/publish flags false; forecast/model null.
Immutable source, detached output. No route/ORM/persistence/provider integration.

URL declarations are never fetched/ownership verified. Server narrower policy
rejects userinfo, controls, invalid numeric IP/IPFuture, encoded/ambiguous hosts
and IDNA joiners; not a complete WHATWG implementation or an SSRF fetch gate.
Literal text must still be escaped by future renderers.

## Verification actually run

16 new tests include414 JS differential cases (46 base routes,418 enum transitions,
198 shared field specs), per-base required/enum mutations and targeted malformed/
risk/UTF16/ASCII/date/destination/flags/rebind tests. Together with prior23 pure
contracts,5 calendar and18 metric tests:62 local passes, no DB setup/provider.
Ruff format/check passed359 files. Deterministic generator --check passed;
source hashes normalize UTF8-LF. CI adds this read-only drift check.
Agent additionally compared3488 field scenarios and probed7590 malformed mutations;
these are synthetic ad hoc probes, not extra committed tests or account evidence.
Independent review found invalid-IP and IDNA-joiner gaps; corrected, regression
tested and re-reviewed with no remaining blocker. No UI asset changed and no new
manual browser visual check claimed. Required PR CI still pending, no merge claim.

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

Finish required CI/review/PR for this validator, then implement the separate
durable owner-scoped synthetic draft service with accepted-analysis binding,
locked expected revision and request replay. Keep operational publisher fields
and protected histories unchanged; no provider/account rollout implied.
