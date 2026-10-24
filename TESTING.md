# Testing strategy

Keep verification proportional to the change. Local product prototypes use synthetic data and must make mock actions/results visible as mock. Do not contact a publishing platform or trigger ad spend in ordinary tests.

## Current CI and demo coverage

- `.github/workflows/ci.yml` runs for pull requests and pushes to `main`. It installs the Django app and pinned development tools on Python 3.13, checks formatting with Ruff, runs lint, audits installed dependencies with `pip-audit`, builds source/wheel distributions, verifies required templates and static assets are present, runs `python manage.py check`, checks migration consistency, and runs Django tests.
- CI uses an ephemeral PostgreSQL 18.6 service with CI-only placeholder credentials. GitHub destroys the service after the run.
- Pinned Playwright/Chromium browser tests cover the synthetic profile-edit demo and authenticated campaign workspace against that CI PostgreSQL service. Campaign coverage includes owner boundaries, creative editing/version history/restoration, live bounded character counters, and narrow-screen overflow. For focused local runs, use the isolated in-memory SQLite settings and regenerate the static manifest after adding static assets. All product examples stay synthetic; no publisher or spend action is called.
- Dependency auditing requires network access to its vulnerability service. Build artifacts under `apps/web/build/` and `apps/web/dist/` are ignored by Git.
- The protected `main` branch requires the `Django system check` from GitHub Actions and an up-to-date PR branch.

## Product verification layers

Synthetic workspace rehearsal coverage checks owner isolation, POST/CSRF,
start/failure/retry/stop, stale input fingerprints, repeated form revisions,
terminal stop and cascading cleanup. A PostgreSQL-only concurrent duplicate
start test exercises separate connections against the draft row lock in CI;
local SQLite skips it. Browser coverage exercises failure, recovery, stop,
new start and event history at narrow/desktop widths. The fake channel performs
no network calls, produces no real metrics and incurs no spend.

1. **Unit:** campaign states, advertiser authorization, budgets, content validation, and transition rules.
2. **Integration:** PostgreSQL constraints and tenant isolation; AI schema and provider contracts with fakes; platform authorization, idempotency, retries, and result reconciliation with sandbox accounts or controlled fakes.
3. **End-to-end:** brief → campaign preview → configured automation state → report. Until a real destination is selected, publishing/results are synthetic and clearly labeled.
4. **Operational:** readiness and deployed revision, secrets/config separation, backups and restore, rollback, emergency stop, and visible job failures.
5. **Usability/accessibility:** keyboard and screen-reader essentials, responsive layouts, clear progress/error states, short intake effort, and comprehension of limits/results.

## Synthetic closure journey

`SYNTHETIC_CLOSURE_UI_ENABLED` is disabled by default. Enable it only in an
isolated synthetic environment with current migrations and a synthetic owner/
workspace; do not enable it against the preserved Google test DB or real data.
The campaign list then links to `/workspace/control/`. GET/HEAD overview/status
are read-only. Only an explicit owner POST with CSRF and the synthetic-only
confirmation starts the fixed example. No outcome/proof/connection input is
accepted. One example/operation is retained per workspace; refresh/replay does
not reset it. Status remains pending because there is no provider executor.

Focused tests: `growthtwin.modules.connections.test_lifecycle_journey`, plus
the store/decision/observation/ticket modules. On October 21, 80 local tests
passed; two PostgreSQL-only competing-writer tests were skipped on SQLite.
Required CI must verify those on its ephemeral PostgreSQL service. Tests cover
owner/active-state isolation, method/CSRF/confirmation boundaries, extra-field
rejection, no-store error responses, replay, transaction rollback and corrupted
state. Separate browser review checked desktop/mobile/keyboard and resume using
a disposable fixture DB, separate cookie names and an unusable-password owner.
The helper-only fixture session is not a product authentication bypass or a
real sign-in test. Preserved Google DB/grants/ledgers were not used.

## AI evaluation

- Keep model quality/latency experiments separate from application correctness tests.
- Use a small, versioned synthetic benchmark covering representative advertiser types and the first chosen campaign/channel tasks.
- Score factuality against known brand facts, policy/claim handling, destination-format validity, schema validity, useful draft quality, latency, cost, and failure behavior. A single sample is not evidence of reliability.
- Existing Qwen/NVIDIA dental-task measurements in `AI_PROVIDERS.md` are exploratory, one-run results. They do not prove quality across customer types and do not authorize autonomous publishing.
- Record provider, model identifier, date, latency, failures, and observed quota; never record keys or real advertiser data. Trial hosted services are not production acceptance tests.

## Phase gates

- Local website and campaign UX can be tested with synthetic data before staging/recovery work is complete.
- Before real platform accounts, an external beta, or production, verify staging E2E, backup/restore, rollback, controlled CI failure blocking, platform permission revocation, spend ceilings, stop behavior, and the main advertiser journey. Record actual results; do not infer them from CI's synthetic test.
- Never use staging or a hosted trial model for real advertiser/customer data or live paid campaigns.

## Fixed fake closure results

Two fixed examples now demonstrate confirmed and uncertain STOP with distinct
server-owned identities. Result POST requires explicit synthetic confirmation,
CSRF and a ten-minute owner/workspace/request/operation/revision signed token.
`test_lifecycle_results` adds 14 local tests and one PostgreSQL-only concurrent
result race. The focused lifecycle selection has 94 passed locally and three
PostgreSQL-only skips. Exact replay must bypass the fake adapter; expired, stale,
wrong-owner/scope, altered-state or injected outcome/proof requests must not write.
No remote exactly-once/recovery guarantee follows from this deterministic fake.
Desktop/mobile browser checks exercised both results, reload and keyboard action;
the normal viewport was restored. No actual Google/credential/erasure operation.

## Synthetic connection/work ordering

`test_lifecycle_work_guard` adds 14 local tests and two PostgreSQL-only orderings
for closure intake versus a fixed fake work/callback. The focused lifecycle set
has 108 local passes and five PostgreSQL skips. New scope registration is internal,
fixture-only and explicit; default/missing/quarantined/generation-mismatched or
closed scope must deny. The same owned workspace row lock orders closure intake
and local fake execution; rollback must restore both request and scope state.
No arbitrary executor, remote request or actual grant write is accepted. Required
CI 39649793207 verified both orderings within 393 PostgreSQL tests and 10 browser tests; post-merge main CI 39650308546 passed. Local SQLite cannot prove this row-lock behavior.
Migration 0002 was applied only to ephemeral test DBs, not preserved Google or
browser fixture DBs. No UI changes or new browser test in this service-only slice.
This is not a production restore or already-sent remote-action guarantee.


## Campaign stage overview

`campaigns.test_journey` adds 16 tests. Together with campaigns.tests,
`test_exports` and `test_rehearsal_views`, 63 focused tests passed with no skips.
Coverage includes owner/inactive/foreign/missing access, GET/HEAD no writes,
405 mutations, error privacy headers, current source/version preference,
plan prerequisites, approval existence versus current consent, stored TEST
state allowlisting and existing dispatch priority after source changes.
Projection queries exclude dispatch payloads; provider/grant/verification calls
are patched to fail. Exact loopback owner/workspace/remote/forwarded visibility
and prerequisites are checked. Currency is taken from the stored draft.
Ruff, formatting and migration drift passed; no new migration.

Browser fixture 127.0.0.1:8011 used the preserved isolated closure preview DB,
unusable-password synthetic owner and Google disabled. Created synthetic draft 1,
selected the first current creative and verified the suggested step changed from
creative selection to plan review without inventing approval/dispatch/results.
Plan Enter navigation, report roundtrip and list-to-journey worked. Desktop and
390x844 viewport screenshots were inspected; mobile document/client widths were
375/375 with no horizontal overflow. Viewport reset. Proof outside Git in the
conversation workspace: campaign-journey-desktop.png and campaign-journey-mobile.png.
The helper session is not a product login or staging E2E test. Restart applied
previous migration 0002 only to that isolated fixture DB; actual Google preserved
DB/grant/ledgers and Heroku were untouched. PR #302 required CI 39653009712 passed 409 PostgreSQL tests and 10 browser E2E tests; post-merge main CI 39653441692 passed.


## Protected TEST navigation

`connections.test_draft_navigation` adds 14 tests; together with existing draft
review/dispatch, total-budget, header and campaign journey checks, 55 focused tests pass.
Coverage includes scoped shared links, escaped names, unchanged fixed consent,
CSRF/host/forwarded/owner/method denial, missing/unknown/uncertain/stale state,
metadata-only status GET and no provider/credential/payload/write on that GET.
Owned errors retain links; unresolved approvals do not expose a campaign link.
Mocked validation/operation responses verify result scope, status codes and links;
they are not new Google evidence. Ruff/format/migration drift passed; no migration.

Desktop/mobile browser reviewed the shared review and uncertain-status screens,
expanded the full package, followed status and campaign-back links using Enter,
and reset viewport. Mobile document/client widths375/375 (390x844 override).
Proof outside Git: test-review-navigation-{desktop,mobile}.png and
 test-status-navigation-{desktop,mobile}.png in the conversation workspace.
Helper Temp/growthtwin_test_navigation_preview.py uses the existing validated
isolated fixture DB/cookies with unusable-password synthetic owner; creates only
fixed synthetic draft2/approval/uncertain metadata. A prominent fixture label and
stubbed configuration distinguish it from actual Google evidence. Google flags
remain false; browser used no operation POSTs. Preview-only GET routes render the
inner presentation with a fixed stub; they do not prove product authentication or
local endpoint authorization. Actual protected views/CSRF are exercised in tests.
Preserved Google DB/grant/ledgers, Heroku and real data remain untouched.

Shared result/error documents preserve same-origin referrers for their local logout form CSRF Origin. Callback/start remain no-referrer; external referrers remain suppressed. Existing header test and result assertions passed.

PR303 first PostgreSQL CI39716734298 rejected an overlength synthetic unknown-state fixture (varchar20). The test label was shortened; application/model constraints unchanged. Corrected latest-head CI39716957472 passed423 PostgreSQL tests and10 browser E2E tests; PR303 merged and main CI39717264957 passed.


## Durable connector identity metadata

`connections.test_connector_identity` adds15 local tests and2 PostgreSQL-only
races. Together with existing `test_lifecycle_work_guard`,29 local tests pass
and4 PostgreSQL races skip on SQLite. PR304 required CI39719120618 verified all four races in440 PostgreSQL tests and10 browser E2E tests; main CI39719367350 passed.
Registration replay, workspace/owner isolation, stale generation/revision,
retired-generation/request reuse, permanently blocked state, replay after later
rotation/block, corrupt history, receipt rollback and database state/provider
constraints are covered. Reads/writes cannot call provider/credential adapters.
New races check simultaneous registration yields one identity/receipt and two
competing rotations admit only one current generation. SQLite is not lock proof.

Ruff/format/migration drift and independent read-only review passed. Migration0003
was applied only during ephemeral local test DB setup, never to the preserved
Google DB or the browser fixture. No UI/browser run for this service-only slice.
No runtime consumer, credential metadata mapping, actual OAuth handshake, remote
exactly-once, stop/revocation or independent restore-barrier guarantee is implied.


## Default-off synthetic authorization attempts

`test_synthetic_authorization` adds23 local tests and2 PostgreSQL races. With
`test_connector_identity`,38 tests pass locally and4 PostgreSQL tests skip.
PR305 required CI39720686706 verified the four pending races in465 PostgreSQL tests and10 browser E2E tests; main CI39720985597 passed. New races require PostgreSQL: a second perform during a running fake must not
execute twice; a block must commit while fake waits and reject its late success.
Other tests cover default/confirmation, scoped generation/revision, expiry before/
during fake, switch/block/rotation while fake runs, stale active replacement,
historical GET without writes, owner/inactive isolation, missing receipt, caller
transaction rejection, provider/credential adapter isolation and immutable-binding
corruption. Accepted metadata must be ALLOW with aware completion within lifetime;
contradictory fake outcome or corrupt accepted metadata cannot replay as success.

Review finding about accepted metadata consistency was fixed and independently
rechecked. Ruff/format/migration drift passed. Migration0004 ran only in ephemeral
test DBs; no preserved Google/fixture DB, credentials, provider, Heroku or UI use.
No browser check for this service-only slice. A running fake is never resumed or
re-executed automatically; an expired/stale active example may be retired before
a new explicitly confirmed example. This is not real OAuth callback verification,
authorization, grant storage, remote exactly-once or independent restore evidence.


## Scoped TEST candidate boundary

`test_scoped_oauth_candidate` adds20 local tests and2 PostgreSQL races. With
existing `test_backend`, `connections.tests` and `test_views`,51 local tests pass
and2 PostgreSQL tests skip. Every client, token-path check, transport, encrypted
write and read is mocked; only fabricated fixtures are used. No actual grant,
client, endpoint or candidate file is accessed. Tests check default-off, legacy
preservation, one exchange per callback receipt, session/state/client binding,
pre/post scope and lifetime, candidate-only schema/path, inactive permission,
transport/write uncertainty, simulated DB failure after possible file write,
late legacy-file presence, immutable binding and no automatic retry/revoke.

PostgreSQL races remove the process lock to exercise durable parallel-callback
reservation, and block the connector while mocked transport waits to prove no
candidate storage follows. Required CI must verify them. Ruff/format/migration
drift and independent source review passed. Migration0005 only ran in ephemeral
test DBs. No browser test or actual filesystem write/decrypt/Google operation.
The mocked orphan test is not real filesystem/DB distributed recovery proof.

PR306 required CI39722697389 and main CI39722996360 subsequently passed487
PostgreSQL tests and10 browser E2E tests, including its two races.

## Candidate envelope and advisory readback

`test_candidate_readback` adds21 local tests and1 PostgreSQL race. Focused with
`test_scoped_oauth_candidate` and `test_backend`:55 local passes and3 PostgreSQL
skips. All client/transport/path/encrypted I/O is mocked. Strict fields/version/
scope/token bounds, wrong owner/workspace/session, default-off/caller transaction,
corrupt receipts, no activation/write, pending/rejected/uncertain dispositions,
legacy/client changes, malformed/missing storage and post-read scope/binding
changes are covered. The PostgreSQL race allows a concurrent block to commit
during read and denies a match afterward. No actual decrypt/file/provider action,
new migration, browser test or recovery certification. See ADR0032.

PR307 required CI39747787250 and main CI39748174729 subsequently passed509
PostgreSQL tests and10 browser E2E tests, including all three candidate races.

## Synthetic authorization session journey

`test_authorization_journey` adds17 endpoint tests. With
`test_synthetic_authorization`:40 local passes,2 PostgreSQL skips. Coverage includes
double default-off, owner/session/CSRF, signed action/scope/expiry, exact form
shape, replay, blocked/expired/running state, no GET work and framework-error
private/no-store/noindex headers. Real backend/candidate/readback calls are
forbidden by mocks. No new migration or actual credential/provider/preserved DB operation.
`e2e.test_connector_rehearsal` passed locally: desktop/mobile/keyboard, both fake
outcomes, refresh and quarantine preservation; screenshots reviewed outside Git.
Local Playwright1.63.0 (existing dev pin) was installed in the development venv;
no dependency manifest changed. See ADR0033 for session/recovery limits.


## Recovery dispositions

Connection recovery dispositions (2026-10-22): owned metadata-only assessment separates callback wait/restart review, uncertainty reconciliation, inactive review and rejected history; scope/session flags never permit retry or activation. Synthetic-only signed CSRF recovery reopens an existing fixed example in a new owner session by changing only its session marker. Receipt expiry/scope/scenario are bound; no begin/perform, new receipt or deadline extension. Run guards deny stale/expired/running/terminal execution.18 new tests plus17 prior journey tests:35 local passes; extended isolated browser and mobile visual check passed. No migration or actual credentials/provider/preserved DB/Heroku operation. See ADR0034. PR308 required CI39752232154 and main CI39752610827 passed527 tests and11 browser tests. Next: explicit RESERVED-only retirement with generation fencing in mocks; uncertainty cannot be retired/retried automatically.


## RESERVED candidate retirement

Reserved candidate retirement (2026-10-22): default-off unwired owned service requires explicit typed confirmation and current quarantined RESERVED scope. Generation rotation and original REJECTED/retired_before_exchange receipt commit together; unique retirement request and replacement-generation metadata are validated against permanent history. Exact replay returns current identity even after later rotate/block. All non-reserved/stale/blocked or other unresolved history denies. No I/O, cleanup, retry, activation or change to legacy grant/stop/reconcile.14 new local tests plus2 PostgreSQL races; with existing adapter/recovery:42 local passes,4 PostgreSQL skips pending CI. Independent final review passed. Migration0006 only in ephemeral test DBs; no actual credential/provider/preserved DB/UI/Heroku operation. See ADR0035. PR309 required CI39756480228 and main CI39756903416 passed545 tests and11 browser tests. Next: separately reviewed scoped endpoint/session/CSRF wiring with mocked transport, normal runtime off.
PostgreSQL races cover both winners: exchange-first denies retirement; retirement-first seals callback with zero transport. Local rollback test injects failure after rotation and verifies both metadata changes roll back. No manual browser check for this service-only slice.


## Closed scoped candidate endpoints

Closed scoped TEST endpoints (2026-10-22): separate overview/start/callback/retire routes bind signed5-minute forms to configured owner/workspace/session and immutable scope. Both endpoint/candidate flags remain False plus exact loopback/DEBUG/no-forward guards. Separate scoped redirect leaves legacy default/runtime unchanged. State digest marker rejects old/wrong callback before consuming current handshake; allowed callback always303-cleans URL. Retirement digest rechecked under service locks after independent review found a check/use race.25 new tests plus existing adapter/retirement/legacy:76 local passes,4 PostgreSQL skips; independent final review approved. No new migration or actual provider/credential/preserved DB/Heroku operation; no manual browser check. See ADR0036. PR311 required CI39765174203 and main CI39765596754 passed586 PostgreSQL tests and11 browser E2E tests. Follow-up readiness audit: the owner-approved scoped redirect was registered and both old/new URIs re-read; API remains Test and OAuth External/Testing. Current customer.test_account and isolated runtime binding remain unverified. See [October 22 audit](docs/product/google-production-access-audit.md#scoped-test-hazırlığı--22-ekim-2026). Next: complete isolated candidate-exercise prerequisites with the legacy grant/ledgers preserved; flags remain off, no OAuth/refresh/adoption/publish/cleanup.


## Isolated closed preparation — 2026-10-22

No application code changed or local automated test suite run. A new temp SQLite
DB was migrated and checked for a distinct explicit owner/workspace pair,
unusable-password owner, quarantined connector and zero candidate/Google ledger
rows. Credential/client/transport functions were denied in the preparation process;
no server/provider/credential I/O occurred. No existing DB was opened. This is
bootstrap evidence only, not concurrency, browser authentication, callback log
safety, TEST-target or actual OAuth evidence. See [preparation record](docs/product/scoped-test-exercise-preparation.md).
Baseline PR312 required CI39768028595 and main CI39768447961 passed586 PostgreSQL
tests and11 browser E2E tests. Follow-up documentation CI must be verified separately.


Scoped TEST preflight and closed runtime (2026-10-22): one bounded legacy-grant
refresh plus one fixed Ads identity read verified the configured non-manager TEST
child and registered client. Encrypted client/grant hashes and preserved DB stat
unchanged; no credential write. Separate closed loopback8002 synthetic login/logout
and404/no-store/no-referrer callback checks passed. Temporary login disabled after
explicit shutdown cleanup. A separately reviewed one-shot candidate launcher was
started under the owner's action-time approval; one RESERVED attempt reached a
Google passkey block and expired before EXCHANGING. Exact candidate file absent;
process stopped, synthetic password disabled and sessions cleared; original
RESERVED history retained without retry/rotation. No successful exchange/candidate/
adoption claim. Normal source flags False. See [current protocol/evidence](docs/product/scoped-test-exercise-preparation.md).
PR313 required CI39792541560 and main CI39795773585 passed586 PostgreSQL tests
and11 browser E2E. No new local automated test suite was run for this slice.


Inactive scoped TEST candidate (2026-10-22): after the user's Google verification
and resumed approved flow, the exact expired RESERVED was retired via the existing
service with stable request/digest and generation fencing; history retained.
A separately reviewed history-bound single-exchange launcher completed callback
into CANDIDATE on the same synthetic owner/workspace. Independent metadata/file-
existence review confirmed quarantined revision1, old rejected receipt, current
candidate and nonempty exact file. No encrypted contents/token validity/candidate
account proof inspected. Logout, process stop and explicit unusable-password/
session0 cleanup completed; source flags False, no activation/consumer/advertising.
Origin-session/process-secret loss prevents existing guarded readback; next design
owner-bound inspection-only recovery with unchanged receipts, using synthetic data.
See [exercise result](docs/product/scoped-test-exercise-preparation.md).
No application code change or new local automatic test suite in this slice.


## Inspection recovery permit protocol — 2026-10-22

27 new tests in test_inspection_recovery:25 passed locally,2 PostgreSQL race skips.
Combined focused invocation with test_candidate_readback and test_candidate_retirement:
65 tests total,60 passed and5 PostgreSQL-only skips. Tests fabricate candidates
without invoking OAuth and verify zero backend/reader calls plus unchanged original
attempt/connector/generation records, including denied operations. New session after
old SECRET_KEY loss is independent of original receipt; later permit key/session
loss fails closed. Cover exact replay/expiry/no renewal, wrong owner/scope/session,
digest/generation/block drift, no caller transaction, DB constraints and two races
(competing issue requests and competing consumers). PR316 required CI39815782725
and post-merge main CI39816401402 passed613 PostgreSQL tests and11 browser E2E,
including both recovery-permit race tests.
Ruff format/check, migration consistency and whitespace checks passed. Migration0007
ran only in ephemeral test DBs. No actual credentials, files, preserved Google DB,
provider, UI or Heroku operation; no actual readback or post-I/O protocol validation.
See [ADR0037](docs/adr/0037-metadata-only-inspection-recovery-permits.md).

## Synthetic inspection recovery executor — 2026-10-22

37 new tests:35 passed locally,2 PostgreSQL-only skips. Combined focused invocation
with permit, original readback and retirement suites:102 total,95 passed,7 skipped.
Fresh in-memory SQLite with config.test_settings and an ephemeral secret only.
All original receipt/identity/generation records stay unchanged in the success
case; only the permit is consumed. No caller snapshot/reader/path is accepted.
Backend/client/transport/storage and existing reader/path hooks remain unused.

Checks cover five fixed synthetic outcomes, only-fixed-client admission, committed
claim before each transaction-free probe, repeat denial, failed initialization/read
without reopening, transient pre-read denial, post-read ownership/session/SECRET_KEY/
scope/receipt/permit/time/flag drift, client/legacy changes and bounded safe results.
Clock checks cover moving before consumption; no monotonic guarantee is claimed.
Two PostgreSQL tests cover competing executors (one fake read) and rotation during
the read (no match). PR317 required CI39836461900 and main CI39837030362 passed650
PostgreSQL tests and11 browser E2E, including those races. Local SQLite is not
row-lock evidence. Ruff format/lint, migration drift and whitespace checks passed;
independent source review found no blockers. No new migration, UI/browser exercise,
actual file/credential/provider/preserved DB/Heroku operation or deployment.
See [ADR0038](docs/adr/0038-synthetic-inspection-recovery-executor.md).

## Closed recovered reader and bounded storage — 2026-10-22

New reader37 tests:35 local passes,2 PostgreSQL-only skips. New storage17 tests all
passed; every filesystem/stat/PowerShell operation was mocked. Four additional
SafeExceptionReporterFilter tests passed with DEBUG=False: reader chain and direct
session-bearing recovery/path helper calls mask their locals. Direct-call helper
annotations are defense in depth; the protected reader entry already covers its chain.
Combined invocation with permit/readback/retirement:123 total,116 passed,7 PostgreSQL-only skips, using
ephemeral in-memory config.test_settings. No preserved DB or credential was opened.

Checks cover exact scope-derived storage locations (same durable legacy location
under a new session), client/candidate decoder caps, duplicate JSON rejection,
safe errors, metadata-only legacy presence, committed claim before all observations,
single candidate read/replay denial, flags/ownership/session, storage/config drift,
client/legacy changes, immutable receipt/permit drift and both time budgets. Regression
tests cover deadline crossing while holding DB locks and root changes during the
second client observation. PostgreSQL races cover competing readers and rotation
during read and await required CI. Ruff format/lint, migration drift and whitespace
checks passed; independent review found the two corrected gaps and no remaining
source blocker. No new migration, UI/browser exercise, actual DPAPI runtime, file,
provider, protected DB or Heroku operation. Script marker tests prove source shape
only; real Windows/ACL/no-follow/credential validity remains unverified.
See [ADR0039](docs/adr/0039-closed-recovered-candidate-readback.md).

### Hosted-runner dependency download guard

PR318 latest-head run39839852480 stalled twice during Playwright's Ubuntu APT
dependency downloads, before application tests. Attempt1 was cancelled after about
10 minutes; its log showed slow azure.archive.ubuntu.com package downloads.
Earlier head5ba81bb/run39839305150 passed704 PostgreSQL tests +11 browser E2E;
that does not verify the later helper-privacy changes or CI change.

The CI job now caps total runtime at20 minutes and Chromium installation at8.
Before installation it configures APT with one retry and20-second HTTP/HTTPS
connection/data timeouts. When the hosted-runner mirror list exists, it selects
official HTTPS archive.ubuntu.com and security.ubuntu.com endpoints. Distribution
suites, package signatures, permissions and every existing check remain unchanged;
installation failure remains fatal. No continue-on-error or test bypass is added.
These limits reject late/stuck installation, not proof of external availability.
See [Ubuntu APT transport documentation](https://manpages.ubuntu.com/manpages/jammy/man1/apt-transport-http.1.html)
and the [runner-image stall report](https://github.com/actions/runner-images/issues/14594).
Actual workflow execution is the validation for these Linux-only CI commands;
no local device APT configuration is changed.

PR318 latest required CI39843136730 and main CI39843726808 passed708 PostgreSQL
tests +11 browser E2E; the bounded official-mirror dependency installation passed
both runs. Earlier cancelled attempts are not the successful evidence.

## Actual Windows bounded-decoder rehearsal — 2026-10-22

Source-reviewed `scripts/rehearse_inspection_storage.py` ran on Windows with actual
DPAPI only for new disposable fabricated files:12 checks passed, cleanup_complete
true, forbidden_boundary_attempts0. DB and network guards precede Django setup;
legacy client/read/transport/path calls are forbidden. No existing credentials or
DB are fixture inputs; only safe result counts are printed.

Valid Turkish JSON and a30000-character payload round-trip; duplicate/malformed/
non-object/NaN JSON, empty/invalid-UTF8/bad/oversized ciphertext, missing file and
oversized text reject. The oversized text ciphertext exceeds131072 bytes before
the later plaintext guard, so plaintext_limit_independently_exercised=false.
No limit changes or unsupported plaintext-boundary proof. Exact manifest cleanup
is nonrecursive. Ruff format/lint and whitespace checks passed. No new local Django
suite was needed for this harness/docs slice; last verified full suite is above.

A separately reviewed immutable RO SQLite/metadata/ACL audit verified the same
preserved DB unchanged, coherent two-attempt history, disabled login/session0,
regular exact client/candidate files and private protected-root ACL. No encrypted
contents were read/decrypted. At that audit migration0007/table were absent; no backup,
migration/permit/provider/actual reader/adoption/activation occurred. See
[current preparation evidence and next plan](docs/product/recovered-inspection-exercise-preparation.md).


## Actual same-DB backup and forward0007 schema preparation - 2026-10-22

Final reviewed private two-phase helper passed Ruff/compilation. Three ACL-related
PREPARE failures stopped before database copy, leaving empty directories only.
Focused native ACL handling passed on an empty owned directory; final PREPARE
secured its fresh root BEFORE copying, verified byte/snapshot-equivalent backup
and actual immutable-RO plan containing only forward connections.0007. Independent
actual manifest/hash/ACL/migration-source review found no APPLY blocker.

Single APPLY passed fresh admission, exact plan and mode=rw existing-file checks;
preexisting application schema/data/history preserved except recorder0007; only
new permit table/indexes; permit_count0; backup unchanged. SQLite internal tables
excluded. No post_migrate management command, restore or APPLY retry. Subsequent
RO audit passed current identity/history, disabled login/session0, table/migration
presence and exact private protected files without reading their encrypted contents.
No permit/provider/readback/activation/deployment or new local Django suite.
See [full evidence and current next step](docs/product/recovered-inspection-exercise-preparation.md).


## Launcher preparation rehearsal - 2026-10-23

14 focused tests in test_inspection_launcher_preparation passed local ephemeral
SQLite:11 session bootstrap/refusal/cleanup cases and3 fabricated-plan checks.
Includes exception after session insertion, wrong scope/usable password/caller
transaction/preexisting session refusal, changed minted row retention and concurrent
other-session retention with explicit cleanup-review failure. Existing user data
stays unchanged on successful bootstrap; no password login is claimed.

Plan tests mock all private helper/file/ACL operations. Independently reviewed
actual read-only plan passed and was repeated after session-only hardening with
same post0007 identity/history/backup admission,
permit0/session0, no protected contents read/current-client proof/execute capability.
Ruff format/lint/whitespace passed; no broad local Django suite or actual protected
session/permit/decoder invocation. Full execution/failure rehearsal remains next.


## Synthetic session deadline hardening - 2026-10-23

20 focused tests passed ephemeral local SQLite (previous14 plus6 new tests): exact
expiry drift during context/reload, unchanged-DB monotonic exhaustion, wall-clock
expiry/backward movement, changed workspace owner and delayed final scope query.
The last case independently advances wall clock or monotonic time during the final
query and proves the after-query deadline check rejects late success.
Expiry is captured before DB insertion; cleanup matches original encoded bytes,
payload and expire_date and retains changed rows. validate() can be reused for
future launcher checkpoints; this is not full execution integration or a hard
cancellation of blocked queries. Ruff lint/format ran from apps/web like CI and
whitespace checks passed. Required PostgreSQL CI pending for this slice. No real
preserved session/permit/credential operation or broad local suite was run.


Fabricated inspection integration (2026-10-23):17 new focused tests pass ephemeral
SQLite; combined with20 preparation/session tests,37 passed. Real ORM/session/
issue/consume and bounded JSON codec are exercised; DPAPI return bytes are mocked.
Covers exact success, consumed invalid/unreadable/client drift, permanent preclaim
marker, committed ISSUED interruption, postconsume expiry/cleanup drift retained
for review, repeated decode quotas, swallowed provider/socket attempts, scope
rejection and direct decoder-guard traceback session masking. Independent source
review found/resolved generator masking gap. Ruff/format/whitespace passed.
No actual protected DB/client/candidate, Windows DPAPI or private-ACL operation.


Fresh Windows fixture integration (2026-10-23):17 new helper +13 creator tests
passed; combined coordinator/preparation run67 local SQLite tests passed. Ruff
format/check and whitespace passed; independent source review completed. All four
real Windows fabricated scenarios separately passed: match(client2/candidate1),
client-changed(2/0), invalid-envelope(2/1), unreadable exact-file-absent(2/1).
Each returned consumed/replayrefused/session0/historypreserved/privateACLverified/
cleanupcomplete/boundary0. Unit native calls were mocked; separate CLI runs used
actual bounded DPAPI. No protected candidate or provider operation.
Full boundary/evidence: docs/product/windows-inspection-fixture.md.


Yaparo rename/relocation (2026-10-23): from the new Unicode OneDrive source and
rebuilt external runtime,767-test app suite completed:746 passed,21 local PostgreSQL-only skips;
11 browser E2E passed. Four actual Windows runtime-resolver tests passed (CI may
skip these native checks);6 relocation-adapter tests included in app run. Local
PostgreSQL check/pending migration/model drift checks passed. Yaparo wheel/sdist
contain required assets. HTTP home/health200 with new branding. Actual read-only
preparation admitted same private backup/history with permit0/session0 and no
credential decode; private helper source/hash untouched, PREPARE/APPLY not rerun.
See docs/continuity/RENAMING.md for technical compatibility IDs and boundaries.


During rename CI39991662424 exposed an existing monotonic exactdeadline rounding
failure (1failure/786tests,4nativeWindows skips). A captured absolute monotonic
interval now replaces elapsed subtraction at BOTH pre/post-query checks, with
wallclock/DB/scope/privacy rules retained.21 preparation tests passed, including
new deterministic fractional1000.1/nextafter/exact1300.1/backwards/postquery cases.
An extra8 mocked view checks passed for provider-removal guidance that does not
assume an external OAuth application rename. Required CI must pass latest head.


## Isolated synthetic creative editor (23 October 2026)

From `experiments/creative-editor`, install its pinned browser dependency with
`npm ci --ignore-scripts --omit=optional`, then run `python test_editor.py` with
the existing private Python/Playwright environment. Five focused tests passed
locally: Turkish save/reopen and decoded PNG, transforms/fixture isolation/mobile,
invalid storage, unsaved-change cancellation and loopback server boundaries.
External requests are blocked and fail the test. No DB/credentials/provider calls.
The required CI job repeats this suite and audits the installed optional-excluded
npm dependency tree. [Evidence and limits](docs/product/creative-editor-spike-results.md).
This does not establish production asset isolation or full-editor comparator success.

## Multi-brand identity slice — 24 October 2026

Focused local workspace plus brand browser run: 31 tests, 29 passed and two
PostgreSQL concurrency tests skipped under in-memory SQLite. The browser creates
two synthetic brands, edits one and verifies the other and prior identity remain
unchanged; desktop/mobile screenshots reviewed. Source review found no blocker.
Ruff lint/format, migration drift and wheel/source asset verification passed.
PostgreSQL races must pass in required CI before merge. No configured DB migration,
customer upload, provider call or production deployment was performed.

Saved-document follow-on:77 focused workspace cases (73 local passes,4 PostgreSQL
skips), plus one actual Chromium create/edit/reopen/download/identity-change test
passed. The downloaded JSON was decoded and checked. Source reviewed by root;
independent helper review was interrupted by workspace-credit errors. Required
PostgreSQL CI is the remaining merge gate. No configured DB migration performed.

Owned visual editor: four focused HTTP tests and one Chromium journey passed.
Checks cover duplicate/nonfinite/oversized JSON, ownership/CSRF, stale/noop saves,
save/reload text/transform preservation, rejected stale tab, actual decoded800x800
PNG, zero external requests, no localStorage and mobile overflow. Screenshots
reviewed. Initial collectstatic failed on an unshipped upstream source map;
removing only that comment resolved it, then all five tests passed. No persistent
configured DB or provider operation. Required CI is still to be checked.

Brand palette/history follow-on (ADR0042):95 focused workspace/browser tests ran,
90 passed and5 PostgreSQL races skipped locally, including competing restore. Browser save/restore1→3/restore2→4, stale
tab, actual PNG decoding and pixel palettes passed. Legacy v1 background remained
unchanged. Atomic history failure rollback and foreign access refusal covered.
Independent backend/JS source review found no blocker; minor naming/loading notes
were addressed. New0004 table only, no legacy data rewrite or provider operation.
