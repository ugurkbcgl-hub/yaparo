# Yaparo — current handoff

Verified: 2026-10-25 22:06 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base main345c14f (PR350 merged); required CI40223511657 and main CI40223860175
succeeded. PR350 passed1003 Django tests (999 pass/4 unrelated skips),25 browser
checks and5 isolated-editor checks. Known preview restarted; home/login HTTP200.
Branch codex/brand-task-contract; PR not yet created at snapshot. Verify live Git/CI.
Durable task: issue328. No migration/configured DB/provider/TEST fixture change.

- ADR0055 adds a frozen schema1 brand-copy-candidate task/result envelope over the
  existing gateway. Actual pinned identity plus campaign/selection/snapshot,
  workspace/brand/document/material IDs, versions and digests bind fixed synthetic
  fixture brief. Fingerprint is correlation data, not authorization/signature.
- Acceptance reconstructs the entire server-owned request and rechecks current
  selection/scope. Same-source cross-campaign result replay and replaced/rehashed
  brief reject. Live edit preserves pinned snapshot; explicit reselection rejects
  the previous task. Candidate/failed/uncertain shapes reuse old candidate validator.
- Only deterministic synthetic-template-v1, zero ceiling/reported cost and no
  reservation accepted. No dispatch/SDK/API/key/queue/ledger added; every candidate
  stays review-required, non-publishable and execution_authorized=False. Full
  reservation/usage reconciliation/durable execution remain future Y09/Y13 gates.
- 46 offline/new-context/existing-gateway checks passed. Scope/archive/transfer,
  schema/profile/identity/material shape/cost/adapter and result mismatches covered.
  Review found missing campaign binding; fixed with campaign/selection/snapshot IDs
  and full factory revalidation plus regressions. Final source review no blocker.
  Ruff/format/migration drift/diff passed. Required PR CI pending; no UI changed.
- AI_PROVIDERS and canonical plan updated only for this verified offline work.
  Historical provider model/price/terms are dated evidence, not freshly verified.
  No usage/balance monitoring, live model quality or real-data permission claimed.

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

Y10 preparation: inspect current primary documentation/maintenance/license and
pinned compatibility for a typed-output library versus the existing direct adapter
boundary, using the same offline synthetic suite. Do not select/install a new SDK
or call a provider without its corresponding review/authorization; no real data.
Keep Y09 reservation/durable-job and human usability/release gates explicit.
