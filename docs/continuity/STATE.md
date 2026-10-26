# Yaparo — current handoff

Verified: 2026-10-26 08:24 Europe/Istanbul (+03:00). Recheck mutable facts.

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
Base main911f53c (PR356 merged), required CI40271981659 and main CI40272428978
succeeded. Branch codex/hosted-text-trial; PR357 open, code commita81aebc, docs
follow-up pending. Required CI must be checked on the latest head before merge.
Durable task: issue328. One additive workspaces0006 migration; configured DB and
protected TEST fixture untouched. Known private preview migration verified below.

- Owner explicitly requested real AI generation. One actual GPT-6 Luna call through
  Azure returned3 Turkish Duru Studio candidates (486 input/440 output tokens),
  USD0.0002686; one real Gemini3.1 Flash Lite Image call pinned to Google Vertex
  returned a decoded/reviewed768×1376 JPEG, USD0.033625. Total USD0.0338936.
  Fixed fictional brand only; no customer input, production route or publishing.
- Captures/private image are under %LOCALAPPDATA%\GrowthTwin\evaluations:
  brand-text-20261026T045335-0f83360e.jsonl;
  brand-image-20261026T045722-5bdfe523.jsonl and matching.jpg. Both settled.
  These prior operator samples total USD0.0338936. See new website call below.
- Fresh public endpoint/ZDR catalog and terms checked. New operator sample runner
  makes one fixed text OR image call, no retry, private fsynced results before
  settlement. Images request ZDR/data-collection denial/no fallback. Whole-repo
  output exclusion corrected; failures distinguish held/already-settled costs.
- ADR0060 now adds a distinct default-off one-shot local website text trial. One
  admitted workspace, fixed Duru facts only, no client/DB brand metadata sent.
  Committed unique intent before reserve/call; ambient transactions refused.
  Persist true model/provider/source/candidates/usage/cost before settlement.
  Reservation/settlement ambiguity is unknown; any existing intent blocks retry.
  No delete/reset, background worker, campaign apply or publishing endpoint.
- Actual browser normal test login + generation succeeded: job1,3 variants,
  GPT-6 Luna/Azure,486 input/455 output tokens, USD0.00027610. Reload and explicit
  same POST preserved one job and unchanged spend/hold. Local spent USD0.16161155;
  historical unresolved USD0.00078075 hold unchanged. Fresh key cap USD16/no reset
  and priced Azure ZDR route checked; no account balance/credit usage inspected.
-222 related local checks (216 pass/6 PG-only skips) before final ambiguity test;
  final trial suite13 (12 pass/1 PG skip), mocked browser passed; real screenshots
  reviewed. Ruff/format/migration drift/diff passed. Independent review fixes done;
  required CI/actual PG concurrent-click test pending. See ADR0060. No quality or
  production promotion. Existing offline template profile remains separate.

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
The latest backup is preview-before-hosted-trial-20261026T051858Z.sqlite3 there.
workspaces0006 applied only here: all previous rows compared unchanged; only the
trial table, one migration/content type and four permissions added. Integrity OK.
The real test then created trial1 for existing disposable test owner/workspace1;
test password was reset only in memory for normal browser QA, never retained.
Private launcher backup: serve_design_preview.before-hosted-trial.py. Current
launcher admits LOCAL_HOSTED_TEXT_TRIAL_ENABLED for workspace1 and receives the
existing protected key only in process memory. Source defaults stay False/None.
Known loopback server PID3676 at snapshot; reverify exact process before restart.
Real UI evidence: live-hosted-ui-evidence.json and live-hosted-text-{desktop,mobile}.png
inside this private root. No automatic provider call occurs on server start/GET.
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

Add a separate one-shot owned image trial using the same fixed fictional Duru
brief, bounded durable image bytes/source/hash/cost and private readback. Recheck
provider conditions before any paid call. Never retry/reset existing text job1 or
the historical unresolved hold, or label hosted output as offline templates.
General brand binding/jobs/customer data/publishing remain later gates. Owner
handles account balance checks; no new infrastructure.
