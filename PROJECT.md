# Yaparo project brief


## Saved synthetic creative work — 24 October 2026

The local brand slice now has identity-pinned saved scene documents: explicit
creation, title/color edits, reopen and owned JSON download. Replays do not reset
work; stale saves are rejected. Brand edits do not rebind existing documents.
The schema is the bounded editor experiment v1. Django now connects an owned
Fabric editor to saved documents: layer text/color/transforms, revision-checked
server saves and client PNG export. Custom assets, creative edit history and
campaign association remain open. This is a local synthetic slice.

## Current direction — 2026-10-23

The owner requested a sustainable, self-operated product built with maintained
open-source components and easily replaceable AI providers. [ADR-0040](docs/adr/0040-owned-core-and-open-source-adoption.md)
accepts this strategy and the [new master plan](docs/product/yaparo-open-source-master-plan.md).
The [repository research](docs/product/open-source-candidate-research.md) distinguishes
candidate packages from adopted implementations. The planning milestone installed
none; the subsequent local experiment now pins Fabric 7.4.0 solely for evaluation.
See [domain map](docs/product/creative-editor-domain-map.md) and
[working synthetic experiment](experiments/creative-editor/README.md). Five focused
browser tests passed. ADR-0041 selects Fabric for the bounded local slice;
production editor readiness and campaign integration remain open.

- Each user may manage multiple brands from the initial brand-kit slice. Each
  brand has its own versioned identity, character, palette/logo, assets, preferences
  and campaign context. Basic multi-brand use is not deferred to the agency phase.
  [Brand-specific experience](docs/product/brand-specific-experience.md) defines
  acceptance and innovation experiments. The first synthetic brand list/create/edit
  slice now preserves identity versions and owner boundaries; assets, campaign
  binding, custom uploads and brand-aware AI remain pending.
- Retain Django/PostgreSQL and application-owned customer, brand, asset, editable
  creative, campaign, consent, money and report records. Prefer reusable packages
  and thin adapters; no whole-platform fork or production hosting switch selected.
- Independence means portable data and self-operated core/editing with replaceable
  providers. Advertising networks, payment processors and hosted AI remain external.
- Prioritize the synthetic brand/material/editor/export journey, then evaluated
  AI, commerce and a complete Google Search path. [Y01–Y32](docs/product/yaparo-delivery-plan.md)
  supersedes the older recovery-first task order. Current slice: Y04; Y01–Y03 local selection is recorded in ADR-0041.
- Basic editing should work without an AI call. Candidate editor/AI/worker
  choices require a pinned-version comparison before adoption. New worker/storage
  costs, real data, publishing and payments retain their existing release gates.
- Customer demand, exact first tariff/guarantee and production provider choices
  remain unverified/open. Research and a green CI are not product-market proof.
- Protected Google TEST histories, private candidate and completed backup/schema
  preparation remain intact; their review is a separate integration workstream.

The dated status entries below retain historical evidence; later entries and
current live repository checks take precedence for mutable facts.

## Current status

- On 2026-10-19 the local application created a fixed synthetic Search campaign/ad group/keyword/responsive ad in the verified Google test account, read back PAUSED and confirmed stop as PAUSED. Durable intent prevented repeat creation while reconciliation recovered a budget-name mismatch. No live serving/spend; this is a separate fixed test, not arbitrary workspace draft dispatch. See ADR-0022 and Google test integration readiness.

- Google test setup progressed on 2026-10-17: test manager/child, dedicated Cloud API project, OAuth web client and one test user exist. Local-only status/start/callback/disconnect routes now use the state/PKCE foundation and Windows-encrypted credential storage; runtime client decryption is verified. The feature is disabled by default. Google redirect registration and encrypted account authorization were verified on October 19. The local UI can now explicitly verify the configured test child with a fixed read-only API call and display a recent result; live browser verification passed. No publishing or spend is enabled. Current Google guidance replaces developer tokens with Cloud project access. See [test integration readiness](docs/product/google-ads-test-account-readiness.md).

- Product direction was clarified on 2026-09-27 at the owner's request: Türkiye is the target market, and the product is for people and organizations that want to advertise. Dental clinics are one example, not the product boundary.
- Local product development is authorized. The existing Django/PostgreSQL foundation and CI remain in use.
- The previous clinic-only Phase 0 demo is a foundation check, not the product itself. The staging profile-edit browser E2E passed against Heroku release v14 (`69476a62`) on 2026-09-30, and on v15 (`c13ba96`) and v16 (`8e29944`) during a controlled rollback on 2026-10-03. The disposable least-privilege synthetic account's password was reset and not recorded. Heroku rollback created v17 from v15 and v18 from v16; health returned HTTP 200 with the matching revision and the profile E2E passed on both. v15/v16 differ only in documentation, and neither rollback applied migrations, so this verifies a same-code release rollback only. The billing page displayed $0.00 current usage and a $1.37 September invoice marked Pending; this is not a finalized usage total. PR #206's revision lookup fix is deployed. Config-var values or secrets were not revealed. On 2026-10-01, the local `growthtwin` schema-only dump restored with 11 matching, empty public tables; no application records were included. A separate isolated PostgreSQL 18.6 cluster was migrated from Django, seeded with one fabricated account, then fully dumped and restored into a new empty database; the marker survived, and Django system/migration checks passed. Neither rehearsal verifies configured-database or Heroku database recovery. Local Django tests use in-memory SQLite by default; CI uses an ephemeral PostgreSQL service. Temporary synthetic rehearsal files remain because tool policy blocked recursive cleanup; no alternate deletion method was attempted. See [Phase 0 verification](docs/phase-0-staging-verification.md).
- The public website prototype uses one fixed synthetic Ankara home-maintenance example. Visitors can choose an objective, example daily limit, and duration; the form does not accept free-text brief, brand, or audience details. The server ignores extra submitted text fields and creates new drafts from the fixed sample. Drafts from earlier versions that do not match this sample are hidden from the public list and cannot be resumed or edited; their stored records are left unchanged and remain subject to session expiry and cleanup. Current synthetic drafts can be listed, resumed, edited for plan options, or deleted within their owning anonymous session. Expired sessions cannot access drafts; `clearsessions` removes expired session records and their drafts. The scheduled cleanup job has run once, but it is best-effort and does not establish a real-data retention guarantee; keep data synthetic. The content module exposes persistence-free `CampaignBrief` and `CampaignPlan` values; the session-owned ORM adapter remains in `site` under [ADR-0006](docs/adr/0006-campaign-brief-boundary.md). Website routes use the deterministic synthetic template and do not call an AI provider. An opt-in loopback Ollama adapter exists for synthetic evaluation only; it is not connected to the website, and current Qwen3 smoke runs were too slow/repetitive for product use. There is no platform connection, publication, or real metrics. Advertiser-provided brief and asset intake remains a future product capability behind the real-data readiness gate.
- Phase 1 acceptance was verified on 2026-09-29 through source/E2E review and manual desktop browser review. PR #100 removed desktop horizontal overflow, improved the temporary-data notice, and keeps the sample report visible after navigation; required PR and post-merge CI passed. Mobile remains covered by browser E2E. This is still a synthetic local prototype, not a launch-ready product.
- Phase 2 now has an authenticated workspace campaign list and local Google Search text preview (PR #113), owner-scoped changes to whitelisted synthetic budget/duration options and confirmed draft removal (PR #114), browser E2E for the owner flow and tenant boundary (PR #115), and a Turkish accessible sign-in journey with public registration closed (PR #116). PR #117 adds an equal-allocation daily planning average based on the synthetic media cap and dates; PR and post-merge CI passed. ADR-0009 defines the future asset intake boundary; PR #120 adds pure state-transition contracts only, with no file or provider operations, and PR #121 tests those transitions. Both PRs and post-merge CI passed. PR #122 adds a pure synthetic campaign action-policy check. PR #125 corrects the handoff scope so local synthetic development stays allowed while Phase 0 checks remain release gates. PR #126 adds allowlisted synthetic evidence-source and timezone-aware observation-time metadata; PR #128 adds informational synthetic policy-version and evaluated-rule identifiers. PR #131 adds stored, owner-scoped, provider-free creative variants to authenticated workspace campaigns; source changes hide stale output. PR #133 adds a preferred review variant bound to its current source version; it is not approval or publication. PR #135 adds an authenticated report shell; PR #138 defines an immutable provider-neutral metric value contract; PR #140 connects typed unavailable metrics to the report shell and labels displayed dates as the planned campaign period. ADR-0017 (PR #141) defines semantics for the six metric categories while preserving native source differences. PR #142 maps official Google Ads API v25 fields for the Search candidate without account access or API requests. PR #143 adds typed reasons for unavailable report values (`not connected`, `unsupported`, `partial`, `stale`), reason-specific provenance rules, and metric-level Turkish explanations. PR #145 documents Google Ads Search zero-row completeness and metric-family freshness behavior. PR #149 adds report observation coverage and a pure source-time freshness evaluator; PR #150 adds `freshness_unknown`; PR #152 documents the source timestamp evidence gap. PR #154 separates planned dates, observed report period, freshness, and retrieval time in the authenticated empty state; required and post-merge CI passed. There is still no verified report source, account connection, publishing, spend, or live forecast. Free-text advertiser inputs remain withheld until the real-data readiness gate; real advertiser data remains out of scope.
- PR #185 adds workspace-owner editing for synthetic ad-copy variants through bounded fields. Edits are appended as linked versions, preserving prior text and clearing the review preference. A synthetic-only confirmation is required, but it cannot verify what a person enters; keep this local and do not enter real advertiser/customer data. It does not verify claims or enable approval, AI, uploads, platform connection, publication, or spend. See ADR-0020.
- PRs #217–219 add a provider-neutral creative-generation boundary, route existing website copy generation through the deterministic synthetic template, and add an opt-in loopback-only Ollama adapter for synthetic evaluation. Structured shape, source, length, key, and repeated-angle checks fail closed; generated results remain review-required and non-publishable. The website still uses templates. Single local Qwen3 1.7B and 4B smoke runs were slow/repetitive, so neither model is selected for product use. No real data, hosted provider, credentials, account, publication, or spend was involved; details are in [AI_PROVIDERS.md](AI_PROVIDERS.md).
- Recent Türkiye readiness work: PRs #163–165 expanded sourced Google policy research and corrected the handoff; their required/post-merge CI passed. PR #166 added supplement approval/claim checks (required `36739134600`, post-merge `36739507855` passed); PR #167 added ordinary-food, novel-food and child-audience checks (`36740203483`, `36740519517` passed); PR #168 added adult-services distinctions (`36741167177`, `36741491268` passed). PR #169 refreshed project status (`36742863063`, `36743130604` passed). PR #170 added Turkish Law 4207 tobacco constraints; required CI `36743525443` and post-merge CI `36744652209` passed. PR #171 added political/election-advertising research; required CI `36745452282` and post-merge CI `36745746001` passed; no campaign is cleared. These are synthetic planning/research changes: no sector selector, live account, API, publication, advertiser data, or spend is connected.
- Heroku staging has the previously approved Basic web dyno and Essential-0 PostgreSQL plus the Standard Free Heroku Scheduler add-on. A daily `python manage.py clearsessions` job is scheduled for 00:00 UTC (03:00 Europe/Istanbul) on the existing Basic dyno. On 2026-09-29, Scheduler showed Last Run at 2026-09-29 00:00 UTC and Next Due at 2026-09-30 00:00 UTC; Heroku logs showed the one-off process exited with status 0. Actual one-off dyno cost remains unverified. Scheduler is best-effort, so this is synthetic-staging cleanup only, not a real-data retention guarantee; see [ADR-0006](docs/adr/0006-campaign-brief-boundary.md).
- Current implementation stack: Django 5.2 LTS + PostgreSQL in one modular monolith (accepted in ADR-0002). No new stack, paid service, or production AI provider is selected. See [continuity state](docs/continuity/STATE.md) for the latest verified repository commit and CI status. Heroku staging release v16 was built from the CI-passing `main` commit `8e29944`; `/health/` reports the full deployed commit. Both required dyno-metadata Labs are enabled.

## Product goal

The workspace now supports an owner-only text download of the current selected
synthetic creative and campaign plan. The file distinguishes generic creative
copy from separate Google Search starter assets, preserves the unpublished
status and media/fee caveats, and rejects stale selection links. This delivers
a review artifact; it does not enable real-data export, platform import or
publication. R-10 participant observations remain pending and do not block
independent development of the remaining campaign lifecycle.

The authenticated workspace also provides a synthetic publishing rehearsal:
start, deliberately fail, retry and stop through an in-process fake adapter.
Owner-scoped state and event records reject stale/duplicate form revisions;
changed inputs block retry, while stop remains available. A running rehearsal
is a stored simulation state, not an active advertisement or worker. No real
account, provider, media spend or performance data is connected. See
[ADR-0021](docs/adr/0021-workspace-publishing-rehearsal.md).

Build a polished, low-effort, self-service advertising platform for the Türkiye market. It should be useful to anyone who wants to advertise: individuals, creators, small and large businesses, and organizations across industries. Dental clinics are one possible customer example, not a special product boundary.

Yaparo's long-term capability benchmark is an integrated, AI-assisted advertising workflow: understand the advertiser's brand and offer; turn a plain-language goal into a campaign plan; generate and refine platform-ready copy, image, and video ads; launch approved campaigns through connected ad accounts; report results across channels; and recommend or perform bounded improvements based on measured performance. Omneky is a product capability reference for this breadth, not a commitment to copy every feature or channel in the first release. Public vendor feature claims do not establish Yaparo's access to those platforms, API eligibility in Türkiye, or feature parity.

The normal path should not require a Yaparo employee or agency operator. The advertiser supplies essential facts, authorizes each selected destination, and sets explicit content, schedule, and spend boundaries. Routine work may proceed autonomously only within those permissions and enforceable limits. When facts, authorization, policy confidence, provider state, or a limit is missing or uncertain, the campaign pauses and the user receives a clear explanation. The exact default review mode and first-release autonomy settings remain open decisions.

The capability direction and owner requirements are clear; a first service blueprint draft is in [docs/product/growthtwin-service-blueprint.md](docs/product/growthtwin-service-blueprint.md). It includes customer-owned document/content analysis and improvement, separate production credits and ad fees/media spend, pre-purchase channel estimates, beginner and professional paths, campaign-level and combined reports, creative testing, a Türkiye channel/legal research matrix, and a readiness gate. [ADR-0008](docs/adr/0008-first-mvp-google-search-leads.md) selects a narrow synthetic workflow: a city service quote/contact campaign, with Google Search as first channel candidate and the advertiser's existing site as destination. [ADR-0009](docs/adr/0009-asset-intake-processing-boundary.md) sets a contract-first safety boundary for future files. Neither decision establishes Google access, customer demand, data-processing terms, pricing, AI credit costs, lead CRM delivery, performance guarantees, API approval or legal readiness. Phase 1.5 remains open for those evidence and launch decisions.

For this project, "advertising" means paid digital advertising campaigns and their creative, launch, measurement, and bounded optimization. Organic social-post scheduling is outside the initial product scope unless later evidence justifies it.

## Users and first market

- Target market: Türkiye. The product is for people and organizations in Türkiye that want to run paid digital advertising, across industries and advertiser sizes.
- Do not hard-code Yaparo to dental clinics, creators, e-commerce, or a single vertical. Shared campaign, brand, and account workflows should support different advertiser types.
- Dental clinics, creators, and small businesses are examples of potential users. None is currently selected as the exclusive first segment.
- Keep the first usable release narrow: validate one campaign workflow and one publishing destination before broad channel coverage. The initial campaign type, pilot cohort, and destination remain open until user discovery and platform/API feasibility are checked.

## User experience principles

- Start with the user's goal in their own words. Ask only for information required to produce a safe, useful campaign; use progressive disclosure for channel, audience, timing, and budget details.
- Show what Yaparo is doing, what it needs, and the current campaign state without making the user manage internal workflow steps.
- Make the generated campaign easy to inspect and revise. Keep budget caps, connected destinations, automation status, and a prominent pause/stop control easy to find.
- Design for mobile and desktop, with Turkish-first copy and room for additional languages.
- Use accessible, consistent components and realistic synthetic data in local prototypes. Do not disguise mock output as a real publication or result.

## Campaign lifecycle

1. Learn the advertiser's brand, offer, assets, audience, and goal from a short guided intake.
2. Turn the goal into a structured campaign plan with objective, audience, channel, placements, timing, and spend boundaries.
3. Generate and refine platform-ready copy, image, video, and variants; validate claims, brand rules, destination formats, and platform policies.
4. Launch or schedule only through an explicitly authorized ad-account connection and within user-defined spend and schedule limits.
5. Collect and explain performance by campaign, channel, and creative; recommend or make follow-up changes only within the advertiser's configured autonomy and caps.
6. Pause with an understandable message when information, confidence, permissions, platform access, or budget is insufficient. Record external actions so they are traceable.

AI may propose and transform campaign material; deterministic application rules enforce authorization, budget caps, valid states, idempotency, and external-action boundaries. Never let a model call a publishing API or increase spend outside these controls.

## Existing resources and intended use

- **This shared Windows checkout:** the single source of truth at `C:\Users\ugrkb\OneDrive\Masaüstü\yaparo`; build and review changes here through feature branches and pull requests.
- **Django 5.2 + PostgreSQL 18.6:** keep the accepted one-application modular-monolith stack for the first website and product workflows. Reconsider the stack only if a working interface demonstrates a concrete limit.
- **GitHub repository and Actions CI:** use pull requests and the existing checks for every change. Keep browser E2E coverage focused on the critical advertiser journey as it is built.
- **Local workstation:** Windows 11, Python 3.13.15, PostgreSQL 18.6, 31.7 GB RAM, RTX 3050 Laptop GPU with 6 GB VRAM, and Ollama. Use it for development and optional synthetic experiments; product runtime and AI quality must not depend on this machine or its GPU.
- **AI providers:** no production model/provider has been selected. Keep task-specific, replaceable adapters behind the application-owned AI gateway. The current website uses deterministic templates; local Qwen3 results failed the small creative gate, GPT-6 Luna remains an offline candidate with generic review-only drafts, and Gemini failed the comparative quality gate. On 2026-10-04, the owner authorized synthetic-only evaluation using existing OpenRouter credits up to USD 16, with no top-up or auto-recharge, and delegated balance checks to themselves; the dedicated key's no-reset cap was verified. Two image requests on the pinned ZDR-eligible Google Vertex route completed upstream and were each charged USD 0.0336 according to matching OpenRouter Logs entries. The local runner failed to save the images; the precise historical rejection point is unknown. Its PNG-only assumption is corrected to validate PNG/JPEG/WebP using response MIME type and matching file extensions. Their USD 0.20 total local reservation has been reconciled. The shared local ledger records USD 0.12744185 spent and USD 0.00078075 reserved for a separate unresolved GPT call; this is not provider billing or the account balance. Further billable calls require renewed owner authorization. OpenRouter video remains excluded because its API is not ZDR-eligible. See [AI provider combinations](docs/product/ai-provider-strategy.md) and [evaluation limits/history](AI_PROVIDERS.md). No production provider, real-data path, customer-facing AI, or recurring AI service is authorized.
- **NVIDIA Build/NIM:** evaluation only, with synthetic inputs. The earlier trial was useful for draft and claim-review experiments but had latency and invalid-JSON failures. Do not use trial endpoints to serve end users or send real advertiser data.
- **Heroku staging:** the owner approved and provisioned one Basic web dyno plus one Essential-0 PostgreSQL database at an observed estimate near USD 12/month before tax. Keep it for synthetic staging/release-readiness checks only; it is not production or an AI serving tier. Add no paid resource without a new decision. On 2026-10-03, authenticated CLI checks showed release v16 / `8e29944`, built from the CI-passing `main` commit at deployment time. Both `runtime-dyno-metadata` and `runtime-dyno-build-metadata` are enabled, and `/health/` reports the exact deployed commit. No resource was added.
- **Secrets:** use the existing local protected secret store or the provider's secret store. Never put secret values in chat, source, Git, logs, screenshots, or handoff files.

## Architecture and AI direction

- Keep the accepted Django/PostgreSQL modular monolith (ADR-0001 and ADR-0002): workspaces/advertisers, brand facts, campaign briefs, content/creative versions, budget and consent policy, publishing adapters, reporting, and background work remain explicit modules.
- Keep provider and publishing integrations behind replaceable server-side adapters. The browser must never receive platform secrets.
- Do not add a separate worker, queue, vector database, object store, frontend runtime, or AI service until a working product slice shows a need and cost is reviewed.
- No production AI model/provider has been selected. Local inference is optional, not a product dependency. Follow [the provider-combination strategy](docs/product/ai-provider-strategy.md) for replaceable synthetic evaluations. The shared local ledger limits evaluation use independently of the verified key cap. The image runner pins to one ZDR-eligible Google Vertex endpoint and reserves at most USD 0.10 per call. Two authorized synthetic attempts on 2026-10-04 completed upstream and were each charged USD 0.0336, per matching provider Logs entries, but the local runner did not save their outputs. The exact failure point is unverified; the PNG-only validation has been fixed to detect PNG/JPEG/WebP and save the corresponding extension. The reservations are settled in the local ledger, now USD 0.12744185 spent and USD 0.00078075 reserved for a separate unresolved GPT request. This local estimate is separate from the OpenRouter account balance, which the owner checks. A further billable call requires renewed authorization. OpenRouter video generation is ZDR-ineligible and is excluded under current privacy controls. This does not authorize real advertiser data, customer-facing AI routes, publication, media spend, credit purchases, or auto-recharge; those require applicable readiness gates and separate decisions.

## Budget and security constraints

- The project reference sets a Phase 0 working limit of USD 100/month, a warning near USD 80/month, and owner approval for a single spend above USD 20. The separate Heroku approval covers only one Basic dyno and one Essential-0 database at about USD 12/month before taxes.
- Advertiser media spend is different from Yaparo infrastructure or subscription spend. Before any campaign can spend money, the advertiser must connect the account and set explicit, enforceable per-campaign and aggregate caps. The application must fail closed on missing or unreadable budget state.
- Use synthetic data in local development, CI, and staging. Never use trial/free AI endpoints with private advertiser data.
- Production use requires verified privacy/data terms, model licensing, platform app/API approval, account token protection and revocation, tenant isolation, audit logs, operational alerts, backups, and a tested stop/rollback path.
- Do not publish from staging, connect real advertiser accounts, deploy production, or provision new paid infrastructure as part of local website prototyping.

## Open decisions to resolve before real publishing

1. The synthetic first workflow and objective are recorded in ADR-0008; validate the city-service quote/contact hypothesis with actual user/problem research before selecting a pilot cohort or accepting real data.
2. Google Search is the first technical channel candidate in ADR-0008. Verify Yaparo Cloud project API access, OAuth/app review and production-account use, the eligible account/currency, campaign-total budget and stop behavior before any live publishing. Meta remains second and TikTok third in the research sequence; neither is integrated.
3. Specify what Yaparo sells in the first release: included work, creative formats, automation limits, exclusions, service packages, and pricing.
4. Distinguish advertiser requests to Yaparo from leads generated by ads. For generated leads, decide what is collected, who receives it, which destinations are supported, consent and access controls, delivery/retry behavior, retention, and deletion.
5. Map AI tasks separately for text, image, and video; evaluate tools/models, licensing, data terms, quality, safeguards, cost, latency, and failure behavior on representative synthetic inputs. No production provider is selected.
6. Define default review mode, opt-in autonomy, account consent, enforceable spend caps, stop conditions, and escalation to the advertiser before enabling live publication or spend.
7. Decide data categories, purposes, recipients, deletion/export, retention, and backup behavior before any real advertiser, customer, or lead data is accepted.
8. Estimate production hosting/inference costs after the first end-to-end pilot workflow is understood, and seek approval before adding recurring services.
9. A narrow synthetic first service, workflow and objective are selected in [ADR-0008](docs/adr/0008-first-mvp-google-search-leads.md); pilot hypothesis and user experience still need validation. Keep the rest on the staged expansion plan.
10. Research channel availability separately from Yaparo's API access; complete a scorecard with Turkish account registration/billing, permissions, forecasts, formats, reports, policies and maintenance.
11. Cost the proposed credit packages, free introductory credits and separate campaign fees; define TRY/tax/payment/refund terms. Do not promise a target-result refund until its metric, attribution, exclusions, cap, reserve, evidence and legal treatment are defined.
12. Decide supported customer document formats, rights/provenance, AI-provider transfer controls, and initial creative tasks for text/image/video using synthetic quality, safety, latency and cost evaluation.

## Omneky capability reference

The owner selected Omneky as a long-term capability benchmark for ad creation, connected campaign launch, cross-channel performance reporting, and bounded optimization. Its current public product pages are a reference, not independent verification or a Yaparo feature commitment. Recheck current capabilities and Türkiye-specific platform/API access when selecting an implementation target. Sources: [Omneky](https://www.omneky.com/) and [Campaign Launcher](https://www.omneky.com/campaign-launcher), checked 2026-09-27.


Local Google workspace preparation (2026-10-19): selected creative and plan can be reviewed as an immutable package and explicitly approved for later PAUSED TEST dispatch. Source/selection/target changes invalidate the current approval. This step performs no Google call and does not yet dispatch workspace drafts. See ADR-0023.


Workspace Google TEST dispatch verified (2026-10-19): selected synthetic creative now creates a separate durable PAUSED campaign from its immutable approval. The second consent explicitly shows example.com test URL override, inclusive daily TRY budget, account-local date-times and Ankara/PRESENCE mapping. Browser create/read/stop passed; 71 focused tests passed. One intent per draft prevents re-creation after timeout/restart; independent read/stop survives source changes. Live serving/spend remain gated. See ADR-0024.


Live Google Search readiness audited (2026-10-19): [the current gate list](docs/product/google-search-live-readiness.md) separates TEST evidence from production account/consent, destination, spend caps, privacy and recovery. A local signed owner-only validateOnly control now verifies a separate CUSTOM_PERIOD/totalAmountMicros candidate; Google TEST accepted the 5,000 TRY synthetic example without creating resources or modifying the daily-budget ledger. 79 focused tests passed. Next verify a new durable PAUSED TEST total-budget resource, retaining old daily read/stop. Live serving/spend remain closed; see ADR-0025.


Total-budget TEST dispatch verified (2026-10-19): new profile v2 creates non-shared CUSTOM_PERIOD budgets with exact totalAmountMicros; stored v1 DAILY ledgers retain read/stop and cannot be converted/reset. Browser created a new synthetic draft, sent 5,000 TRY total PAUSED, reconciled repeat create and confirmed stop; old daily stop also passed. 82 focused tests passed. No serving/spend or production cap exhaustion evidence; see ADR-0026. Next inspect current Cloud API/OAuth production-access gates read-only before planning any upgrade or real account flow.


Read-only Cloud audit (2026-10-19): Ads API is enabled with Test access (15,000 test operations/day); Explorer Apply button visible, not submitted. OAuth is External/Testing with one test user; Publish app disabled pending Branding. Public home/privacy/terms URLs and authorized domains are absent; owner has no domain yet. Scope declaration tables empty (not proof that the existing runtime TEST grant was revoked). See [production-access audit](docs/product/google-production-access-audit.md). No access/permission/publication/account changes were made.

Public identity preparation (2026-10-19): [page requirements](docs/product/public-identity-page-requirements.md) map current code data flows, missing business/domain/contact facts and category-specific retention/deletion decisions. Protected Google approval/dispatch snapshots contain content and need a deletion/recovery design that preserves no-resend safety. Local draft contact/privacy/terms pages and public footer links are implemented; 5 focused tests, ruff and desktop/mobile browser review passed. No final legal text, production readiness, domain purchase or Google permission change is implied.

Data lifecycle design (2026-10-19): [ADR-0027](docs/adr/0027-data-lifecycle-and-no-resend-boundary.md) separates stop, OAuth revocation, local data erasure, recipient/backup erasure and account closure. It specifies category-specific retention decisions, minimal no-resend barriers, in-flight/callback races and restore quarantine. This is a design contract only; durations, legal review and production implementation remain open. No data/grant was accessed or deleted.

Lifecycle decision slice (2026-10-19): a pure synthetic evaluator now returns typed eligible closure steps and independent Turkish outcomes; request/recovery/barrier gaps fail closed, BLOCKED erasure requires review and immediate revoke does not wait for stop. 15 focused DB-free tests and ruff passed; independent review finding corrected and rechecked. No routes, persistence, provider calls, real deletion or production authorization is connected. See ADR-0027 follow-up.

Lifecycle observation slice (2026-10-19): a pure synthetic reducer now binds outcome evidence to workspace/connection/request/generation, revision and a pending operation ticket. Exact replay is a no-op; conflicts, stale or unsolicited results and closed requests are rejected. 14 new tests plus 15 decision tests passed; ruff and independent review passed. This is not a callback handler, durable state, provider proof or executor; existing Google TEST records and routes are unchanged. See ADR-0027.

Lifecycle ticket slice (2026-10-19): pure eligible-step issuance now preserves unresolved operations, rejects retired operation-ID reuse and makes exact issuance replay a no-op. Immediate revocation has a separate bounded priority ticket; both outcome orders preserve the other operation. 13 new tests plus the prior 29 passed (42 DB-free total), with ruff and independent review. No runtime/executor/persistence/credential operations are connected.

Lifecycle preview (2026-10-20): `/kontrol-onizleme/` shows five fixed synthetic scenarios through the pure contracts, with explicit simulation labels and no real action buttons, accounts or submitted evidence. 56 focused DB-free checks (9 preview + 5 information + 42 contracts), ruff and desktop/mobile/keyboard review passed; independent review found no blocking issue. No Google DB/grant/ledger access. Next: isolated owner-scoped synthetic persistence and atomic revision checks, still without provider execution or actual erasure.

Synthetic lifecycle persistence (2026-10-21): owner-scoped service-only request/operation storage now uses typed versioned metadata, unique request/receipt identities, transactional receipt writes and revision-conditional updates. Creation replay preserves current progress; stale/conflicting updates fail closed. No HTTP/provider/credential/erasure path is connected, and the stored fixture barrier does not guard existing Google routes. 62 local focused tests passed; PostgreSQL CI 39642369641 subsequently passed all 343 tests (including the competing-writer test) and 10 browser tests; main CI 39642731033 passed after PR #298 merged. Migration drift/ruff checks and independent re-review passed. Only ephemeral test DB migrations were run; preserved Google DB/grant/ledgers and Heroku are unchanged. See ADR-0027. Next: fixed-fixture authenticated owner start/status journey, with CSRF-safe start and no browser-supplied outcome/proof flags.

Synthetic owner closure journey (2026-10-21): a default-off fixed-example start/status flow now uses the owner-scoped store under `/workspace/control/`. CSRF-protected POST requires explicit synthetic confirmation; extra submitted proof/outcome/ID fields are rejected. Stable server fixture IDs and one transaction preserve one request/STOP receipt under repeat start; GET/HEAD status is read-only and clearly distinguishes example outcomes from real account results. Campaign-list navigation is flag-gated. 80 focused local tests passed; PR #299 required PostgreSQL CI 39644787052 passed 362 tests including concurrency and 10 browser E2E tests; main CI 39645131181 also passed. Ruff, migration drift, independent review and desktop/mobile/keyboard browser checks passed. Browser fixture on loopback 8011 has an isolated DB/cookies and no real account or password. No provider executor, Google DB/grant/ledger, Heroku, schema or production change. Next: a bounded explicit fake-only STOP result demonstration for the saved example using operation/revision-bound observations; no browser-supplied proof or real provider action.

Bounded synthetic STOP results (2026-10-21): the owner journey now records a fixed confirmed or uncertain result from a local deterministic fake. Separate scenario IDs preserve the existing default fixture. Explicit CSRF-protected confirmation and a 10-minute signed owner/workspace/request/operation/revision token bind the result; raw browser outcome/proof fields are rejected. Exact persisted replay bypasses the fake and creates no second operation/event. GET/HEAD remains read-only; revocation/erasure states stay separate. 94 local focused tests passed; PR #300 required CI 39647636463 passed 377 PostgreSQL tests and 10 browser E2E tests; post-merge main CI 39648069200 passed; ruff, migration drift, independent review and desktop/mobile/keyboard checks passed. Preview 8011 retained the isolated fixture DB across restart. No real Google DB/grant/ledger, provider, credential, Heroku, schema or spend change. Next: isolated synthetic new-work/callback guard integration, then the unified advertiser journey. See ADR-0027.

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
