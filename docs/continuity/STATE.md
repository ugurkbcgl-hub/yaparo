# Yaparo — current handoff

Verified: 2026-10-27 15:17 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Objective and constraints

Owned-core/open-source plan ADR0040/Y01–Y32. Current8014 UX: progressive brief,
3creative directions/editing, explainable product-level ad plan, review.
User authorized source connection/freshness layer after the authored dynamic demo.
Local synthetic only; no real customer/account/spend/publishing readiness implied.
No usage checks/monitors. Reviewed green PRs may merge, never direct main push.
Existing OpenRouter pool USD16; owner handles balance. No new paid service/recharge.
Download/export remains undecided/deferred. Preserve private data/ledger/TEST state.

## Repository

C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
Branch codex/unified-journey-prototype; PR369 OPEN for owner UX review.
Baseline9944b3d CI40498591371 SUCCESS verified. That does not verify the new source
layer; check exact new head/CI after push. Main base abc2093 / PR368.
No production deployment or application database migration this turn.

## Current milestone: real public source + freshness layer

experiments/decision-studio still serves127.0.0.1:8014. Existing8013/8002 preserved.
New sources.py: normalized source record/lifecycle checks, fixed HTTPS public FX
adapters for TCMB and ECB, provider-specific cache and date/value validation.
TCMB timed out from this environment. Actual ECB fetch + IAB readback succeeded:
source2026-10-26, EURUSD1.1188/EURTRY55.6746 => USDTRY49.76278155. Treat this as
historical evidence, not a current constant. Native Windows Schannel verifies TLS;
no insecure option/proxy/credential use. Unix uses verified stdlib HTTPS.

Closed same-origin JSON status/refresh endpoints; explicit issuer picker defaults
ECB, no automatic issuer fallback. Show publication/fetch/expiry separately;
querying an old publication does not make it new. TTL1h/max source age4calendar
days/cooldown60s, per-issuer lock, atomic public cache outside Git/OneDrive:
%LOCALAPPDATA%\Yaparo\source-cache. Full holiday calendar remains pending.
Only public quote persists; no source XML, customer/brief/account secret stored.
Page auto-load/expiry refresh, matching cache reuse and explicit Refresh supported.
No background scheduler when closed; next request rechecks expiry.

Record identity binds source/scope/context/date/quality/payload hash. Reject wrong
account/context, synthetic quality masquerading as official, future/expired or
corrupt data. Public USDTRY can be shared across plan contexts; private ad
forecasts cannot. HTTP scope fixed local-synthetic; no caller tenant/account,
arbitrary URL or source record admission. CSP permits same-origin fetch only;
upstream fixed GET contains no campaign context. No advertising/AI API invoked.

sources.js discards late mismatched replies. New/expired quote marks prior plan
stale; explicit recompute records FX source/date/rate/id in plan and final review.
Historical SC01 mode retains original example FX. Interactive mode can use real
public FX, but ad CPC/CPM/CPA/reach/account assumptions remain authored simulation.
All ad forecast registry entries show access_required/no snapshot; actual Google/
Meta/etc connectors remain unconnected. publishablefalse. No model/key/media cost.
Contract: docs/product/source-freshness-layer.md and experiment README.

## Prior prototype/research preserved

Five authored profiles (cafe/boutique/B2B/local service/workshop), contextual
copy/CTA/illustration, alternatives/history/undo/editor. Helper previews bounded
changes with Apply and refuses stale proposals. Not a real LLM. Initial brief
changes require creative reconfirmation. Pure engine preserves gates/minimum/cap,
integer allocation/unallocated budget and shared business cap. Source data unchanged.

External research XLSX/DOCX remain in Yaparo Araştırma. Normalized data.js contains
79questions/249options/20products/1460scores/8weights/16policyrows/20SC01fixtures.
Owner later recovered OneDrive/Belgeler/Yaparo_TR_Karar_Motoru_Dataset/yaparo_package:
validator/sample regression and34manifest hashes passed. JSON94branch pairs are
populated unlike Excel, with typed question/channel/workflow targets. Reference
UNSEEN_CONTEXT probe still allocated3000TRY via channel-only fallback; do not
replace our strict guards. Package not imported. Full typed79form/policy evidence,
previous clipped Turkey map migration, real AI/ad forecasts/backend integration,
privacy/recovery/account/spend/launch gates remain open.

## Verification actually run

8offline source tests and5isolated browser journeys passed; unit/browser sources
are injected fixtures and make no external calls. Includes ECB cross/issuer,
source/fetch dates, expiry/cache/restart/failure/concurrency, context/quality,
HTTP origin/closed schema/no arbitrary URL, refresh→stale→recompute→review/source
switch. Node original20scores/SC01/88budget bounds and interactive/context/command/
live-FX-minimum checks passed. Ruff/format/syntax passed. CI step includes source
checks. No broad application test rerun claimed locally; exact new CI pending.
Private test evidence %TEMP%\yaparo-decision-6zw9q7ny.
Actual IAB source-live-iab.png there shows ECB source26October, fetched27October
15:16:54/expiry16:16:54 and source-aware recomputation. Actual source selection
is ECB; TCMB live success is NOT claimed. Old8002/privateDB/AI ledger untouched.

## Protected prior work

Python %USERPROFILE%\.yaparo\.venv; secrets outside OneDrive.
Private preview %TEMP%\yaparo-public-preview-q2ql3pkq/preview.sqlite3; preserve old
campaigns/brand choices/plans/holds/AI sources. Login READ helper
%USERPROFILE%\.yaparo\prepare_preview_login.py read; never print its password.
Google candidate quarantined %TEMP%\gwt-scoped-preparation-_jafwrsl; do not repeat
PREPARE/APPLY/reset/refresh. ADR0068 unresolved holds preserved; ADR0067–0071
ownership/replay/financial contracts remain authoritative for real integration.

## Next action

Qualify the first account-authorized read-only advertising forecast adapter
against this snapshot/freshness contract. Check actual access/readiness before
querying; preserve protected TEST state and never promote simulation to live data.
