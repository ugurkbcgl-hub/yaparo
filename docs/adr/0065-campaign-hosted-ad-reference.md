# ADR0065 — Explicit campaign reference to a saved AI ad revision

Accepted 26 October 2026 for default-off local synthetic planning.

An admitted owner explicitly selects an owned HostedAdRevision for a campaign in
the same admitted workspace. CampaignHostedAdChoice is separate from the existing
BrandCreativeDocument selection, Search text/preference/approval/dispatch, provider
jobs and account grants. It records a protected revision FK, complete validated
source/content/profile/layout snapshot, selection version and unique request UUID.
No BrandIdentity association or brand suitability is inferred. Even the sample
campaign's brand text may differ from the fixed Duru trial; the UI labels this as
planning only, not Google Search visual support, rights or publishing approval.

The new LOCAL_HOSTED_AD_CAMPAIGN_ENABLED defaults False and requires existing local
trial admission/fresh active ownership. Closed single-value, bounded CSRF forms
carry only source/draft/revision/expected-selection/request identifiers. New choices
must match the current saved draft revision and source fingerprint. Stale forms or
request reuse in another context refuse. Exact replay returns the original choice
without resetting later choices. Reads rebuild the stored snapshot from checked
sources plus the protected immutable revision, not the mutable current text.

Campaign rows are locked first with of=(self), then workspace/text/image sources
and hosted draft as needed. This matches the legacy campaign→workspace lock graph;
workspace-first would deadlock against existing campaign operations. Concurrent
expected-version selections serialize; only one can append. Append-only APIs
reject individual choice edits/deletes; ordinary campaign deletion still cascades
its local planning references, as with the older design-choice model. This is not
SQL-tamper-proof storage or a retention guarantee.

The current selection has a version-addressed read-only preview and private checked
image route. Later normal draft edits keep its text/profile/source pixels pinned;
explicit reselection appends a new choice. Old selection URLs refuse after a newer
choice rather than silently show another image. The existing Canvas2D renderer has
a read-only mode: text inputs are readonly, save/package controls disabled/hidden,
submit blocked, no mutation routes on preview/image. Exact selected PNG export is
available. Private/no-store/noindex headers cover auth/errors/method refusals.
Normal source image/draft/package routes retain their previous behavior.

Migration campaigns0010 adds only the choice table and constraints; existing
campaign/source/history rows are not rewritten. No automatic cleanup or reverse
migration over later choice history is authorized. No new AI request, ledger cost,
advertiser account, production deployment or advertising spend is introduced.

Evidence:32 focused tests,28 passed/4 PostgreSQL-only skips, including the previous
saved-ad/package cases and a browser journey choosing, editing the source elsewhere,
reopening unchanged old text/PNG, mobile preview, explicit reselection and stale URL
refusal. New service/HTTP tests cover replay/version/source/context, append-only
history, simulated metadata corruption, failed append, ownership/flags/workspaces,
CSRF/preparse/duplicate fields and private readonly routes. Two PostgreSQL tests
must pass required CI: competing selections and both select/read against the legacy
campaign→workspace lock graph. Independent read-only review verified the lock-order
fix and found no remaining blocker. Provider/ledger spies forbid all calls.

The same private preview DB received only forward campaigns0010 after a consistent
backup; all old rows were preserved, new choice table initially empty. Actual normal
test login selected portrait revision1 for synthetic campaign1 and opened selection1.
Independent Chromium downloaded the1080×1350 PNG, equal byte-for-byte to the previous
saved source-package ad.png. Readback preserved37 prior non-auth tables except the
expected standard migration/content-type/permission additions; one new choice row.
Evidence:campaign-ai-selection-evidence.json and campaign-ai-preview-{1440,390}.png
in the known private root. No configured DB, Google fixture or provider access.

Next: campaign-version-specific source package for the explicitly selected snapshot,
including a campaign-selection manifest, without changing the independent draft
package or inferring brand/publishing permission.
