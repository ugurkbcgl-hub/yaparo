# Yaparo — current handoff

Verified: 2026-10-26 15:03 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base main0388f8f (PR362 merged), required CI40317099228 passed1109 Django tests
(4 skips)/36 browser tests; main CI40318090943 also passed.
Current branch codex/campaign-ai-source-package; PR363 open at snapshot,
code16fb355. Verify latest-head required CI before merge.
Task issue328. No new migration; private schema workspaces0009/campaigns0010.

- ADR0066 adds separate six-file campaign ZIP with campaign.json, pinned canonical
  ad_json bytes/hash and exact selection identity. Versioned private JSON route
  reuses selected() checks/locks. Browser compares every context field and raw-byte
  snapshot hash before existing source/content/geometry checks; mismatches/stale
  reselection refuse. No cross-language canonical reserialization. PKs are strings.
  Independent five-file package and readonly form/save contracts remain unchanged.
 36 focused tests:32 pass/4 PG skips, including9 browser journeys; six-file CRC/
  hashes/PNG/source/pinned old revision, wrong context/digest and stale refusal pass.
  Ruff/format/drift/diff and independent source review passed; latest full CI pending.
  Actual normal browser campaign1/selection1 package-ready message; independent
  Chromium downloaded/verified all6 files and1080x1350 PNG. All38 non-auth tables
  unchanged. Private campaign-selected-source-package.zip, campaign-ai-package-
  evidence.json, campaign-ai-package-{1440,390}.png. No DB/source/history/choice/
  hold mutation, new AI cost or provider credential. Same preview DB, no migration.

- ADR0065: default-off LOCAL_HOSTED_AD_CAMPAIGN_ENABLED adds explicit owned
  same-workspace saved HostedAdRevision choice for local campaign planning.
  Unique request replay, expected selection/current draft/source checks, append-only
  choice metadata and protected revision/source snapshot. Old brand/Fabric choices,
  Search text/dispatch and real platform access untouched. No inferred BrandIdentity.
  Current version-addressed readonly preview retains old content/pixels after edits;
  reselection is explicit and old selection URLs refuse. Private readonly image.
  Campaign-first of=self then source lock graph avoids legacy inversion.32 focused
  tests:28 pass/4 PG skips, including7 browser journeys. Two new PG concurrency
  checks (competing choices, legacy lock graph select/read) passed PR362 required CI.
  Independent final review no blockers. Source/package regression cases pass.
  Same private DB forward0010 backup:preview-before-campaign-ai-visual-20261026T113849Z.sqlite3.
  Old rows preserved; only migration/type/permissions and new empty table at upgrade.
  Actual normal browser selected portrait84e039da-c124-48f7-b811-a309d2360b01 revision1
  for campaign1, selection1. Independent PNG equals previous saved package's ad.png;
  37 prior non-auth tables preserved and only one choice added. Evidence:
  campaign-ai-selection-evidence.json,campaign-ai-preview-{1440,390}.png,
  campaign-1-ai-selection-1.png. No AI charge or source/history/hold mutation.

- Established saved-AI chain: ADR0062/PR359 independent editable overlay with
  source manifest/history/stale checks; required CI40283604347 and main40284342258
  passed. ADR0063/PR360 separate square/portrait geometry/history/replay, no crop;
  required CI40285500335 passed1096 Django/33 browser checks. ADR0064/PR361 adds
  saved-only five-file ZIP with exact canvas/source PNG, snapshot/file hashes and
  bounded browser assembly; required CI40311510323 passed1100 Django/35 browser
  checks and main40314817748 passed. PNG/package are client renders, not signed
  attestations. Font-fit remains client-only; fixed renderer/system Arial required.
  Normal defaults off. No inferred BrandIdentity, provider promotion or live publish.
- Paid saved text/image job1 remain completed/settled:3 text variants, GPT-6 Luna/
  Azure USD0.00027610; image768x1376, requested Gemini3.1 Flash Lite Image/Google
  Vertex USD0.033625. Historical local spent USD0.19523655 and unresolved
  USD0.00078075 hold stay intact. No retries/resets or account balance inspection.
  Original fa426f70-5e12-4f5c-9b83-f40a72ac1c90 revision2 and other independent
  draft/profile histories remain. See ADR0062–0064 for earlier actual evidence.

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
Current private schema: workspaces0009/campaigns0010. Before0008:
preview-before-hosted-ad-20261026T065103Z.sqlite3; all prior rows compared unchanged,
only two draft/history tables, one migration, two content types/eight permissions
added. After actual edit, preview-after-hosted-ad-20261026T065916Z.sqlite3 readback
verified source manifest/fingerprint and history1/2. Source DB was not replaced.
This is local backup readback, not configured PostgreSQL/Heroku recovery proof.

Private launcher backup: serve_design_preview.before-hosted-ad.py. Current
serve_design_preview.py admits text/image/ad-draft/campaign-choice flags for workspace1, loopback
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

Define and test immutable BrandIdentity/brief/material-version bindings for the
next brand-aware hosted-generation task/result slice using synthetic mocked
transport first. Preserve fixed Duru trial/source/profile/selection histories and
unknown brand provenance; do not retroactively bind them or enable production jobs.
