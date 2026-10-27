# Single-screen contextual brief — local prototype

Owner correction, 27 October 2026: restore the original one-screen brief rather
than a five-panel sub-journey. Keep contextual dropdown narrowing, and allow a
manual Other answer wherever the predefined options do not fit.

## Implemented

One form contains communication job, business model, sector, relevant response
destination, desired action, free text/audience/usage and optional branch notes.
No family-selection screens, progress wizard, Back/Next or hidden question panels.
Prepared examples are directly available again. Initial taxonomy remains blank.

Owned policy `yaparo-brief-flow-v2` narrows business choices by communication job,
sector choices by business model and actions by purpose/explicit destination.
These are versioned UX shortlists, not eligibility, law or current platform specs.
All14canonical communication jobs/11business models/18sectors/16actions remain
reachable on appropriate paths. Business and sector are separate dimensions;
a shop's explicit own-website destination supports an online-purchase action.
Unknown parent values are not given a fabricated compatible category. When the
owner deliberately chooses Other, independent known business/sector options may
still be offered for explicit selection; this is not inferred classification.

## Manual Other

Communication, business, sector, action and response destination have a manual
Other path. A short text field appears only for that choice. Trimmed nonempty
text is required, limited to200characters, treated as literal text and recorded
in `brief.custom` under its field key. Existing conditional Other choices
(promotion, announcement and event type) also expose an explanation, stored by
source question ID and pruned when their branch disappears. Sector uses canonical `other`; other
primary selectors use `__other__`. No custom string becomes a source enum or
verified platform category. Returning to a normal choice removes its custom
field/value from the current brief; hidden branch notes are also pruned.

Custom descriptions remain unresolved. Organic-only work may create an explicitly
authored draft; paid allocation uses missing-forecast mode and stays zero until
classification is qualified. No automatic mapping, model call, spend, account
access or publishing is created by typing Other. It is not silently called an
approved category. The current prototype does not implement custom classification.

Risk declarations survive parent changes and starter/helper profile replacement.
Changing a dropdown does not remove a declared risk or qualify publication.
Existing source freshness, downstream invalidation and plan-first journey stay.
No database change, deployment, upload or paid production.

## Source distinction and verification

The supplied report section4.1/4.4 supports contextual questions and retaining
intent. Recovered visibility rules do not define a complete option compatibility
matrix. The new narrowing policy is owned, not falsely copied from those rules.
External DOCX/XLSX/package and normalized research observations remain unchanged.
Full79typed questions/94rules, evidence and conflict handling are still pending.

Pure tests cover canonical reachability, current-context shortlists, explicit
destination override and recursive pruning. Browser checks cover one-screen
layout, narrowing, Other required/blank/length/literal handling, custom payload,
return to canonical choices, conditional Other/pruning, example switching and
history restoration, zero paid allocation and all existing journey/source/
helper/mobile boundaries. Results are recorded in continuity after execution.
