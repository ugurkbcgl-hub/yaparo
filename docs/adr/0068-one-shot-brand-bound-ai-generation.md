# ADR0068 — One-shot brand-bound synthetic AI generation

Accepted 26 October 2026 for local, separately reviewed synthetic evaluation only.

ADR0067's saved request remains an unauthorized zero-cost preparation envelope.
Separate default-off LOCAL_BRAND_AI_ENABLED and an exact request UUID→fingerprint
operator allowlist admit only reviewed synthetic content. Existing DEBUG/owner/
loopback/private-form boundaries still apply. A user-entered brief or checkbox
does not admit arbitrary customer data or authorize paid production generation.

BrandGenerationAttempt (workspaces0011) has one protected intent per request.
It binds request fingerprint, exact provider input hash and copy/image kind.
Brand/source ownership and pinned history are revalidated before and after work;
brand→document locking follows the existing graph. Intent commits before budget
reservation and provider I/O. Conditional state transitions require exactly one
matching row. Concurrent/repeated clicks cannot dispatch a second call. Failure,
timeout, financial uncertainty or late revocation retains the intent and forbids
automatic retry; no claim of exactly-once delivery by an external provider.

Text uses the existing gateway with actual pinned brand name, palette, tone,
tagline, description, objective and audience. The brand adapter alone allows1024
output tokens; old fixed trials retain512. Image direction uses description,
brand name, palette and tone with a fixed vertical9:16 profile, no text/logo/people
and clear upper-third space. Audience/objective are stored context, not image
targeting controls. Source pixels and logo binaries are NOT supplied to either
provider. Material bindings prove context metadata, not visual reproduction.

Existing ZDR/data-collection-denial adapters remain; image has pinned requested
Google Vertex route/no fallback. Requested image model/route labels are not
independently returned identity evidence. Existing shared USD16 evaluation cap,
verified provider hard-cap assertion, text USD0.01/image USD0.10 per-call ceilings
and local reservation ledger apply. No credit purchase or account balance check.

Bounded text variants/usage/cost or original+normalized image bytes/hashes/size/
dimensions are captured before financial settlement. Provider image extension
is checked against detected bytes, then its MIME type goes to the normalizer.
Completed readback rebuilds input/source bindings, validates cost/reservation,
text usage/shape or exact original→PNG conversion. Private image GET and result
pages deny foreign/corrupt/unsettled output; POST requires CSRF/fingerprint and
closed small URLencoded form. Error records contain bounded stage/category only.

Actual evaluation on the same private preview DB:

- Request1 copy reached HTTP200 but finish_reason=length at512 tokens. Request2
  image reached HTTP200/complete but the initial app confused extension and MIME.
  Both attempts remain unverified/held with no saved output. Provider logs showed
  rounded charges USD0.000305 and USD0.0336, respectively. No raw response/receipt
  survived for precise reconciliation; these are not zero-cost failures. No reset,
  retry of the old requests or ad hoc release of their holds was performed.
- After correcting the adapter and tests, NEW request3
  dd955529-bdd0-43d5-bc32-05f3eac71ca9 returned3 Turkish variants via GPT-6 Luna/
  Azure,513 input/1010 output tokens, USD0.00055630. NEW request4
  78885b7c-0412-4ce9-b8c6-debc5a5cd61d returned a768×1376 JPEG (128201 bytes),
  normalized PNG854996 bytes, USD0.03364200. Both are completed/settled and bind
  brand1 identity2/source4b2de5c5-17bd-4835-a928-25f7a0588efc revision1.
- Successful cost total USD0.03419830. Local cumulative settled spent
  USD0.22943485, unresolved holds USD0.10170650 including historical0.00078075.
  This is local bookkeeping, not account balance or a complete settled bill.
- Normal in-app browser generated and reopened both results. Manual review found
  three short Turkish variants and two cups in blue/terracotta with natural light,
  no text/logo, clear upper space. This is smoke evidence, not a quality benchmark,
  colorimetric/rights/claims guarantee or reproduction of supplied products.
- Forward0011 followed consistent backup preview-before-brand-ai-20261026T163458Z.sqlite3.
  All old rows across36 prior non-auth/non-framework tables are preserved; new
  requests/attempts were added. Old fixed trials/drafts/campaign/Google fixture
  were not rebound. Readback after restart WITHOUT provider key/hard-cap assertion
  still shows saved results. Private evidence brand-ai-live-evidence.json,
  brand-ai-image-iab.png and brand-bound-real-image.png stays outside Git.

Focused local checks cover successful/repeated intent, reservation failure,
timeout, captured settlement failure, late revocation, invalid usage/cost,
conditional transition failure, corrupt cap/image, JPEG/PNG extension contract,
foreign/private HTTP, method/intake/CSRF/fingerprint, adapter headroom and normal
browser generation/reload/repeated POST/mobile. PostgreSQL competing-click check
must pass required CI. Independent source re-review found no blocker.

Next: compose these owned saved brand outputs into an explicitly selected,
identity-pinned editable creative with immutable source/cost provenance, without
another provider call. Separately reconcile uncertain historical billing using
durable exact receipts before allowing retries. General jobs/queue, arbitrary
uploads, production provider qualification and live advertising remain gated.
