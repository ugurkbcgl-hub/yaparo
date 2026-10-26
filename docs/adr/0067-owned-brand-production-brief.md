# ADR0067 — Owned versioned brand production brief

Accepted 26 October 2026 for local synthetic preparation, not hosted execution.

The owner can prepare a production request from a brand page. It pins an exact
BrandIdentity, saved BrandCreativeRevision, hero/logo material version metadata
and a user-entered synthetic brief. Brief fields are description, audience,
objective and requested copy/image deliverable, with fixed tr-TR language. These
are intent metadata, not implemented provider capabilities or campaign promises.

BrandProductionRequest stores an immutable per-brand request version, UUID,
protected brand/identity/source-revision FKs, brief, complete JSON envelope and
fingerprint. The envelope includes actual palette/tone/tagline/logo identity fields,
source scene digest and material IDs/versions/identity/catalog digests. Catalog
digests are metadata, not binary checks, malware scans or rights proof. Historical
material identity versions are explicit rather than silently labelled as current.
Old fixed Duru hosted jobs/ad drafts/selection/package records are not rebound.

New creation requires fresh active ownership, nonarchived brand, current identity,
current source revision and expected per-brand request version. Sources must have
the existing bound-material contract and matching identity. Brand→document locks
reuse the editor graph. Concurrent expected-version submissions can append only
one record. Exact UUID replay with identical context/brief returns the original;
changed/reused context refuses. Later identity/document edits preserve the original
request through its protected revision and identity, while new requests must use
the current identity. Readback locks/rebuilds the pinned envelope and fingerprint;
ownership/archive/corruption refuse. Append-only application APIs are not an SQL
tamper-proof vault. Referenced source/brand deletion is protected; archiving still
denies access without deleting records.

Separate default-off LOCAL_BRAND_PRODUCTION_BRIEF_ENABLED plus DEBUG gates this
metadata-only UI/service. Owner forms accept a current source option, bounded UTF16
description1200/audience200, closed objective/deliverable choices and hidden version/
UUID fields. Description supports paragraph whitespace; audience is single-line.
Other controls/lone surrogates/unknown fields/duplicate POST values refuse. Only
small URLencoded bodies (16KiB for this prefix) are parsed before CSRF. Private/
no-store/noindex headers cover auth/errors/readonly detail/method refusal. User
text is template-escaped; sensitive description/audience fields are masked in Django
error reports. Stale form text remains on409 with an explicit fresh-form link in a
separate tab. Current source choices can make HTTP replay after source changes409;
this does not weaken service-level exact replay or overwrite newer records.

The provider-neutral envelope has execution.authorized=False, provider=None and
zero cost ceiling. A no-I/O mock receipt only checks request/fingerprint correlation;
strict bool/int checks reject permission/cost substitutions. Owned acceptance
reconstructs stored sources before checking that receipt. No model, generated copy,
image, key, queue, reservation, result persistence, publishing or spend is enabled.
UI explicitly says the request is saved and AI content has not yet been produced.

Migration workspaces0010 adds one request table; existing source/AI/campaign history
is unchanged.18 focused new/legacy context/browser tests passed (17 pass/1 PG skip).
They cover two brands, pinned old identity/revision after edits, replay/stale source/
version, source protection, corruption/archive/foreign ownership, strict brief and
mock receipt, HTTP escaping/CSRF/intake/scope and browser stale preservation/two
request versions/mobile overflow. The new PostgreSQL competing-version test must
pass required CI. Existing provider/ledger entry points are forbidden spies. Ruff,
format/drift/diff and independent review passed after strictness and stale-form UX
corrections. This is not hosted model quality or production-readiness evidence.

Actual known preview DB received only forward0010 after a consistent backup; prior
rows preserved and new table initially empty. Duru brand1 was already identity2,
but its old designs were unbound. Normal in-app UI created a NEW bound square source
4b2de5c5-17bd-4835-a928-25f7a0588efc, then saved production request
2b55f540-7f83-4b07-aec4-0b25d975a22d version1 against identity2/source revision1.
Readback verified palette/brief/scene fingerprint and two material bindings.
38 prior non-auth tables' old rows preserved; only standard migration/permissions,
new source/catalog/binding rows and one request were added. Existing paid trial,
historical hold, campaign selections and protected Google fixture untouched.
Private evidence:brand-production-brief-evidence.json/brand-production-brief-iab.png.
No actual provider call or new AI cost.

Next: build the separate brand-bound execution/result adapter rehearsal from an
owned request, with mocked transport and source revalidation before/after dispatch.
Do not pass the current saved brief to a paid provider until the appropriate
execution/data/financial gates are explicitly implemented and reviewed.
