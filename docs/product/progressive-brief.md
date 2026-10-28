# Intent and expected response — local brief prototype

Owner direction, 28 October 2026: begin with what the person wants to do and what
the viewer should do. Keep the interaction on one screen. Reveal the relevant
context form after the pair is selected; avoid a second wizard inside the brief.

## Entry and context

Nine purpose cards cover introduction, sales, events, requests/appointments,
recruitment, fundraising, announcements, community/education and public messages.
The second choice contains only responses relevant to that purpose. Neither entry
choice offers Other or unsure. Launch, celebration, education and public-issue
subtypes are explicitly editable inside their context form; they are not silently
classified as membership or reputation. Changing subtype clears an incompatible
response and asks for a new one.

Usage (paid/organic/both), business model, sector and response destination are
collected after the pair. Business/sector shortlists remain contextual. Destination
options follow the chosen response; changing business or destination must not
silently replace that response. Custom business, sector and destination descriptions
are supported in the detail form. Free description/audience/message are optional;
empty text is not treated as a known business fact. Starter profiles remain available.

Owned UX policy `yaparo-brief-flow-v3` is separate from source showWhen rules.
Source taxonomy and research files remain unchanged. Source `unsure` is deliberately
not exposed at entry. All other communication kinds retain explicit paths.

Fundraising reveals organiser, permit, validity/finance and consent notes. Permit,
consent and statement-approval selectors record a declaration or preparation state,
never verified evidence. They do not admit a paid campaign. Document upload and
actual bank-detail verification remain outside this local synthetic prototype.
Typed permit/finance/date controls and full pair-specific form refinement remain open.

## State and manual details

Purpose/response edits invalidate the existing plan/content. Branch answers and
conditional Other explanations are pruned when their purpose disappears. Risk
declarations survive purpose/profile changes. History restoration rerenders the
two entry selections and the context form from the saved brief.

Manual Other requires trimmed nonempty text up to 200 characters. Values are
literal notes in `brief.custom`, not automatic category mappings. Returning to a
canonical choice removes the note. Unresolved custom entries keep paid allocation
at zero; organic authored drafts remain possible. No real AI, upload, account,
spend or publishing access is introduced.

## Verification scope

Pure checks cover response relevance, narrowed destinations, source kinds,
business/sector shortlists and hidden-answer pruning. Existing browser journeys
are updated to select the entry cards before filling the context form and check
state preservation, custom notes, plan invalidation and history. Actual execution
results belong in STATE.md; passing old tests is not evidence for this revision.
