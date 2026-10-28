# Yaparo — current handoff

Verified: 2026-10-28 10:37 Europe/Istanbul (+03:00). Recheck Git/PR/CI.

## Objective and constraints

Owned-core/open-source plan ADR0040/Y01–Y32. Preferred local prototype8014 follows
ADR0072: brief → channel/material plan →3shared concepts/editing → placement
adaptations → review. User now wants two entry decisions (intent + expected viewer
response), then the relevant short form on the same screen. No nested wizard.
Local synthetic development only. Real customer/account/spend/publishing and
production deployment retain release gates. Usage monitoring is disabled. Reviewed
green PRs may merge under standing authority; never push directly to main.
Owner manages OpenRouter balance; no new paid service/recharge. Download/export
remains undecided/deferred. Preserve private ledger/TEST/account history.

## Repository

Checkout C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote https://github.com/ugurkbcgl-hub/yaparo
Branch codex/unified-journey-prototype; PR369 OPEN.
Predecessor9ddc022 full CI40649316034 SUCCESS verified, including15browser journeys.
Current destination-details follow-up below requires its own CI after push. Prior
baseline01a77b4 CI40534250684 SUCCESS. No deployment or DB migration.

## Current change: intent + response before context

Nine initial purpose cards; relevant viewer-response choices follow. Both entry
questions omit Other/unsure. Context form appears after the pair, with usage,
business/sector, response destination and conditional source notes. Launch,
celebration, education and public-issue subtypes remain explicitly selectable.
Source taxonomy/data unchanged. Owned brief policyv3 separates initial response
from business/destination; latter edits do not erase it. Destinations narrow to
the chosen response. Purpose/response changes invalidate the prior plan/content.
Saved history/examples rerender both choices and context. Notes remain optional;
no synthetic brand/audience/description is silently prefilled in a fresh session.

Manual Other remains in business/sector/destination and relevant branch detail
fields, trimmed1–200characters and literal brief.custom notes. Hidden notes are
pruned; risk survives purpose/profile changes. Unresolved custom entries keep
paid allocation zero. Permit/consent/statement status controls record declarations
or preparation, never verification. Sales/fundraising now expose four/three primary
question groups, with extra notes collapsed. Date ranges, prior/current prices
and support kind/channel/target use structured draft answers. End-before-start
is refused; material/volunteer support clears incompatible payment/amount and
hides its monetary target. These values do not feed operational budget/eligibility.
Permit/evidence and remaining typed forms remain open. Business labels simplified.
See docs/product/progressive-brief.md.

Destination details now collect required URLs for website/marketplace/form/app/
social profile; phone for phone/WhatsApp; address OR map link for physical places.
Format/required checks refuse executable/credential-bearing URLs and bad phones.
Type changes/hiding clear old details; business rerenders/history retain the same
destination. Details invalidate plans and appear as literal text in final review.
Direct event registrations/applications/social routes now collect destinations;
owned none/social_profile stay separate from source enums. brief.destination uses
version yaparo-destination-v1/type/values. No URL fetch, location query, geocoding
or transmission; targeting region stays separate from visit address.

Current local17browser journeys passed24.566s (%TEMP%/yaparo-decision-aghfxfy7),
including required/bad URL, literal review, history, map-only location, type-change
pruning, event form destination and phone validation. Pure destination/schema/
source-immutability tests and syntax/configured Ruff passed. Independent source
review found no blocker in integration. Actual IAB website desktop/mobile390px
and location mobile reviewed with no horizontal overflow375/390; viewport reset.
Evidence %TEMP%/yaparo-destination-20261028: website-desktop.png,
website-mobile.png, location-mobile.png. Prior visual evidence below retained.

Local15browser journeys passed22.945s (%TEMP%/yaparo-decision-6nop5vr6); focused
structured-date/noncash test reran successfully after hiding irrelevant target
(1.552s, %TEMP%/yaparo-decision-qvjwjtjj). Includes original plan/creative/source/
helper/mobile, intent/keyboard/history and new typed-answer/date/pruning behavior.
Configured Ruff/format and JavaScript syntax checks passed. Independent source
review found no blocking regression in structured answer/state/layout handling.

Actual IAB visual checks now completed at desktop1265px and mobile390px. Initial
sales form exposed8details; primary groups corrected that. Mobile support selects
were cramped; one-column controls corrected it. Verified dates readable and no
horizontal overflow (document375px/viewport390px). Viewport reset afterwards.
Evidence %TEMP%/yaparo-visual-20261028: fundraising-desktop.png,
fundraising-mobile.png, sales-mobile.png. Local browser access works this turn;
the old disabled-browser note is obsolete. HTTP8014 server remains local.
No provider,
account, secret, upload, paid service, migration, deployment or publish action.

## Preserved previous capabilities

Plan-first paid/organic/both routes,20product minimum/cap allocation and retained
budget; shared ideas/editor with explicit text/image placement demo adaptations.
Search receives text. Video render/upload and actual production costs remain open.
All generated content/ad assumptions in8014 remain authored simulation.

Public FX freshness/cache via TCMB/ECB, explicit issuer, expiry/context/quality
checks and pinned provenance remain. Prior actual ECB fetch/readback succeeded;
TCMB timed out. This is historical evidence, not a fresh quote. Private ad forecast
connectors remain access_required. Only public cache outside OneDrive persists.
Sources: docs/product/source-freshness-layer.md and prototype README.

External research DOCX/XLSX/package unchanged. Full79typed source questions,
94rule integration, policy evidence, privacy/recovery and platform launch gates
remain open. Prior8013 and Django8002 stay separate.

## Protected prior work

Python %USERPROFILE%\.yaparo\.venv; secrets/databases outside OneDrive.
Private preview %TEMP%\yaparo-public-preview-q2ql3pkq/preview.sqlite3; preserve
campaigns, brands, plans, holds and AI sources. Login READ helper
%USERPROFILE%\.yaparo\prepare_preview_login.py read; never print its password.
Google candidate quarantined %TEMP%\gwt-scoped-preparation-_jafwrsl; never repeat
completed PREPARE/APPLY/reset/refresh or restore over consumed history. ADR0068
unresolved holds and ADR0067–0071 ownership/replay/financial contracts retained.

## Next action

Extend compact typed context fields to event details after the current PR369 CI
is verified. Keep real
AI/account/forecast/spend/launch gates closed.
