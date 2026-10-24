# ADR-0041: Bounded Fabric candidate and versioned multi-brand identity

- Status: Accepted for local synthetic implementation; not production readiness
- Date: 2026-10-23
- Authority: Owner delegated implementation decisions and explicitly requested
  multi-brand experiences and sustained delivery in larger integrated packages.

## Evidence and decision

ADR-0040 requested Fabric versus a complete MIT editor on an identical task.
The [recorded spike](../product/creative-editor-spike-results.md) proved the narrow
Fabric7.4.0 task; react-design-editor0.2.1 failed declaration build and its resolved
dependency tree had critical audit findings. Its full browser task was not run.

For this bounded slice, reject that candidate at the mandatory build/security gate
rather than bringing its unneeded HTML/code/chart/media runtime into the product.
Select Fabric7.4.0 as the provisional local editor implementation and proceed
with brand foundations. This explicitly changes the requirement to run the same
task on an already disqualified candidate; it does not claim that comparison
passed. Y02/Y03 close only for this local selection and demonstrated narrow task.
Whole-product editor adoption, upgrade/rollback, font portability, asset storage
and all Y06 acceptance remain open. Revisit an alternative if Fabric fails them.

## Brand identity

Use the existing Workspace ownership boundary. A Brand belongs to one workspace;
its identity is a sequence of versioned records, not mutable global settings.
Basic multiple brands are part of Y04. Team/agency roles remain separate work.
The first implementation accepts two fixed synthetic fixtures per workspace;
this is a rehearsal limitation, not the final product's brand-count limit.

Expose bounded palette, tone and preset tagline edits. Require expected_version
and transactionally lock the brand when publishing a new identity revision.
Stale edits fail visibly; past revisions are not edited through application paths.
Brand and workspace authorization is checked server-side on every operation.

No existing campaign is automatically assigned a guessed Brand. Its current
brand_name and approval/dispatch history remain intact. Future explicit campaign
binding must preserve approved identity/content versions and independent stop.
No private uploads, external inference, new paid services or actual advertising
are enabled by this decision. Logo/photo upload, custom brand facts, creative
memory, async production and full portability are still pending implementation.

## Acceptance

One owner can create and switch two synthetic brands, edit identity with a new
revision, see prior revisions and keep the other brand unchanged. A second owner
cannot access either brand. Invalid fields, forged fixture/workspace, duplicate
creation and stale saves are covered by focused local and PostgreSQL CI checks.
Browser verification must show the complete create/edit/switch experience and
mobile layout. A successful local rehearsal is not a production launch gate.

## Follow-on local document binding — 24 October 2026

A saved synthetic creative document pins one immutable BrandIdentity. Ownership
and brand are derived through that identity, never accepted from scene metadata.
Creation explicitly names the brand and expected current identity version; a
request UUID prevents duplicate creation. Saving requires the document revision;
a stale writer cannot silently replace a newer saved scene. The revision is a
concurrency token, not a full creative edit-history or undo implementation.

The first UI only edits bounded title/subtitle and text colors and exports the
owned scene JSON. It does not provide arbitrary scene imports, custom assets,
Fabric editing inside Django or PNG rendering. Scene v1 retains the experiment's
fixed dimensions/layers/assets. Its title seeds from the pinned identity tagline
and primary color; secondary color and tone are preserved by the identity link,
but are not silently mapped to unsupported v1 fields. Existing campaign records
and publication approvals remain unchanged. Full visual integration remains Y06.

## Owned visual editor follow-on — 24 October 2026

The bounded Fabric editor is now connected through explicit brand/document routes.
Server-rendered escaped JSON contains only validated owned scene, current revision
and same-origin save URL. Save requires authenticated owner, CSRF, JSON content,
16KB body cap, unique keys, finite numbers and exact bounded scene validation.
Current brand/document ownership and revision are rechecked by the persistence
service. Stale saves fail; failed/uncertain network requests are not retried.

Fabric7.4.0 is served locally with MIT license and source/hash notice; only its
missing source-map comment is removed. No CDN or provider is needed. The saved
scene remains Yaparo v1, not Fabric JSON; localStorage is not used. PNG exports
current canvas, potentially unsaved, and is not a persisted approved deliverable.
Brand secondary/background/logo color, custom fonts/uploads, full history/undo,
upgrade roundtrip and campaign association remain unfinished Y04–Y07 work.
