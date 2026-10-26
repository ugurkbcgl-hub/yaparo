# Yaparo — current handoff

Verified: 2026-10-26 09:07 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base main10fb185 (PR357 merged), required CI40274018693 and main CI40274611818
succeeded. Branch codex/hosted-image-trial; PR358 open at snapshot, code7419f04.
Required CI must be rechecked on the latest head before merge. Durable task issue328.
One additive workspaces0007 migration; configured DB/protected TEST untouched.

- ADR0060 text job1 remains completed/settled,3 real GPT-6 Luna/Azure candidates,
 486 input/455 output tokens, USD0.00027610. It was compared exactly before/after
  the image trial. No reset/retry or mutation of this paid intent is allowed.
- ADR0061 adds a separate default-off one-shot image trial. Same fixed fictional
  Duru IMAGE_PROMPT only; no editable brand/client/DB text, URL or file intake.
  Unique committed workspace intent, no ambient transaction, no retry/delete/reset.
  Bounded transport moved into AI gateway; operator script compatibility preserved.
  Strict duplicate/finite JSON24MB for images; text default64KiB unchanged.
- Store known cost before decode, original<=3MiB/hash before normalization, PNG<=8MiB
  with4MP/4096-edge bounds and separate hash/dimensions/tool metadata. Only verified
  PNG has owned display/download routes. Original has no route. Both cost phases
  mark ambiguity unknown before ledger operations; received results precede settle.
- Actual normal browser login + image button succeeded: image job1,768x1376 JPEG,
 98,295 original bytes/592,509 PNG bytes, USD0.033625. Requested model Gemini3.1
  Flash Lite Image/Google Vertex; API response does not independently prove route
  identity. Download bytes equal saved PNG; refresh/replay made no new charge.
  Agent reviewed actual image and mobile/desktop UI; no mobile overflow.
- Local spent USD0.19523655; historical unresolved hold USD0.00078075 intact.
  Fresh image catalog capabilities/price, active ZDR route and key USD16/no-reset
  cap verified; no account balance/credit usage inspected. No new paid service.
-80 focused checks (78 pass/2 PG-only skips),14 raster/parser/browser checks passed;
  Ruff/format/migration drift/diff passed. Independent source review passed. Actual
  PG race/required PR CI pending. No commercial quality, malware/rights or release
  approval inferred. Existing offline template profile remains separate.
- Initial PR CI ran1077 tests: only the new browser's immediate image-load assertion
  failed (4 unrelated skips). It now polls complete/naturalWidth instead of measuring
  before decode. Targeted browser rerun passed; latest full CI must be rechecked.
  No provider retry/new charge was used for this test correction.
- Earlier operator samples remain private under %LOCALAPPDATA%\GrowthTwin\evaluations:
  brand-text-20261026T045335-0f83360e.jsonl and
  brand-image-20261026T045722-5bdfe523.jsonl/matching.jpg. Both settled; do not rerun.

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
Current private schema includes workspaces0007 and campaigns0009. Before0007,
preview-before-hosted-image-20261026T060228Z.sqlite3 was created. Every prior row
compared unchanged after migration; additions only image table, one migration/
content type and four permissions. Integrity passed. After the real call,
preview-after-hosted-image-20261026T060425Z.sqlite3 was read independently: both
image hashes/full decode/dimensions and existing text verified. Source DB was
never replaced; this is backup readback, not configured DB restore proof.

Private launcher backup: serve_design_preview.before-hosted-image.py. Current
serve_design_preview.py admits text/image flags for workspace1 and gets the
existing protected key only in process memory. Normal source defaults False/None.
It binds loopback8002 and refuses pending migrations. Before restart verify the
actual listener process matches this exact known script; launcher/child PIDs differ
on Windows, so do not trust a recorded parent PID. Never replace an unknown listener.
No automatic call occurs on server start/GET. Existing text/image intents block
another dispatch. Do not reset/recreate the preview DB to get another call.

Actual evidence: live-hosted-image-evidence.json,
live-hosted-image-{desktop,mobile}.png, live-duru-studio-ai.png in private root.
Text evidence: live-hosted-ui-evidence.json and live-hosted-text-{desktop,mobile}.png.
Existing disposable test owner's temporary password was restored to its original
hash after QA; no plaintext retained. Browser tests used normal authentication.
No authenticated owner session in the user's in-app browser is claimed; that tab
may show login. Headless actual browser generation/readback/download were verified.

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

Explicitly combine a selected saved real text and this owned AI image into a new
editable ad draft, with genuine task/source provenance and preserved originals.
Do not label the AI image as fixed palette material or alter a campaign selection
implicitly. This next slice should need no provider call. Never retry/reset paid
text/image job1 or the historical unresolved hold. Customer data/publishing/general
jobs remain later gates; owner handles account balance checks.
