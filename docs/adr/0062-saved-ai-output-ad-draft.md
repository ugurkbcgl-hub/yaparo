# ADR-0062: Independent editable draft from saved AI outputs

- Status: Accepted local fictional-data slice, default off
- Date:2026-10-26
- Continues ADR0060/0061; no new generation, spend or publishing authority.

The owner may select one saved Duru text candidate and explicitly create a new
composition using the owned saved AI image. Keep this as an independent
HostedAdDraft, not a BrandCreativeDocument, palette material or inferred brand
identity. The existing Fabric scene v1–v4, material, campaign and selection
contracts remain unchanged. The new bounded Canvas2D profile has a fixed Duru
wordmark/layout/font and the evaluated768×1376 portrait. It permits title, body,
CTA and text-color edits, save/reopen and PNG export, without an AI request.

Admission requires a separate default-off LOCAL_HOSTED_AD_DRAFT_ENABLED plus the
existing DEBUG/image/text workspace admission and fresh active ownership. It does
not require or load a provider credential. Source lookup accepts no client job,
brand, file, URL or image ID. Revalidate both completed/settled jobs, checked text
and PNG at each create/read/save. The immutable manifest binds workspace/owner,
both job IDs/profiles/source hashes/model-route/cost metadata, the text batch and
selected candidate, original/PNG hashes, dimensions and normalization tool.
Requested image model/route stay labelled as such, not returned provider identity.

Commit draft and initial history atomically. Uniqueness over text/image/candidate
makes repeated creation return the same edited draft, not reseed it. Owner and
source references use PROTECT. Writes lock workspace→text/image jobs→draft and
use expected revision/source fingerprint with CAS. Changed saves append a history
snapshot in the same transaction; stale writes refuse, no-op saves do not append.
History is append-only through application APIs, not an SQL tamper-proof vault.
There is no new delete/restore or automatic campaign selection/publishing action.

HTML forms are closed, single-valued, CSRF-protected and bounded before body parsing.
Private/no-store/noindex headers cover auth/CSRF/framework errors and private image
reads. Bootstrap uses json_script; editable text is never interpreted as HTML.
Text bounds use UTF16 units (title60/body100/CTA30), no controls/newlines/lone
surrogates; only six-digit colors. Server validation is semantic/length validation,
not font pixel-fit proof. The client measures wrap/overflow, never truncates, and
refuses save/export until corrected. A forged length-valid direct save can still
need such correction before UI export; a general server font/layout engine is open.

Only the draft-bound private image route supplies the image. The browser checks
same-origin fixed path, no redirects, bounded PNG MIME/signature, SHA256 and decoded
dimensions before save/export. No fallback illustration. Save failures preserve
submitted fields and leave the current saved revision intact. PNG is enabled only
when displayed fields match the saved bootstrap and no save error exists; export
names the saved revision, not an uncommitted edit. Its canvas keeps exact source
dimensions regardless of display size. Wrapping preserves words where they fit;
long words split without dropping characters. Download pixels below the text panel
remain the source image's pixels. This is a fixed layout, not general layer editing.

Evidence:236 related local tests (227 passed/9 PostgreSQL-only skips), including
two browser tests for edit/reopen, old-tab refusal, repeated creation, exact PNG
dimensions/pixels and denied/changed private images. Provider and ledger entry
points are forbidden by spies. Static assets were collected before browser QA.
Ruff/format/migration drift/diff passed. Independent source review found no blocker;
required actual PostgreSQL concurrent create/save and full CI must pass before merge.

Only known private preview received workspaces0008 after a fresh backup. All prior
rows were compared unchanged; additions were two tables, one migration, two content
types and eight permissions. Actual in-app browser created draft
fa426f70-5e12-4f5c-9b83-f40a72ac1c90, then changed the CTA and saved revision2.
History1/2 and source fingerprint were independently read from a consistent backup.
The in-app download event did not report a path; independent Chromium successfully
downloaded the actual saved768×1376 PNG, whose content was visually reviewed.
Do not claim the in-app download-path observation succeeded. Actual source image,
text and35 preexisting non-auth/session tables compared unchanged; the local ledger
also stayed identical. New AI costUSD0. The preview was restarted without provider
credentials; existing test login used protected local credentials and normal UI.
No configured database, protected Google candidate, infrastructure or deployment.

Next: introduce a separate versioned layout profile with explicit square/portrait
choices and exact-size PNG output. Preserve this profile and existing draft/source
revisions; do not silently reinterpret their layout or infer a brand binding.
