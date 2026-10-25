# Yaparo — current handoff

Verified: 2026-10-25 10:42 Europe/Istanbul (+03:00). Recheck mutable facts.

## Objective and preferences

Owned-core/open-source plan; current Y05-B generated raster/storage rehearsal.
Usage monitoring disabled by owner; do not query limits. Reviewed green PRs may
merge under standing authorization; never push directly to main. Local synthetic
work only; actual customer data/accounts, payments/publishing remain gated.

## Repository and delivery

Checkout: C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote: https://github.com/ugurkbcgl-hub/yaparo
Private Python: %USERPROFILE%\.yaparo\.venv; secrets outside OneDrive.
Base main e0feec4 (PR337 merged); main CI40167834694 succeeded.
PR336 required CI40167348893 and main CI40167513738 succeeded.
Current implementation branch feat/synthetic-raster-rehearsal, PR338. Recheck
its current merge/CI status live. No unrelated working-tree changes at creation.
Durable task: GitHub issue328. Recheck Git/PR/CI before acting.

- New creative scenes v2 pin brand palette: background, logo/icon/wordmark and
  text colors with initial readability fallback; font remains Arial only.
- Existing v1 scenes keep prior data/rendering; schema flips on save/restore deny.
- Initial/changed-save snapshots commit atomically; owned restore appends new
  revision. Later work remains. No-op/stale/replay and failed history writes safe.
- Legacy documents capture current baseline only on first changed save; unknown
  old edits are not reconstructed. History list50; stored older rows retained.
- Four HTTP/editor checks plus backend suites and enhanced Chromium:95 tests,
  90 passed/5 PostgreSQL-only SQLite skips including the new restore race.
  Browser restored1→3 then2→4, decoded PNG and verified actual v2 palette pixels
  and unchanged v1 background. Desktop/mobile reviewed; outside requests0.
- Independent backend/JS and final atomic-bootstrap delta review approved.
- Migration0004 also applied to the SAME disposable local preview SQLite with
  private backup and preserved brand/document counts. Server restarted on8002;
  home HTTP200 verified. Browser is on the login page; authenticated manual
  visual check of the refreshed preview remains unfinished.
- PR336 adds two fixed-source metadata records per synthetic brand, identity-
  pinned immutable versions and a private catalog on the brand page (ADR0043).
  No binary exists; byte size is null and metadata digest is not a file hash.
- Pre-CSRF middleware rejects multipart/unknown/oversized bodies. Leading-zero
  route and mocked parser verify multipart parsing does not start.
- Initial local full run:892 tests,866 passed/26 SQLite skips. CI40164225778
  failed on existing browser reload losing its page, not a backend assertion.
  Added explicit navigation wait; focused assets+browser18 tests passed. Enhanced
  browser test then prepared the actual catalog with CSRF, showed two unmeasured
  sizes and continued save/reopen/download successfully. Final independent review
  found no blockers. Final required CI40167348893 passed PostgreSQL, browser,
  build/static/lint/migration/dependency checks before PR336 merged.
- Assets0001 applied to the SAME disposable local preview SQLite after a private
  backup; brand/document counts preserved. Server restarted on8002; home/login
  HTTP200 verified. No authenticated manual preview review claimed. Temporary
  preview login file removed. No configured/real DB or protected fixture changed.
- PR338: default-off internal generated JPEG/PNG/WebP original→normalization→
  private readback→cleanup rehearsal (ADR0044). DEBUG also required. No routes,
  customer bytes, durable catalog mutation or provider operation. Pillow13.0.0
  pinned in development dependencies; source/type/byte/edge/pixel/frame limits.
- Real byte hashes/sizes and tool provenance; output EXIF/comments stripped.
  Structure verified is not malware CLEAN, READY, legal rights or publish proof.
- Actual Windows current-user-only directory ACL, exclusive UUID files and exact
  inventoried deletion tested. POSIX permissions covered by CI. Not an atomic
  same-user attack defense or parser sandbox; crash orphan recovery remains open.
- 28 focused asset tests passed on Windows; independent source review found no
  blockers. Ruff, Django checks, migration drift and dependency audit passed.
  Required final-head CI must pass before merge. No new migration or database
  operation except ephemeral tests; existing preview/protected fixture unchanged.
- Desktop PR attachment limit100 remains; use PR URLs. Usage monitoring disabled.

## Preserved implementation evidence and boundaries

Rename/relocation evidence: docs/continuity/RENAMING.md. Keep stable Python package
and migration names, DB growthtwin/growthtwin_app, salts/UUIDs/receipts, DPAPI roots,
Google/Heroku technical identities. No global replacements or secret moves.

Local prototype has owner-scoped synthetic drafts/editable text/history/export,
report empty states and rehearsals. Google daily/total-budget PAUSED TEST
create/read/repeat/stop was previously verified; no live serving/cap-exhaustion
or real conversion proof. Existing lifecycle contracts/fake scenarios do not
prove actual grant revocation/erasure. Preserve legacy stop/reconcile independently.

The actual scoped candidate remains quarantined. Its credential contents/account
access were not verified by this planning task. Origin session/process secret
were lost at logout; do not substitute a session/hash/identity or recreate history.
Private root: %TEMP%\gwt-scoped-preparation-_jafwrsl\synthetic.sqlite3.
preparation.json, retirement-intent.json and inspection-schema-preparation.json
retain exact history and private backup pointer. Completed PREPARE/forward0007
APPLY must not rerun. No new DB, permit retry/reset, activation or provider refresh.
Detailed continuation: docs/product/recovered-inspection-exercise-preparation.md
and docs/product/windows-inspection-fixture.md. Fabricated fixture tests are not
proof of the preserved real candidate. Actual launcher review remains a separate
Y19 integration task, not a blocker for the synthetic creative-studio slice.

Earlier cloud record: API Test/OAuth Testing/one test user and incomplete branding;
not freshly rechecked here. Fresh campaign staging E2E, configured DB/files restore,
code/schema recovery, domain/identity/privacy, production token/tenant controls,
actual metrics and payment/financial consent remain open release gates.

The expired work heartbeat and low-usage monitor remain PAUSED; no automation was
created/resumed by the new maintenance cadence proposal. No unattended work claim.

## Next action

Complete PR338 CI/merge, then durable original/derivative records and a private
storage adapter with crash/orphan reconciliation and backup/restore evidence.
Use generated fixtures first; customer upload/scanning/parser isolation and
privacy release gates remain open. This rehearsal does not complete Y05.
