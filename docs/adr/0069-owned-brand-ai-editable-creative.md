# ADR0069 — Editable creative from owned saved brand AI results

Accepted 26 October 2026 for local synthetic composition; default off.

ADR0068 results can now be explicitly selected into a separate BrandAdDraft.
Do not retrofit HostedAdDraft, old fixed Duru trials, Fabric scenes or campaign
choices. LOCAL_BRAND_AD_ENABLED, DEBUG and existing brand-request/result gates
must admit the owner. This workflow has no provider, credential or budget action.

Selection requires two completed/settled results of kinds copy/image belonging
to the same owned nonarchived brand, exact BrandIdentity and source revision.
Each result is rebuilt through brand_generation.read; the selected text key must
exist. A source digest from review is rechecked at creation. Requests may have
different copy/image directions, explicitly preserved in the manifest; there is
no inferred semantic agreement or content approval. The initial profile
brand-saved-ai-overlay-v1 accepts the evaluated768×1376 image only.

workspaces0012 adds protected brand/identity/attempt references, immutable source
manifest/fingerprint, bounded editable fields, revision and append-only history.
The manifest pins both full preparation envelopes, fingerprints, exact input
hashes, selected text, output metadata and costs, original/PNG hashes, actual text
provider and explicitly requested image route/model. It preserves logo metadata,
not a logo binary. No silent source replacement. Brand→source document→ordered
attempts→draft locks preserve the existing graph; repeated creation returns the
edited draft. Creation/history and revision-conditional saves/history are atomic.
No-op saves preserve revision; stale saves refuse. Ownership/archive/allowlist
revocation, corrupt source or mismatched history deny subsequent reads.

Separate owner routes at /workspace/brands/<brand>/ads/ provide saved text/image
selection, review, explicit create, edit/save and private image. Closed forms,
CSRF, small URLencoded intake and private/no-store/noindex headers cover methods,
auth and framework errors. Failed save keeps submitted fields with export closed.
No query or form value can supply a URL, image byte payload or result metadata.

Separate brand-ad.js preserves the legacy renderer. It uses the pinned brand name
(measured and wrapped), initial primary text color and secondary accent, with a
neutral text panel. Fields title60/body100/CTA30 use the existing UTF16/control/
six-digit-color validator. Browser font-fit refuses overflow without truncation.
Only the draft's exact same-origin image path is fetched, with redirects denied,
bounded PNG/signature/hash/decoded-size verification. Invalid bytes disable save
and PNG. PNG export requires unchanged fields matching the saved bootstrap and
no failed save. It uses fixed Canvas2D/system Arial; browser/font differences may
affect pixels. Server length validation is not server-side font-fit proof; a
forged length-valid save may require correction before UI export.

Logo is explicitly not applied. This is a fixed overlay with editable text/color,
not general layer/position editing. No ZIP, format conversion, campaign selection,
publishing, rights/claims approval or production qualification is added.

Evidence:

- New backend/browser checks cover identity/source/owner isolation, a successful
  second owned brand with its own name/palette, manifest/history corruption,
  unsettled output, replay preserving edits, stale saves, protected sources and
  private HTTP/CSRF/intake/method guards. PostgreSQL create/save races require CI.
- Browser normal selection→create→edit→save→reopen→repeat create→PNG passes;
  old-tab fields survive409. A long brand name wraps without viewport overflow.
  A valid PNG with a different hash disables save/export. Provider/budget spies
  remain untouched. Existing fixed draft regressions are exercised separately.
- Actual SAME private preview DB received only forward0012 after backup
  preview-before-brand-ad-20261026T171740Z.sqlite3. Initial new tables empty;
  all old rows preserved, standard migration/2 content types/8 permissions added.
  No protected Google or configured database operation.
- Normal IAB selected request3 text/key slogan and request4 image for brand1
  identity2, created8e17aa42-009a-440a-a9e5-e87f755c9967 and saved CTA
  “Koleksiyonu tanı” as revision2. Readback/history1/2 and pinned sources verified.
  Independent normal Chromium login downloaded actual768×1376 PNG and checked
  lower image pixels exactly against the stored source; desktop/mobile passed.
  IAB download was clicked but its filesystem result was not observed there.
  All37 preexisting non-auth/non-framework tables and the local ledger are
  unchanged after composition. New AI cost USD0. Provider key remains absent.
- Private evidence: brand-ad-live-evidence.json, brand-ad-real-v2.png,
  brand-ad-iab.png and brand-ad-{1440,390}.png. Manual PNG review passed.
  Independent source review found no blocker; required latest-head CI before merge.

Next: saved-only brand creative package with exact PNG, source bytes and pinned
identity/request/result/edit provenance. Preserve this profile/history and all
old campaign choices. Reuse saved outputs without a provider call.
