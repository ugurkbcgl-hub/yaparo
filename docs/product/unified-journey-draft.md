# Unified journey — interaction draft

27 October 2026. Owner requested a clickable local draft before further product
integration. This is a UX proposal under review, not a qualified release or an
accepted promise that all advertised channels/AI/editor capabilities work today.

## Experience contract

One work surface with four visible stages: request → three concepts → advertising
plan → final review. Previously entered information remains available during the
open-tab journey. Back navigation does not start a new campaign or AI request.

1. A short free-text request, optional fictional raster reference and optional
   **Kimlik ve tarz** (identity/style). A person, product, event or business can
   start without owning a formal brand profile. No mandatory brand wizard.
2. Three genuinely different creative directions, not three cosmetic duplicates.
   Select one, edit in a dialog within the same work, ask for a same-direction
   alternative, or see a new trio. Keep earlier choices/edits accessible.
3. Gather goal, audience, region, destination, total media budget and dates after
   creative selection. Recommend channel shares with reasons and an editable
   total of 100%; do not infer effectiveness from region alone or fabricate reach.
4. Show selected content and all material decisions before any future launch.
   Production credits, media budget and service fees stay distinct. Real charges
   and publishing need explicit consent and readiness gates.

The helper is available throughout; direct controls remain equally usable. Desktop
side panel, mobile fixed toggle. Decisions should be visible and reversible;
chat must not silently change spending, selected assets or publishing permission.
Identity/style is an optional user-facing term for this experiment; it does not
rename database brands or discard existing ownership/history contracts.

## What the prototype actually does

`experiments/unified-journey` is an isolated buildless HTML/CSS/JS experiment served
on loopback, normally port8013. Existing Django preview on8002, campaigns, stored
AI results, ledgers and private Google candidate are untouched.

- Three locally drawn SVG compositions and deterministic example titles, not
  AI-generated personalized ads. No remote images/fonts/scripts or dependencies.
- Editable title/body, position/size controls and pointer-drag title preview;
  explicit apply/cancel and bounded edit undo. This is not the full Fabric editor
  integration. It demonstrates the desired return-to-same-work interaction.
- New trio / previous trio preserve matched request context and content edits.
- Optional local PNG/JPEG <=5MB and <=16M pixels via blob preview; no upload,
  provider transmission, durable file or image-generation operation.
- Optional identity name/accent on previews. Tone is recorded as a preference;
  no claim that a model actually applied it.
- Fixed-rule helper responses, visibly identified as a simulation. Arbitrary
  conversational production and semantic brief extraction are NOT implemented.
- Turkey-only geography with geodesic radius1..800km intersected against pinned
  Natural Earth Turkey polygons; offshore/foreign parts removed, outside-land
  centers refused. Approximate country vector/coordinates, not a street map or
  operational platform boundary proof. No GPS, geocoder, tile/CDN request.
- Fourteen researched digital channel families, explicit geo/account/route
  qualifiers. Documented geo candidates selectable; unknown precision disabled0.
  User can deselect or set relative priorities; integer-kuruş shares sum exactly.
  Actual accounts/formats/inventory and enforcement are still unqualified.
- Explicit hypothetical scenario math per channel/total, shared editable CPM/CTR/
  density/repetition. No real platform forecast, market rate, population or unique
  reach. Budget/scope/priority/assumptions update outputs; duration updates daily
  budget only. Never infer which channel performs better from these examples.
- Invalid center/radius/area/budget/assumptions or no chosen candidate refuses a
  fresh summary. All form, map, checkbox and priority changes lock stale review.
  Final snapshot binds clipped geometry, channel shares and scenario assumptions.
- See [Turkey channel catalog and formulas](turkey-channel-catalog-draft.md) and
  experiment third-party notices for sources, qualification gaps and asset hashes.
- Complete plan/review in browser memory. No local/session storage, cookie,
  database write, export, payment, launch button or real campaign creation.
  Refresh/closing loses the draft, explicitly disclosed in the UI.
- Allowlisted assets only, Host check, no-store and connect-src none. No public
  serving, file listing, server file upload or application-secret loading.

## Validation and decisions

Focused browser checks cover selection→edit→alternative→undo→new/previous trio,
plan shares→review,1/800km and invalid boundaries, actual Turkey intersection,
channel selection/priority, conserved kuruş, scenario dependencies, asset hashes,
stale-summary lock including
progress navigation/map clicks, changed-brief history binding, refresh/reset, no outbound
requests, literal handling of markup, mobile overflow/helper, and server allowlist,
Host and POST boundaries. Visual review checks desktop and390px layouts.

Owner feedback is still needed on stage count, amount of guidance, creative card
presentation and the identity/style term. This task does not settle pricing,
refunds, channel efficacy, persistent conversation/data retention or download
availability. User-image consent/rights/scanning, real assistant tool permissions,
cost-aware generation and tenant-safe persistence remain production work.

Next: review the draft with the owner, then map the accepted interaction to existing
owned creative/editor/campaign contracts. Do not wire paid calls or replace the
existing flow before that review. Existing release gates remain mandatory.

## Geography evidence — checked 27 October 2026

- Google Ads help specifies minimum1km, varying country availability, minimum
  privacy/user-area thresholds and approximate location accuracy; Hotel Ads is an
  explicit counterexample to universal campaign support:
  https://support.google.com/google-ads/answer/1722043?hl=en
- Google Ads API system limits specify proximity radius800km /500mi:
  https://developers.google.com/google-ads/api/docs/best-practices/system-limits
- Google proximity mechanism uses a center/radius rather than an address label:
  https://developers.google.com/google-ads/api/docs/targeting/location-targeting
- TikTok's current location help lists country/region/city/district/postal options
  with country/account restrictions; it does not establish point-radius support:
  https://ads.tiktok.com/help/article/location-targeting
- Meta's primary targeting reference was not accessible in this research. Do NOT
  infer unavailable support from that failure. Leave capability unknown pending
  current primary documentation and account-level checks.

These are geo-type capability notes, not a recommendation to buy Google inventory
or a production allocation policy. Strictly local intent must use appropriate
presence settings and verified account/campaign capabilities in real integration;
no fallback to interest-in-area or broader targeting without explicit consent.


Turkey/channel update evidence: six focused checks passed, including actual
80km Edirne circle clipping with no residual outside polygon, foreign center
refusal, user deselection/all-off/priority, scenario budget/CPM/area dependency,
mobile and pinned third-party asset integrity. Independent source review found
no blocker; npm audit reported no vulnerabilities. No new runtime dependency was
added to Django, no paid API was called and no existing private record was read.
