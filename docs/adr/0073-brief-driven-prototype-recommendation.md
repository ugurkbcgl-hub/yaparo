# ADR-0073: Brief-driven recommendation in the local prototype

Status: Accepted for local synthetic development, 29 October 2026.

The owner removed the repeated planning classification questions. The plan must
use the owned first-stage answers together with explicit geography, dates and
media budget. This supersedes the prototype's requirement to manually choose
legacy business/sector/audience classes in step2; ADR0072 stage order remains.

## Decision

`OutcomeContract.analyze(snapshot)` validates and binds the exact first-stage
snapshot. It exposes literal subject, purpose, outcome, audience and destination,
explicit risks and known/unknown facts. It never infers a sector or old business/
audience taxonomy from free text. Missing risk is not_declared, not a declaration
of normal/approved scope. Forced fundraising and other explicit risks coexist.

`Decision.evaluateOwned` re-derives these fields internally and ignores retired
controls. Only exact supported outcome projections proceed to paid demo planning;
unsupported goals and nonpaid/undecided usage refuse. Explicit radius geometry,
dates, budget and numerical bounds validate before authored forecasts are built.

Known objective, geographic scale and budget rules contribute to the local
starting rank. Unknown business/sector/platform-audience/measurement/creative
dimensions are omitted rather than assigned invented classes or scores. The rank
normalizes points over the known weight and records coverage separately (normally
40/100 from objective25, geography10 and budget5). This partial rank is not the
original complete expert score, confidence, success probability or market evidence.
The old evaluate entry point and complete benchmark remain unchanged for legacy.

An explicitly selected business audience may condition the existing authored
forecast scenario; this remains fictional cost/reach data, not a verified platform
audience or live prediction. Missing measurement, tracking and catalogs remain
unverified; retired readiness controls cannot qualify them. Policy/risk refusal,
asset/minimum/channel/shared caps, reserve and downstream invalidation remain.
All actual account, data, generation, financial and publishing gates stay closed.

## Presentation and consequences

Step2 has no repeated classification/audience/measurement form. The declared
audience is summarized with an edit link back to stage1. Commercial economics is
separately optional. A read-only explanation lists the first-stage basis and
unverified readiness; public FX is not an ad forecast and its closed local context
does not receive the raw first-stage snapshot. No new service/provider is added.

Legacy hidden IDs are compatibility-only, disabled and ignored by the owned
adapter. Owned plan-context metadata is v2, marked first_stage_analysis and never
verified. No durable app-data migration or production inference is authorized.
Moving this into the application requires a separately versioned owned contract,
real provider/account evidence and existing release/permission/spend gates.

Checks cover46 analysis paths, exact signatures, unknown classes, explicit risks,
hidden-control injection, radius/date/usage refusal, caps/reserve and unchanged
legacy benchmarks, plus first-stage/plan/browser and desktop/mobile checks.
