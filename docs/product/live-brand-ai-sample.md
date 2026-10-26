# Real hosted brand sample — 26 October 2026

The owner explicitly requested real AI production. Two single paid calls used
the existing approved OpenRouter credential and shared USD16 evaluation ledger.
Both inputs describe only the fictional Duru Studio ceramics brand. This is
actual provider evidence, separate from the offline template editor profile.
Neither call approves customer data handling, publishing or a production model.

## Verified calls

| Output | Model / route | Provider-reported cost |
| --- | --- | --- |
| Three Turkish copy candidates | `openai/gpt-6-luna`, returned provider Azure | USD0.0002686 |
| One product illustration/photo | `google/gemini-3.1-flash-lite-image`, pinned `google-vertex/global` | USD0.033625 |
| This session total | Two calls, no retry | USD0.0338936 |

Text usage:486 input tokens,440 output tokens. Image bytes decoded successfully
with Pillow as JPEG,768×1376 pixels. The request asked for1K and9:16; measured
pixels are recorded rather than claiming exact9:16 or silently cropping. The image
API runner does not return upstream identity metadata: the image route is the
requested single pinned endpoint, not a separately reported response identity.

Result/start/settlement JSONL and the actual JPEG are outside Git under
`%LOCALAPPDATA%\GrowthTwin\evaluations`. Capture IDs are
`brand-text-20261026T045335-0f83360e` and
`brand-image-20261026T045722-5bdfe523`. Text source fingerprint:
`c0092a996d53c5e2e26dffe6ddc373fb929a80c9110a8b8b4afb5ca476408b77`.
The image capture records its prompt fingerprint and returned-file SHA256.

After settlement the local ledger reports USD0.16133545 spent and USD0.00078075
still held for the unrelated historical unresolved GPT call. That hold was not
released or retried. These are local records, not the current account balance.
No balance/credit usage value was inspected. Before these calls, the existing
key's hard cap was verified as USD16 with no reset; the owner manages balance.

## Actual text candidates

1. **El yapımı seramik kupalar** — Duru Studio’nun el yapımı seramik kupa
   koleksiyonunu keşfet.
2. **Mat zeytin yeşili, kum beji** — Duru Studio koleksiyonunun renklerini keşfet.
3. **Sade gündelik sofra tasarımı** — Duru Studio’nun sade sofra yaklaşımını keşfet.

All three use **Koleksiyonu keşfet** as their call to action. Agent review against
the fixed facts found no invented price, discount, stock, delivery promise or
outcome guarantee. The wording is short and usable as a first smoke sample, but
generic; one successful call is not persuasive-copy or conversion-quality proof.

Visual review: two textured mugs in olive/sand tones, natural side light, simple
wooden tabletop, no visible text/logo/people, and a large clear upper area for
later typesetting. The mugs are invented, not faithful representations of any real
product; real product identity/reference-image fidelity remains untested. No image
editing, compositing or commercial rights clearance is claimed by this review.

## Repeatable bounded tool

From `apps/web`, `python -m scripts.generate_openrouter_brand_sample --kind text
--run` or `--kind image --run` makes exactly one fixed synthetic request. This is
an operator tool, not an unattended job or product endpoint. It requires the
protected key in the process environment and the independently verified no-reset
hard-limit assertion. Do not paste keys into commands or chat. The text ceiling
is USD0.01; the image ceiling USD0.10; both share the existing USD16 ledger.

No-network tests cover budget refusal, output-path refusal, provider/privacy
pinning, result capture before settlement, successful text/image accounting,
timeout without retry, missing accounting and failure after settlement. Image
bytes and result metadata are flushed before settlement; failure leaves a hold
unless settlement already succeeded, which is explicitly reported. Captures are
not a crash-recovery/idempotent provider-job system. Do not auto-retry an ambiguous
call. The older image runner now also requests ZDR/data-collection denial and
correctly excludes the whole repository from output storage.

## Current provider checks and next step

On2026-10-26 the public image endpoint catalog supported1K,9:16 andn=1 on
`google-vertex/global`; its output token price was USD0.00003. The same endpoint
appeared in the public ZDR catalog. Text used fresh eligible Azure routing with
the existing schema and price bounds. Requests enforce ZDR, deny data collection
and disallow fallback for the image. These checks do not guarantee availability
or terms for later calls; recheck before another paid batch.

Sources: [OpenRouter terms](https://openrouter.ai/terms),
[routing](https://openrouter.ai/docs/guides/routing/provider-selection),
[ZDR](https://openrouter.ai/docs/guides/features/zdr),
[public ZDR catalog](https://openrouter.ai/api/v1/endpoints/zdr),
[image API](https://openrouter.ai/docs/guides/overview/multimodal/image-generation),
[image endpoint catalog](https://openrouter.ai/api/v1/images/models/google/gemini-3.1-flash-lite-image/endpoints),
[Google service terms](https://cloud.google.com/terms/service-terms).

**Next:** add a separate, owner-scoped hosted-result trial profile and read-only
product preview with true provider/source/cost provenance; keep the existing
offline template profile honest. Then connect one explicitly requested generation
through budget reservation and durable job/idempotency controls. The current
website does not yet execute these hosted calls through its Generate controls.
No new infrastructure, migration, protected Google candidate change, customer
data use, ad publishing or deployment was performed.
