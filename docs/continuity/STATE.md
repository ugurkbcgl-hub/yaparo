# Yaparo — current handoff

Verified: 2026-10-26 13:58 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base mainca54002 (PR360 merged), required CI40285500335 passed1096 Django tests
(4 skips)/33 browser tests; main CI40286189012 passed. Current branch
codex/hosted-ad-package; PR361 open at snapshot, code c20706d. Verify latest-head
required CI before merge.
Task issue328. No new migration; private schema remains workspaces0009.

- ADR0064 adds current saved-draft ZIP with ad.png,source.png,draft.json,
  manifest.json and README.txt. Owned version-addressed JSON locks/rechecks current
  saved source/history; stale/foreign/disabled/corrupt requests refuse. Browser
  checks snapshot binding and saved fields again after async export; no client
  image upload. Narrow fixed-five-entry bounded ZIP_STORED writer, per-file hashes.
  Client-rendered provenance, NOT a signed/server-rendered/rights approval artifact.
 23 focused tests:21 pass/2 PG skips; six browser tests cover all profile packages,
  PNG equality/CRC/hashes/source, malformed/oversized/stale/edit-during-fetch cases.
  Independent review no blockers; full latest-head required CI pending.
  Actual in-app package-ready message and independent Chromium ZIP readback on
  portrait84e039da-c124-48f7-b811-a309d2360b01 revision1. Actual source hash/1080x1350
  verified;37 non-auth DB tables unchanged. Private duru-portrait-source-package.zip,
  ad-package-evidence.json and live-ad-package-{1440,390}.png. No new AI cost or
  provider credential, database/source/history/hold change. Test login renewed
  normally from existing protected credential, no rotation. User tab remains open.

- ADR0063 adds square1080×1080 and portrait1080×1350 profiles. Exact immutable
  geometry in source manifest, separate UUID/history/replay for each format, full
  proportional image fit with side space, no crop. Original overlay/alpha preserved.
  Profile tamper/save-format changes refuse.19 focused tests:17 pass/2 PG skips;
  browser exact-size/fit/mobile/alpha checks pass; independent review no blockers.
  Full latest-head CI pending. No provider or ledger calls or new AI cost.
  Same private DB forward0009 backup:preview-before-ad-formats-20261026T072051Z.sqlite3;
  all old rows preserved. Source records/historical hold untouched. Browser normal
  test login created square0bb917d8-d03b-4be6-9808-b2ed66cd9d82 and
  portrait84e039da-c124-48f7-b811-a309d2360b01. ad-formats-evidence.json verifies
  37 prior non-auth tables/rows preserved; only two drafts/history snapshots added. Do not reverse0009
  automatically after multiple formats; old uniqueness can conflict (ADR0063).

- ADR0062 adds an independent HostedAdDraft over completed text/image jobs, not a
  BrandCreativeDocument, palette fixture or inferred BrandIdentity. Explicit choice,
  immutable source manifest/fingerprint, unique text/image/candidate replay, fresh
  active ownership and default-off local admission. Old Fabric v1-v4 untouched.
- Writes lock workspace->text/image source->draft; expected revision/source CAS,
  atomic append-only application history. Repeated creation reopens edited draft.
  No provider/budget operation, campaign selection, new generation or publishing.
- Fixed768x1376 Canvas2D layout: title/body/CTA/color edits. Server validates UTF16/
  controls/colors/bounds; measured pixel fit is client-only, refuses overflow without
  truncation. Private PNG loader checks no redirects, MIME/signature,8MiB, hash and
  decoded dimensions. Only unchanged saved on-screen content can export revision-
  named PNG; failed save retains fields and disables export. No fallback image.
-236 related tests (227 pass/9 PG-only skips), including2 browser cases covering
  replay-after-edit, stale-tab409, exact pixels/dimensions and403/wronghash refusals.
  Provider/ledger spies forbid all calls. Ruff/format/migration drift/diff passed;
  independent source review passed. Actual PG concurrent create/save/full CI pending.
- Actual in-app normal test login created draft
  fa426f70-5e12-4f5c-9b83-f40a72ac1c90 from first real candidate and saved CTA edit
  as revision2; history1/2 retained. In-app download event did not return a path;
  independent Chromium downloaded/reopened the actual saved PNG768x1376.35 prior
  non-auth/session tables and local ledger compared unchanged. New AI costUSD0.
- Previous paid text/image job1 stay completed/settled and unchanged: text3 variants,
  GPT-6 Luna/Azure USD0.00027610; image768x1376, requested Gemini3.1 Flash Lite Image/
  Google Vertex, USD0.033625. Historical local spent USD0.19523655 and unresolved
  USD0.00078075 hold intact. Do not retry/reset intents or inspect account balance.

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
Current private schema: workspaces0009/campaigns0009. Before0008:
preview-before-hosted-ad-20261026T065103Z.sqlite3; all prior rows compared unchanged,
only two draft/history tables, one migration, two content types/eight permissions
added. After actual edit, preview-after-hosted-ad-20261026T065916Z.sqlite3 readback
verified source manifest/fingerprint and history1/2. Source DB was not replaced.
This is local backup readback, not configured PostgreSQL/Heroku recovery proof.

Private launcher backup: serve_design_preview.before-hosted-ad.py. Current
serve_design_preview.py admits text/image/ad-draft flags for workspace1, loopback
8002, refuses pending migrations. Current editor preview process was started
WITHOUT provider key or hard-cap assertion; do not add either for this offline
composition slice. Normal source flags stay False/None. Verify exact listener
process/script before restart; never replace an unknown listener. Do not recreate
DB or reset paid intents to work around failures. Static assets were recollected.

Actual evidence: live-hosted-ad-evidence.json, live-hosted-ad-{1440,390}.png,
duru-editable-ad-v2.png; hosted-ad-before.json hashes35 preexisting tables excluding
normal auth/session changes and new draft tables. PNG SHA256:
f7ca1903714e2342bb6b45fac2eb08a0c7b940675dd7862723c0a8fdf0ca38f5.
Text/image evidence remains in prior live-hosted-{ui,image}-evidence.json files.

Visible in-app browser test session was renewed with NORMAL login after restart
and left on the saved draft; no password was reset this turn. Existing disposable
login is protected at %USERPROFILE%\.yaparo\preview-test-login.dpapi. The existing
private prepare_preview_login.py read mode can supply it in process memory; never
print its output or run credential-rotation/default mode merely to log in.
User/browser may later log out; reverify. Never store secrets in Git or snapshots.

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

Add explicit owned saved HostedAdDraft revision selection as a local campaign's
visual planning reference with a pinned read-only preview and source/ownership
checks. No inferred BrandIdentity binding, Search dispatch/publish change, new AI
call or customer launch. Preserve existing sources, profiles, histories and hold.
