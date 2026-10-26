# ADR0070 — In-site brand campaign planning; downloads undecided

Accepted 26 October 2026, local synthetic only. Supersedes ADR0069's proposed next
package priority: the owner explicitly deferred download/export product decisions.
Do not treat existing PNG/ZIP prototypes as a commitment to offer downloads.
Prioritize generation→editing→explicit campaign use inside the site. No new
download/package feature is part of this change.

Existing WorkspaceCampaignDraft records have only a free-text brand label. Add a
nullable PROTECT Brand FK; all existing campaigns remain NULL, without inferred
matching or adoption. A separate default-off LOCAL_BRAND_CAMPAIGN_ENABLED path
lets an admitted owner explicitly create a NEW campaign plan from an owned saved
BrandAdDraft revision. Brand/workspace/name/brief come from validated pinned
sources. Ankara and5000 TRY are fixed, clearly labelled synthetic plan values,
not user-selected targeting or spend approval. Destination is empty, no flight,
dispatch, scheduler, provider, credit or payment operation occurs. Current Google
Search placeholder schema does not imply that its API can publish this image.

New CampaignBrandAdChoice pins a protected BrandAdRevision and a complete checked
snapshot (identity/request/result/source/cost/edit context), permanent request UUID,
kind create/select and per-campaign version. Repeated create returns the same
campaign/choice without changing later selections; stale new starts refuse.
Selection requires same owned active brand AND workspace, current saved revision,
source fingerprint and expected selection version. Exact replay validates the
original context. Append-only history is an application contract, not SQL vault.

Existing-campaign select/read locks campaign SELF first, then the established
brand/workspace→source document→ordered attempts→ad graph. New creation holds
source locks and only INSERTs a brand-new campaign. Creation replay never takes
an existing campaign lock while holding brand/workspace; its checked return is
read-only. This avoids inversion with legacy campaign→workspace writers.

Selected preview rebuilds the protected historical revision content, while
validating current ownership/source/history. Later draft edits leave the selected
content intact. Explicit reselection advances the version; old selection URLs
refuse. Foreign workspace/brand/owner, archive, corrupt snapshots or revoked source
admission deny. Old fixed-source and Fabric selection paths admit only unbound
campaigns; their old rows/choices remain separate and unchanged.

Editor has an explicit synthetic-plan confirmation and source-bound POST form.
Its campaign button waits for verified image bytes AND fields matching saved
content; dirty edits disable it, saving/reopening enables it. Campaign use is
separate from the prototype can_export flag. Private CSRF/small-URLencoded/body/
method/no-store/noindex guards cover new routes. Campaign detail links to the new
choice page for bound campaigns. Read-only renderer reuses brand-ad.js with a
separate exact campaign image path, checked PNG hash/size/dimensions and no visible
save/download/package action. No published-ad or performance claim.

Validation: focused backend/browser checks cover create replay/collision/stale,
explicit confirmation/private HTTP, source/owner/workspace/archive corruption,
historical preview→edit→explicit reselection, stale URL refusal, dirty-editor
button and mobile overflow. Four PostgreSQL races cover simultaneous starts,
competing choices, selection/edit consistency and creation replay versus legacy
campaign/workspace locks. Required latest-head CI must pass before merge.
Provider/budget spies remain untouched. Independent source review found no source,
tenant or lock blocker; its dirty-editor finding was fixed and tested.

Actual SAME private DB received only forward campaigns0011 after backup
preview-before-brand-campaign-20261026T180122Z.sqlite3. All prior column values/rows
preserved, old campaign brand FKs NULL; initial new choice table empty. Standard
migration/type/permissions only. Existing brand attempts/holds/drafts/Google fixture
were not rebound or reset. Normal IAB created campaign3 from brand1 ad
8e17aa42-009a-440a-a9e5-e87f755c9967 revision2, selection1, and opened its site-only
preview. Normal authenticated create replay twice added no campaign/choice.
Independent browser desktop/mobile verified readonly saved content and no visible
download;39 prior application tables' old rows preserved and local ledger unchanged.
Private evidence brand-campaign-live-evidence.json, brand-campaign-iab.png and
brand-campaign-{1440,390}.png. No new AI/media cost, key or production deployment.

Next: replace fixed synthetic campaign parameters with an owned in-site setup for
objective, audience, budget and schedule, while keeping publishing/spend gates
closed. Download/export remains an explicit open product decision.
