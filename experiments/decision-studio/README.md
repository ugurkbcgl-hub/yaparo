# Yaparo research decision studio

Local-only, synthetic UX successor to `../unified-journey`. Start `serve.py`
(default loopback port8014). No install/build, app database, credentials, external
runtime asset, AI/ad call, upload, campaign persistence, payment or publishing. Public FX source/cache is the exception below. The
old8013 draft and existing8002 application are preserved.

## Implemented

Default authored interactive demo: five quick-start profiles (cafe, boutique,
B2B software, local service and workshop), context-bound copy/CTA/illustration,
new trio/similar/undo/history, and a helper that proposes bounded changes with
an explicit Apply button. Text/CTA/body are visible in the creative and editor.
This is authored local response logic, not an LLM. Generation provenance records
`authored_demo_response`, its version, modelnull and externalQueryfalse.

Four-step single-workspace flow: structured communication job + business model +
desired action + free text + audience/sector → three fixed creative directions →
campaign decision → review. Optional identity/message and question-level
`showWhen` conditional notes; no repeated business/intent collection. Creative
angle/hook/tone/CTA/static format and local edit revisions survive navigation.
Text/position editor, similar option, undo and previous trio stay within the flow.
Helper is explicitly prepared local response logic, not a live language model.

Product-level20-channel catalog, eight-dimension research scoring, explanatory
cards, prerequisites, technical/test minimums, useful caps and retained budget.
Selected channels have compact TL input/range/percentage display. Other paid,
partner/managed and owned actions are separate. Manual changes obey minimum,
channel cap and shared portfolio budget/cap; zero removes a channel. They do not
force100%. Recompute resets manual edits from the current fields. Changed inputs
make the last decision stale and block review until recomputed.

## Source and provenance

Owner supplied `Yaparo_TR_Kanal_Oneri_Dataset.xlsx` (SHA256
`c4b07b4b5e827ccdbc07415b9e9dcd702eb477e8c24d452b4cceb0380c6a37ed`)
and `Yaparo_TR_Reklam_Karar_Sistemi_Raporu.docx` (SHA256
`025da7409ab08a6aaad99c04238d6a49cbc0748b02d18dbdbdf8d7ef1fbdd332`).
Both remain unmodified outside the repository. Normalized public research rows
are in `dist/data.js`:79questions/249options/94incompletebranchrows/20products/
1460scores/8weights/16policyrows/20SC01fixtures/8scenarios/21sources.
Source504formula values are original workbook cache, NOT recalculated. Comparison
against the20 cached score results is a local adapter test, not an independent
validation of the workbook. The initially absent reference engine was later
recovered and tested separately; it is not wired into this prototype.

The ZIP/reference JS/schema/reason-code dictionary were later supplied in the
external yaparo_package. Its validator/hash checks passed; its channel-only
fallback was flagged. Workbook94branch rows lack source value/target question;
do not execute those incomplete rows. Package JSON rules have populated pairs,
but are not imported yet. See the research-decision-studio note.
All option Active cells blank: retain null. Use question `showWhen` for the
implemented conditional fields. Some narrative source IDs conflict with the
manifest; source manifest identities are retained, not independently verified.

## Financial and data boundaries

`engine.js` is a new owned, deterministic prototype adapter, not the recovered
reference JS engine. SC01 reproduces Meta1800TRY + Google1200TRY at3000TRY/7days,
and all20 weighted scores. First apply conservative policy/account/asset/objective/
forecast gates, then threshold60, useful minima, portfolio roles and score² water
filling in integer kuruş. Shared operations/profit cap is counted once. CPA is
limited to the lesser of declared CPA and per-customer contribution; all inputs
remain illustrative, not a qualified unit-economics model.

The unchanged research dataset has SC01 forecast rows only. In the selectable
historical reproduction mode they are bound to dated2026-10-27,7days, İstanbul,
Kadıköy, local_retail, local_nearby, fashion_beauty_lifestyle, district_city,
store_visits and basic_utm. Different context, missing forecast or policy review
receives NO allocation, not a fallback equal mix. Budget/economy changes can be
explored within that fixture. Values never become current platform forecasts.
10000TRY input leaves6800TRY unallocated in that historical mode. A checkbox cannot qualify an account,
asset, partner contract or document. No observed platform account is used.
Policy text is research input, not legal advice or production qualification.
All results `externalQuery:false`, `model:null`, `publishable:false`.

`simulation.js` adds a separate default `interactive` mode. It creates NEW
synthetic observations from current sector/goal/geo/days/asset/readiness inputs,
never edits or rebinds the workbook SC01 observations. Exact context signature
must match. Observations carry `authored_simulation_NOT_market_data` and the
demo version; timestamp means local creation, not platform freshness. Fabricated
CPC/CPM/CPA/reach values and assumption-ready accounts are explicitly labelled.
Radius simulation admits only catalog rows mentioning radius; this is a demo
classification, not qualification of actual platform enforcement. Missing mode
still refuses allocation. Historical mode keeps OLD example FX; interactive
mode may use a fresh selected public FX record. No current ad price is implied.
All outputs remain nonpublishable. No runtime key loaded.

Helper recognizes prepared intents (budget/days/radius/city, simplify,
alternative/new trio, explain, short brief). A preview Apply button updates
allowlisted fields; no arbitrary code or unrestricted agent action. Review of a
changed brief requires new creative confirmation. Unsupported messages receive
stage-specific guidance, not invented successful execution. Context/history
remain in tab memory; AI/media costs0 and no advertising requests.
Prepared Apply actions pin the brief, selected creative revisions, plan fields
and allocation revision; changed conditions refuse an old action rather than
overwriting newer choices. Unknown technical minimums also remain excluded.

## Public sources and freshness

See [source contract](../../docs/product/source-freshness-layer.md). Fixed TCMB/
ECB public XML adapters, explicit issuer choice, separate source/fetch/expiry dates,
1hour cache,4day max observation age,60second cooldown, context/quality guards.
TCMB timed out here; actual ECB fetch/readback passed. Public FX alone persists
outside Git/OneDrive. No advertiser source is connected; the UI says access_required.
Same-origin status/refresh endpoints, CSP connect-src self, no arbitrary URL or
credential. Verified TLS retained. Changed/expired quotes invalidate a plan;
recompute pins source provenance while ad estimates remain labelled simulation.

## Not yet implemented

- Full79-question typed/validated workflow, all16 policy gates, actual document
  verification, claim/consent checks and semantic free-text conflict resolution.
  Conditional complex fields currently collect notes only; never approve policy.
- Seven other scenario forecasts: descriptions only, no fabricated observations.
- Actual account forecast adapters and their provider-specific TTL/context policy,
  account minimums, geo/format qualification, calibration and operational API.
- Actual creative/AI/chat generation, asset upload, backend ownership/persistence.
- Previous8013 Turkey polygon/radius map is preserved there; this new design
  currently has plan notes/radius input only and refuses radius allocation.
- Production integration, spend/publish/payment and download/export decisions.

## Checks

`node experiments/decision-studio/engine.test.cjs`

`node experiments/decision-studio/simulation.test.cjs`

`python experiments/decision-studio/test_sources.py`

`python experiments/decision-studio/check.py` (existing development Playwright)

Engine: exact sample and20cachedscores, zero/missing/stale/policy cases,
min/max/manual boundaries and88budget cases. Browser: edit/choose/recompute,
stale refusal, retained budget, conditional/policy/no-forecast, mobile/helper,
literal text, no outbound traffic/storage and HTTP Host/path boundaries.
Interactive checks add context binding, radii, readiness/policy refusal, source
immutability, distinct authored profiles, command bounds and apply-before-mutate
browser checks, retained selection/history and final review. Five browser tests
and8offline source tests pass. Browser sources are mocked; actual ECB evidence
is separate. Screenshots go to a private temporary evidence folder; not committed.
