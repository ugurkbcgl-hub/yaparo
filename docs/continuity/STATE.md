# Yaparo — current handoff

Verified: 2026-10-25 20:50 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base main393515d (PR345 merged); required CI40198604735 and main CI40199056437
succeeded. Branch feat/campaign-design-selection; PR346 open. Required CI40218129191
was in progress at snapshot; final independent source review found no blocker.
Resolve current branch/head/PR/CI live. No unrelated edits at task start.
Durable task: GitHub issue328. New campaigns0009 creates only the local choice table;
no backfill or configured database change. Preview migration not yet applied.

- ADR0052 adds default-off/DEBUG same-workspace campaign → owned brand/saved-design
  selection, pinned to an immutable revision. New document edits do not change it;
  explicit reselection is required. Existing Search text/approval/dispatch untouched.
- Append-only choices have exact UUID replay and stale-version refusal. Latest
  unavailable reference never falls back to earlier history. Bound sources only;
  no invented legacy provenance. Draft removal preserves source snapshots.
- Selection locks only its draft; a scoped INSERT subquery rechecks revision,
  owner/workspace/activity/archive at write boundary without adding source locks.
  Independent review confirmed the prior lock inversion was resolved. Four actual
  PostgreSQL concurrency tests must pass required CI before merge.
- Private chooser uses closed typed POST, CSRF, preparse multipart/size refusal and
  no-store/noindex headers. Same-origin referrer preserves actual browser CSRF.
  Editor return hint accepts only owned same-workspace bounded integer campaign.
- 295 relevant local tests:284 passed/11 PostgreSQL-only skips. Final6 HTTP/browser
  checks passed after UI refinement. Actual selection → stale refusal → editor
  revision2 → preserved pinned revision1 → explicit reselection passed. Desktop/
  mobile screenshots reviewed. Ruff/format/migration-drift/diff checks passed.
  Required CI and postmerge preview update are not yet claimed.

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
Prior workspaces0005 applied there only after verified private backup; original
brand/document/material/raster counts preserved. No data reset or new DB for UI.
Private serve_design_preview.py runs loopback8002 with DEBUG and only the palette
flag plus a fresh in-memory signing key; it refuses pending migrations. Verify
and restart that exact script/process if needed after merge/collectstatic, never
replace an unknown listener. Home/login and actual unversioned DEBUG static JS/CSS
were HTTP200 after PR345. No authenticated manual preview claimed; browser evidence
uses isolated test fixtures. Do not infer production readiness from these checks.

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

Finish the reviewed campaign-design selection PR and required CI, then apply only
campaigns0009 to the SAME disposable preview after an exclusive private SQLite
backup and exact migration-plan verification. Enable the new flag in its private
launcher only. Next product slice: read-only visual preview/export of the exact
campaign-pinned snapshot, distinct from the current editable document.
