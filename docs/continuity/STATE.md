# Yaparo — current handoff

Verified: 2026-10-25 21:08 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base main1a34919 (PR347 merged). Main CI40219202806 and prior product CI40218224320
succeeded. Branch codex/pinned-design-preview; PR not yet created at snapshot.
Resolve current branch/head/PR/CI live. Durable task: issue328. No new migration,
configured database, provider or protected TEST fixture change.

- ADR0052 explicit same-workspace campaign/brand/design reference remains immutable,
  versioned, stale-safe and separate from existing Search/approval/dispatch/stop.
- ADR0053 adds GET/HEAD-only read-only preview and PNG of the pinned snapshot.
  Version-addressed URLs reject changed selections rather than following them.
  Already loaded pages retain their explicitly shown snapshot, without checking
  current selection again at the instant of client PNG generation.
- Source bytes use a scoped version-addressed private route and existing raster
  hash/version validation. Missing/inaccessible images keep download disabled.
  Same-owner-other-workspace, archive/transfer/flags/auth and preparse POST refusal
  checked. Private no-store/noindex responses and bounded CSP remain in place.
- Shared fixed renderer now supplies bitmap drawing, palette load, Fabric object
  construction and logical PNG export to both editor and StaticCanvas preview.
  Editor retains its controls, validation, saves, history and undo. New asset paths
  are required by package verification; no arbitrary image source or write added.
- 307 relevant local service/HTTP/browser checks:296 pass/11 PostgreSQL-only skips.
  Actual illustration and palette portrait PNGs remain pixel-identical after live
  edit/save and at mobile width; palette failure disables download. Existing editor
  save/reopen/stale/undo/export journeys passed. Mobile screenshot reviewed.
  Ruff/format/migration drift/diff checks passed. Initial test run required refreshed
  local static manifest; second harness failure was corrected to edit through the
  actual browser rather than ORM inside Playwright's async runtime.
- Final source review found no blocker. Required PR CI and postmerge preview restart
  not yet claimed. Existing disposable preview needs only a known-process restart
  after merge; campaigns0009 was already applied by PR346 with backup proof below.

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

Extend owned ZIP export to the campaign-selected immutable snapshot with an
explicit campaign/selection/revision manifest. Existing document ZIP still exports
the current saved document; do not silently substitute it for the selected revision.
Reuse source/hash/scope contracts, preserve Search/approval/dispatch/stop and keep
local synthetic/default-off boundaries. No generic archive importer or new service.
