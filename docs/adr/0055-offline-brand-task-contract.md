# ADR-0055: Offline brand-bound copy task contract

- Status: Accepted local offline contract; hosted execution is not enabled
- Date: 2026-10-25
- Continues ADR0040/0052 and delivery-plan Y09.

## Decision

Keep the existing provider-neutral CreativeGenerationRequest/Result and validators.
Add a separate `brand-copy-candidate-v1` profile and versioned frozen task/result
envelopes. Do not install a model/typed-output SDK, change providers, configure
credentials or expose a new product/API route. Only synthetic-template-v1 is an
allowed adapter in this initial offline profile. No external API is called.

An owner-scoped factory reads the campaign's explicitly selected saved snapshot.
The immutable context includes campaign/selection/snapshot IDs, workspace/brand,
identity version, document/revision, selection version, identity/scene digests and
the exact hero/logo material IDs, versions and metadata catalog digests. Material
catalog digests are not binary hashes, scan evidence or rights proof. Actual tone,
palette, tagline and logo identity fields are typed immutable task input and must
match the pinned identity digest. Source labels are not factual/legal clearance.

The copy brief uses only the existing fixed synthetic brand fixture facts. It does
not silently import the legacy Search campaign's separate brand/brief or editable
scene text. Original campaign/design/source records are unchanged. A task ID and
canonical request fingerprint bind the entire envelope, including brief, profile,
adapter allowlist and budget fields. This digest is correlation/integrity data,
not a signature, credential or permission proof.

At acceptance, reconstruct the entire expected request from the currently owned
selection using the same task ID. Reject a different fingerprint before reusing
the existing candidate-shape validator. This rejects cross-campaign same-source
replay, caller-replaced/rehashed brief, reselection, transfer/archive and source
context mismatches. Later live document edits do not change the pinned snapshot;
reselection is explicit. General manually built dataclasses are not owned authority.
These read checks do not provide database-level immutability or perpetual access.

## Result, budget and execution boundaries

Result schema1 supports candidate/failed/uncertain with task ID, request fingerprint
and adapter identity. Only candidate can contain shaped creative variants; failed
or uncertain cannot smuggle candidate copy. Unknown versions/states, wrong task,
fingerprint, adapter, generator ID or reported cost refuse. Structural validity is
not factual grounding, brand quality, policy approval or publication permission.
Every result remains review-required and non-publishable.

The initial profile allows only a zero micro-USD ceiling/reported cost and no
reservation ID. Nonzero budgets, fabricated reservations and other adapters reject.
The envelope never grants execution authorization. This models the fields and
denial boundary; it does NOT reserve money, reconcile provider usage, implement a
durable queue/attempt/retry ledger or guarantee exactly-once execution. Those
execution/accounting gates remain for later Y09/Y13 work before paid dispatch.

## Evidence and remaining work

46 offline/new-context/existing-gateway tests passed. Coverage includes immutable
identity/source/task correlation, old snapshot after live edit, reselection,
foreign/same-owner-other-workspace/archive/owner-transfer/flag refusal, unsupported
schema/adapter/cost and failed/uncertain shapes. Review found a missing campaign
binding; campaign/selection/snapshot IDs and full factory revalidation resolved it,
with same-source cross-campaign and replaced-brief regressions. Ruff/format,
migration drift and diff checks passed. Required PR CI is checked separately.

Next Y10 preparation: compare the existing direct adapter boundary with a pinned
typed-output library using the SAME offline synthetic suite; inspect maintenance,
license and compatibility before choosing/installing anything. No live evaluation,
provider promotion, quality/safety claim or production gate is implied here.
