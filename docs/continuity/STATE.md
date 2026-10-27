# Yaparo — current handoff

Verified: 2026-10-27 08:46 Europe/Istanbul (+03:00). Recheck mutable facts.

## Objective and preferences

Owned-core/open-source plan (ADR0040, Y01–Y32). Current local synthetic journey:
brand/material/editor → reviewed real AI → saved creative/campaign planning.
Usage monitoring is disabled; never query usage or restart monitors. Reviewed
green PRs may merge under standing authorization; never push main directly.
Existing approved OpenRouter evaluation pool USD16; owner handles balance checks.
No new service/recharge, customer data, real account, media spend or publishing.
Owner explicitly DEFERRED download/export decisions: no package work is next,
old PNG/ZIP prototypes are not accepted product scope. Prioritize in-site use.

## Repository and current milestone

Checkout: C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote: https://github.com/ugurkbcgl-hub/yaparo
Private Python: %USERPROFILE%\.yaparo\.venv; secrets remain outside OneDrive.
Base mainabc2093 / PR368 merged; required CI40412311595 passed1166 Django
(4 skips)/45 browser checks; main CI40413608566 passed.
Current branch codex/unified-journey-prototype; PR369 open; prior implementationea5ff75.
Prior headea5ff75 CI40454155066 passed. Turkey/catalog update pending latest-head CI.
Owner UX review before integration; do not claim merged.
Owner explicitly requested a simpler unified-flow draft before integration.
Isolated experiments/unified-journey serves allowlisted static prototype on8013:
request → three distinct examples → same-flow edit → plan → summary, optional
identity/style, desktop helper/mobile toggle. Fixed local cards/helper only;
no actual AI, channel efficacy, upload, DB, persistence, export, spend or publishing.
Open-tab memory only; refresh loses input as visibly disclosed. Existing8002 and
private data/ledgers untouched. Draft contract: docs/product/unified-journey-draft.md.
Review fixes preserve request context with previous trio and edited-title undo;
image picker keyboard-accessible. Current Turkey/catalog update: radius1..800km
geodesic circle intersected with pinned NaturalEarth Turkey multipolygon, offshore/
foreign parts removed and outside-land centers rejected; approximate vector only,
not street map or operational serving proof. MIT polygon-clipping0.15.7 vendored,
lock/licenses/hashes retained; npm audit no reported vulnerabilities.
14 researched digital-channel families; user chooses documented geo candidates
and relative priorities1..10. Unknown/unsupported precision0. Integer-kuruş
allocation conserved; no selected candidate means no allocation/summary. Google+
Microsoft radius geo candidates, wider country catalog qualified separately.
Shared explicit hypothetical CPM/CTR/density/repetition produce scenario metrics;
not real forecasts/market rates/population/unique reach or channel ranking.
All plan/geo/channel/priority/assumption changes invalidate stale review. Snapshot
pins clippedgeometry/assumptions/allocations. Six focused checks passed (including
80km Edirne outside-difference0, foreign center, priorities, budgets/CPM/area,
mobile and asset hashes). Independent source review found no blocker.
Private evidence: %TEMP%\yaparo-journey-4ofpibtn (turkey-channels/turkey-mobile PNGs).
Actual IAB confirmed Edirne80km: approximately8789km² /44% inside, clipped to
Turkey; private turkey-iab.png. User-facing prototype remains on8013. No API/DB/GPS/paid operation; no provider
key loaded. Docs: unified-journey-draft.md and turkey-channel-catalog-draft.md.

Current ADR0071: separate default-off LOCAL_BRAND_CAMPAIGN_SETTINGS_ENABLED adds
owned versioned goal/audience/region/TRY budget/start/end planning. Protected
CampaignPlanRevision carries campaign/brand/workspace/actor context, closed JSON,
digest and request UUID. Campaign SELF→brand/workspace locks, expected-version
stale refusal, exact historical replay without rollback/expiry. Minor-unit integer
budget,1..365 inclusive days; fresh writes check Istanbul today after locks.
No legacy operational objective/city/budget/flight changes, ad reselection, provider,
scheduler or spending action. Bound list/detail/journey use current plan overview;
corrupt plan refuses instead of showing legacy example data. No new downloads.
Nine backend tests7 pass/2 PG skips, one browser journey passed: Turkish comma
budget, save/reopen/list, stale input preservation, long-text mobile. Combined20
settings/brand-campaign/backend/browser checks14 pass/6 PG skips;50 existing
campaign/journey checks passed. Lint/format/drift and independent review passed.
Actual normal IAB saved campaign3 plan1:traffic, synthetic audience, İstanbul,
250050 kuruş,1–7 November2026 (7 inclusive days). Form2500,50 and list/overview
2.500,50 TRY agree. Two authenticated save replays added no row.40 previous
application tables including legacy fields/ad choice/hold are unchanged; ledger
unchanged/new cost0. Private brand-settings-live-evidence.json,
brand-settings-iab.png, brand-settings-{1440,390}.png, brand-settings-list.png.

Completed ADR0070: nullable PROTECT campaign.brand, no legacy backfill. Default-off
LOCAL_BRAND_CAMPAIGN_ENABLED lets owner create a NEW synthetic campaign from an
owned saved BrandAdDraft, immutable CampaignBrandAdChoice, replay-safe start and
revision/version-bound explicit reselection. Existing-campaign locks are campaign
SELF→brand/workspace→source→attempt→ad. Creation replay never locks an existing
campaign under brand lock. Old choices stay separate; old selection paths admit
only unbound campaigns. Historical selected content survives later draft edits;
reselection invalidates old selection URLs. Private CSRF/body/method guards.
New choice protects its parent campaign/source revision: deletion409 retains
create nonce; old unbound deletion remains available. Campaign start waits for checked image and fields matching saved content, using
can_use_saved independently of export. New campaign preview is readonly with NO
visible download/package action. Existing prototype exports are undecided.
New campaign's Ankara/5000 TRY are fixed EXAMPLE planning values, not targeting or
spend consent; empty destination/no flight. No provider, publish, media or AI cost.
Final10 focused tests6 pass/4 PG-only skips; prior39 expanded new/legacy/backend/
browser checks29 pass/10 PG-only skips. Four new PG races passed PR367 CI. Ruff/drift
passed; independent final source re-review no blocker after dirty-editor fix.
Actual normal IAB created campaign3/choice1 from brand1 ad
8e17aa42-009a-440a-a9e5-e87f755c9967 revision2 and opened selected preview1.
Two actual authenticated create POST replays added no plan.39 prior application
tables' old rows/column values preserved; old campaigns1/2 remain brandNULL.
Ledger unchanged/new cost0. Private brand-campaign-live-evidence.json,
brand-campaign-iab.png, brand-campaign-{1440,390}.png; mobile no overflow.

Completed ADR0069: separate default-off LOCAL_BRAND_AD_ENABLED owns explicit saved
text/image selection→BrandAdDraft→edit/save/reopen→saved PNG. Same brand/identity/
source revision required; protected attempts/identity, full pinned provenance,
brand→document→attempt→draft locks, unique create replay, CAS/history and private
CSRF routes. Separate brand-ad.js wraps actual name, palette text/accent, fixed
768×1376 overlay, measured no-truncation fit and verified private PNG. Logo binary
not applied; no ZIP/general layers/campaign selection. No new provider or cost.
10 new focused tests8 pass/2 PG skips, including second brand, long-name/mobile,
valid different PNG hash refusal, stale/replay and private guards. Independent
source review no blocker. Combined41 new/legacy/backend/browser checks passed (36 pass/5 PG skips);
Ruff/format/drift passed; PR366 required PostgreSQL CI subsequently passed.
Actual normal IAB created brand1 draft8e17aa42-009a-440a-a9e5-e87f755c9967 from
request3/key slogan + request4 image, identity2, then saved CTA “Koleksiyonu tanı”
as revision2. Normal independent Chromium login downloaded/verified768×1376 PNG;
lower source pixels exact, desktop/mobile passed. IAB download clicked but path
not observed. Private brand-ad-live-evidence.json, brand-ad-real-v2.png,
brand-ad-iab.png, brand-ad-{1440,390}.png.37 preexisting non-auth/non-framework
tables and local ledger unchanged after composition; new draft/history1/2 only.

ADR0068 adds default-off LOCAL_BRAND_AI_ENABLED plus exact reviewed synthetic
request UUID/fingerprint admission, independent of ADR0067's unauthorized envelope.
workspaces0011 BrandGenerationAttempt commits one intent before budget/provider;
conditional transitions, capture-before-settlement, bound readback and no retry.
New per-brand copy adapter1024 tokens preserves old512 trials. Image adapter now
validates extension against bytes and supplies detected MIME to normalization.
No source pixels/logo binary supplied. Private CSRF POST/result/image reads.

Actual normal website generation against brand1 Duru identity2, bound source
4b2de5c5-17bd-4835-a928-25f7a0588efc revision1:
- request3 dd955529-bdd0-43d5-bc32-05f3eac71ca9:3 Turkish variants, GPT-6 Luna/Azure,
  513 input/1010 output, USD0.00055630, completed/settled.
- request4 78885b7c-0412-4ce9-b8c6-debc5a5cd61d:768×1376 JPEG128201 bytes,
  normalized PNG854996 bytes, requested Gemini3.1 Flash Lite Image/Google Vertex,
  USD0.03364200, completed/settled. Blue/terracotta cups, no text/logo, natural light.
- successful total USD0.03419830. Local cumulative settled spent USD0.22943485;
  holds USD0.10170650 including historical0.00078075. NOT account balance.
- initial request1 text HTTP200 truncated at512 tokens; request2 image HTTP200/
  complete rejected by initial extension/MIME bug. Both preserved unverified/held,
  no output/precise receipt; visible rounded provider charges0.000305/0.0336.
  Never delete/reset/retry or release holds ad hoc. Safe stage/category diagnostics
  now added. Exact historical billing reconciliation remains separate work.

Checks:19 focused tests17 pass/2 PG skips before final two new guard cases;
subsequent12 generation checks11 pass/1 PG skip, including JPEG/mismatch and HTTP
method/CSRF/intake/fingerprint. Browser mock journey/reload/repeatedPOST/mobile
passed; actual user browser generation and key-free restart/readback passed.
Both focused browser checks (copy/replay and decoded responsive image) passed.
Actual normal HTTP login + two repeated generate POSTs per completed request
returned saved results; attempt count and local ledger unchanged (key-free runtime).
Ruff/format/drift passed; PR365 full required PostgreSQL CI subsequently passed.
Independent source re-review found no blocker. This is smoke, not quality benchmark.

## Same private preview — preserve it

%TEMP%\yaparo-public-preview-q2ql3pkq / preview.sqlite3 / loopback8002.
Schema workspaces0012 / campaigns0013. Forward campaigns0013 backup:
preview-before-brand-settings-20261026T221231Z.sqlite3; all prior rows preserved,
new plan table initially empty; only migration/type/permissions at upgrade.
Previous forward campaigns0012 backup:
preview-before-brand-campaign-protect-20261026T214643Z.sqlite3; all current tables/
rows intact, only migration recorder1 added. Never rerun completed upgrades.
Previous forward campaigns0011 backup:
preview-before-brand-campaign-20261026T180122Z.sqlite3; previous rows/columns
preserved, old campaigns' new brand FKs allNULL at upgrade, new choice table empty.
Standard migration+1 type+4 permissions only; never rerun this completed upgrade.
Previous forward workspaces0012 backup:
preview-before-brand-ad-20261026T171740Z.sqlite3; old rows preserved, only two new
empty tables/standard migration+2 content types+8 permissions at upgrade.
Previous forward0011 backup:
preview-before-brand-ai-20261026T163458Z.sqlite3. All old rows across36 prior
non-auth/non-framework tables preserved; four requests/four attempts now exist.
Old fixed trials/drafts/source/history/campaign choices remain independent.
Current known serve_design_preview.py enables brand-ad/campaign/settings flags locally,
restarted WITHOUT provider key or
hard-cap assertion. Exact private brand-ai-approved.json permits only requests1–4;
no new request automatically gets paid permission. Normal repo flags stay off.
Verify exact listener command before restarting. Never recreate/replace DB or
reset intent/history. Private evidence brand-ai-live-evidence.json,
brand-ai-image-iab.png, brand-bound-real-image.png. Saved results survive restart.
Normal IAB test login renewed with existing protected credential, no rotation:
%USERPROFILE%\.yaparo\preview-test-login.dpapi, prepare_preview_login.py READ mode.
Never print helper output or use default mode just to log in. Provider key remains
in existing Windows protected store; never print or copy into repo/docs/chat.

Established previous milestones: ADR0060/61 fixed Duru text/image trials;
ADR0062 editable independent draft; ADR0063 square/portrait; ADR0064 saved ZIP;
ADR0065 pinned campaign choice; ADR0066 campaign ZIP; ADR0067 immutable owned
brand brief/source context. None is retroactively rebound to new requests.
General upload/rights/scan/isolation/font/production editor gates remain open.

## Preserved integration and release gates

Rename: docs/continuity/RENAMING.md. Keep stable Python/migration labels, UUIDs,
DB/DPAPI/OAuth IDs; no global replacement or identity/credential reset.
Actual scoped Google candidate remains quarantined; token/account proof is not
established here. Origin session/process secret was lost. Private root:
%TEMP%\gwt-scoped-preparation-_jafwrsl / synthetic.sqlite3. Completed PREPARE and
forward0007 APPLY MUST NOT rerun. No new permit/retry/reset/activation/refresh.
See recovered-inspection-exercise-preparation.md / windows-inspection-fixture.md
under docs/product. Fabricated fixture proof is not actual candidate evidence.
Historical Google PAUSED TEST evidence is not live delivery/performance proof.
Fresh staging E2E, configured DB/files restore, code/schema rollback, privacy/
domain, upload isolation, tenant token controls, real platform metrics/permissions,
payments and financial consent remain release gates. No production-ready claim.
Old usage/time monitors remain disabled. A15-minute heartbeat's actual execution
was not verified by this product task; scheduling is not proof of work.

## Next action

Review the unified journey prototype with the owner before product integration.
Then map the accepted UX to existing owned creative/editor/campaign contracts.
Do not wire paid AI or replace current flows yet. Download/export stays undecided;
real accounts, customer files, payment and publishing gates remain closed.
