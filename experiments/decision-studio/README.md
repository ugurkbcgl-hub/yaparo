# Yaparo research decision studio

Local-only, synthetic UX successor to `../unified-journey`. Start `serve.py`
(default loopback port8014). No install/build, database, credentials, external
runtime asset, provider call, upload, persistence, payment or publishing. The
old8013 draft and existing8002 application are preserved.

## Implemented

Four-step single-workspace flow: structured communication job + business model +
desired action + free text + audience/sector → three fixed creative directions →
campaign decision → review. Optional identity/message and question-level
`showWhen` conditional notes; no repeated business/intent collection. Creative
angle/hook/tone/CTA/static format and local edit revisions survive navigation.
Text/position editor, similar option, undo and previous trio stay within the flow.
Helper is explicitly fixed-rule, not a live language model.

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
validation of the workbook or a reproduction of an absent reference engine.

ZIP/reference JS/schema/reason-code dictionary mentioned in pasted text were not
supplied. All94branch rows lack source value/target question; do not execute them.
All option Active cells blank: retain null. Use question `showWhen` for the
implemented conditional fields. Some narrative source IDs conflict with the
manifest; source manifest identities are retained, not independently verified.

## Financial and data boundaries

`engine.js` is a new owned, deterministic prototype adapter, not the missing
reference JS engine. SC01 reproduces Meta1800TRY + Google1200TRY at3000TRY/7days,
and all20 weighted scores. First apply conservative policy/account/asset/objective/
forecast gates, then threshold60, useful minima, portfolio roles and score² water
filling in integer kuruş. Shared operations/profit cap is counted once. CPA is
limited to the lesser of declared CPA and per-customer contribution; all inputs
remain illustrative, not a qualified unit-economics model.

Only SC01 has forecast rows. They are bound to dated2026-10-27,7days, İstanbul,
Kadıköy, local_retail, local_nearby, fashion_beauty_lifestyle, district_city,
store_visits and basic_utm. Different context, missing forecast or policy review
receives NO allocation, not a fallback equal mix. Budget/economy changes can be
explored within that fixture. Values never become current platform forecasts.
10000TRY input leaves6800TRY unallocated. A checkbox cannot qualify an account,
asset, partner contract or document. No observed platform account is used.
Policy text is research input, not legal advice or production qualification.
All results `externalQuery:false`, `model:null`, `publishable:false`.

## Not yet implemented

- Full79-question typed/validated workflow, all16 policy gates, actual document
  verification, claim/consent checks and semantic free-text conflict resolution.
  Conditional complex fields currently collect notes only; never approve policy.
- Seven other scenario forecasts: descriptions only, no fabricated observations.
- Actual provider forecast adapters, cache TTL/context signatures, current FX,
  account minimums, geo/format qualification, calibration and operational API.
- Actual creative/AI/chat generation, asset upload, backend ownership/persistence.
- Previous8013 Turkey polygon/radius map is preserved there; this new design
  currently has plan notes/radius input only and refuses radius allocation.
- Production integration, spend/publish/payment and download/export decisions.

## Checks

`node experiments/decision-studio/engine.test.cjs`

`python experiments/decision-studio/check.py` (existing development Playwright)

Engine: exact sample and20cachedscores, zero/missing/stale/policy cases,
min/max/manual boundaries and88budget cases. Browser: edit/choose/recompute,
stale refusal, retained budget, conditional/policy/no-forecast, mobile/helper,
literal text, no outbound traffic/storage and HTTP Host/path boundaries.
Screenshots go to a private temporary evidence folder; not committed.
