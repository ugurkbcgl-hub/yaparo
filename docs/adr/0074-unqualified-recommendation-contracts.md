# ADR-0074: Unqualified recommendation contract foundation

Accepted29October2026 for provider-free local synthetic development after the
owner approved the recommendation-engine plan. This is the first WP01 slice,
not completed durable application integration or accepted first-stage analysis.

## Decision

Pure immutable values in
`apps/web/growthtwin/modules/campaigns/recommendations/contracts.py`:
OwnerScope, DeclaredBrief, PlanBounds, AccountReference, EvidenceMetric,
Allocation, DraftContent and DraftRevision. No ORM, route, credential, transport,
clock read, provider call, worker or new dependency is introduced.

DeclaredBrief preserves a bounded canonical first-stage envelope with exact
version and46 compatible purpose/outcome routes, usage and explicit risk.
Canonical JSON is immutable and detached from mutable input. Fundraising risk
coexists with a declared health/other risk; absent risk never becomes normal.
**It is always declared_unqualified.** The route parity test checks vocabulary,
not every dynamic field/required/conditional answer. Unknown/hidden answer keys
may be retained as declarations, never consumed as accepted business facts.
The complete bank validator must be ported/reviewed server-side before acceptance.
Client valid/analysis/readiness fields cannot make these values qualified.

PlanBounds separates business country, account country and target markets,
currency, language, timezone, local inclusive1..365day dates, media budget and
literal region declaration. Supported money metadata is initially TRY/USD/EUR;
country-code syntax does not assert supported markets. No platform radius or
location qualification is inferred. Organic/content-only/unsure contracts have
zero media budget/no allocations; existing WorkspaceCampaignDraft positive-budget
constraints and operational fields remain unchanged. Paid may retain all
budget as reserve without an allocation or recommendation claim.

Allocation money is strict positive integer minor units; sum+reserve exactly
equals the declared media budget. Unknown is not zero. Evidence available0 is
distinct from missing/unsupported/unauthorized/stale/partial/conflicting/error/
not-applicable with null and a reason. Monetary results can be signed (negative
net contribution); counts cannot be negative and monetary minor units are integral.
This is not yet the WP02 metric-definition/outcome/attribution dictionary.

Evidence binds exact owner/draft scope and brief+plan context; official forecast
and platform actual declarations require account/connector/generation metadata.
No active account/generation registry or issuer attestation is consulted: these
are structural metadata, not proof of provider access. status_at checks declared
fetch/expiry only; provider publication max-age, terms, completeness, quality,
scope permissions and operational usability remain WP03/integration work.
No synthetic snapshot can enable publishing through this module.

Pure propose_revision verifies supplied scope/history ordering, sequential
revisions, unique request IDs, expected revision and exact replay binding. Exact
replay returns the original record even after a later revision or date expiry;
it does not make the old revision current. New backdated local plans refuse.
matches_current checks exact metadata only, not source freshness, account
activation or consent. DraftContent.publication_enabled always returns False.

Scope/history must eventually come from an authorized, locked owner service;
caller-supplied metadata is not authorization. Digest is integrity/binding,
not authentication, signature, encrypted storage or a durable replay ledger.
No database persistence, concurrency guarantee, migration or approval is claimed.

## Calendar consistency correction

Existing campaigns/planning.py computed a descriptive daily average with an
exclusive end date, unlike accepted ADR0071/brand_settings. Count both local
calendar endpoints, including same-day1 and leap days. This changes only that
preview average, never stored budgets, publisher pacing or platform spend caps.
Missing dates still yield no average. Five SimpleTestCase regressions use unsaved
objects without a database connection.

## Verification and next boundary

23 pure tests cover46-route parity, canonical binding/mutation, risk, strict
types, zero/unknown, signed money, dates/currencies, account generation/context,
allocation/reserve, cross-scope/history/replay and stale metadata. Combined with
five calendar and existing metric tests:46 local passes, no DB setup/provider.
Instant comparisons use UTC, including repeated DST-fold wall times; local
calendar dates still use the selected timezone for new-plan date checks.
Configured formatting/lint and independent read-only source review passed.
PR374 required CI40838250522 passed the reviewed d43214f head:1194 PostgreSQL
suite tests (4 explicit skips),45 app browser E2E and prototype/source/build
checks. Exact-head guarded squash mergece36b03 completed29October2026.
These ephemeral DB tests are not evidence of changes to preserved local databases
or actual provider accounts. Post-merge main CI was still running when checked.

No prototype8014 UI asset changed; no new visual claim is made. The accepted
prototype/editor and protected Google/AI histories remain untouched.

Next: complete/review the server-owned first-stage field validator and accepted
analysis contract using all46 banks before designing a durable owner service.
Only then map to a separately reviewed persistence schema. WP02/WP03 may use the
unqualified values as synthetic test inputs, never as accepted customer analysis.
