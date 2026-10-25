# ADR-0052: Explicit campaign design reference

- Status: Accepted for local synthetic implementation
- Date: 2026-10-25
- Continues Y07 and ADR-0042/0047/0051.

Add a default-off/DEBUG local campaign → brand/saved-design choice. Only bound
documents in the campaign's SAME owned workspace qualify. No existing draft is
backfilled. This is an informational visual planning reference: existing synthetic
Google Search brand/text, approval fingerprints, dispatch/stop and financial
boundaries are unchanged. Selection is not publication approval or Google image
eligibility. Full brand-aware generation/publishing integration remains open.

CampaignDesignChoice is append-only through the application API, with unique
request UUID and (draft,version). Its PROTECT FK pins an immutable creative-history
snapshot, which preserves source material references through the document. Later
document edits do not move the choice. The owner must explicitly select the new
saved revision; stale forms deny. Exact replay returns its original record even
after later choices, without resetting the latest choice. Explicit draft removal
cascades local choice rows only; document/history remain. This is not a SQL vault,
permanent advertising consent/no-resend ledger or customer erasure policy.

Serialize choices with a draft-only FOR UPDATE OF self. Source snapshots are
immutable; source brand/workspace/document reads do not add locks to the legacy
campaign/brand graph. Before INSERT validate normal typed candidate fields; then
the internal bulk insert uses a scoped snapshot-ID Subquery rechecking active
owner, workspace, unarchived brand and expected current document revision at the
write boundary. No qualifying source produces NULL and the non-null FK rejects
the entire nested transaction. Existing campaign lock behavior is not weakened.
PostgreSQL tests cover same-request replay, competing choices, a committed source
edit before INSERT and concurrency with the existing campaign-edit service.

The private chooser lists up to20 valid current documents with brand/title/format
and saved revision. Campaign summary shows the pinned revision/title and warns
when a later document revision exists. Archived/foreign current choice is shown
as unavailable, never silently replaced by older valid history. Opening the live
editor is labelled as current work; a numeric same-owner/workspace campaign hint
adds a fixed internal return link. It is not a free redirect or authority input.

POST requires CSRF and exact hidden fields. Pre-CSRF middleware rejects multipart,
oversized/unknown bodies before parsing, including leading-zero routes. Chooser
responses/errors are private/no-store/noindex. Same-origin referrer policy keeps
normal form Origin/CSRF behavior while suppressing cross-origin referrer. Campaign
detail is no-store. No file, URL, creative proof, provider or payment input exists.

Migration campaigns0009 creates only the sidecar/history table; no prior rows,
brand identities, scenes, TEST records or tokens are rewritten. Local preview
rollout requires its own private backup and exact migration plan verification.
Normal source flag remains False; actual account/customer/production gates stay.

Verification: owner/workspace/active/archive/type boundaries, immutable snapshot
and removal protection, request replay, stale source/choice, rollback and final
owner/revision checks; HTTP CSRF/intake/private errors and return-hint scope; real
browser choose → edit → return → explicit reselect, stale-tab refusal and mobile
layout. Actual PostgreSQL race tests must pass required CI before merge.

Next: read-only visual preview of the campaign's pinned saved snapshot, with
exports tied to that exact revision rather than silently using the live document.
