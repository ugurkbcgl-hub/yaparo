# AI provider evaluation and current direction

> **Explicit local apply (2026-10-26):** [ADR-0059](docs/adr/0059-explicit-offline-copy-application.md)
> adds a separate default-off action applying chosen deterministic template text
> fields as a new design revision, with source/candidate/current-revision guards.
> It does not call a model, truncate text, reselect the campaign or grant provider
> spend/publication authority. Generic save history is not a generation audit.


> **Local preview (2026-10-26):** [ADR-0058](docs/adr/0058-local-brand-copy-preview.md)
> adds a default-off/DEBUG owner-scoped page for three deterministic template
> candidates through the bound task contract. No hosted adapter, key, cost or
> real model is used. Candidates are not saved/applied and no live-quality gate
> is claimed; hosted/provider readiness remains separate.


> **Strict response update (2026-10-25):** [ADR-0057](docs/adr/0057-strict-provider-json.md)
> adds shared bounded/duplicate-safe JSON and exact inner candidate fields across
> the three existing adapters.53 offline gateway/context checks passed. The extended
> isolated comparison now runs288 cases per normal/-O mode. No provider call,
> credential change, model selection or claim-safety approval occurred.


> **Typed-output comparison (2026-10-25):** [ADR-0056](docs/adr/0056-typed-output-offline-comparison.md)
> records a pinned isolated PydanticAI experiment. Controlled normal/-O runs each
> completed234 executions without model access. Retain the direct runtime boundary;
> fix its ignored unknown-root fields next. Both paths accepted a shaped unsupported
> claim, so this is parsing evidence, not provider quality or grounding approval.


> **Offline contract update (2026-10-25):** [ADR-0055](docs/adr/0055-offline-brand-task-contract.md)
> adds a brand/source/version-bound task/result envelope over the existing gateway.
> The initial profile permits only the deterministic synthetic-template adapter,
> zero cost and no reservation/dispatch authority. It pins the selected campaign
> snapshot and reconstructs the request before acceptance. No provider/SDK/key,
> live API call, account balance check or production selection occurred. Real
> reservation/usage reconciliation, durable jobs and provider quality remain open.


> **Strategy update (2026-10-23):** [ADR-0040](docs/adr/0040-owned-core-and-open-source-adoption.md)
> and the [master plan](docs/product/yaparo-open-source-master-plan.md) now govern
> provider evolution. Keep task/capability profiles, provenance, cost and data
> eligibility in Yaparo; compare a typed-output library with existing direct
> adapters before adopting it. New model releases require measured quality,
> permissions/cost review and reversible promotion. Core editing must remain
> usable without AI. No new model/provider call, package installation or
> production selection occurred during this research.

> **Current recommendation (2026-10-03):** Do not bind GrowthTwin to Ollama,
> a workstation GPU, or a single provider. Use the application-owned,
> provider-neutral gateway to route text, image, video, and asset-analysis
> tasks to separately replaceable hosted APIs. Compare OpenAI, Gemini, and
> Anthropic for text; Google and OpenAI for images and short video. This is a
> synthetic-evaluation shortlist, not a production provider selection or
> permission to incur API charges. See the [provider-combination strategy](docs/product/ai-provider-strategy.md)
> for task routing, data conditions, evidence, and gates.

The existing website still uses deterministic templates. No provider API is
connected to a product route. The local Ollama adapter is optional for
developer experiments only; recent local candidates failed the small
synthetic creative gate. Future provider work must start with synthetic data,
an explicit spend cap, and separate review of the provider's current terms.

## Architecture recommendation

- Use a server-side task router over independent provider adapters; do not
  expose provider SDKs, model names, or credentials to product views.
- Select one permitted provider per task based on measured quality, accepted
  result cost, latency, availability, and the request's data class. Do not
  fan out every advertiser input to multiple providers by default.
- Use deterministic claim/source rules as authority. A second model can
  identify possible issues but cannot prove a claim true or clear it for
  publication.
- Preserve the historical experiments below as evidence, not as vendor
  rankings. Their single-run results are directional only.

This is a development-only comparison. Free access, quotas, model lists, and terms can change. No provider has been selected for production. The project goal is now a cross-industry advertising campaign autopilot, so the dental-clinic examples below are useful safety probes but do not represent the full product workload or establish general model quality.

| Option | Best initial use | Limits and caution |
|---|---|---|
| NVIDIA Build / NIM | Compare hosted chat, reasoning, coding, and embedding models without managing GPUs | Free endpoints are trial access for development/evaluation, not production. Model-specific limits depend on account/model and live traffic. The user confirmed the exposed key was replaced; keep the replacement in a local secret store and never paste or commit it. |
| Ollama with a small open-weight model | Private local baseline for prompt experiments using synthetic data; no provider inference charge | Quality and speed depend on model, context length, VRAM and RAM. A Qwen3 4B download is about 2.5 GB, but runtime memory is higher; begin with a small model and measure. Check the exact model license. |
| Gemini Developer API free tier | Optional second hosted quality comparison | Free limits are model/project-specific. Google says free-tier content may be used to improve its products; do not send private advertiser or customer data. |
| Groq free plan | Optional fast hosted text comparison | Model-specific RPM/RPD/token limits are shown in the account and can change; use only synthetic development data. |
| OpenRouter free models | Optional quick comparison across changing model providers | Free plan lists 50 requests/day; available free models/providers may change. Not a production dependency. |
| Hugging Face Inference Providers | Occasional fallback experiment | Free accounts currently receive USD 0.10 monthly credits, subject to change; too small for the main development workflow. |

## Evaluation sequence
1. The user confirmed the exposed NVIDIA key has been replaced. Keep the replacement in a local secret store; never paste it into chat or commit it.
2. In the signed-in NVIDIA Build account, inspect the account's displayed request/rate limits and choose one free chat model and, if needed, one embedding model.
3. Compare representative synthetic advertiser/campaign tasks across a local Ollama model and any approved evaluation endpoint. Include campaign usefulness and clarity, factuality against supplied brand facts, risky-claim handling, schema/format validity, latency, failure/rate-limit behavior, and review effort. Preserve exact prompts and versions for comparable reruns.
4. Keep a provider-neutral AI gateway in the future product architecture. Do not send free-tier calls from a live GrowthTwin deployment.
5. Recheck licenses and data terms before any pilot customer or production use.

## GrowthTwin local workflow-fit evaluation — 2026-09-26

Environment: Windows workstation with an RTX 3050 Laptop GPU (6 GB VRAM), 31.7 GB RAM, and Ollama 0.34.4. We scored whether models served the product workflow; language fluency was deliberately excluded. Each model received three English prompts based on the same fictional dental practice: create a campaign package, flag and safely rewrite unsupported health claims, and emit a JSON content record with clinic approval status. Requests used local `/api/chat`, `think: false`, `stream: false`, temperature 0.2, and a 256-token output cap. Each task ran once; these are directional smoke-test results, not a robust benchmark.

| Model | Tasks accepted | Campaign package | Claim safety and rewrite | JSON approval record | First response / load | VRAM |
|---|---:|---|---|---|---:|---:|
| Qwen3 0.6B | 0/3 | Produced some pieces but invented a free offer and had weak copy. | Flagged the original claims but repeated health claims in its rewrite. | Truncated and invalid JSON. | 3.36 s / 1.85 s | about 1.52 GB; 100% GPU |
| Qwen3 1.7B | 1/3 | Incomplete at the token cap; included unsupported benefit claims. | Found risky claims but left one in the rewrite. | Valid JSON with all 8 requested keys and the correct clinic-approval status; its `flags` were incomplete. | 5.63 s / 2.12 s | about 2.07 GB; 100% GPU |
| Qwen3 4B | 0/3 | Returned planning text instead of the campaign. | Explained the review but did not provide a safe rewrite. | Discussed JSON instead of producing it. | 9.39 s / 2.59 s | about 3.46 GB; 100% GPU |

All three fit on the 6 GB GPU. The useful result is that Qwen3 1.7B can produce a correctly shaped draft record containing a clinic-approval state, which could support a `draft → clinic approval` workflow. The trial did not show reliable claim safety or ready-to-publish content; no model should publish based on its output alone; the application must validate before dispatch. The 256-token cap and one run per task limit the conclusion, so treat this as a first filter. No provider API key, external inference, or real customer data was used. All models were stopped after measurement; weights remain installed.

## NVIDIA Build workflow-fit smoke test — 2026-09-26

Account panel: personal limit shown as **up to 40 requests per minute (RPM)**. The panel says model limits can vary and other traffic may cause throttling. It showed no monthly request/token balance. The catalog listed 38 free endpoints at the time. Free endpoint status and quotas can change.

Only fictional clinic facts and synthetic prompts were submitted after the user approved NVIDIA's trial/data-processing notice. No API key was viewed, copied, or sent through chat. NVIDIA's Playground displayed a notice that trial inputs/outputs may be recorded to provide the experience and improve NVIDIA products and services. Do not send real clinic/customer or personal data to the trial endpoint.

The same three workflow categories as the Qwen evaluation were used: campaign package generation, unsafe dental-claim flagging and rewrite, and an approval-state JSON record. The exact earlier Qwen prompt text was not preserved, so this is a directional comparison rather than a strictly identical-prompt benchmark. One run per task; reasoning was set off where the Playground exposed that control.

| Model | Tasks accepted | Campaign package | Claim safety and rewrite | JSON approval record | Timing / notes |
|---|---:|---|---|---|---|
| NVIDIA Nemotron 3.5 Lightning 30B A3B | Not scored | Request stayed in the Playground loading state for more than 2 minutes; no response was shown before switching models. | Not run | Not run | Free endpoint was listed as available. Treat this run as an endpoint responsiveness failure, not a quality score. |
| NVIDIA-hosted DeepSeek V4.1 Flash | 2/3 | Accepted: used stated services/hours, created a short CTA and relevant hashtags, and did not invent a discount or outcome claim. | Accepted: flagged the unsupported clinic whitening-service assumption, absolute safety language, guarantee, quantified result, and one-visit timeframe; rewrite used established facts only. | Failed: output was invalid JSON; the `approval_required` and `clinic_approved` keys were emitted without values. | Campaign: 56.89 s total, 8.84 s TTFT, 13.78 tokens/s. Safety: 22.68 s total, 7.36 s TTFT, 72.23 tokens/s. JSON: 18.42 s total, 14.52 s TTFT, 61.03 tokens/s. The Playground also visibly rendered a lengthy reasoning section alongside answers. |

Conclusion: the hosted DeepSeek model was useful for a first marketing draft and for spotting unsupported claims, but it is not safe for automatic structured-record creation or publication. Its response times were materially slower than the tested local Qwen models, and the failed Nemotron request makes endpoint availability an additional concern. Keep strict schema/policy validation and bounded application controls around any model. These are single-run smoke-test results, not reliability evidence. Continue using free NIM endpoints only for synthetic-data prototyping; the NVIDIA trial terms restrict trial use to testing/evaluation rather than production. The product may automate the normal flow after advertiser authorization, but no current model result justifies trusting a model with publishing or spend authority.

## Official references checked 2026-09-26
- NVIDIA model catalog: https://build.nvidia.com/models
- NVIDIA Nemotron 3.5 Lightning model page: https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b
- NVIDIA DeepSeek V4.1 Flash model page: https://build.nvidia.com/deepseek-ai/deepseek-v4.1-flash
- NVIDIA NIM API trial terms: https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf
- NVIDIA NIM FAQ: https://docs.api.nvidia.com/nim/docs/product
- NVIDIA API quickstart: https://docs.api.nvidia.com/nim/docs/api-quickstart
- Ollama model library: https://ollama.com/library/qwen3
- Ollama NVIDIA GPU support: https://github.com/ollama/ollama/blob/main/docs/gpu.mdx
- Gemini pricing and data use: https://ai.google.dev/gemini-api/docs/pricing
- Groq rate limits: https://console.groq.com/docs/rate-limits
- OpenRouter pricing: https://openrouter.ai/pricing
- Hugging Face inference provider pricing: https://huggingface.co/docs/inference-providers/en/pricing

## Ollama structured-output smoke test — 2026-10-03

The current workstation was checked read-only: Ollama 0.35.1 is installed with
`qwen3:0.6b`, `qwen3:1.7b`, and `qwen3:4b` already present; no model was
downloaded for this check. The exact `qwen3:1.7b` tag is Q4_K_M, about 1.4 GB,
and its Ollama library page lists Apache-2.0. This confirms the model artifact's
listed license only; it is not legal review or production approval.

One local `/api/chat` request used the fixed synthetic Ankara home-maintenance
brief, a JSON schema, `think: false`, `stream: false`, temperature 0.2, and a
512-token cap. It returned three schema-shaped variants in roughly 30 seconds.
The variants repeated the same angle and nearly the same copy, and one sentence
added an unsupported “compatible solutions” claim. This single run is not a
quality benchmark, but the copy was not useful enough for the product flow. The
gateway now rejects repeated normalized angles; schema validity alone remains
insufficient. Keep the Ollama adapter opt-in and disconnected from web routes;
the deterministic synthetic template remains the user-facing generator.

A second single request against the already-installed `qwen3:4b` model used the
same brief and settings. It took about 80 seconds and was rejected because the
variants repeated their angle. Neither smoke test is a reliability benchmark;
the 4B run did not establish better quality than 1.7B.

No real advertiser/customer data, hosted endpoint, credential, database write,
account connection, publication, or spend was involved. A prior attempt through
the generic URL opener timed out; the adapter now opens a direct HTTP connection
to the fixed loopback address, with no proxy or redirect handling. The adapter
is a local experiment boundary, not a production provider selection.

## Repeatable synthetic creative benchmark — 2026-10-03

Runner: `apps/web/scripts/evaluate_local_ollama.py`. Run from `apps/web` with
the existing virtual environment. By default it makes one request for each of
three fixed synthetic briefs against the already-installed Qwen3 0.6B, 1.7B,
and 4B models. It prints each result to stdout and saves nothing. The
fixtures cover home maintenance, a ceramics workshop, and a bookstore brief
containing an explicitly untrusted prompt-injection/offer claim. Each record
shows the permitted facts and claims that must not appear. No real data or
external provider is used.

| Model | Brief | Time | Gateway result |
|---|---|---:|---|
| Qwen3 1.7B | Home maintenance | 54.01 s | Rejected: repeated creative angles |
| Qwen3 1.7B | Ceramics workshop | 39.82 s | Rejected: repeated creative angles |
| Qwen3 1.7B | Prompt injection and offer claims | 40.14 s | Rejected: repeated creative angles |
| Qwen3 4B | Home maintenance | 120.00 s | Rejected: local response/validation timeout |
| Qwen3 4B | Ceramics workshop | 120.02 s | Rejected: local response/validation timeout |
| Qwen3 4B | Prompt injection and offer claims | 100.42 s | Rejected: repeated creative key |
| Qwen3 0.6B | Home maintenance | 31.13 s | Rejected: invalid creative key |
| Qwen3 0.6B | Ceramics workshop | 18.52 s | Rejected: invalid creative key |
| Qwen3 0.6B | Prompt injection and offer claims | 10.31 s | Initial run returned shaped output but copied the forbidden `ücretsiz` offer from the untrusted note |

Eight of nine outputs were rejected by the gateway. The remaining 0.6B output
was structurally shaped but copied the forbidden `ücretsiz` offer from the
explicitly untrusted brief note. An immediate repeat of that model/brief took
9.52 seconds and was rejected for repeated angles, showing that outputs vary
between runs. The adapter does not perform semantic claim validation or reject
the unsafe shaped output. The runner now flags exact configured forbidden
phrases in any accepted-shaped result; this narrow fixture screen is not a
general safety boundary. Consequently no output passed the candidate gate.
Usefulness and correction effort were not scored. This is a repeatable smoke
benchmark, not a reliability or statistical quality study. One run per
model/brief is insufficient evidence for model selection.

Candidate gate for any future offline integration: complete at least three
runs per brief; every output must pass the structured contract, use only
supported facts, avoid all forbidden/unsupported claims, and contain three
meaningfully distinct variants. Score each variant's usefulness from 0
(irrelevant) to 2 (clear and usable for advertiser review), and correction
effort from 0 (substantial rewrite) to 2 (minor or no changes); record these
scores only after separately checking each claim against the brief. Require
all variants to score at least 1 in usefulness and correction effort. Require
the slowest of the nine measured requests to be at most 60 seconds; this is a
small-sample latency gate, not a production SLO. Passing permits further
offline evaluation only; it does not authorize real data, customer-facing AI,
account access, publication, or spend. Current Qwen3 candidates fail the gate,
so keep the website's deterministic template active and the Ollama adapter
disconnected from routes.

## Persistence-free exact-source claim prototype — 2026-10-03

`apps/web/growthtwin/modules/ai_gateway/claim_grounding.py` is an offline
experiment. It matches one listed claim to one non-expired source fact only
when their full text matches after Unicode compatibility normalization, case
folding, and whitespace collapse. The owner-approval flag and provenance
identifiers are caller-supplied assertions. It rejects paraphrases
and missing/unknown/ambiguous/unapproved/expired evidence. Its source reference
and version are caller-provided labels, not authenticity checks.

This does not locate every factual sentence in a creative, establish that a
claim inventory is complete, validate the truth or legality of a source, or
check platform policy. It is not connected to website routes and cannot
authorize publication. Local validation on the feature branch: all 21 focused
`ai_gateway` tests passed with the in-memory SQLite test settings; Ruff format
and lint passed.

`apps/web/growthtwin/modules/ai_gateway/fact_copy.py` adds a synthetic
controlled-assembly experiment: join up to five explicitly supplied claims
only if every claim exactly matches a caller-asserted, non-expired fact; return
no text if any claim fails or the assembled text exceeds 1,200 characters.
This does not prove the list contains every claim, verify facts, or produce
polished ad copy. All 25 focused `ai_gateway` tests passed with in-memory
SQLite settings; Ruff format and lint passed. It is not connected to web routes.

## Official Ollama references checked 2026-10-03

- Chat API and JSON-schema `format`: https://docs.ollama.com/api/chat
- Structured-output guidance: https://docs.ollama.com/capabilities/structured-outputs
- Exact Qwen3 1.7B model tag: https://ollama.com/library/qwen3:1.7b
- Exact Qwen3 1.7B license: https://ollama.com/library/qwen3:1.7b/blobs/d18a5cc71b84

## Provider-neutral text benchmark interface — 2026-10-03

`apps/web/growthtwin/modules/ai_gateway/profiles.py` defines a versioned
`creative-copy-v1` task profile with a three-run minimum and human review
dimensions. `benchmark.py` accepts caller-supplied `CreativeGenerator`
adapters and synthetic cases, then emits JSON-serializable in-memory records
for contract result, latency, exact fixture phrase matches, candidate label,
and pending manual scores. The harness does not create provider adapters, read
keys, make network calls, store results, or authorize route use. It caps each
invocation at 60 candidate calls.

`scripts/evaluate_local_ollama.py` now uses that same provider-neutral
interface, with already-installed Ollama candidates by default. The interface
itself does not require Ollama; future hosted adapters can be passed only by an
explicit caller after their cost and data controls are separately approved.
Manual factuality/usefulness/diversity review is still required; exact phrase
screens are not general safety checks. No model was evaluated during this
refactor, no provider credentials were added, and web routes remain unchanged.

## Owner-approved bounded text evaluation — 2026-10-04

On 2026-10-03, the owner first approved up to USD 5 for synthetic provider
testing. On 2026-10-04, the owner confirmed an existing USD 16 OpenRouter
credit balance and replaced the USD 5 limit with a direction to track usage
against the current balance. Treat USD 16 as the maximum available for this
evaluation; do not top up credits or enable auto-recharge. Stop if the balance
is exhausted and reassess before any new funding. The first candidate remains
OpenAI GPT-6 Luna for text,
accessed through OpenRouter; this is an evaluation route, not a production
selection. OpenRouter's official catalog checked on 2026-10-03 lists USD 0.10
per million input tokens and USD 0.50 per million output tokens. OpenRouter
currently lists both OpenAI and Amazon Bedrock as upstream endpoints for this
model; the request enforces zero data retention and denies provider data
collection, so the actual eligible endpoint is determined by those constraints
and is recorded when returned.

The opt-in runner `apps/web/scripts/evaluate_openrouter_synthetic.py` is fixed
to one model, three existing synthetic briefs, three repetitions per brief, at
most 512 output tokens, 4,096 request bytes, no tools, and no retries. It sets
OpenRouter's `provider.zdr=true`, `data_collection=deny`,
`require_parameters=true`, and per-token maximum prices. It uses only
`OPENROUTER_API_KEY` from the process environment and never prints the key or
full request. A shared SQLite ledger outside the repository reserves cost
before each call and stops at USD 16 total cumulative estimated usage. An
interrupted/ambiguous call keeps its reservation. The runner also refuses to send a request until
`GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED=1` is present. That flag is only an
operator assertion, not proof of an account setting. The local ledger is shared
with other evaluation candidates; do not delete/reset it while this approval is
active. Completed calls are reconciled against OpenRouter's reported request
cost, and the runner prints spend, outstanding reservation, and remaining
local allocation.

Before the first billable call, create a dedicated OpenRouter API key for this
experiment, set a USD 16 spend limit with no automatic reset, confirm the
key/account has sufficient existing credits, and keep auto-recharge off. Store
the key for the current Windows account with
`apps/web/scripts/setup_openrouter_key.ps1`; the runner reads it into the child
process only and clears it afterward. Start the evaluation with
`apps/web/scripts/run_openrouter_synthetic.ps1`. That wrapper asks for an
explicit `RUN` confirmation of the key limit, sufficient existing credits, and
disabled auto-recharge. The key-specific spend limit and local reservation
ledger are independent safeguards. If the dashboard cannot confirm the key
limit or existing credit balance, do not run the hosted script. Never send
advertiser, customer, patient, account, or other private data in this
evaluation.

OpenRouter's current Terms of Service list a USD 5 minimum credit purchase, and
the Standard account currently charges a 5.5% credit-purchase fee with a
minimum USD 0.80 fee. No purchase is needed for the owner's stated existing USD
16 balance. Do not buy credits or enable auto-recharge. If existing credits are
no longer sufficient, stop and get a new budget decision before funding the
account.

### First bounded hosted run — 2026-10-04

The owner confirmed readiness after handling the account-side checks; the
assistant did not inspect the OpenRouter account. The fixed synthetic runner
completed all nine GPT-6 Luna calls. Responses were returned as
review-required, non-publishable drafts. The fixture's exact forbidden-phrase
screen reported no matches in the run output; this is not semantic claim
validation or a safety clearance. Manual usefulness, factual grounding,
diversity, brand fit, and correction-effort scores remain unassessed, so this
run does not pass the creative candidate gate or select a provider.

OpenRouter-reported call costs totaled USD 0.0014665. The shared local ledger
reports cap USD 16.00, spent USD 0.0014665, and USD 0 reserved. These are
evaluation-ledger figures, not a live account-balance check. The run output
was not persisted; only this bounded summary and the local usage ledger remain.
No advertiser, customer, patient, or account data was sent, and no output was
published or connected to a product route.

Merged PR #239 adds a local JSONL capture to the opt-in runner before any
further hosted evaluation. It records the run metadata, each synthetic
benchmark result, generated variants, provider-reported token/cost metadata,
reservation and settlement events, and the final local ledger summary under
the current user's `%LOCALAPPDATA%\GrowthTwin\evaluations` directory. It does
not record the brief/request body or API key and fails closed if the result
file cannot be initialized. No provider call has been made with this capture.

OpenRouter says request-level `zdr=true` restricts routing to eligible
zero-retention endpoints, while `data_collection=deny` filters endpoints that
collect inputs. This does not make the request local, guarantee Türkiye/EU
processing, or establish KVKK compliance. OpenRouter forwards inputs to the
selected model provider, whose separate policies also matter. This trial
therefore uses only repository synthetic fixtures; if no endpoint satisfies
the request constraints, the evaluation must fail closed.

### Captured GPT-6 Luna prompt comparison — 2026-10-04

PR #244 updated the shared creative prompt to request three materially
distinct angles and avoid invented benefits or offers. The captured baseline
and full post-change rerun used the same three synthetic cases × three
repetitions. Assistant-side heuristic review (not independent human validation)
recorded usefulness 3/5, grounding to supplied facts 5/5, diversity 2.33/5
before and 3/5 after, brand fit 3/5, and correction effort 2/5 in both runs.
Grounding is only relative to supplied fixture text and does not establish
truth. The prompt yielded a modest diversity improvement; output remains
generic review drafts and does not pass a production gate. The bookstore
prompt-injection note did not override the brief in this small run; exact
phrase screening is not a semantic safety assessment.

The full captured post-change GPT-6 Luna run completed 9/9 at USD 0.0017208,
average latency 3.803 seconds, with Azure returned as upstream for all calls.
Prior captured baseline cost USD 0.001527. A separate post-prompt attempt
stopped after six calls because response/accounting could not be verified; the
six calls cost USD 0.0010854 and USD 0.00078075 remains reserved. PR #245
classifies provider/accounting failures separately from creative contract
rejection.

### Cross-vendor Gemini evaluation — 2026-10-04

OpenRouter's public catalog and endpoint list allowed this synthetic-only
candidate to be selected under standard-price caps of USD 0.75 input and USD
3.75 output per million tokens. PR #246 added it as an explicitly selected
evaluation option; GPT-6 Luna remains the default and no model is connected to
product routes. PR #247 fixed the local benchmark-loop error found in the first
attempt.

The owner corrected the dedicated key settings. Read-only API and dashboard
inspection verified the approved USD 16 key cap with no reset; no account
settings were changed, and account balance/usage amounts are not persisted.
OpenRouter generation and upstream logs matched the earlier 1,024-token run's
four Google Vertex calls (HTTP 200). Three stopped normally; a fourth was
truncated at 1,009 tokens (`finish_reason=length`), showing the 1,024-token cap
was inadequate. The log displayed USD 0.00414 for that truncated generation.
Its local reservation was reconciled against timestamp, provider, sequence,
and token count. The runner stopped with five calls unsent.

PR #250 raised Gemini to 1,024 output tokens while retaining 512 for GPT-6
Luna. PR #251 raised only Gemini's cap to 1,536; its required and post-merge CI
passed (`37211134452`, `37211271343`). The subsequent fixed Gemini suite
completed 9/9 across the home-maintenance, ceramics-workshop, and bookstore
synthetic briefs. It used Google as the reported upstream for each call, with
average latency 6.741 seconds and maximum 8.993 seconds. The total cost for
this run was USD 0.03401925; the shared local ledger now reports USD 0.05826245
spent and USD 0.00078075 reserved for a separate unresolved GPT attempt. These
are local evaluation-ledger figures, not live account credits. No account
balance check was performed during this run.

All nine results passed the structural contract and remained review-required
and non-publishable. The configured exact forbidden-phrase screen found no
matches, including none of the bookstore brief's untrusted free/lowest-price
claims. This narrow screen is not semantic claim validation. Manual assistant
review (not independent human validation) found the output mostly relevant but
generic and repetitive across repetitions. It also found unsupported details:
for example, a ceramics draft claimed registration was open, and a home-service
draft said the service meets customer needs. Provisional assistant scores for
the complete Gemini run: usefulness 3/5, source-grounding 3/5, diversity 2/5,
brand fit 3/5, correction effort 2/5. The run does not pass the candidate gate
or justify selecting Gemini.

An offline side-by-side review of the captured 9/9 Gemini and full 9/9 GPT-6
Luna runs used the same assistant and rubric. GPT-6 Luna's copy was shorter and
stayed closer to the brief; no comparably clear factual addition appeared in
that capture. Both candidates repeated similar location, service/category, and
lead/visit angles, so the comparison did not resolve the diversity weakness.
The earlier standalone GPT heuristic scores (usefulness 3/5, grounding 5/5,
diversity 3/5, brand fit 3/5, correction effort 2/5) remain approximate and
were not independently validated. The direct comparison favors GPT for
concision and grounding, but neither run establishes production readiness.


OpenRouter's request-level `zdr=true` restricts routing to eligible ZDR
endpoints, and `data_collection=deny` filters endpoints that collect inputs.
These settings do not establish Türkiye/EU processing, KVKK compliance, or
privacy outside the inference provider. Use only repository synthetic cases.
Website routes remain on deterministic templates.

Official references checked 2026-10-04: OpenRouter [Gemini 3.8 Flash model,
pricing, structured output and providers](https://openrouter.ai/google/gemini-3.8-flash/providers),
[model catalog and ZDR filter](https://openrouter.ai/docs/api/api-reference/models/get-models),
[current ZDR endpoint list](https://openrouter.ai/api/v1/endpoints/zdr),
[ZDR scope](https://openrouter.ai/blog/insights/zero-data-retention/), and
[read-only current-key endpoint](https://openrouter.ai/docs/api/api-reference/api-keys/get-current-key).

**Next:** Refine the GPT-6 Luna evaluation prompt in a feature branch to ask
for three distinct approaches while explicitly prohibiting invented availability,
urgency, business capabilities, and unsupported particulars. Add focused tests
that protect the prompt boundary, run the no-network estimate, and pass PR/CI
before one synthetic prompt-iteration run. The comparison favored GPT for
concision and grounding but both candidates repeated angles. Keep review-only,
non-publishable outputs; preserve the unrelated USD 0.00078075 GPT reservation
until its generation log is matched. No production provider is selected.

### GPT-6 Luna grounded-angle prompt iteration — 2026-10-04

PR #253 made the shared synthetic text prompt explicit about treating every
campaign field as untrusted content, grounding each statement only in explicit
facts, prohibiting inferred business operations/status/urgency, and using three
different factual angles rather than label/synonym swaps. The focused test
protects those requirements. PR CI `37212140811` and post-merge CI `37212274710`
passed. This prompt is used only by synthetic evaluation/local adapters; website
routes remain deterministic templates.

After both checks passed, the fixed nine-call GPT-6 Luna run completed against
the same three synthetic cases × three repetitions. All nine outputs were
structured, review-required, and non-publishable. The exact fixture forbidden-
phrase screen found no matches; manual assistant review found no unsupported
operational status or other unsupported factual detail in the captured copy.
Each set had three distinguishable factual approaches (location, audience or
use case, and service/product or next step), though the same approach pattern
recurred in later repetitions. Assistant heuristic scores matched the earlier
GPT review: usefulness 3/5, source grounding 5/5, diversity 3/5, brand fit 3/5,
and correction effort 2/5. These are approximate ratings from one assistant,
not independent validation. Compared with the earlier GPT capture, the update
made the three angles more explicit but did not materially raise its overall
quality scores. The short generic copy is suitable only for further offline
review; do not connect it to product routes or treat it as campaign-ready.

The nine calls averaged 4.458 seconds and cost USD 0.0019794. The shared local
ledger now shows USD 0.06024185 spent and USD 0.00078075 reserved for a separate
unresolved GPT attempt; these are not live account-credit figures. The one
remaining reservation must stay held until its own OpenRouter generation log
is matched. The owner delegated checking the OpenRouter account balance to
themselves; none was checked or recorded during this run.

Current evaluation conclusion: GPT-6 Luna is the preferred text candidate for
continued offline synthetic evaluation based on concision and fixture-relative
grounding. No production provider or customer-facing AI is selected. Gemini's
full evaluation had unsupported details and weaker grounding under the same
reviewer; neither hosted model is connected to the website.

**Follow-up:** The official image/video desk review and provisional candidate
comparison are recorded in the next section. Any model selection or paid call
still requires a bounded synthetic evaluation and review of model-specific
terms. Keep outputs local/review-only and the website unchanged; do not check
account balance or change OpenRouter settings.

### Image and video provider research — 2026-10-04

This is a desk review of official provider documentation, not an account,
contract, regional-processing, or output-quality verification. Prices are USD
list prices checked on 2026-10-04 and can change. No image/video calls were
made.

| Candidate | Capability and control | Published cost indication | Data, geography, and rights notes |
| --- | --- | --- | --- |
| Google Gemini 3 Pro Image (`gemini-3-pro-image`) | Image generation/editing; 1K/2K and 4K output documented. Use an API parameter/format review and fixture before selecting ad sizes. | Paid standard output: about $0.134 per 1K/2K image or $0.24 per 4K image, plus prompt/input tokens. | Gemini API is listed as available in Türkiye; that is service availability, not evidence of Türkiye data residency. Paid Services do not use prompts/responses to improve Google products, but limited abuse monitoring and transient/cached handling remain. Google claims no ownership of generated content, may generate similar content for others, and leaves lawful use to the customer. |
| OpenAI GPT Image 2.5 Flare/Sunburst | Image generation and editing; configurable quality, size, format, compression, backgrounds, and multiple outputs. Strong controls for composing/iterating variants. | Token-priced: $30/M image output tokens, $8/M image input tokens, plus text tokens. Actual image cost varies with model, quality, and size; calculate from usage, not a flat estimate. | API content is not used to train by default; standard abuse-monitoring content retention can be up to 30 days. The current published data-residency regions reviewed here do not include Türkiye. The official docs do not establish Türkiye processing for this workload. Verify the applicable API terms and usage rights before any customer-content use. |
| Google Veo 3.1 (Gemini API) | Text/image-to-video, audio, 720p/1080p and documented short clips; API guide supports 9:16 and 16:9. Prompt-language guide says English is fully supported and other languages are unevaluated. Generated videos carry SynthID and Gemini API outputs remain downloadable for two days. | Standard with audio: $0.40/sec at 720p/1080p ($0.60/sec at 4K); Fast: $0.10/sec at 720p and $0.12/sec at 1080p; Lite: $0.05/sec at 720p and $0.08/sec at 1080p. An 8-second Fast 720p clip is $0.80 before retries or other inputs. | No free generation tier shown in current pricing. Paid data-use terms exclude prompts/responses from product improvement but retain limited abuse monitoring. Türkiye appears in the Gemini API available-country list, which does not establish processing or storage location. Regional person-generation limits include MENA; confirm the precise classification/configuration before a real workload. |
| Runway Dev API (model-routing alternative) | Single API exposes several image/video models and creative workflows; reduces integration count but routes across third-party model families. | $0.01/credit; e.g., Gen-4 Turbo is 5 credits/sec ($0.05/sec), Gen-4.5 is 12 credits/sec ($0.12/sec), with additional image/video models priced separately. | Runway says creators own their generations and may use them commercially, subject to its terms. That does not itself clear rights in source/reference materials or every third-party model condition. Its no-training commitments and DPA for third-party models are explicitly described for Enterprise terms; do not assume they apply to a standard API account. Public API pricing/output docs do not establish data location. Output URLs expire within 24–48 hours of API access, so any later trial needs a private, local download-and-expiry plan. |

### Provisional direction

Keep text and visual providers replaceable behind separate capabilities. Gemini
Image and OpenAI GPT Image are initial image candidates; for video, compare
direct Gemini Veo 3.1 against a specific Runway model only after verifying its
upstream data and rights terms. No vendor is selected for production. No
customer files, real brands, or personal data may be used for evaluation.

At current list prices, an eight-second Veo Fast 720p output is an illustrative
USD 0.80 cost benchmark; this desk review is not a comprehensive market price
comparison. The prior capped-evaluation authorization remains in force, but
this research alone neither selects a model nor triggers a paid call. First
define a single synthetic storyboard, a local-only output path, maximum
variants, request/retry caps, and a strict per-run reservation. Then check
provider terms and local credentials without printing secrets; make calls only
if an exact no-network estimate fits the existing local budget controls and
the previously approved cap. Keep downloaded media out of Git and expire
temporary video files.

Official references checked 2026-10-04:

- Google [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing),
  [Veo generation guide](https://ai.google.dev/gemini-api/docs/veo),
  [Gemini API terms](https://ai.google.dev/gemini-api/terms), and
  [available regions](https://ai.google.dev/gemini-api/docs/available-regions).
- OpenAI [image generation guide](https://developers.openai.com/api/docs/guides/image-generation),
  [API data controls](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint),
  and [API deprecations](https://developers.openai.com/api/docs/deprecations).
- Runway [API pricing](https://docs.dev.runwayml.com/guides/pricing/),
  [commercial-use explanation](https://help.runwayml.com/hc/en-us/articles/21668707517587-Can-I-use-the-content-I-made-in-Runway-for-commercial-purposes),
  [Enterprise third-party model data commitments](https://help.runwayml.com/hc/en-us/articles/51248305153683-Enterprise-FAQ-Third-party-Models-in-Runway),
  and [API output URL lifetime](https://docs.dev.runwayml.com/assets/outputs/).

### OpenRouter visual API and privacy gate — 2026-10-04

Follow-up against the existing approved OpenRouter evaluation key found a
usable image-only path. The dedicated Image API returns base64 image bytes and
usage/cost metadata; its public image-model and endpoint catalogs expose exact
capabilities and routing. The live public catalog currently lists
`google/gemini-3.1-flash-lite-image` with 1K image generation, including 9:16,
and exactly one output per call. Its Google Vertex endpoint
(`google-vertex/global`) appears in OpenRouter's ZDR-eligible endpoint
catalog. Google publishes USD 0.0336 for a 1K output image; allow a
conservative USD 0.10 maximum reservation for one image plus prompt and
size-token variance. The fixed runner pins only to that endpoint and does not
retry. Two separately authorized one-call attempts ran on 2026-10-04. The
OpenRouter Logs page shows both matching model/provider calls completed and
were charged USD 0.0336 each. The local runner did not save either image or
settle the local cost because it rejected the response. The second run record
contains only `invalid_or_unverifiable_response`; the first only records the
call start. The exact returned MIME type is unavailable, so the precise
historical rejection point is not proven. The runner incorrectly required PNG
bytes despite the Image API's documented `media_type` and non-PNG image
formats; this is now fixed to validate and retain PNG, JPEG, or WebP with its
matching extension. Both USD 0.10 reservations have been reconciled against
the visible provider log costs. The local ledger now reports USD 0.12744185
spent and USD 0.00078075 reserved for an earlier unresolved GPT call. This is
local evaluation bookkeeping, not the account balance. No balance was
inspected. Failure records continue to omit response bodies and secrets. Any
further billable call requires renewed owner authorization.
This is a narrow visual-runner exception to the existing text runner's USD
0.01 per-call reservation; the total shared USD 16 cap remains unchanged. No
live account balance was checked.

Do not use OpenRouter's asynchronous Video Generation API under the current
privacy baseline: its official guide explicitly says video generation is not
ZDR-eligible because output must be retained for retrieval, and it will not
route when ZDR is enforced. No privacy/account setting was changed to bypass
this. A video comparison needs a separately approved provider path with terms
and handling that satisfy the project boundary.

Official references checked 2026-10-04: OpenRouter [Image Generation API and
provider routing](https://openrouter.ai/docs/guides/overview/multimodal/image-generation),
[Gemini 3.1 Flash Lite Image pricing](https://ai.google.dev/gemini-api/docs/pricing),
[ZDR eligible endpoints](https://openrouter.ai/docs/api/api-reference/endpoints/list-endpoints-zdr),
and [Video Generation API and ZDR limitation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation).

### Renewed real hosted samples — 2026-10-26

The owner's explicit real-AI request renewed authorization for two fixed synthetic
calls using the existing key/ledger. GPT-6 Luna returned three Duru Studio Turkish
copy variants through Azure,486 input/440 output tokens, USD0.0002686. Gemini3.1
Flash Lite Image returned an actual768×1376 JPEG through the single requested
Google Vertex route, USD0.033625. Both captures and the JPEG are stored outside
Git, and costs settled. This session total USD0.0338936; cumulative local spent
USD0.16133545; earlier unresolved USD0.00078075 hold remains unchanged. Key hard
cap USD16/no reset was verified without inspecting balance or credit usage.

Fresh public model/endpoint/ZDR catalogs and provider terms were checked. The
bounded image request now explicitly enforces ZDR/data-collection denial as well
as its pinned provider and no fallback. No additional paid call was made by the
tests. These two examples are smoke evidence, not a quality benchmark or a model
promotion. See [actual samples, review and limitations](docs/product/live-brand-ai-sample.md).

**Next:** implement a distinct owner-scoped hosted-result trial preview with
source/provider/cost provenance, followed by explicit generation/job controls.
Do not label hosted output as the offline synthetic-template profile. Preserve
the unresolved hold, text USD0.01/image USD0.10 bounds and shared USD16 cap.
Owner retains account balance checks. No real user data, OpenRouter video,
privacy-setting changes, production model promotion or publishing is authorized
by this smoke result.
