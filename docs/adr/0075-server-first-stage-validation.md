# ADR-0075: Server-owned first-stage validation and analysis

Accepted29October2026 for provider-free synthetic development (WP01, issue375).
Extends ADR0073/0074 without changing the accepted four-stage user journey.

## Decision

`campaigns/recommendations/bank.py` owns immutable Python field definitions for
the current nine intent banks and46 exact purpose/outcome routes, including
conditional Other/audience/date/location/price/qualification/destination fields.
Ported field IDs, enum values/labels, roles, limits and required conditions match
the existing owned JavaScript bank. No JavaScript runtime is required by the app.

`validation.py::validate_snapshot` re-derives active fields, normalized answers,
scalar/multiselect validation and cross-field constraints. Default mode rejects
unknown/inactive input keys. Explicit prune_hidden=True returns a separate preview
with the removed keys; acceptance requires constructing from that clean snapshot.
Hidden old destinations never contribute to accepted analysis. Global risk remains
active and cannot be removed by a purpose change or by marking fundraising normal.

Envelope/version/route/answer types and sizes are bounded before interpretation.
Errors contain trusted field IDs and reason codes, never echo answer values.
UTF16 limits and ECMAScript trim/ASCII digit semantics are deliberately handled;
bool is not a number, numeric strings are not numbers, optional null is not absent.
Cross-checks retain real dates/order, location address-or-map, physical event visit,
discount price order, contradictory experience and overnight opening hours.
Zero material quantity still activates its required unit.

Server URL validation permits HTTP(S) declarations, never performs a fetch and
does not prove ownership, accessibility or delivery. It rejects userinfo, forbidden
whitespace/control/backslashes, invalid ports/IP literals, ambiguous encoded hosts
and joiners before IDNA conversion. It deliberately also rejects some browser-
accepted empty-label/legacy numeric host forms. This is a narrower declaration
policy, not a complete implementation of WHATWG URL parsing or an SSRF fetch gate.
Literal text is retained, never interpreted as markup/instructions or classified
as a sector/policy permission. Future rendering must still escape it normally.

`AcceptedBrief` reruns validation in its constructor and requires canonical
normalized data. Its binding includes validator and bank versions. Client valid,
analysis, policy or readiness flags cannot produce this value. Accepted means
**server_form_valid_declaration**, not verified truth, legal suitability, measured
capacity, account access, payment or publishing consent. Existing DeclaredBrief
stays declared_unqualified; no automatic promotion of old metadata occurs.

Correct the earlier unqualified metadata enum gaps: actual source delivery is
hybrid, not combined; fundraising is also an explicit selectable risk. No durable
record used these contracts yet, and no stored IDs/data/schema are migrated.

`analysis.py::AcceptedAnalysis` accepts only AcceptedBrief and re-derives literal
subject/identity/message/audience, exact outcome/KPI/CTA/destination, explicit and
forced risks, known/unknown states and existing exact taxonomy-only projection.
Unsupported paid mappings stay null. Uncreated forms/custom destinations remain
unresolved. Every fact stays user-declared/unverified; forecast is null, measurement
false, externalQuery false, model null, platformQualified/publishReady false.
The result dictionary is detached; immutable source and versioned bindings remain.

## Integration boundary

No HTTP route, UI asset, ORM model, migration, persistence, owner lookup, credential,
provider, AI call or ad/spend operation is introduced. There is no new runtime
dependency. This module validates pure synthetic inputs; it does not activate a
real-data flow. DraftContent still requires the old DeclaredBrief exact type;
accepted analysis is separate until the durable owner service is reviewed.

The next package must resolve trusted owner/workspace/brand scope, bind accepted
analysis plus plan/allocations/evidence and enforce transaction/revision/request
uniqueness. It must not reinterpret prior Google/AI/plan history or project these
values into publisher consent. Existing launch/recovery/provider gates remain.

## Reproducible verification

`experiments/decision-studio/export-bank-fixtures.cjs` produces a synthetic
reference corpus from the actual owned JS bank/outcome resolver. UTF8-LF source
hashes bind the corpus; --check regenerates and compares deterministically in CI.
The app never executes this generator or consumes its fixtures at runtime.

The414 cases cover46 base routes,418 enum transitions and198 shared field specs.
They compare active field schemas, pruning/validation and normalized literal
semantics. Conditional combinations are sampled, not exhaustively proven. The
old JS raw-binding whitespace quirk is intentionally not copied into normalized
server analysis. Negative cases include stale keys, no-data destinations,
price/date/qualification conflicts and invalid contact formats.

Sixteen new tests include this differential corpus plus each base required-field
and bad-enum mutation, canonical/flag rejection, UTF16/control/ASCII/date/URL
boundaries, risk retention, outcome invalidation and detached immutable results.
Combined with existing23 contracts,5 calendar and18 metric tests:62 local passes,
no DB setup/provider. Ruff format/check and generator --check passed. Independent
review found invalid IP and IDNA-joiner gaps; both fixed with regressions and
re-reviewed. Extra agent probes were synthetic only, not additional account proof.
Required PR CI remains the merge gate; no manual visual check is claimed because
no browser UI changed. Existing prototype/browser regressions remain required.
