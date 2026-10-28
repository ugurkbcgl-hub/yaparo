# ADR-0072 — Plan before placement-specific production

Date: 2026-10-27. Status: accepted direction from owner's current request;
implemented only in the isolated local synthetic 8014 prototype.

## Problem and decision

Generating a finished image before selecting its destination confuses a shared
creative idea with a deliverable and can waste production. Use four stages:
request → plan → create → review/publish. The last stage is a future product
intent; publishing is disabled in this prototype.

Select paid, organic-only or combined intent first. Paid planning considers the
objective, context, budget, schedule, permissions and material/capability limits.
Organic chooses destinations without requiring a paid budget/forecast. A combined
plan keeps media spend separate from organic production requirements.

A draft plan determines which placements need which outputs, how many variants
and why. Confirm feasibility before charged production. Show three inexpensive
shared concepts, let the owner select/edit one, then create only its necessary
placement variants. A Search text asset is distinct from a social image; resizing
a single finished image is not a channel strategy. Shared core IDs/revisions,
placement requirement IDs and versioned recipes bind outputs.

Channel selection and production capability form a feedback loop. Video refusal
or missing usable material excludes video-requiring paid products in this bounded
demo; allocation is recomputed under existing minimum/cap rules. Existing video
is a declaration, not verified rights, scan, account or upload readiness. A missing
renderer/rights/spec/cost remains an explicit pending task, never a produced video.
Future generation needs an estimate and approval separate from media spend.

Plan/input/source/allocation/material changes invalidate downstream adaptation
binding. Core text/position edits invalidate adaptations, not the media decision.
Assistant proposals bind the route, organic destinations and material preferences.

## Implemented boundary

Owned deterministic production.js has closed prototype recipes for 20 research
products (owned actions excluded), selected paid rows only and five organic
destinations. Unknown recipes stay pending. Quantities are explicit one-item demo
recipes, not an optimized variation count. Text/image adaptations are authored
local preview records; video/catalog/partner tasks remain pending. No AI request,
cost reservation, asset upload, database migration, payment or publish operation.
Public source freshness remains separate: FX is live where available; ad forecasts
and detailed placement specs are not qualified by that fact.

## Current primary references, checked 27 October 2026

- [Google responsive Search ads](https://developers.google.com/google-ads/api/docs/responsive-search-ads/overview): headline/description assets support a distinct text output.
- [TikTok creative practices](https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en): platform-specific creative, sound/vertical/safe-zone guidance is more than resizing.
- [Meta Reels](https://www.facebook.com/business/ads/facebook-instagram-reels-ads): placement-specific creative guidance; video is a preferred recipe here, not a claim that Meta bans images on Reels.

These support the architecture, not full specs/availability/legal or performance
qualification for every catalog product. Do not encode illustrative aspect ratios
as universally current hard rules. Version/account/placement-specific source
qualification is still required before production publishing.

## Follow-up

Review the new journey, then qualify placement specs, material rights/reuse,
capability and cost contracts against source freshness before hosted generation.
Retain all account/privacy/financial/recovery/launch gates and protected TEST state.
