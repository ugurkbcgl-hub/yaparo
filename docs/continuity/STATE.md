# Yaparo — current handoff

Verified: 2026-10-26 05:09 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base maind3c5362 contains PR353, merged after current exact-head verification.
Required CI40227564071 succeeded (1019 Django tests:1015 pass/4 skips;25 browser
checks;5 isolated editor checks;288+288 isolated parsing runs). Recheck main CI.
Branch codex/brand-copy-preview; PR not yet created at snapshot. Verify live Git/CI.
Durable task: issue328. No migration/configured DB/provider/TEST fixture change.

- ADR0058 adds default-off/DEBUG owner-scoped read-only three-candidate preview via
  the bound task factory, only SyntheticTemplateGenerator, then full revalidation.
  No live adapter/key/spend, candidate/task persistence or scene/campaign edits.
- The selected snapshot stays pinned; current user edits/history are preserved.
  UI labels fictional templates, displays source facts/identity metadata and links
  separately to selection, selected preview and current editor. No apply action.
- New copy route inherits GET/HEAD-only preparse unsafe/multipart refusal and private
  no-store/noindex headers. CSP scripts none; HTML escaping verified. Base logout
  remains available; task area contains no form/input/write controls.
- Eight focused service/HTTP/browser checks passed, plus58 existing gateway/task/
  design-view checks. Scope/flags/stale/archive/mid-build change/escaping/preparse
  refusal and unchanged user revision2/title covered. Desktop/mobile no overflow;
  screenshot reviewed. Source review no blocker. Ruff/format/migration drift/diff
  passed; required CI pending.
- Product flags stay off. After reviewed green merge, enable only the new preview
  flag in the SAME private disposable preview launcher and restart its known process.
  No new DB/migrate/reset or provider call. Existing release gates stay open.

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

Define and implement explicit application of an owned offline candidate to a new
saved document revision. Recheck owner/selection/current revision, validate title/
subtitle field fit (no silent truncation), preserve history and reject stale posts.
Do not grant hosted provider, spend, real-data or publishing authority. Inspect
current editor/task/save contracts before choosing the smallest reversible design.
