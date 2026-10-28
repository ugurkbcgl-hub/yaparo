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

Owned UX policy `yaparo-brief-flow-v4` is separate from source showWhen rules.

Owner review on28October rejected shared commercial questions in fundraising.
Current v4 projects purpose-specific context headings and answer shortlists for
the9 main families (13 internal subtypes). Fundraising+donate offers only a social
support work or a charity event; information routes may also choose an awareness
publication. Fundraising sector choices exclude commercial product/B2B categories.
Event, hiring, education, membership and public-message contexts also have owned
shortlists. Manual Other remains explicit and never qualifies automatic paid spend.

Source IDs/options are unchanged. These projections describe the current work;
they do not prove real business ownership, account eligibility or economics and
must not feed live forecasts without an explicit owned domain model. Response
changes rerender the context options, clear incompatible selections and prune
irrelevant details. Donation finance/permit-detail fields appear only for donate;
permit status and risk/beneficiary declarations remain. Existing policy gates
continue to block fundraising regardless of a selected event business category.

The complete desired first-stage design is
[first-stage-question-bank.json](first-stage-question-bank.json):9 purpose banks,
recommended outcome choices, purpose-specific questions/answers and14 outcome
extensions. This is authored product design informed by official form/objective
guidance, not an imported platform rulebook or a fully implemented runtime catalog.
Remaining UI work includes separately typed event date/location, job role/work
model and fundraising purpose fields. Do not claim the9 complete new forms are
implemented; current change corrects existing context/branch visibility first.
Source taxonomy and research files remain unchanged. Source `unsure` is deliberately
not exposed at entry. All other communication kinds retain explicit paths.

Fundraising reveals organiser, permit, validity/finance and consent notes. Permit,
consent and statement-approval selectors record a declaration or preparation state,
never verified evidence. They do not admit a paid campaign. Document upload and
actual bank-detail verification remain outside this local synthetic prototype.
Sales now leads with four relevant question groups; fundraising with three. Other
questions remain in a collapsed extra-details section, with no loss of saved notes.
Business labels use plain descriptions rather than internal business terminology.

Campaign periods use separate native start/end date fields, refusing an end before
the start. Price notes use separate prior/current numeric amounts. Fundraising
finance records support kind, declared delivery channel and optional monetary
target. Material/volunteer support clears an incompatible payment channel and
monetary target. This projection does not validate a bank account, permit or
payment entitlement; all current release/admission gates remain.

Structured draft answers are objects under their source question ID: date ranges
use start/end, prices regular/offer, fundraising kind/channel/target. Values stay
literal strings entered by the user; they are not transferred to spend/cap models.
They survive form rerenders/history and are pruned with their source branch.
Full permit/evidence controls and the remaining typed forms remain open.

## Destination details — 28 October follow-up

Selecting a destination reveals its required details: website, marketplace,
form/registration, app and social profile require an HTTP(S) URL; phone/WhatsApp
requires a phone number; a physical destination requires an address or map URL.
Destination availability is not inferred from a correctly formed link. URL
format validation rejects executable schemes, credentials and embedded whitespace;
phone validation checks permitted characters and10–15digits. No link is fetched,
opened or sent to an external provider. Map URLs are entered literally; no map
provider, geolocation permission or address lookup is added.

Direct event registrations, job applications and social-follow responses now
collect destinations too, even where source S1_B02 does not apply. An owned
social_profile destination and an awareness-only none option are explicit UI
extensions. They are not inserted into source enums. Known applicable source
destinations remain in branch.S1_B02; every destination uses the separate
brief.destination projection {version:yaparo-destination-v1,type,values}.

Details remain page-memory draft values, independent of targeting geography.
Changing destination type or hiding it removes old values. Unchanged destinations
survive business/sector rerenders and saved-trio history. Changes invalidate the
plan/content; literal details appear in the final review. Prepared synthetic
profiles use reserved .example URLs or explicitly synthetic address/phone data.
Manual Other still requires its existing explanation and remains unqualified.

Fundraising site/platform delivery also asks for its donation-page URL. When a
generic website destination is already active, that field supplies the link and
the duplicate finance URL is hidden/pruned. Returning to donation-only delivery
asks for a fresh link rather than reviving a now-hidden value. A declared bank
channel still does not collect/verify a bank account in this prototype.

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
