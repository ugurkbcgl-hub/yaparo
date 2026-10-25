# Yaparo — current handoff

Verified: 2026-10-25 21:54 Europe/Istanbul (+03:00). Recheck mutable facts.

## Objective and preferences

Owned-core/open-source product plan (ADR0040, Y01–Y32); current local synthetic
brand/material/editor/export journey. Usage monitoring is disabled by the owner;
do not query usage or reactivate monitors. Reviewed green PRs may merge under
standing authorization; never push directly to main. No new paid service, real
customer data/accounts, media spend, payment or production publishing is enabled.
Budget and product decisions remain in PROJECT.md and accepted ADRs.

## Repository and current package

Checkout: C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote: https://github.com/ugurkbcgl-hub/yaparo
Private Python: %USERPROFILE%\.yaparo\.venv; secrets outside OneDrive.
Base main91461a3 (PR349 merged). Required CI40221446082 and main CI40221876779
succeeded. PR349 passed997 Django tests (993 pass/4 unrelated skips),23 browser
checks and5 isolated-editor checks. Known disposable preview was restarted with
no migration; home/login HTTP200 and owned ZIP route required login.
Branch codex/campaign-design-journey; PR not yet created at snapshot. Recheck live.
Durable task: issue328. No new migration/configured DB/provider/TEST fixture change.

- Y08 actual baseline found direct creation lost campaign return navigation through
  global brand list → brand → document → editor. Baseline blocked; not completion.
- Chooser now offers only active same-workspace brand creation links. Typed bounded
  optional campaign GET hint carries through create/failed-create/retry/document/
  editor; ownership and workspace are rechecked. No new POST authority, free return
  URL or automatic choice. Shared helper replaces editor-only duplicate validation.
- Two completed synthetic desktop/mobile rehearsal runs cover nine checkpoints to
  actual PNG/selected ZIP. No JS errors or overflow; exact selected revision/title
  checked. Timings and baseline boundaries recorded in y08-synthetic-journey report;
  they are not human speed or production SLA evidence. Mobile screenshot reviewed.
- 34 related local service/HTTP/browser checks:31 pass/3 PostgreSQL-only skips.
  Foreign/same-owner-other-workspace/flags/invalid hints and create-error return
  covered; existing persistence/selection preserved. Source review no blocker.
  Broader workspace module133 checks:128 pass/5 PostgreSQL-only skips.
  Ruff/format/migration drift/diff passed. Required CI and preview restart pending.
- This slice excludes brand onboarding, identity/material side paths and human
  observations. Six consented human observations remain open; no Y08/full-release
  completion claim. Existing source/approval/dispatch and protected fixtures intact.

## Established local capabilities and limits

Multiple owned synthetic brands have immutable identity versions. Saved scenes
pin identity and, for newer documents, exact hero/logo material versions. Source
references PROTECT used versions from parent deletion. Legacy unbound scenes keep
unknown provenance rather than inventing it. Save/restore history is append-only;
restore creates a new revision and stale writes/replays deny.

ADR0043 fixed-source catalog is metadata only, not binary/hash/rights/scan proof.
ADR0045 stores a default-off fixed palette original/normalized PNG pair atomically
in DB; private read rechecks ownership and hashes/sizes. ADR0046 adds internal
scoped deletion and fresh SQLite backup/restore/decode/deletion proof. Configured
PostgreSQL/Heroku recovery and customer retention remain unverified.

PR343/ADR0049 adds deterministic owned saved-design ZIP (scene, source/identity
manifest, README and actual palette original/normalized PNG). Fixed renderer and
system Arial remain required; no general archive importer or standalone editor.
PR344/ADR0050 adds 50 scene-only client-memory undo/redo steps and shortcuts;
successful save/restore/reload clears them, failed saves preserve edits. Committed
history stays separate. Current v4 browser checks preserve both mechanisms.

## Same disposable local preview

Private root: %TEMP%\yaparo-public-preview-q2ql3pkq, DB preview.sqlite3.
workspaces0005 and now campaigns0009 applied only here after private backups.
The latest backup is preview-before-campaign-design.sqlite3 in that private root.
First strict inventory check stopped on Django's expected post_migrate additions;
no retry/reset occurred. Read-only comparison then verified ALL existing rows
match backup exactly, with only one migration, one content type and four standard
model permissions added. New choice table is empty; SQLite integrity_check passed.
Private serve_design_preview.py runs loopback8002 with DEBUG, palette persistence
and campaign-design flags plus a fresh in-memory signing key; source defaults stay
off. It refuses pending migrations. Only restart this exact script/process, never
replace an unknown listener. Home/login HTTP200 and owned-design route redirected
to login after PR346. Browser panel open was queued by the app; no authenticated
manual preview claimed. Actual authenticated journey evidence uses isolated E2E
fixtures. Do not infer production readiness from these checks.

## Preserved integration and release boundaries

Rename evidence: docs/continuity/RENAMING.md. Keep stable Python/migration labels,
DB growthtwin/growthtwin_app, salts/UUIDs/receipts, DPAPI roots and Google/Heroku
technical identities. No global replacements, secret moves or identity resets.

Actual scoped Google candidate remains quarantined. Credential contents/token/
account access are unverified here. Origin session/process secret was lost at
logout; never substitute session/hash/identity or recreate history. Private root:
%TEMP%\gwt-scoped-preparation-_jafwrsl\synthetic.sqlite3. preparation.json,
retirement-intent.json and inspection-schema-preparation.json retain exact history
and backup pointer. Completed PREPARE/forward0007 APPLY MUST NOT rerun. No new DB,
permit retry/reset, activation or provider refresh. Separate Y19 continuation:
docs/product/recovered-inspection-exercise-preparation.md and
docs/product/windows-inspection-fixture.md. Fabricated fixture proof is not actual
candidate proof. Preserve independent legacy stop/reconcile paths.

Earlier Google DAILY/total-budget PAUSED TEST create/read/repeat/stop is historical
TEST evidence, not live serving, cap-exhaustion, conversion or performance proof.
Fresh campaign staging E2E, configured DB/files restore, code/schema rollback,
domain/identity/privacy, upload/scanning/parser isolation, tenant token controls,
real platform permissions/metrics and payment/financial consent remain release
gates. Y05/Y06 and production readiness are not complete.

Old time-limited and low-usage monitors remain disabled by owner preference.
A15-minute thread heartbeat was registered; actual execution was not verified by
this product task. A schedule must never be presented as proof of work performed.

## Next action

Y09: read AI_PROVIDERS.md and relevant ADRs, inspect the existing AI gateway and
request/result contracts, then define a narrow brand/source/version-bound capability
profile. Reuse existing provider boundaries; do not add a new SDK/provider/cost or
send real data. Keep unresolved human usability and release gates explicit.
