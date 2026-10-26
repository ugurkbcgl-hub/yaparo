# Yaparo — current handoff

Verified: 2026-10-26 07:42 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base mainfcf5917 (PR354 merged), required CI40257731616 and main CI40258270000
succeeded. PR354 passed1027 Django tests (1023 pass/4 skips),26 browser checks.
Known private preview launcher now has copy-preview flag True (backup saved), source
flags remain False. Known process restarted without migrate; home/login HTTP200.
Branch codex/apply-brand-copy; PR not yet created at snapshot. Recheck live Git/CI.
Durable task: issue328. No migration/configured DB/provider/TEST fixture change.

- ADR0059 adds separate default-off explicit title-only/title+subtitle application.
  Server reconstructs the bound offline task and exact candidate digest; typed
  single-valued POST has no client text/ownership. UTF16 scene field fit/no truncation.
  Current saved scene's chosen text fields change; layout/colors/assets/CTA preserved.
- Successful write appends existing save history; no-op/stale/replay rejects. Campaign
  stays pinned to old snapshot until explicit reselection. Generic save reason is
  not a durable AI generation/task/candidate audit; no extra provenance persisted.
- Existing brand/workspace→document lock order, no draft lock. Revalidate inside
  locks and scope latest exact choice in the same UPDATE via eligibility subquery.
  Old _write_document calls default None unchanged; atomic failure rolls back.
- 295 related local checks:281 pass/14 PostgreSQL-only skips. Actual browser stale
  refusal preserves concurrent user title, then title/body actions create revisions
 4/5 with history/selection1 preserved. Final browser rerun and screenshot review
  passed after disabled-button styling. Four new PG races require CI before merge:
  two applies, editor/apply, committed reselection-before-UPDATE, legacy edit locks.
- Closed CSRF form/size/preparse/unknown+duplicate field refusal, private errors,
  scope/flag/source/hash/no-partial-write covered. Final independent source review
  found no blocker. Ruff/format/migration drift/diff passed; required CI pending.
  No hosted API/key/spend/billing/production change.
- After green merge only enable apply flag in same private launcher and restart
  its known process; do not migrate/reset or create a new preview database.

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

Prepare meaningful brand/source-grounded synthetic text evaluation using the existing
gateway. Inspect current task/copy/claim contracts, then recheck live provider model,
terms/privacy/cost conditions before any permitted evaluation call. Do not connect
hosted generation to product routes or infer quality from template parsing tests.
No real data/new paid infrastructure; owner handles account balance checks.
