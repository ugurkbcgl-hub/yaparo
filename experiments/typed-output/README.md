# Isolated typed-output comparison

25 October2026. Y10 structural experiment; not a product integration.

ADR0056/PR352 recorded the original13-case baseline below. ADR0057 extends the
CURRENT runner to16 cases after the owned strict-parser correction:288 runs per
normal/optimized mode,576 total. Unknown-root fields now reject in both paths.
New duplicate-root and duplicate-variant-key cases reject in direct parsing but
are accepted by the typed JSON decoder in these controlled fixtures; a non-object
root rejects in both. Application claim checks are still separate. The current
runner expects the corrected direct behavior; the baseline is historical.

Run `run.py` with the existing development Python (which supplies pip-audit).
The runner creates and removes its own temporary virtual environment, installs
only exact pinned binary wheels from requirements.txt, checks dependencies and
audits that environment. It runs compare.py normally and with `-O`, requiring
identical observed outcomes. Product requirements and the active venv are unchanged.
Package installation and vulnerability lookup use network; comparison calls do not.

## Pinned candidate and primary evidence

- [PydanticAI v2.61.0 release](https://github.com/pydantic/pydantic-ai/releases/tag/v2.61.0)
  was the stable tag selected during this review; no automatic upgrade is used.
- [Tagged MIT license](https://github.com/pydantic/pydantic-ai/blob/v2.61.0/LICENSE)
  and [slim package metadata](https://github.com/pydantic/pydantic-ai/blob/v2.61.0/pydantic_ai_slim/pyproject.toml)
  were inspected: Python>=3.11 supports this Python3.13 experiment. No provider
  extras, full agent distribution, hosted Logfire or SDK are installed.
- [Tagged testing guidance](https://github.com/pydantic/pydantic-ai/blob/v2.61.0/docs/testing.md)
  describes FunctionModel and ALLOW_MODEL_REQUESTS=False for deterministic tests;
  such tests do not measure model quality.

The resolved experiment pins Pydantic2.14.1 and18 distributions including pip.
Fresh Windows setup: pip check passed; pip-audit found no known vulnerabilities
at this date. This is not a comprehensive supply-chain, transitive-license or
production safety certification. Linux is also exercised by required CI.

## Original baseline: equal fixtures, explicit limits

Use the SAME three existing synthetic benchmark briefs and SAME13 controlled
response cases for both paths, three repetitions per case. Direct path executes
the existing OpenRouter adapter with its HTTP connection replaced by a mock and
an explicit dummy credential. Typed path executes actual FunctionModel with a
strict extra-forbid output schema, then the SAME application result validator.
No adapter allowlist/product task profile is promoted or impersonated.

Comparison-phase DNS, socket connections, connect_ex, datagrams and asyncio
transport creation are blocked. Provider model requests are disabled; tracing is
off. Windows' internal asyncio socketpair is initialized before the comparison
guard. This is a Python test guard, NOT operating-system network isolation.
No secret file/account/balance is read. No real model request or provider charge.

Each normal/optimized run completed234 path executions;468 total in the fresh
runner. Only one local function/mock response per execution, no retry/fan-out.
Observed acceptance and expected values are separate; explicit error checks
remain active under `-O`. Printed rows contain brief/case IDs, outcome and timings,
not prompt/response bodies, credentials or customer data.

| Controlled response | Direct | Typed + domain checks |
|---|---|---|
| Valid variants |Accept|Accept|
| Invalid JSON / missing variants |Reject|Reject|
| Unknown root field |Ignored; variants accepted|Reject|
| Extra variant field / wrong type / excessive length |Reject|Reject|
| Blank or repeated angle / repeated key / empty or excessive list |Reject|Reject|
| Structurally valid unsupported guarantee |Accept-shaped|Accept-shaped|

Across39 brief/case pairs, direct accepted9 and typed accepted6; all three
differences are the unknown-root-field case. Every result stays non-publishable.
The unsupported guarantee demonstrates that both need separate source/claim
validation; accepted-shaped is NOT a quality/safety pass. No human quality scores,
real provider reliability, usage accounting or legal clearance were measured.
Timings include different setup paths (Agent versus mock HTTP) and are explicitly
NOT a fair adapter/provider latency comparison or performance SLA.

## Decision and maintenance

Retain the current direct adapter in the product. Do not adopt PydanticAI as a
runtime dependency for this narrow parsing task: the demonstrated extra-field
benefit has now been implemented with a smaller owned boundary correction. The isolated
experiment stays as reproducible evidence; larger orchestration needs may justify
a later comparison. The corrected direct boundary and extended ambiguity regressions are recorded in
ADR0057. Candidate claim grounding remains separate.

Upgrades require an explicit requirements/guard version change, fresh dependency
and license review, audit and identical-fixture rerun. Rollback is removing the
experiment/CI step; no database, provider, credential or product dependency changed.
