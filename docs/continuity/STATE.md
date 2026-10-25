# Yaparo — current handoff

Verified: 2026-10-25 15:57 Europe/Istanbul (+03:00). Recheck mutable facts.

## Objective and preferences

Owned-core/open-source plan; current owned synthetic design-package slice.
Usage monitoring disabled by owner; do not query limits. Reviewed green PRs may
merge under standing authorization; never push directly to main. Local synthetic
work only; actual customer data/accounts, payments/publishing remain gated.

## Repository and delivery

Checkout: C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote: https://github.com/ugurkbcgl-hub/yaparo
Private Python: %USERPROFILE%\.yaparo\.venv; secrets outside OneDrive.
Base main23ad073 (PR342 merged); required CI40194312612 and main CI40194730203
succeeded. Implementation branch feat/owned-design-bundle; PR not yet created at
snapshot. Resolve its current PR/head/checks live before merging. No unrelated
edits at task start.
PR336 required CI40167348893 and main CI40167513738 succeeded.
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
- PR338 required CI40173841958 and main CI40174121931 passed;28 focused local
  asset tests and independent source review passed before that merge.
- New ADR0045 slice: separate fixed palette source, identity-pinned material
  version and immutable original/normalized PNG pair atomically stored in the
  existing DB. Measured hashes/sizes/tool; no filesystem orphan during DB writes.
  Repeat preserves the existing image. Existing scene keys/rendering unchanged.
- Default-off persistence flag plus DEBUG; Pillow remains development-only.
  Local owned generate form and private PNG route; multipart refused pre-CSRF.
  Final binary query repeats current owner/active/archive conditions after an
  independent review found and we fixed an ownership race; regression passed.
- Latest focused assets+browser41 tests:40 passed/1 PostgreSQL race skip. Prior
  assets+workspaces133 tests:127 passed/6 PG skips before read-race fix. Enhanced
  browser created/reopened/repeated image; PNG pixels and mobile overflow checked,
  mobile screenshot reviewed. Final independent delta review found no blocker.
  Ruff and migration drift passed. PR339 merged after required CI:916 tests,
  912 passed/4 skips plus15 browser tests. Assets0002 then applied to the SAME
  disposable preview after private backup; one generated palette stored, original
  brand/document counts preserved, home/login HTTP200. Configured DB and protected
  fixture unchanged. New recovery/removal task has not modified that preview.
- ADR0046: internal default-off scoped palette deletion removes parent/version
  and original/derivative together. Missing scoped ID is a no-op; old-ID replay
  cannot remove a new sample. Corrupt pair refuses deletion; cascade failure
  rolls back all rows. No deletion HTTP endpoint or retention policy.
- No-input fresh private SQLite CLI migrated only a new fixture, backed it up,
  restored into a second fresh file, compared hashes/sizes/identity/tool and PNG
  pixels, removed restored rows and preserved whole source/backup hashes. Exact
  temporary inventory cleaned. Actual Windows normal and -O runs passed.
  Initial open SQLite handles caused cleanup refusal; explicit closes fixed it;
  the two failed generated fixtures were inventoried and removed individually.
- Latest47 asset tests:46 passes/1 PG skip. Independent review found no blocker;
  added configured-Django-process refusal before filesystem admission. Ruff and
  migration drift passed. No migration, configured DB/provider/deployment action.
  Isolated SQLite proof is not configured PostgreSQL/Heroku/crash/privacy proof.
- Desktop PR attachment limit100 remains; use PR URLs. Usage monitoring disabled.

## Preserved implementation evidence and boundaries

ADR0049: owned saved-design ZIP contains canonical scene, source/identity manifest,
Turkish README and actual palette original/normalized PNG with size/SHA256/tool.
Fixed drawings/logo remain metadata; Arial and compatible Yaparo renderer required.
Legacy unbound records deny package export, retain scene JSON; no invented origins.
Default-off/DEBUG, private/no-store/nosniff, fixed paths, deterministic stored ZIP,
12 MiB cap, read-only owned snapshot. No importer or customer archive input.
No-input fresh private source/target DB rehearsal restores only its own generated
fixed fixture into new owner/document/material IDs; scene, all source metadata,
bytes/pixels and reexport match. Source DB/ZIP unchanged; exact inventory cleaned.
Actual Windows normal and -O runs passed.169 related checks:163 passed/6 PG-only
SQLite skips; final9 service/HTTP/subprocess/browser checks passed after adding cap
refusal and reviewing desktop/mobile package UI. Ruff/migration drift passed;
independent source review found no blocker. No new migration/configured DB change.

PR341/ADR0047 pins new fixed hero/logo sources and protects referenced versions;
legacy v1/v2 keep their source/history without backfill. New ADR0048 selects the
exact owned generated palette UUID only for new v3 scenes; replay/source/schema
switches deny. Current brand style and older source identity remain separate.
Private same-origin PNG load checks deadline/size/MIME/signature/dimensions;
missing/corrupt/denied/redirected image leaves save/export disabled. Actual
save/reopen/restore, decoded PNG pixels, desktop/mobile and no outside requests
verified.163 focused workspaces/assets/browser checks:157 passed/6 PG-only SQLite
skips. Ruff, migration drift and independent source review passed. Initial browser
failure used stale collected JS; collectstatic rebuilt it and final checks passed.
No new source migration, provider, protected fixture or deployment action.
Prior workspaces0005 applied ONLY to the SAME disposable local preview after a
private native SQLite backup. Brand/document/material/raster counts preserved;
backup hash unchanged. No configured real PostgreSQL/staging DB accessed.

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

Old time-limited heartbeat and low-usage monitor remain PAUSED. Owner requested
and we created ACTIVE15-minute thread heartbeat
yaparo-15-dakikada-bir-geli-tirmeye-devam. It resumes local synthetic work under
existing safeguards; no usage monitoring. A schedule is not proof a run executed.

## Next action

After reviewed design-bundle PR CI/merge, add per-action undo/redo for unsaved
editor changes, distinct from committed history; keyboard access and failed-save
edit preservation required. No general importer/customer upload is authorized.
Same disposable local preview schema is current; loopback8002 runtime was started
with the palette flag and an in-memory signing key in the prior slice. Refresh
that same runtime after merge to expose new bundle route; never reset its data.
No authenticated manual preview claimed. Configured DB recovery, customer upload/
scanning/parser isolation/privacy and full portable editing remain open; Y05/Y06
not complete.
