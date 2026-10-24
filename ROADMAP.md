# Yaparo roadmap


## Saved synthetic creative work — 24 October 2026

The local brand slice now has identity-pinned saved scene documents: explicit
creation, title/color edits, reopen and owned JSON download. Replays do not reset
work; stale saves are rejected. Brand edits do not rebind existing documents.
The schema is the bounded editor experiment v1. Django now connects an owned
Fabric editor to saved documents: layer text/color/transforms, revision-checked
server saves and client PNG export. Custom assets, creative edit history and
campaign association remain open. This is a local synthetic slice.

## Active delivery plan — 2026-10-23

Owner direction: build a sustainable Yaparo-owned product using maintained,
self-hostable components and replaceable AI services. Follow [ADR-0040](docs/adr/0040-owned-core-and-open-source-adoption.md)
and the [master plan](docs/product/yaparo-open-source-master-plan.md).

The [Y01–Y32 sequence and acceptance criteria](docs/product/yaparo-delivery-plan.md)
is now the active backlog: brand/assets/editor/export → evaluated AI and durable
jobs → accounts/credits/payment → Google Search and real measurement → gated
pilot → evidence-based channel/video/optimization expansion. Customer discovery
and legal/platform readiness run alongside local synthetic implementation.

**Current:** Y01 mapped; Y02–Y03 bounded local editor decision recorded in
[ADR-0041](docs/adr/0041-bounded-fabric-and-brand-identity.md). Y04 now has
owner-scoped synthetic brand creation/list/edit, immutable identity versions and
stale-edit protection. Desktop/mobile journey passed locally. Custom logo/font
intake, creative/campaign binding and production editor readiness remain open.
**Next:** complete portable identity styling and creative history before custom asset intake.

The owner's multi-brand requirement is now part of Y04: separate identity,
character, assets and creative history per brand. See [brand experience and
acceptance](docs/product/brand-specific-experience.md). Y29 remains advanced
portfolio/team work; basic multi-brand use is earlier. Brand-aware AI and
story-led video are specified as staged experiments, not ready capabilities.

This supersedes the ordering of the 21 October recovery-first sequence below,
not its security requirements. Keep protected TEST candidate/history/backup and
old read/stop paths intact; no reset, bypass or repeated preparation. Complete
real-data/financial/platform/operational gates before any customer pilot.

Earlier sections remain dated implementation evidence and longer-term scope.

## Direction reset — 2026-09-27

The owner clarified that Türkiye is the target market and Yaparo should serve anyone who wants to advertise. Dental clinics, creators, and small businesses are examples, not product boundaries. Omneky is a long-term capability benchmark for ad creation, campaign launch, unified reporting, and bounded optimization. See [PROJECT.md](PROJECT.md), [ARCHITECTURE.md](ARCHITECTURE.md), accepted [ADR-0004](docs/adr/0004-self-service-advertising-autopilot.md), and [ADR-0005](docs/adr/0005-turkey-first-advertising-platform.md).

The product should remove routine Yaparo-operator work after an advertiser explains a goal, authorizes an account, and sets explicit limits. Routine work may run within those boundaries; the system must pause and notify the advertiser when it cannot safely proceed. Omneky-style multi-channel breadth is a long-term target, not the first-release scope. Current work prioritizes the local website and synthetic-data development; it does not authorize production publishing, real ad spend, or additional paid infrastructure.

## Existing foundation — in place for local product work

- Public GitHub repository, protected `main`, pull-request workflow, and CI are active. Use pull requests for repository changes and verify live branch/PR status before acting.
- Django 5.2 LTS + PostgreSQL 18 is the accepted local stack and is already scaffolded under `apps/web`.
- CI checks Django configuration, formatting, linting, dependency vulnerabilities, package builds, migrations, and focused tests. A synthetic profile edit E2E exists locally and in CI.
- Local browser E2E and GitHub-hosted CI provide the initial feedback loop. Keep local UI work on synthetic data.
- Heroku staging has an approved Basic web dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. On 2026-09-29, the Scheduler page recorded the daily synthetic session-cleanup job at 00:00 UTC as last run, and Heroku logs showed its one-off process exited with status 0. Actual one-off dyno cost remains unverified. The deployed app is for synthetic staging only.

## Phase 1 — Product experience prototype

**Goal:** demonstrate a clear, low-effort paid-advertising journey for a user in Türkiye without waiting for external APIs, paid infrastructure, or a production model.

Status: **Phase 1 acceptance verified on 2026-09-29 for the original synthetic prototype.** The current public slice uses one fixed synthetic Ankara home-maintenance example; visitors can choose an objective, example daily limit, and duration, while free-text brief/brand/audience intake is disabled pending the real-data readiness gate. Older session drafts that do not match the fixed example remain stored but are hidden and cannot be resumed or edited. Current session-scoped synthetic drafts derive a plan summary and demonstrate preview, simulated pause, editable deterministic copy, and sample report. The earlier desktop review fixed horizontal overflow, a hard-to-read data notice, and a report transition that could leave the report off-screen (PR #100). Browser E2E checks the current mobile journey. There is no connected account, AI provider, publishing, or real metrics. Durable advertiser/workspace persistence remains deferred until ownership and lifecycle boundaries are specified; see ADR-0006 and ADR-0007.

- Build the public product entry and a mobile-friendly campaign workspace in the existing Django application.
- Future product intake should let any advertiser in the Türkiye target market describe a goal with a short plain-language brief, then ask only for essential missing details such as audience, destination, timing, and maximum spend. The current public prototype stays on its fixed synthetic example until data readiness is established.
- Demonstrate brand/offer intake, a campaign plan, and on-brand ad concepts in a simple experience.
- Show a believable lifecycle with synthetic output: request received, plan prepared, creative preview, destination/schedule, simulated publication, and performance summary. Label mock publishing and metrics clearly.
- Keep editing, current status, spend boundary, and pause/stop visible. Do not hard-code clinic fields.
- **Acceptance:** a new visitor can understand the offer; a synthetic advertiser can move through brief → campaign preview → mock result without staff help; the layout works on mobile and desktop; no external account, AI provider, or publishing API is called.

## Phase 1.5 — Product and service blueprint

**Goal:** define what the first usable service does from advertiser request through campaign results, before building account/workspace flows that could invite real data.

This work is required before expanding the authenticated workspace beyond its current synthetic-only owner flow or accepting real advertiser, customer, or lead data. The long-term direction and owner requirements are expanded in [the product/service blueprint](docs/product/growthtwin-service-blueprint.md). Phase 1.5 remains **in progress** until its open decisions and narrow MVP are resolved. The blueprint records the full desired service while separating customer requirements, recommendations, findings, and undecided implementation/commercial/legal choices.

- Specify the two content paths: Yaparo-created content paid from credits, and customer-owned documents/assets that can be analyzed, edited, improved, adapted and versioned without overwriting the original.
- Map beginner and professional experiences across intake, strategy, content, pre-purchase plan/estimates, price breakdown, approval, publication, reporting, experimentation, pause, recovery, export and deletion.
- Treat owner-provided credit anchors (100 credits = USD 10; USD 100 for 1,000 purchased credits plus 20% bonus = 1,200 credits) and free initial credits as pricing requirements to cost and validate; distinguish creation credits, Yaparo campaign fees, platform media spend, tax and currency. The precise rate card and outcome/refund guarantee remain unresolved pending economics and legal review.
- Research Türkiye channel availability separately from Yaparo's API/SaaS approval. Score objective/format, OAuth and app review, forecast/report coverage, account/currency, lead sync, policies, maintenance and cost. Initial official-source findings and unknown channels are recorded in the blueprint; do not describe a candidate as integrated until access is verified.
- Define the pre-purchase calculator's channel-level budget, estimated reach/impressions/engagement ranges, assumptions, source and freshness, confidence, fees and platform spend. Never invent or present uncertain results as guarantees.
- Follow the [AI provider-combination strategy](docs/product/ai-provider-strategy.md): the local GPU is optional, not a runtime dependency. The provider-neutral creative-copy profile/harness supports bounded synthetic evaluation. GPT-6 Luna comparisons show a modest diversity improvement after a prompt iteration, but drafts remain generic and non-publishable. PR #246 adds a Gemini 3.8 Flash evaluation option; its first attempt stopped after one call with provider usage unverified, while the other eight calls were not sent. PR #247 fixes the benchmark exception path. On 2026-10-04, the owner authorized evaluation using existing OpenRouter credits up to USD 16 without top-up or auto-recharge; a dedicated no-reset cap was verified, and the owner checks the account balance. Two separately authorized image calls through the pinned ZDR-eligible Google Vertex endpoint completed upstream and were each charged USD 0.0336, matching OpenRouter Logs entries. The local runner failed to save output; exact response rejection remains unverified. It incorrectly required PNG, so now detects PNG/JPEG/WebP using documented media type and stores the matching extension. The USD 0.20 local reservation was reconciled; the local ledger records USD 0.12744185 spent and USD 0.00078075 reserved for an earlier unresolved GPT call, separate from provider billing. Any additional billable call requires renewed owner authorization. Keep providers disconnected from product routes; do not use OpenRouter video under current ZDR controls. No production provider is selected.
- Separate advertiser service requests from generated campaign leads; decide collection, purpose, destination, consent, account/role access, delivery/retry/audit, retention and deletion.
- Record Turkish advertising, KVKK/cross-border transfer, commercial electronic message, IP and sector-policy review as launch gates. Product policy checks are versioned and explainable; they do not replace counsel.
- Define spend/schedule/content boundaries, user authorization, tenant ownership, data recipients, category-specific retention/deletion/export, backup and restore. Keep all development and staging data synthetic.

**Current artifact:** `docs/product/growthtwin-service-blueprint.md` (draft, research timestamp 2026-09-29). It captures the service model, pricing arithmetic, channel evidence, calculator, strategy/testing, Türkiye legal review areas, launch readiness gate, phased delivery, source list and decision register.

The code-to-plan inventory is [the current system gap analysis](docs/product/current-system-gap-analysis.md). It records that a narrow single-owner authenticated workspace and synthetic campaign draft are implemented for local work; team roles, customer assets, a complete campaign/pricing/policy domain, provider adapters, and live integrations are not ready. The analysis is an implementation dependency map, not approval to collect real data or to settle open product decisions.

**Acceptance:** owner-facing review selects one initial advertiser workflow/objective and cohort hypothesis, first platform candidate (or records an explicit API/access blocker), first service boundary, lead destination/consent approach, supported first creative tasks, credit/fee hypothesis, beginner/pro defaults and bounded autonomy. Open legal, partner, privacy and pricing items have named evidence and next steps. The blueprint does not itself authorize real accounts, data, payment, publishing, ad spend or paid infrastructure. Those remain blocked until the separate readiness gate and owner decision.

**Decision:** the project owner delegated product and sequencing decisions. ADR-0008 selects a synthetic Ankara city-service quote/contact workflow, Google Search as the first technical channel candidate, the advertiser's own site as destination, no raw lead custody in Yaparo, and a fake-only adapter boundary. This is a prototype scope decision; user-demand validation, API access approval, forecasts, real-data/legal review, fees and live spend remain open gates.

**Completed:** PR #110 adds the workspace-owned synthetic campaign draft and owner-scoped services; PR #111 adds focused tenant-isolation/input validation tests. The anonymous `site.CampaignDraft` path remains separate.

**Completed:** PR #112 adds provider-free, source-traceable Google Search text assets with current RSA character limits and explicit unavailable forecast/keyword states. Local planning tests pass; the plan cannot publish or spend.

**Completed:** PR #113 adds a login-protected workspace list and preview launched from a fixed synthetic example. It uses owner-scoped create/read, shows source fields and unavailable forecasts, and keeps session drafts/public prototype separate. Free-text advertiser inputs are withheld until the real-data readiness gate. PR and post-merge CI passed.

**Completed:** PR #114 lets the owner change only bounded synthetic budget/duration choices or remove their own saved draft. Tenant isolation and choice enforcement are tested. PR and post-merge CI passed.

**Completed:** PR #115 adds browser end-to-end coverage for the authenticated synthetic workspace path, including mobile layout, owner isolation and bounded draft changes. PR and post-merge CI passed.

**Completed:** PR #116 replaces the stale Phase 0 login screen with a Turkish, accessible sign-in page that explains the synthetic-only scope, preserves the requested return path, and keeps public registration closed. PR and post-merge CI passed.

**Completed:** PR #117 shows the campaign's equal-allocation daily planning average, clearly separated from a platform spend limit or performance forecast. PR and post-merge CI passed.

## Phase 2 — Local campaign vertical slice

**Delivery focus (2026-10-15):** R-10 participant observations remain an open
acceptance item, but do not block independent engineering work. Complete the
first campaign journey in this order: downloadable current draft; a clearly
simulated channel lifecycle with safe retry and stop; controlled channel test
account integration once access is available; then the separate real-data and
production launch gates. Do not label the complete product ready while these
gates are open.

**Draft download (2026-10-15):** authenticated owners can download a UTF-8 text
review file containing the current preferred creative version, current plan,
media/fee distinction, separate Search starter assets and unresolved readiness
items. Changed source, version or preference invalidates an old download link.
The response is private/no-store and does not export other creative history or
account information. It is a synthetic review copy, not a platform-import
payload or publication authorization. No provider, migration or spend is added.

**Synthetic publishing rehearsal (2026-10-15):** the owner can start a fake
channel operation, deliberately simulate a connection failure, retry the same
operation and stop it. The revision/fingerprint boundary rejects duplicate or
stale forms; input changes prevent retry of the old plan. New starts after stop
create a new operation. State and event records cascade with draft deletion.
The page shows the last 20 events and keeps no-real-ad/no-spend language visible.
This is the local lifecycle slice in [ADR-0021](docs/adr/0021-workspace-publishing-rehearsal.md),
not live dispatch safety or distributed provider reconciliation. Next verify
test-account/API access prerequisites before implementing a real channel adapter.

**Goal:** connect the website to deterministic campaign records and evaluate draft generation without creating external side effects.

**Synthetic-prototype gate completed:** authenticated workspace ownership and owner-scoped campaign drafts exist for local synthetic scenarios. The [current system gap analysis](docs/product/current-system-gap-analysis.md) tracks the implementation boundary. Anonymous session drafts remain separate and are never backfilled automatically. Before real data or customer files, define the complete purpose-specific campaign/brand lifecycle, retention, export, deletion, tenant roles, and recovery guarantees; do not invent a universal retention period. See [ADR-0007](docs/adr/0007-workspace-ownership-and-retention.md).

Status: the minimal user-owned `Workspace` and owner-scoped synthetic campaign flow are implemented. PR #110 connected the campaign draft, #111 verified isolation, #112 added a provider-free Search plan, #113 added the authenticated fixed-sample list/preview, #114 added owner-scoped bounded setting changes/removal, #115 browser E2E coverage, #116 accessible sign-in with public registration closed, and #117 transparent arithmetic pacing. PRs #120–#121 define/test future asset states only; PR #122 adds a fail-closed synthetic action-policy contract. PR #185 adds bounded synthetic copy editing with immutable versions; PR #195 removes public free-text brief intake in favor of the fixed synthetic example. PR #198 records the audit that confirms workspace copy editing is suitable only for local synthetic use. Anonymous public drafts remain separate. All campaign records and inputs remain synthetic-only.

- Model advertiser/workspace, brand facts and assets, campaign brief, versioned multi-format ad creatives, destinations, user-defined caps, and status history.
- Add a server-side AI gateway with validated structured output and provider adapters. Begin with local Ollama plus synthetic data; use NIM only for synthetic evaluation.
- Add quality checks for missing/unsupported claims, format constraints, and budget/schedule completeness. A rejected or ambiguous output stays paused.
- Verify tenant isolation, schema validation, retry/idempotency behavior, and the campaign user journey.
- **Acceptance:** the local end-to-end path saves a campaign, produces or safely rejects structured ad drafts, explains its state, and cannot publish or incur ad spend.

**Asset boundary decided:** [ADR-0009](docs/adr/0009-asset-intake-processing-boundary.md) defines contract-first handling of future customer files. It keeps ownership, rights declaration, task permission and AI-provider permission separate; requires quarantine, scanning, provenance, fail-closed states and complete deletion; and explicitly does not authorize upload, persistence, storage, parsing, or AI calls.

**Completed in PR #120:** pure, storage/provider-independent asset workflow types define declaration gates, clean/unsafe/error scan outcomes, extraction, provider permission, and deletion states. The code performs no file operations, persistence, or AI calls.

**Completed in PR #121:** focused synthetic tests cover declaration gates, scan outcomes, extraction, provider permission, invalid construction, and deletion. Local tests, required PR CI, and post-merge CI passed. User upload and real data remain closed.

**Completed in PR #122:** add a pure synthetic policy check for authorization, destination/channel/content state, campaign and aggregate budget caps, schedule, and stop conditions. It reports reasons, fails closed on unknown inputs, and never authorizes live dispatch. Its caller-supplied evidence remains untrusted.

**Completed in PR #126:** add allowlisted synthetic evidence-source labels and a timezone-aware observation time to the policy result. Unknown labels and missing/naive timestamps fail closed. The returned metadata remains caller-supplied and untrusted; it is not authentication, freshness proof, atomic spend reservation, or live authorization.

**Completed in PR #128:** add a stable synthetic policy version and identifiers for the deterministic checks reported with each decision. This metadata is informational and in memory; the version does not authenticate evidence. No persistence, live integration, spend reservation, or dispatch authorization is included.

**Completed in PR #131:** bring the provider-free creative-variant workflow into the authenticated workspace campaign path. Versions are owner-scoped; brief/brand/city changes hide stale copy, while budget/schedule changes leave it current. The anonymous demo remains separate and no external AI/provider call was added.

**Completed in PR #133:** let the campaign owner choose one current copy variant as the preferred draft. Store the selection against the current version, hide it when source inputs change, clear it when a new version is generated, and label it as an informational review preference. No approval or publication action is implied. See [ADR-0014](docs/adr/0014-workspace-creative-preference.md). The workflow remains synthetic and provider-free.

**Completed in PR #185:** let the campaign owner revise a synthetic variant in a CSRF-protected, length-bounded form. Each edit appends a linked owner-edit version, preserves earlier copy, and clears any previous review preference. Earlier versions with the current source are viewable. A synthetic-only confirmation is required. This is not claim verification, approval, or publication; real advertiser text, AI, upload, account connection, and spend remain unavailable. See [ADR-0020](docs/adr/0020-workspace-synthetic-creative-editing.md).

**Completed in PRs #217–218:** define a provider-neutral creative-generation contract, validate bounded structured drafts, and route the anonymous fixed-sample and authenticated workspace copy paths through the deterministic local template adapter. Workspace versions record the generator identifier and preserve it across edits/restores; older versions are untouched. Generated results always remain review-required and non-publishable. No external AI provider, account, migration, publication, or spend is connected. The `synthetic_only` marker is a caller assertion, not authorization to process real data.

**Completed in PR #219:** add an opt-in Ollama adapter pinned to loopback, with structured JSON output and bounded request/response validation. Two single-run local Qwen3 1.7B/4B smoke tests were slow and repetitive; the adapter rejects repeated angles and remains disconnected from web routes. Neither model is selected for product use. See [AI provider evaluation](AI_PROVIDERS.md).

**Completed locally on 2026-10-03:** add `apps/web/scripts/evaluate_local_ollama.py` and run three synthetic brief types against installed Qwen3 0.6B/1.7B/4B. Eight of nine first-pass outputs were rejected for repeated/invalid keys/angles or timeout; the one shaped 0.6B output copied a forbidden offer from an untrusted note. A repeat of that brief was rejected for repeated angles. The runner now reports exact forbidden fixture phrases; this narrow screen is not semantic validation. No candidate is selected. `AI_PROVIDERS.md` records results and the offline-candidate gate.

**Claim-grounding design draft:** `docs/product/ai-claim-grounding-contract.md` proposes approved-source provenance and fail-closed handling. It is not an accepted ADR or an authorization to process real data.

**Prototype in PR #224:** add a persistence-free exact-source claim matcher and synthetic tests. It checks only an explicitly supplied individual claim against one owner-approved, non-expired fact; it does not discover claims or prove inventory completeness, source truth, law, or platform policy. It is not connected to web routes. Local focused tests and Ruff pass. Next demonstrate controlled copy assembly over exact approved fact text and assess its usefulness on synthetic briefs before any general model output is integrated.

**Controlled assembly in PR #225:** add a bounded, persistence-free synthetic helper that joins up to five individually exact-matched source statements and returns no copy if any supplied claim is unsupported or the total text exceeds its limit. It adds no model-generated wording. The caller's claim list remains unverified for completeness; source truth and legal/policy suitability remain out of scope. It is not connected to product routes. Local gateway tests and Ruff pass.

**Completed in PR #135:** give each authenticated workspace campaign a report page with reach, impressions, clicks, other interactions, contact requests, and media spend. Mark values unavailable until a verified channel source exists; show source and update status, with no fabricated metrics. Keep this distinct from the public prototype's simulated sample report. See [ADR-0015](docs/adr/0015-authenticated-campaign-report-empty-state.md).

**Completed in PR #138:** define a provider-neutral report metric contract that distinguishes unavailable data from a real zero and carries reporting window, unit/currency, source, and timezone-aware observation time. Focused tests use synthetic fixtures only. The contract is persistence-free and does not connect platforms or fabricate live results. See [ADR-0016](docs/adr/0016-campaign-report-metric-contract.md).

**Completed in PR #140:** connect typed unavailable metric values to the authenticated report shell. Show the planned campaign period only when its dates are defined; do not imply observed delivery. No source, value, persistence, or provider is added.

**Metric semantics (ADR-0017; documentation update pending PR #141):** define provider-neutral meanings for the six report categories, their attribution boundaries, reporting windows, currency, and unknown/stale-data handling. Do not flatten differing native platform definitions into comparable values. Keep this as a design contract; do not connect a platform or imply live reporting.

**Completed in PR #142 (research only):** map Google Ads API v25 official source fields to ADR-0017's metric definitions without an account or API request. The Search candidate mapping leaves reach unavailable, avoids double-counting interactions as clicks, and does not treat attributed conversions as delivered lead records.

**Completed in PR #143:** extend the provider-neutral report contract with explicit `not_connected`, `unsupported`, `partial`, and `stale` reasons, reason-specific provenance requirements, and metric-level user-facing explanations. A source-confirmed zero remains an available numeric zero. Required PR CI `36602784613` and post-merge CI `36603066285` passed. No provider, account, persistence, or real data was added. See [ADR-0018](docs/adr/0018-explicit-unavailable-report-metric-reasons.md).

**Completed in PR #145 (research only):** document source-specific zero-row completeness and freshness rules for the Google Search candidate. Official guidance confirms that segmented all-zero rows and dates with no metrics can be omitted, common metrics have different update guidance from conversions, and historical values can be adjusted later. Retrieval time must remain distinct from metric coverage/freshness; an absent row cannot become zero without independent completeness evidence. No adapter or account connection was implemented. Required PR CI `36604492004` and post-merge CI `36604748472` passed. See the [Google Search mapping](docs/product/google-search-report-metric-mapping.md).

**Completed in PR #149:** add a provider-neutral observation contract that separates requested and covered windows, source response completion, row presence, retrieval time, and freshness evidence. A pure evaluator classifies source-data time under an explicit source/metric-family rule; missing or future-dated source evidence is `unknown`, and retrieval time alone does not affect freshness. Available values require a complete exact-period row and evaluator-produced `current` status. Synthetic thresholds are policy examples only, not provider guarantees. No adapter, account, or real data is added. Required PR CI `36617325319` and post-merge CI `36617630617` passed. See [ADR-0019](docs/adr/0019-report-observation-coverage.md).

**Completed in PR #150:** distinguish a complete report observation with unknown freshness from stale and partial data, with a typed `freshness_unknown` unavailable reason. Keep it valueless and require the evaluator result to match; no live adapter was added. Required PR CI `36618254042` and post-merge CI `36618532218` passed.

**Completed in PR #152:** document the Google Ads evidence limits for per-row source time, report-window coverage, retrieval time, and provider SLO guidance. The reviewed official guides do not define a row-level `source_data_as_of` contract; record this as an evidence gap, not proof that no endpoint or metadata exists. Keep freshness unknown when the source cannot support the claim; no live adapter was added. Required CI `36619787628` and post-merge CI `36620109320` passed.

**Completed in PR #154:** separate planned campaign dates, actually observed reporting dates, and freshness status in the report summary. Until a verified source is connected, show no observed period and freshness as unknown. No SLO guarantee or live adapter was added. Required PR CI `36622723566` and post-merge CI `36622985685` passed.

**Completed manual review (2026-09-29):** inspected the authenticated report empty state at a narrow ~596 px viewport and a ~1265 px desktop viewport using isolated synthetic data. Planned dates, absent observed period, unknown freshness, and six unavailable metrics remained legible; no horizontal overflow was visible. No code or live integration changed. The prior anonymous browser session no longer exposes two still-stored synthetic drafts; see [continuity state](docs/continuity/STATE.md).

**Completed research (2026-09-29):** Google Ads Search remains a technical candidate for Türkiye based on documented `TR` targeting and the current country-restrictions list. The official API access levels, SaaS permissible-use review, payment-country dependencies, report capabilities, and test-account limits are recorded in the [feasibility note](docs/product/google-ads-search-turkiye-api-feasibility.md). Yaparo's own production access, external-client approval, Turkish account onboarding, forecasts, and legal/policy readiness remain unverified. No account or live API was used.

**Completed initial legal/product landscape (2026-09-29):** mapped official sources for ad-claim substantiation, online consumer checkout, commercial email/SMS/call follow-up, KVKK notice/consent and international transfers, and the current health-sector advertising rules. Product gates and unresolved legal questions are in the [Türkiye readiness map](docs/product/turkiye-advertising-privacy-readiness.md). This is not a complete legal review; no real data, payment or live campaign was enabled.

**Completed in the 2026-09-29/30 research slices:** [Google Search Türkiye sector eligibility matrix](docs/product/google-search-turkiye-sector-eligibility.md) records a dated, sourced pass for the synthetic local-service example and selected restricted/unsupported Google Ads categories. It separates tobacco and prohibited crypto offers, certification-gated crypto categories whose current approved-location list omits Türkiye, crypto-adjacent offers requiring Turkish-law review, housing/employment policy scope, and sourced political/election timing, audience and account-verification gates. It defines `eligible`, `restricted`, `not_supported`, and `needs_review` states with fail-closed behavior. The political/election row remains `needs_review`; legal interpretation of paid Search requires qualified review. This is planning research only; no specific advertiser, offer or campaign is cleared, and no account, API or publication approval is implied.

**Completed supplement research (2026-09-30):** the matrix now separates supplements from medicines/medical devices and ordinary foods. It records product-by-product Ministry approval lookup, claim-level Turkish review, Google's specific global unapproved-substance prohibitions, and the 2026 restriction against advertising supplements as replacements for normal diet. This does not assess any individual product, ingredient list, claim, or creative. Ordinary foods and adult services remain `needs_review`; no sector selector or external action is enabled.

**Completed ordinary-food research (2026-09-30):** the matrix records the general Turkish prohibition on misleading food advertising, current food-label/claim review needs, Google's general misrepresentation rules, and the limited territory/network scope of its HFSS policy. It also marks novel foods and child-directed campaigns for exact product/channel checks. No individual food or claim is cleared; see PR #167.

**Completed adult-services research (2026-09-30):** the matrix separates Google-prohibited paid sexual companionship/escort offers from dating services that require Google certification and adult-only handling, and from other sexual-content categories with age, query, destination and local-law restrictions. It records the related Turkish criminal-law questions without deciding that a particular advertiser or intermediary is lawful. No specific service is cleared; see PR #168.

**Completed in the 2026-09-30 synthetic slice:** ADR-0018 and `approvals.eligibility` define an in-memory, provider-free decision contract for the four matrix outcomes. Missing/stale rule metadata and unknown/unmet conditions fail closed; combining platform and legal rule claims keeps the most restrictive result. The contract is not connected to campaign views, persistence, account APIs, or publication.

**Completed in the 2026-09-30 preview slice:** the authenticated campaign detail page shows the dated status for the fixed synthetic home-maintenance example, its source/version and demo-only re-review date, and a clear explanation that the check is not legal clearance or permission to publish. Its 30-day review interval only demonstrates the stale-rule transition; it is not a legal or platform deadline. The local evaluator moves overdue rules to `needs_review`; there is no account/API or publication connection.

**Current research slice:** PR #166's supplement research passed required CI `36739134600` and post-merge CI `36739507855`. PR #167's ordinary-food research passed `36740203483` and `36740519517`; PR #168's adult-services work passed `36741167177` and `36741491268`; PR #169's status refresh passed `36742863063` and `36743130604`. PR #170 added Turkish Law 4207 constraints to the Google tobacco policy stop; required CI `36743525443` and post-merge CI `36744652209` passed. PR #171 documents political/election advertising gates for Türkiye; required CI `36745452282` and post-merge CI `36745746001` passed. Keep unresolved offers at `needs_review`, examples synthetic, and the preview disconnected from external actions.

## Phase 3 — First publishing and reporting integration

October 19: fixed Google test create/read/pause lifecycle verified through the local application, with atomic PAUSED resources and durable no-resend intent. Selected workspace drafts now have immutable review/consent and a separate durable PAUSED TEST dispatch lifecycle (ADR-0023/0024). Live serving/spend remain closed; see ADR-0022.

October 17 setup: dedicated Google test accounts, Cloud Test API access, OAuth web client and one test user are prepared. Local-only OAuth routes and encrypted storage are implemented but disabled by default. Google token exchange, encrypted storage and a targeted test-account API read are verified. The local UI now displays a recent explicit test verification; no publication is enabled. Follow the remaining test-integration gates in [test integration readiness](docs/product/google-ads-test-account-readiness.md).

**Goal:** prove one authorized destination before expanding channel coverage.

- Choose the first paid-ad platform only after checking access and eligibility in Türkiye, app review, supported campaign/creative formats, authorization requirements, reporting coverage, policy constraints, and maintenance cost.
- Build OAuth/account connection and revocation, narrow scopes, a test/sandbox path, immutable action records, safe retries, and a user-visible emergency stop.
- Require explicit advertiser authorization and a hard platform-enforced spend boundary. Never let a model modify a cap or directly invoke a publishing API.
- Import performance data and present plain-language results. Do not imply that automated optimization is supported until the API and safe bounds are verified.
- **Acceptance:** a controlled test account can publish, report, stop, and recover from a simulated provider failure without exceeding its configured limits.

## Phase 4 — Limited beta and production readiness

**Goal:** invite a small pilot group only after the real operational and data protections are ready.

- Finish staging E2E, backup/restore, rollback, deployment-revision health reporting, and a tested CI merge gate.
- Review platform approvals, privacy notice/consent, model/provider data terms, data deletion/export, retention, OAuth token handling, accessibility, monitoring, and incident procedures.
- Estimate production hosting and AI costs; ask the owner before any new recurring service or advertiser campaign-spend feature is enabled.
- Select a small pilot cohort from the Türkiye market after the first workflow is validated; clinics may be included but are not the exclusive target.
- **Acceptance:** a documented pilot run stays within the approved service budget and advertiser caps, can be stopped and recovered, and produces a useful report with no unreviewed safety failures.

## Phase 5 — Omnichannel capability expansion

**Goal:** expand toward the Omneky capability benchmark after one complete channel is validated and the product has evidence from real user workflows.

- Add channels one at a time after verifying Türkiye-specific API access, platform approval, formats, reporting, policy obligations, and operating costs.
- Expand ad production and editing across image, short-form video, and other supported formats; make creative variations and review tools easy to use.
- Add cross-channel and creative-level analytics, plain-language insights, and explainable recommendations.
- Add A/B testing and bounded optimization only where the platform supports reliable measurements and advertiser-defined guardrails.
- **Acceptance:** every supported channel and optimization action has tested authorization, spend/schedule limits, traceable state changes, idempotent retries, stop/revoke behavior, and understandable reporting. Unsupported or uncertain actions remain paused.

## Deferred until evidence supports them

- Broad simultaneous channel coverage, vertical-specific workflow depth, native mobile clients, organic-content calendars, long-form video generation, full CRM, vector search, microservices, a separate queue service, and automatic cross-channel budget allocation.
- Production AI/provider selection and production hosting. The provider-neutral architecture and synthetic candidate shortlist are documented. The owner-reported USD 16 existing OpenRouter balance supports bounded synthetic evaluation only, after the owner verifies account-side settings and the local cost controls are ready; no production selection is implied. Do not top up or enable auto-recharge.

## Existing Phase 0 tasks retained as gates

Use the [Phase 0 staging verification sequence](docs/phase-0-staging-verification.md) to complete the remaining database backup/restore and cost/CI gates safely. The staging profile-edit browser E2E passed on v14 (`69476a62`), v15 (`c13ba96`), and v16 (`8e29944`) with the disposable synthetic account. On 2026-10-03 Heroku rollback created v17 from v15 and v18 from v16; matching health revisions and E2E passed on both, and neither release applied migrations. The v15/v16 source diff contains documentation files only, so this verifies the rollback mechanism for same application code. GitHub CI and `main` branch protection were also verified. The billing page displayed $0.00 current usage and a $1.37 September invoice marked Pending; this is not a finalized total. No additional resource was added. Configured database/Heroku recovery remains unverified.

The local `growthtwin` schema-only dump/restore passed on 2026-10-01 (11 public tables matched; target contained no rows). A separate, isolated PostgreSQL 18.6 cluster also passed a full Django migration plus fabricated-account custom-format dump/restore; the marker, Django system check, and migration check passed. Neither rehearsal verifies the `growthtwin` database's records or Heroku recovery. Temporary synthetic rehearsal files remain; the recursive cleanup attempt was blocked by tool policy and no alternate deletion method was attempted. Controlled staging rollback is verified only between v15 and v16, which contain identical application code; rollback across code or schema changes remains unverified. The September invoice is still marked Pending, and actual final usage is unknown. These checks are useful before an external beta or production release, but no longer block a local synthetic-data website prototype. Continue to use the existing approved Heroku resources only; do not add a paid dyno, database, add-on, AI service, or production environment without a new owner decision.

Session-scoped prototype drafts must remain synthetic. Heroku staging now has a
daily `python manage.py clearsessions` job scheduled at 00:00 UTC through
Heroku Scheduler. The 2026-09-29 00:00 UTC execution is verified in Heroku logs
with exit status 0. Actual one-off dyno cost remains unverified. Scheduler is
best-effort; do not infer a real-data retention guarantee from session expiry
or this schedule.


Local Google workspace preparation (2026-10-19): selected creative and plan can be reviewed as an immutable package and explicitly approved for later PAUSED TEST dispatch. Source/selection/target changes invalidate the current approval. This step performs no Google call and does not yet dispatch workspace drafts. See ADR-0023.


Workspace Google TEST dispatch verified (2026-10-19): selected synthetic creative now creates a separate durable PAUSED campaign from its immutable approval. The second consent explicitly shows example.com test URL override, inclusive daily TRY budget, account-local date-times and Ankara/PRESENCE mapping. Browser create/read/stop passed; 71 focused tests passed. One intent per draft prevents re-creation after timeout/restart; independent read/stop survives source changes. Live serving/spend remain gated. See ADR-0024.


Live Google Search readiness audited (2026-10-19): [the current gate list](docs/product/google-search-live-readiness.md) separates TEST evidence from production account/consent, destination, spend caps, privacy and recovery. A local signed owner-only validateOnly control now verifies a separate CUSTOM_PERIOD/totalAmountMicros candidate; Google TEST accepted the 5,000 TRY synthetic example without creating resources or modifying the daily-budget ledger. 79 focused tests passed. Next verify a new durable PAUSED TEST total-budget resource, retaining old daily read/stop. Live serving/spend remain closed; see ADR-0025.


Total-budget TEST dispatch verified (2026-10-19): new profile v2 creates non-shared CUSTOM_PERIOD budgets with exact totalAmountMicros; stored v1 DAILY ledgers retain read/stop and cannot be converted/reset. Browser created a new synthetic draft, sent 5,000 TRY total PAUSED, reconciled repeat create and confirmed stop; old daily stop also passed. 82 focused tests passed. No serving/spend or production cap exhaustion evidence; see ADR-0026. Next inspect current Cloud API/OAuth production-access gates read-only before planning any upgrade or real account flow.


Read-only Cloud audit (2026-10-19): Ads API is enabled with Test access (15,000 test operations/day); Explorer Apply button visible, not submitted. OAuth is External/Testing with one test user; Publish app disabled pending Branding. Public home/privacy/terms URLs and authorized domains are absent; owner has no domain yet. Scope declaration tables empty (not proof that the existing runtime TEST grant was revoked). See [production-access audit](docs/product/google-production-access-audit.md). No access/permission/publication/account changes were made.

Public identity preparation (2026-10-19): [page requirements](docs/product/public-identity-page-requirements.md) now define identity/domain dependencies, page acceptance criteria, code-derived data flows, protected ledger deletion/recovery gaps and missing owner/legal decisions. Local, clearly draft contact/privacy/terms pages with footer links and no data collection are implemented. 5 focused tests, ruff and desktop/mobile browser checks passed. Final identity/domain and data lifecycle decisions remain open. Test/production projects and credentials stay separate in the production plan; no project, domain or service was provisioned.

Data lifecycle contract (2026-10-19): [ADR-0027](docs/adr/0027-data-lifecycle-and-no-resend-boundary.md) defines separate action outcomes, category triggers/open retention facts, revocation scope and immutable-ledger/restore boundaries. Pure decision, scoped observation and eligible ticket issuance contracts are implemented; 42 focused DB-free tests, ruff and independent reviews passed. Exact replay is a no-op; stale/conflicting evidence is rejected and unresolved tickets cannot be replaced. Immediate revocation has a bounded separate priority slot. The October 20 read-only fixed-synthetic preview is implemented; 56 focused checks including its nine tests and five information-page tests passed, plus desktop/mobile/keyboard review. No provider execution or deletion effects. Next: isolated owner-scoped synthetic request/operation persistence with atomic revision checks. Real periods, erasure execution, provider/backup evidence and qualified review remain launch gates.

Synthetic lifecycle persistence (2026-10-21): owner-scoped service-only request/operation storage now uses typed versioned metadata, unique request/receipt identities, transactional receipt writes and revision-conditional updates. Creation replay preserves current progress; stale/conflicting updates fail closed. No HTTP/provider/credential/erasure path is connected, and the stored fixture barrier does not guard existing Google routes. 62 local focused tests passed; PostgreSQL CI 39642369641 subsequently passed all 343 tests (including the competing-writer test) and 10 browser tests; main CI 39642731033 passed after PR #298 merged. Migration drift/ruff checks and independent re-review passed. Only ephemeral test DB migrations were run; preserved Google DB/grant/ledgers and Heroku are unchanged. See ADR-0027. Next: fixed-fixture authenticated owner start/status journey, with CSRF-safe start and no browser-supplied outcome/proof flags.

Synthetic owner closure journey (2026-10-21): a default-off fixed-example start/status flow now uses the owner-scoped store under `/workspace/control/`. CSRF-protected POST requires explicit synthetic confirmation; extra submitted proof/outcome/ID fields are rejected. Stable server fixture IDs and one transaction preserve one request/STOP receipt under repeat start; GET/HEAD status is read-only and clearly distinguishes example outcomes from real account results. Campaign-list navigation is flag-gated. 80 focused local tests passed; PR #299 required PostgreSQL CI 39644787052 passed 362 tests including concurrency and 10 browser E2E tests; main CI 39645131181 also passed. Ruff, migration drift, independent review and desktop/mobile/keyboard browser checks passed. Browser fixture on loopback 8011 has an isolated DB/cookies and no real account or password. No provider executor, Google DB/grant/ledger, Heroku, schema or production change. Next: a bounded explicit fake-only STOP result demonstration for the saved example using operation/revision-bound observations; no browser-supplied proof or real provider action.

Bounded synthetic STOP results (2026-10-21): the owner journey now records a fixed confirmed or uncertain result from a local deterministic fake. Separate scenario IDs preserve the existing default fixture. Explicit CSRF-protected confirmation and a 10-minute signed owner/workspace/request/operation/revision token bind the result; raw browser outcome/proof fields are rejected. Exact persisted replay bypasses the fake and creates no second operation/event. GET/HEAD remains read-only; revocation/erasure states stay separate. 94 local focused tests passed; PR #300 required CI 39647636463 passed 377 PostgreSQL tests and 10 browser E2E tests; post-merge main CI 39648069200 passed; ruff, migration drift, independent review and desktop/mobile/keyboard checks passed. Preview 8011 retained the isolated fixture DB across restart. No real Google DB/grant/ledger, provider, credential, Heroku, schema or spend change. Next: isolated synthetic new-work/callback guard integration, then the unified advertiser journey. See ADR-0027.

## Accepted delivery sequence — 2026-10-21

1. Finish the saved synthetic closure example with explicit fixed fake STOP
   results, preserving replay/conflict safety. Completed in merged PR #300 with
   required and post-merge CI verified.
2. Bind closure safety to new-work and callback processing, initially only in an
   isolated synthetic coordinator/fake adapter. Verify scoped ownership/generation,
   durable blocking and late/in-flight outcomes; inspect existing TEST hooks from
   code before a separately reviewed real-runtime mapping. Synthetic part completed
   in merged PR #301; actual Google runtime mapping remains a production gate.
3. Unify campaign creation, current creative choice, budget/target review, consent,
   dispatch status and reporting into a coherent advertiser journey. Keep unknown
   metrics and readiness gaps explicit and customer data gated. Read-only six-stage
   overview merged in PR #302 with required/main CI passed. Protected TEST page
   navigation merged in PR #303; required/main CI passed. The current slice
   begins the isolated connector identity/generation prerequisite for step4.
4. Complete production identity/domain/contact, truthful public policies and data
   lifecycle decisions, provider/tenant secret handling, configured DB recovery,
   current campaign staging E2E and Google production-access requirements. Costs,
   permissions, account access and legal decisions require their applicable gates.
5. Only after those gates: separately authorized first real campaign with verified
   advertiser/account/financial consent, enforceable spend caps, stop and reports.

Then expand customer asset intake/versioning, evaluated production AI, credit/
service/payment accounting, creative experiments and additional ad channels.
This sequence does not itself buy a domain/service, publish an app, raise access,
accept real data, spend media budget or select a production provider.

Synthetic connection work guard (2026-10-21): a positive fixed-fixture scope registry defaults to quarantine. Only current registered OPEN scope/generation/revision can run local fake CREATE/REFRESH/CALLBACK_SAVE. Closure intake and fake work share the owned workspace lock; closure creation and scope blocking commit together. Late callbacks/replay, missing/unknown scope, old generation and quarantine deny work; STOP success does not reopen it. 108 local focused tests passed with five PostgreSQL-only skips; PR #301 required CI 39649793207 subsequently passed 393 PostgreSQL tests including those races and 10 browser E2E tests; post-merge main CI 39650308546 passed. Ruff, migration drift and independent review passed. At the guard milestone migration 0002 ran only in ephemeral test DBs. The later journey browser restart also applied it to the isolated fixture DB; preserved Google DB/grant/ledgers and Heroku remain unchanged. Source-only actual TEST hook map is in ADR-0027; fixture IDs are not actual Google connections and no real runtime guard is wired. Next: unified local advertiser campaign stages, retaining production identity/privacy/access/recovery/financial gates.


Campaign stage overview (2026-10-21): owner-scoped `/workspace/campaigns/<id>/journey/` joins campaign, current creative preference, plan/budget, TEST approval, stored TEST dispatch and report navigation. Ordinary GET reads only scoped local metadata; no credentials, provider requests or writes. Approval existence is not current consent; stored TEST state is not live status or serving. Source/version changes invalidate creative preference, and existing dispatch review takes priority over a new submission. Exact existing loopback controls and prerequisite visibility are retained. 63 focused tests (16 new) passed; ruff, migration drift, independent review and desktop/mobile/keyboard checks passed. No new migration or actual Google operation. PR #302 required CI 39653009712 passed 409 PostgreSQL tests and 10 browser E2E tests; post-merge main CI 39653441692 passed. See ADR-0028. Protected TEST page navigation follows below.


Protected TEST journey navigation (2026-10-22): review, stored status, dispatch result and validateOnly result now share the owner campaign shell and links to stages/plan/report. Owned recoverable errors preserve navigation; unresolved/foreign drafts expose no campaign link. Stored status GET reads metadata only, with no payload, credential, provider request or write; no intent means no read/stop controls. Shared allowlisted labels distinguish stored TEST state from an explicit operation-time observation. Existing exact loopback/owner/CSRF/signed consent/no-resend/stop behavior is unchanged. 55 focused tests (14 new navigation tests) passed; ruff/format/migration drift, independent review and isolated desktop/mobile/keyboard review passed. No new migration or actual Google operation. PR #303 required CI39716957472 passed423 PostgreSQL tests and10 browser E2E tests; post-merge main CI39717264957 passed. Durable identity foundation follows below.


Durable connector identity foundation (2026-10-22): separate ConnectorIdentity/ConnectorGeneration metadata gives one google_ads_test slot per owned workspace, server-generated connection/generation UUIDs and a permanent request/generation receipt chain. Registration/rotation replay returns current metadata, including later generations or a permanent block; stale/conflicting requests and inconsistent history fail closed. All reads/writes lock owned workspace then connection; rotation uses conditional revision/generation update and atomic receipt writes. Only quarantined/blocked states exist; neither authorizes provider work, and no activation/reopen API is present. 15 new local tests plus 14 existing work-guard tests passed (29 total); four PostgreSQL-only races subsequently passed in PR304 required CI39719120618 (440 PostgreSQL tests and10 browser tests); main CI39719367350 also passed. Ruff/format/migration drift and independent source review passed. Migration0003 ran only in ephemeral test DBs. No runtime/credential/grant/closure mapping or actual provider, preserved DB, browser fixture, Heroku or UI change. See ADR-0029. Next: a closed-by-default, generation-bound authorization-attempt receipt/result coordinator using local fake outcomes before separately reviewed actual OAuth hook integration.


Synthetic authorization attempt coordinator (2026-10-22): default-off internal rehearsal binds fixed-example attempts to owned connector UUID/generation/revision, typed confirmation/scenario and a fixed10-minute lifetime. A DB constraint allows only one pending/running attempt per connection. Running reservation commits before the local fixed fake; result acceptance rechecks ownership, current generation/state, expiry, switch and immutable attempt binding. Concurrent/in-flight/terminal replay cannot invoke the fake again; failed/late/stale/blocked/disabled/contradictory outcomes never become accepted. Accepted is only an ALLOW example completed within its lifetime, not a grant or provider permission; identity stays quarantined. New25 tests (23 local,2 PostgreSQL races) plus identity tests:38 local passes and4 PostgreSQL skips. Ruff/format/migration drift and independent re-review passed after tightening corrupt accepted metadata checks. Migration0004 applied only in ephemeral test DBs. No actual OAuth/credential/provider/runtime/UI/preserved DB change. PR305 required CI39720686706 passed465 PostgreSQL tests and10 browser E2E tests; main CI39720985597 passed. See ADR0030.


Scoped Google TEST candidate boundary (2026-10-22): a new default-off, unwired adapter binds a separate process-local state/PKCE handshake to owned workspace/session hash, connector UUID/generation/revision and a5-minute durable receipt. Existing legacy grant presence blocks exchange before client loading; no current grant migration. Exchanging receipt commits before mocked transport; current scope, lifetime and immutable binding are rechecked before a separate encrypted google-candidate-* envelope. Candidate metadata never activates the quarantined connector and current readers/routes ignore that schema/path. After outbound uncertainty, failed storage/DB persistence or late scope change, no automatic exchange retry or revoke occurs. Twenty new local tests plus legacy backend/OAuth/store/view tests:51 local passes,2 PostgreSQL skips. Ruff/format/migration drift and independent source review passed. Migration0005 applied only to ephemeral test DBs; no actual credential/provider/filesystem/preserved DB/Heroku/UI operation. See ADR0031. PR306 required CI39722697389 and main CI39722996360 passed487 PostgreSQL tests and10 browser E2E tests.


Scoped candidate advisory readback (2026-10-22): strict version-one envelope binding matches owned receipt/schema/scope/client and bounded refresh material. Default-off unwired inspection reads only committed current quarantined candidates; pending/rejected/uncertain attempts have explicit dispositions and cannot promote possible orphans. Post-read ownership/current scope/immutable receipt/client/legacy checks gate an advisory match only; no activation, provider permission, mutation or retry. Five-minute handshake expiry does not expire stored inactive candidates. Twenty-one new local tests and one PostgreSQL race; focused candidate/readback/backend run:55 local passes,3 local race skips; PR307 required CI39747787250 and main CI39748174729 passed509 PostgreSQL tests and10 browser E2E tests. No migration or actual secret/provider/preserved DB/browser/Heroku operation. See ADR0032. Next: fixture-only owner/session/CSRF endpoint design and rehearsal before separately reviewed real adapter rollout.


Synthetic authorization session journey (2026-10-22): double-default-off owner/session/CSRF pages now rehearse two fixed examples via the synthetic coordinator only. Signed ten-minute tickets bind exact server scope/action; start only reserves, separate perform runs the fake, GET never runs work, replay cannot duplicate it. Origin-session metadata marker limits status/result access. Framework errors receive private/no-store/noindex headers after independent review identified missing prefix coverage. Seventeen new endpoint tests plus coordinator:40 local passes,2 PostgreSQL skips. Isolated desktop/mobile/keyboard browser test passed; screenshots reviewed. No real adapter/provider/credential/preserved DB operation or migration. Last-example session marker and no recovery after session loss are explicit fixture limitations. See ADR0033. Next: design/test pending or uncertain candidate and lost-session recovery dispositions while preserving legacy grants and separate stop/reconcile access. Actual adapter rollout remains gated.


Connection recovery dispositions (2026-10-22): owned metadata-only assessment separates callback wait/restart review, uncertainty reconciliation, inactive review and rejected history; scope/session flags never permit retry or activation. Synthetic-only signed CSRF recovery reopens an existing fixed example in a new owner session by changing only its session marker. Receipt expiry/scope/scenario are bound; no begin/perform, new receipt or deadline extension. Run guards deny stale/expired/running/terminal execution.18 new tests plus17 prior journey tests:35 local passes; extended isolated browser and mobile visual check passed. No migration or actual credentials/provider/preserved DB/Heroku operation. See ADR0034. PR308 required CI39752232154 and main CI39752610827 passed527 tests and11 browser tests. Next: explicit RESERVED-only retirement with generation fencing in mocks; uncertainty cannot be retired/retried automatically.


Reserved candidate retirement (2026-10-22): default-off unwired owned service requires explicit typed confirmation and current quarantined RESERVED scope. Generation rotation and original REJECTED/retired_before_exchange receipt commit together; unique retirement request and replacement-generation metadata are validated against permanent history. Exact replay returns current identity even after later rotate/block. All non-reserved/stale/blocked or other unresolved history denies. No I/O, cleanup, retry, activation or change to legacy grant/stop/reconcile.14 new local tests plus2 PostgreSQL races; with existing adapter/recovery:42 local passes,4 PostgreSQL skips pending CI. Independent final review passed. Migration0006 only in ephemeral test DBs; no actual credential/provider/preserved DB/UI/Heroku operation. See ADR0035. PR309 required CI39756480228 and main CI39756903416 passed545 tests and11 browser tests. Next: separately reviewed scoped endpoint/session/CSRF wiring with mocked transport, normal runtime off.


Closed scoped TEST endpoints (2026-10-22): separate overview/start/callback/retire routes bind signed5-minute forms to configured owner/workspace/session and immutable scope. Both endpoint/candidate flags remain False plus exact loopback/DEBUG/no-forward guards. Separate scoped redirect leaves legacy default/runtime unchanged. State digest marker rejects old/wrong callback before consuming current handshake; allowed callback always303-cleans URL. Retirement digest rechecked under service locks after independent review found a check/use race.25 new tests plus existing adapter/retirement/legacy:76 local passes,4 PostgreSQL skips; independent final review approved. No new migration or actual provider/credential/preserved DB/Heroku operation; no manual browser check. See ADR0036. PR311 required CI39765174203 and main CI39765596754 passed586 PostgreSQL tests and11 browser E2E tests. Follow-up readiness audit: the owner-approved scoped redirect was registered and both old/new URIs re-read; API remains Test and OAuth External/Testing. Current customer.test_account and isolated runtime binding remain unverified. See [October 22 audit](docs/product/google-production-access-audit.md#scoped-test-hazırlığı--22-ekim-2026). Next: complete isolated candidate-exercise prerequisites with the legacy grant/ledgers preserved; flags remain off, no OAuth/refresh/adoption/publish/cleanup.


Closed isolated preparation (2026-10-22): a fresh temporary SQLite database now
has distinct explicit numeric owner/workspace IDs, an unusable-password synthetic
owner and quarantined connector. Zero candidate/Google ledger rows; normal scoped
flags remain False. Credential/client/transport calls denied in preparation; no
server, OAuth, refresh, preserved DB/grant/ledger or Heroku operation. Existing
fixed encrypted client is NOT a separate client and was not loaded. Fresh TEST
child proof, runtime/client/session/logging and uncertainty prerequisites remain
open. See [exercise preparation](docs/product/scoped-test-exercise-preparation.md).
PR312 required CI39768028595 and main CI39768447961 passed586 PostgreSQL tests
and11 browser E2E; not actual isolated OAuth evidence.


Scoped TEST preflight and closed runtime (2026-10-22): one bounded legacy-grant
refresh plus one fixed Ads identity read verified the configured non-manager TEST
child and registered client. Encrypted client/grant hashes and preserved DB stat
unchanged; no credential write. Separate closed loopback8002 synthetic login/logout
and404/no-store/no-referrer callback checks passed. Temporary login disabled after
explicit shutdown cleanup. A separately reviewed one-shot candidate launcher was
started under the owner's action-time approval; one RESERVED attempt reached a
Google passkey block and expired before EXCHANGING. Exact candidate file absent;
process stopped, synthetic password disabled and sessions cleared; original
RESERVED history retained without retry/rotation. No successful exchange/candidate/
adoption claim. Normal source flags False. See [current protocol/evidence](docs/product/scoped-test-exercise-preparation.md).
PR313 required CI39792541560 and main CI39795773585 passed586 PostgreSQL tests
and11 browser E2E. No new local automated test suite was run for this slice.


Inactive scoped TEST candidate (2026-10-22): after the user's Google verification
and resumed approved flow, the exact expired RESERVED was retired via the existing
service with stable request/digest and generation fencing; history retained.
A separately reviewed history-bound single-exchange launcher completed callback
into CANDIDATE on the same synthetic owner/workspace. Independent metadata/file-
existence review confirmed quarantined revision1, old rejected receipt, current
candidate and nonempty exact file. No encrypted contents/token validity/candidate
account proof inspected. Logout, process stop and explicit unusable-password/
session0 cleanup completed; source flags False, no activation/consumer/advertising.
Origin-session/process-secret loss prevents existing guarded readback; next design
owner-bound inspection-only recovery with unchanged receipts, using synthetic data.
See [exercise result](docs/product/scoped-test-exercise-preparation.md).
No application code change or new local automatic test suite in this slice.


Inspection recovery permit metadata (2026-10-22): a default-off service now issues
and irreversibly consumes a five-minute, new-session owner/workspace/candidate/
generation/revision/immutable-receipt-bound permit. Original candidate/session hash
and history never change. One permit per candidate; exact replay preserves current
state/deadline, no replacement/renewal, caller transaction or double consumption.
CONSUMED is metadata only, not file-read proof or permission for existing readers.
No reader, HTTP, credential/path/client/provider/activation integration. New27 tests
plus readback/retirement:60 local passes,5 PostgreSQL-only skips; formatting/lint,
migration drift and independent source review passed. Migration0007 only in ephemeral
test DBs; no protected Google DB/grant/Heroku operation. See [ADR0037](docs/adr/0037-metadata-only-inspection-recovery-permits.md).
PR316 required CI39815782725 and main CI39816401402 passed613 PostgreSQL tests
and11 browser E2E, including both permit races. The mocked executor follows below.

Synthetic inspection recovery executor (2026-10-22): a separate double-default-off
service consumes the permit directly before an internal fixed in-memory probe.
Only the fabricated inspection-client receipt is eligible; callers cannot supply
a reader, path, envelope or snapshot. Owned quarantined scope, original receipt
digest, new-session HMAC, exact consumed snapshot and permit time are rechecked
after claim, before simulated read and after completion. Fixture client/legacy
checks surround that read outside DB locks. Results contain only safe metadata
and explicit synthetic_match or bounded negative dispositions. CONSUMED remains a
claim, not a stored inspection result; errors do not enable retry or replacement.
New37 tests:35 local passes,2 PostgreSQL skips. With permit/readback/retirement
suites:95 local passes,7 PostgreSQL skips; formatting/lint/migration drift and
independent source review passed. No actual reader/provider/file operation,
migration, UI, activation or deployment.
See [ADR0038](docs/adr/0038-synthetic-inspection-recovery-executor.md).
PR317 required CI39836461900 and main CI39837030362 passed650 PostgreSQL tests
and11 browser E2E. The separately gated recovered reader follows below.

Closed recovered reader (2026-10-22): a new default-off service verifies the
configured owner/workspace and captures exact client/legacy/candidate locations,
then directly consumes the permit before any file observation. Bounded client
and candidate decoding replaces the old unlimited reader only in this adapter;
legacy contents remain unread. Scope/session/digest/time and captured configuration
are rechecked, including after final client observation and DB-lock waits. A local
envelope match is advisory, not token/account proof or activation. Source has no
HTTP route, refresh/provider/write/adoption operation; normal switches remain off.
58 new tests:56 local passes,2 PostgreSQL skips. Combined focused suites:116 passes,
7 PostgreSQL skips; formatting/lint/migration drift and independent review passed.
Direct session-bearing helper calls also mask Django traceback locals; four tests
verify actual reporter filtering. The protected reader entry already masks its chain.
No new migration or actual protected DB/file/credential/provider/Heroku operation.
PowerShell checks are mocked source contracts, not actual Windows DPAPI evidence.
See [ADR0039](docs/adr/0039-closed-recovered-candidate-readback.md).
PR318 required CI39843136730 and main CI39843726808 passed708 PostgreSQL tests
and11 browser E2E. The dependency-download guard passed on both runs.

Windows inspection rehearsal/preparation (2026-10-22): a source-reviewed harness
actually encrypted/read disposable fabricated files on Windows;12 checks passed,
cleanup complete and DB/network/legacy boundary attempts zero. Valid Turkish and
30000-character payloads round-tripped; malformed/missing/oversized inputs rejected.
The plaintext-overflow example hit the encrypted cap first; no independent later
plaintext-cap proof. A separate read-only audit of the SAME prepared DB verified
unchanged bytes/size/mtime, coherent retired/current history, disabled login/session0,
regular exact client/candidate and private ACLs; no credential contents opened.
At that audit migration0007/permit table were absent; no schema/credential operation.
Subsequently, after PR320 handoff and renewed owner instruction, a private SAME-DB
backup and exact ONLY-forward0007 plan were verified and independently reviewed.
One APPLY completed: old application schema/data/history preserved except the0007
recorder row, new permit table empty, backup unchanged. Post-operation RO audit
passed. Three earlier ACL preparation failures stopped before copying DB data;
reviewed native ACL handling resolved them. No permit/credential read/provider/
activation/deployment. See [exercise preparation](docs/product/recovered-inspection-exercise-preparation.md).
Next: separately reviewed one-shot client-bound inspection launcher/failure plan;
never rerun completed preparation, reset history/claims or restore over consumption.


Launcher preparation (2026-10-23): reviewed read-only plan passed same post0007
candidate/history/private-backup admission with zero permits/sessions. Separate
synthetic operator-session bootstrap primitive passed14 focused fabricated local
checks; it is not called by plan. No actual session/permit/credential/provider
operation or execute command. Next: integrate/rehearse/review the single-attempt
launcher and terminal-failure flow before any actual claim. See exercise preparation.


Session expiry hardening (2026-10-23): the isolated synthetic session primitive now
captures expire_date before insertion and rechecks the exact row, owned scope,
wall-clock and five-minute monotonic budget before returning, including after DB
queries. Changed expiry is retained for review, not silently deleted.20 focused
fabricated local tests passed; no preserved session/permit/decoder/provider use.


Fabricated inspection coordinator (2026-10-23): internal test-only orchestration
now combines the synthetic operator session, permanent exclusive attempt marker,
one permit issue and the real consume-before-decode reader. Fixed derived decoder
paths/quotas, denied provider/write/socket boundaries and cleanup/history checks
produce scalar results only. No CLI, production route, private fixture creator,
Windows DPAPI runtime evidence or protected-candidate execution is introduced.
See docs/product/recovered-inspection-exercise-preparation.md.


Fresh private Windows fixture (2026-10-23): a no-path/no-credential-input CLI now
creates only a new private fabricated DB/client/receipt, runs the real bounded
DPAPI + one-shot inspection coordinator and disposes exact inventoried files.
Actual four fresh scenarios (match, client change, invalid envelope, missing file)
passed with consumed permit, replay refusal, session0/history preserved, verified
private ACLs, complete cleanup and zero forbidden boundary attempts.30 new mocked
unit tests plus37 prior focused tests passed (67 total). Independent source review
passed, including swallowed startup DB/network guards. Defaults remain off; this
is NOT actual preserved-candidate/account/provider evidence. No repeat of completed
protected PREPARE/APPLY, refresh/activation or deployment. See
[Windows fixture evidence](docs/product/windows-inspection-fixture.md).


## Yaparo rename and relocated checkout - 2026-10-23

The owner renamed the product to Yaparo and moved the source/Git checkout to
`C:\Users\ugrkb\OneDrive\Masaüstü\yaparo`. GitHub is now
https://github.com/ugurkbcgl-hub/yaparo (same repository and protection). The fresh
private Python runtime is `%USERPROFILE%\.yaparo\.venv`; secrets and databases stay
outside sync under existing compatibility IDs. Public UI and distribution name
are Yaparo/yaparo-web; Python package, migration labels, DPAPI/database/OAuth IDs
remain stable. Local app/browser/PostgreSQL/packaging/read-only recovery admission
checks passed. No schema/data reset, provider call, deployment or publishing.
See [relocation evidence](docs/continuity/RENAMING.md).
