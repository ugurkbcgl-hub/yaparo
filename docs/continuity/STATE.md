# Yaparo — current handoff

Verified: 2026-10-28 17:32 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Objective and constraints

Owned-core/open-source ADR0040/Y01–Y32; plan-first ADR0072. Owner supplied V2
research: two entry choices → composed form, followed by real-data planning.
First catalog/form slice is isolated; existing8014 simulation is preserved.
Local synthetic only; real customer/account/spend/publishing and production gates
remain. Usage monitoring disabled. Reviewed green PRs may merge, never push main.
Owner manages OpenRouter balance; no new paid service/recharge. Download/export
undecided, not the next deliverable.

## Repository

Checkout C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
Branch codex/unified-journey-prototype; PR369 OPEN.
Live recheck this turn:4541b21 full CI40683169197 SUCCESS, PR369 OPEN. The following
question-bank correction is a new package and needs fresh CI after push.
No deployment or DB migration. Source/current UI use the same feature branch.

## Current owner priority and question bank milestone

Owner supplied a fundraising screenshot with irrelevant B2B/product choices and
confirmed the requested file covers the WHOLE first stage: two choices plus each
route's short form. Official GOV.UK/NHS form guidance, Google Ads objectives,
LinkedIn job guidelines and VGM help informed owned design, not copied schemas.
Canonical docs/product/first-stage-question-bank.json contains9 banks with
purpose-specific questions/answer sets, outcomes,13 outcome additions and sources.
Word output: C:\Users\ugrkb\OneDrive\Masaüstü\Yaparo Araştırma\Yaparo_Ilk_Asama_Soru_Bankasi.docx
All9 rendered pages viewed; final QA %TEMP%/yaparo-question-bank-final. First render
needed local LibreOffice PATH; a subprocess text-decoding warning occurred but
PDF/all9 PNGs were produced and reviewed. Source research files unchanged.

Runtime correction in8014 owned brief policyv4: purpose-specific context question
headings/options across9 families/13 subtypes. Fundraising+donate only social-support
work/charity-event contexts, never product/B2B/shop choices. Sector lists narrowed;
manual Other remains explicit. Outcome changes prune finance/permit details that
no longer apply; permit status and risk declarations remain. Source data.js unchanged.
Independent review found no permit/spend bypass: fundraising policy blocks by
communication/action, independent of business selection. Context labels do not
prove real business ownership or qualify live forecasts/economics.

Local19 browser tests passed27.966s; pure brief-flow, syntax, Ruff/format and diff
checks passed. Actual desktop/mobile screenshots were viewed at
%TEMP%/yaparo-decision-tb19fxg0/donation-bank-desktop.png and donation-bank-mobile.png.
No horizontal overflow found. IAB direct recheck still unavailable; these are
isolated test-browser screenshots. No real API/account/spend/publishing action.

Scope distinction: full9 new question banks are designed in the Word/JSON; current
UI corrects existing categories/branches, not all new typed questions. Event
date/location, job role/work model, fundraising purpose etc still need independent
fields instead of composite source questions. V2 preview remains separate.

## Current milestone: V2 catalog and form preview

Read supplied DOCX/XLSX/pasted request; source workbook unchanged. Seven catalogs
imported with pinned SHA256, source rows, duplicate/FK/formula/JSON/matrix checks:
10 intents,20 outcomes,200 routes,131 fields,161 options,43 modules,10 rules.
Referenced ZIP was not found in the supplied research directory; upstream
engine/test claims were not executed or adopted as evidence.

Owned v2-flow composes route/modules/source visibility, prunes hidden answers,
separates brief/plan/publish requirements and refuses unknown rules/types.91 routes
resolved;109 require clarification, never paid allocation. Basic typed fields
validate locally. Unsupported geo/account/money/document widgets remain explicitly
pending. Event/hiring/store briefs cannot finish until geo components exist.
Stage2–4 screens remain open.

Separate /v2.html runs on local8015 process. Pair collapses to summary after
Continue; relevant stage1 questions appear, extras collapsed. Changing pair clears
draft. Answers remain only in tab memory. Check button reports missing information;
no allocation/forecast/AI/upload/account/spend/publishing call. Existing / and8014
remain older authored-demo workflow. See docs/product/v2-flow-integration.md and
PROJECT/ROADMAP V2 correction.

## Verification actually run

Local18 browser journeys passed25.759s, including V2 pair/form, unsafe URL, hidden
link pruning, mismatched pair and390px overflow. Evidence
%TEMP%/yaparo-decision-e0na9knw. Focused V2 reran after adding desktop evidence:
1.502s, %TEMP%/yaparo-decision-rqo7s7gy. Desktop1100/mobile390 screenshots were
viewed; no overflow/cut controls found. Initial actual IAB inspection worked;
later calls failed with unavailable browser access after user steering. Latest
visual evidence is from isolated test browser screenshots, not a fresh IAB pass.

V2 pure200-route/conditional/pruning/URL/enum/numeric-boundary/positive-brief checks,
prior brief-flow tests and8 source-service tests passed. Ruff format/check and
V2 app syntax passed. Independent review found numeric schema-key mismatch; fixed
to minimum/maximum/exclusiveMinimum with regressions, then no blocker reported.
Importer source-hash/reproduction and negative checks passed; source unchanged.
These local results do not claim full remote application CI for V2.
Focus-retention browser regression passed1.524s; evidence
%TEMP%/yaparo-decision-hdlk2ceh. Ruff format/diff checks also passed.

## Preserved capabilities and protected work

8014: compact paired brief/required destinations, dates/noncash details, plan-first
paid/organic/both,20-product min/cap allocation, shared ideas/editor and placement
adaptations. Content/market assumptions authored simulation. TCMB/ECB FX
freshness/cache remains; prior ECB readback succeeded, TCMB timed out (historical
only). Private forecasts access_required. External research sources unchanged.

Python %USERPROFILE%\.yaparo\.venv; secrets/databases outside OneDrive.
Private preview %TEMP%\yaparo-public-preview-q2ql3pkq/preview.sqlite3; preserve
campaigns, brands, plans, holds and AI sources. Login READ helper
%USERPROFILE%\.yaparo\prepare_preview_login.py read; never print its password.
Google candidate quarantined %TEMP%\gwt-scoped-preparation-_jafwrsl; never repeat
completed PREPARE/APPLY/reset/refresh or restore over consumed history. ADR0068
unresolved holds and ADR0067–0071 ownership/replay/financial contracts retained.
Prior8013/Django8002 remain separate.

## Next action

Verify current PR CI, then implement the first-stage owned bank renderer/typed
fields from first-stage-question-bank.json, beginning with donation and testing
each compatible purpose/outcome. Do not jump to stage2 before the first-stage fix.
Keep real account/forecast/AI/spend/launch gates closed.
