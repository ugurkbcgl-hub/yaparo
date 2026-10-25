# ADR-0056: Keep direct adapters after the narrow typed-output comparison

- Status: Accepted for current narrow task; PydanticAI remains experiment-only
- Date: 2026-10-25
- Continues ADR0040/0055 and Y10.

The [isolated comparison](../../experiments/typed-output/README.md) installs
PydanticAI-slim2.61.0 and exact transitive versions in a temporary venv, separate
from product dependencies. Primary tagged metadata/license/testing docs were
reviewed. Fresh Windows pip check/audit passed, with no known vulnerabilities at
the recorded date. CI independently installs/audits/runs the experiment on Linux.

Actual existing direct adapter with mocked HTTP and actual FunctionModel receive
the same3 briefs/13 response cases/3 repetitions. Both then use the application's
domain candidate validator. Normal and optimized runs each complete234 executions
with identical observed outcomes. No live model, SDK extra, account/key lookup,
provider charge or product-route change is involved. Python network guards are
not an OS sandbox; timing paths are not comparable provider performance measures.

Typed output rejects unknown root fields that the current direct adapter ignores.
Other structural/domain rejection cases agree. Both accept a shaped unsupported
claim: neither is factual grounding, safe advertising or output-quality proof.
The comparison does not measure provider behavior or satisfy live quality gates.

Keep the existing direct boundary for this scope; do not add an agent framework
to runtime for a benefit reproducible by a small strict-parser correction. Retain
the pinned, audited experiment as evidence, not blanket rejection of typed tools.
Revisit if a concrete orchestration/output need justifies its dependency footprint.

Next: reject unknown top-level generated-output fields in the existing direct
parser and verify malformed/ambiguous JSON behavior without provider access.
Financial reservations, durable jobs, source/claim validation, human usability and
production provider gates remain open. No paid execution is enabled by this ADR.
