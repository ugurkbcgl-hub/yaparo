# Progressive brief — local prototype

Owner correction, 27 October 2026: the first screen still presented too many
independent choices. Later choices must narrow visibly; category-incompatible
options should not survive to the final action list.

## Source distinction

The supplied Turkey decision report section4.1 asks for a broad communication
job before conditional questions. Section4.4 calls for progressive disclosure,
only the relevant branch, retained context, unknown answers and explicit conflict
resolution. Recovered branch_rules contains question/workflow/channel targets;
it does not define a complete communication-to-action option filter. The new
option policy is owned, versioned `yaparo-brief-flow-v1`, not falsely attributed
to the report or treated as a verified platform/legal rule. The external DOCX,
workbook, package and normalized source observations are unchanged.

## Implemented UI

Five short panels within the existing first journey step:
1. Purpose family → communication job (5 families, at most4 child choices).
2. Business family → business model (5 families, at most3 child choices).
3. Sector family → sector (6 families, at most4 child choices).
4. Relevant destination when applicable → desired action (at most5 actions).
5. Free text, audience and usage, with only relevant optional source questions.

Only the current panel is shown. A child is hidden until its parent family is
chosen. Initial taxonomy is blank, never silently set to a retail business.
Summary chips allow correction; Back and progress labels retain orientation.
Demo starter profiles are inside a collapsed optional example drawer.

The canonical14communication jobs,11business models,18sectors and16actions remain
reachable through explicit paths. Grouping does not claim an industry uniquely
implies a business model. A company may organize an event, and a physical shop
may sell online. Explicit source S1_B02 sales/response destination overrides a
business-model shortlist for commercial jobs. No donation/job/application CTA is
shown in a normal shop-to-store promotion path. Changing purpose, business or
destination clears incompatible choices; no new child is silently selected.

## State and boundaries

Recursive question-visibility pruning removes hidden branch answers from memory
and the submitted brief. Latest primary answers override saved values; unknown
question IDs are not accepted. A changed branch cannot later resurrect old permit
or offer notes. Separate risk declarations persist; selecting a nicer category
cannot clear an existing risk and qualify publication. All financial/policy/account
and launch gates remain unchanged. Source complex-field controls remain bounded
prototype notes, not document uploads, typed legal evidence or verified consent.

Each saved local brief includes the option policy version. Existing plan-first
flow, organic/paid distinction and downstream stale/adaptation guards remain.
No LLM request, API cost, DB change, account access, publishing or deployment.

## Verification

Pure checks cover full canonical coverage, context shortlists, explicit destination
override and recursive hidden-answer cleanup. Browser journeys cover initial
visible load, parent changes, current-only payload, risk preservation, mobile
width and all existing plan/content/source/helper routes. Test results are
recorded in continuity STATE after execution; no source-reported test is assumed.

Next: owner review of question wording, then extend typed conditional field and
unknown-answer handling with evidence-backed conflict validation. This small UX
slice does not claim all79source questions/94rules are fully implemented.
