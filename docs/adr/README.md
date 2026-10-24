# Architecture Decision Records

ADRs capture decisions that would be costly or confusing to reverse. Keep proposals separate from accepted decisions and link relevant ADRs from architecture/project docs.

## Workflow

1. Create the next numbered file from `0000-template.md`.
2. Describe the context, decision drivers, options, consequences, and status.
3. Use `Proposed` while review or user input is pending. Change to `Accepted` only after the authorized decision is made; record the date and owner.
4. Supersede an accepted ADR with a new ADR; do not erase the history.
5. Keep product scope, provider, hosting, cost, and data-handling changes visible for user review.

## Decisions

- [0041 — Bounded Fabric and versioned multi-brand identity](0041-bounded-fabric-and-brand-identity.md) — Accepted for local synthetic implementation

- [0040 — Yaparo-owned core and staged open-source adoption](0040-owned-core-and-open-source-adoption.md) — Accepted strategy/priority; new components remain evaluation candidates

- [0001 — Modular monolith boundaries](0001-modular-monolith.md) — Accepted
- [0002 — Application stack and local environment](0002-application-stack-and-local-environment.md) — Accepted
- [0003 — Heroku Phase 0 staging](0003-heroku-phase-0-staging.md) — Accepted
- [0004 — Self-service advertising autopilot](0004-self-service-advertising-autopilot.md) — Accepted
- [0005 — Türkiye-first advertising platform for all advertiser types](0005-turkey-first-advertising-platform.md) — Accepted
- [0006 — Campaign brief ownership and first data boundary](0006-campaign-brief-boundary.md) — Accepted
- [0007 — Workspace ownership and campaign data lifecycle](0007-workspace-ownership-and-retention.md) — Accepted
- [0008 — First synthetic campaign workflow and channel candidate](0008-first-mvp-google-search-leads.md) — Accepted
- [0009 — Asset intake and processing boundary](0009-asset-intake-processing-boundary.md) — Accepted for contract design and synthetic-only local development
- [0010 — Synthetic action policy contract](0010-synthetic-action-policy-contract.md) — Accepted for local synthetic-data development only
- [0011 — Synthetic policy-evidence metadata](0011-synthetic-policy-evidence-metadata.md) — Accepted for local synthetic-data development only
- [0012 — Synthetic policy version and rule identifiers](0012-synthetic-policy-identifiers.md) — Accepted for local synthetic-data development only
- [0013 — Workspace synthetic creative versions](0013-workspace-synthetic-creative-versions.md) — Accepted for local synthetic-data development only
- [0014 — Workspace creative review preference](0014-workspace-creative-preference.md) — Accepted for local synthetic-data development only
- [0015 — Authenticated campaign report without a data source](0015-authenticated-campaign-report-empty-state.md) — Accepted for local synthetic-data development only
- [0016 — Provider-neutral campaign report metric contract](0016-campaign-report-metric-contract.md) — Accepted for local synthetic-data development only
- [0017 — Provider-neutral campaign report metric semantics](0017-campaign-report-metric-semantics.md) — Accepted for local design and synthetic-data development only
- [0018 — Explicit unavailable report metric reasons](0018-explicit-unavailable-report-metric-reasons.md) — Accepted for local synthetic-data development only
- [0019 — Report observation coverage and retrieval metadata](0019-report-observation-coverage.md) — Accepted for local synthetic-data development only
- [0020 — Owner editing for synthetic creative drafts](0020-workspace-synthetic-creative-editing.md) — Accepted for local synthetic-data development only
- [0021 — Owner-scoped synthetic publishing rehearsal](0021-workspace-publishing-rehearsal.md) — Accepted for local synthetic-data development only
- [Google Search report metric mapping](../product/google-search-report-metric-mapping.md) — Official-source research only; no API access or connection

- [0028 — Read-only owner campaign stage overview](0028-campaign-stage-overview.md) — Accepted for local synthetic development only

- [0029 — Durable connector identity/generations](0029-durable-connector-identity-generations.md) — Accepted for isolated synthetic validation only

- [0030 — Generation-bound synthetic authorization attempts](0030-synthetic-generation-bound-authorization-attempts.md) — Accepted for isolated rehearsal only

- [0031 — Scoped Google TEST candidate boundary](0031-scoped-google-test-candidate-boundary.md) — Accepted for mocked adapter validation only

- [0042 — Pinned brand palette and saved creative history](0042-brand-palette-and-creative-history.md)
