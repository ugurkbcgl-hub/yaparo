# ADR0071 — Versioned in-site campaign setup

Accepted 27 October 2026 for local synthetic planning only. Downloads remain an
open product decision (ADR0070); no new export or provider integration is added.

Default-off LOCAL_BRAND_CAMPAIGN_SETTINGS_ENABLED plus existing brand-campaign/
DEBUG gates admit an active owner of a nonarchived, same-workspace bound brand.
The owner can set planning goal (awareness/traffic/leads), synthetic audience,
region, total TRY media budget and start/end dates. These are intent metadata,
not platform targeting, channel capabilities, payment consent or scheduled work.

CampaignPlanRevision (campaigns0013) protects campaign/actor, version, permanent
request UUID, closed payload, fingerprint and creation time. Payload schema binds
campaign/workspace/brand/actor, TRY and Europe/Istanbul. Latest and replay reads
rebuild that context, validate values and digest; corruption refuses instead of
falling back to old example values. API history is append-only, not a SQL vault.

Writes lock campaign SELF→brand/workspace, reconstruct active scope and require
expected version. First write expects0. Exact UUID replay preserves its original
context and returns that record without rolling back newer revisions. A new UUID
with stale version refuses. Each explicit successful new save appends one record.
Original operational WorkspaceCampaignDraft fields (objective/city/budget/flight),
selected creative/choice/history and provider/Google ledgers remain unchanged.
No plan revision is projected into an operational publisher/scheduler.

Budget is a strict integer number of kuruş,1..999999999 (prototype input bound,
not an approved spend cap or price). Bool/float/NaN/zero/negative/fractional kuruş
refuse. Form permits comma or dot decimal without grouped thousands; ambiguous
grouping and more than two decimals refuse. Saved form shows two decimal places.
Audience200/region100 UTF16 units must be trimmed, nonempty single-line text,
without controls/lone surrogates. Goal and payload fields are closed sets.

ISO dates are canonical. Duration counts BOTH endpoints:1..365 days, same-day1.
New writes recheck the current Istanbul date after scope locks and require start
today or later. Historical reads/exact replay do not expire when the day changes.
There is no automatic execution or financial effect on the selected dates.

Private owner/CSRF GET/HEAD/POST setup form uses small URLencoded bodies, closed
single-valued fields, sensitive POST masking and private/no-store/noindex headers.
Failed/stale saves retain entered fields with a fresh-form link in another tab.
Brand campaign overview and list show the same validated settings. Bound detail/
journey links route into this overview rather than legacy example channel/budget.
Unbound legacy campaign pages are unchanged. Corrupt latest plan shows unavailable
or409, never a plausible old budget. Long text wraps on mobile.

Evidence:

- New backend/browser checks cover exact localized cents, inclusive date limits,
  post-lock date change, historical replay, versions/stale tabs, cross-scope nonce,
  ownership/archive/workspace/flag guards, corrupt payload/no fallback, closed
  HTTP/CSRF, form readback, list consistency and200-character mobile wrapping.
  Two PostgreSQL races cover expected-version competition and plan save alongside
  creative selection with campaign-first locks; required CI before merge.
- Combined20 plan/brand campaign/backend/browser checks passed14 with6 PG skips;
  fifty existing campaign/journey checks passed. Provider/budget spies untouched.
  Independent source review no blocker. Lint/format/migration drift passed.
- Actual SAME private preview received only forward0013 after backup
  preview-before-brand-settings-20261026T221231Z.sqlite3. Prior rows preserved;
  new table initially empty, standard migration/type/permissions only.
- Normal IAB saved campaign3 plan1: traffic, synthetic ceramics audience,
  İstanbul,250050 kuruş,1–7 November2026 (7 inclusive days). Reopened form shows
  2500,50 and list/overview show2.500,50 TRY. Two actual authenticated save POST
  replays added no row. Forty prior application tables, including legacy campaign
  fields and selected ad revision2/choice1, remain unchanged. Local ledger unchanged;
  new AI/media cost0, provider credential remains absent.
- Private evidence:brand-settings-live-evidence.json, brand-settings-iab.png,
  brand-settings-{1440,390}.png and brand-settings-list.png. Actual desktop/mobile
  readback and list consistency passed. No configured DB, Google candidate,
  production deployment, external targeting or spend operation.

Next: assess destination and channel/creative compatibility and show concrete
in-site readiness gaps. Do not treat plan settings as publication/spend authority.
