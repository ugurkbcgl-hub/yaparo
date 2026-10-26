# ADR-0059: Explicit offline candidate application to a new design revision

- Status: Accepted local synthetic slice; hosted generation remains closed
- Date: 2026-10-26
- Continues ADR0055/0058 and the local Y11 journey.

Add a separate default-off SYNTHETIC_BRAND_COPY_APPLY_ENABLED flag. DEBUG, the
preview flag and owned campaign-design selection are still required. Preview-only
mode stays read-only when apply is off. No migration, new SDK/provider or API call.

Each candidate offers title-only or title+subtitle application. The closed CSRF
form carries task UUID/fingerprint, candidate key/digest, expected live document
revision and an explicit field mode; it never accepts raw candidate text, brand or
document IDs. Regenerate only the zero-cost deterministic template on POST, rebuild
the server-owned task and match the exact candidate digest. This is not a design
for rerunning hosted inference on POST. Future hosted results need durable jobs,
usage/provenance and the separate evaluation/financial gates.

Use the existing scene text validator (including UTF-16 length and encoding) to
test field fit. No truncation, layout/font/color/asset/CTA mutation or automatic
campaign reselection. Oversized body disables full application and server refuses
forged attempts; title-only stays explicit. The current saved scene, not the older
selected snapshot, is copied and only chosen text fields replaced. Unsaved edits
in another browser cannot be read; the page asks the user to save them first.

Successful apply appends a normal saved document revision, preserving prior
snapshots. Same candidate/no change refuses rather than creating an empty revision.
Old or replayed expected revisions refuse without duplicate writes. Campaign
selection remains its original immutable snapshot; choosing the new revision for
the campaign is a separate explicit action. History reason remains generic save:
this proves local content/history, not a durable AI task/candidate generation audit.
Task/candidate correlation is validated at apply but is not separately persisted.

Preserve the editor's brand/workspace → document lock order and never lock the
draft in this service. Legacy campaign editing locks draft/workspace, so adding a
draft lock here would invert ordering. Revalidate ownership/source/task while
locked; an eligibility subquery in the same document UPDATE checks latest exact
campaign choice, snapshot, owner/workspace/activity/archive. A changed observed
pre-statement choice causes no update and atomic rollback, including any baseline
snapshot work. This is statement-snapshot validation, not a perpetual selection
grant after the write. Existing saves use optional eligibility=None unchanged.

Only POST is allowed. Exact single-valued fields, CSRF, bounded urlencoded body and
preparse multipart refusal apply. No client text/unknown/duplicate metadata fields
are accepted. Success/error/auth responses remain private/no-store/noindex; failure
returns409 with a route to current campaign selection and no reflected payload.

Local evidence:295 related service/HTTP/browser tests (281 pass/14 PostgreSQL-only
skips), plus a final browser rerun after disabled-button visual refinement. Actual
browser old-tab refusal preserves the concurrent user title; explicit title then
title/body application creates revisions4/5 with history and selected snapshot1
unchanged. Oversize/no-truncation, flags/scope/CSRF/duplicate metadata/preparse and
write-bound selection rollback are checked. Mobile/desktop screenshots reviewed.
Four new actual PostgreSQL races must pass required CI: two applies, editor/apply,
committed reselection before UPDATE, and legacy campaign-edit lock compatibility.

Next: prepare a meaningful brand/source-grounded synthetic text evaluation for the
existing evaluation gateway. Recheck current provider terms/model/cost/privacy
conditions before any permitted trial; do not connect hosted generation to this
product route or claim real quality from the deterministic template journey.
