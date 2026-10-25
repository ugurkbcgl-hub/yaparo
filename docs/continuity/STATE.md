# Yaparo — current handoff

Verified: 2026-10-25 16:38 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base main49f7708 (PR344 merged); required CI40196763270 and main CI40197158851
succeeded. Branch feat/portrait-design-format; PR not yet created at snapshot.
Resolve current branch/head/PR/CI live. No unrelated edits at task start.
Durable task: GitHub issue328. No new migration or configured DB change.

- ADR0051 adds explicit v4 square800×800 / portrait800×1000 UI creation with fixed
  illustration or owned palette source. Format/source/dimensions pin permanently;
  replay/save/restore cannot switch them. Omitted service/form option preserves
  cached forms and legacy v2/v3 creation. Existing v1–v3 data/rendering unchanged.
- Preview aspect ratio and y bounds follow the saved height. PNG export uses exact
  logical dimensions then restores display viewport in finally; no scene or undo
  mutation. Palette detection is shared across model/material/bootstrap/bundle.
- V4 ZIP declares renderer contract v1-v4. No-input private bundle rehearsal now
  transfers the fixed v4 portrait through its manifest to a fresh owner/workspace,
  compares metadata/bytes/pixels/reexport and preserves source DB/archive hashes.
  Exact generated inventory cleanup passed on actual Windows normal and -O runs.
- 184 related service/assets/HTTP/browser checks:178 passed/6 PostgreSQL-only SQLite
  skips. Actual PNG dimensions/bottom/palette pixels,999/390 responsive viewports,
  local undo, save/reopen/restore, export then drag/undo and legacy v1–v3 PNGs passed.
  Mobile drag test first targeted offscreen canvas; explicit scroll fixed the test.
  Desktop/mobile screenshots reviewed; ruff/format/migration drift/diff checks passed.
  Independent final source review found no blocker. Required CI not yet claimed.

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
were HTTP200 after PR344. No authenticated manual preview claimed; browser evidence
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

After reviewed format PR passes required CI and merges, build the first owned
synthetic campaign → explicit brand/design selection journey with a pinned saved
revision. Inspect current campaign/domain contracts first; old drafts stay unbound,
other workspaces stay inaccessible and selection is not publishing approval.
