# ADR-0042: Pinned brand palette and saved creative history

- Status: Accepted for local synthetic implementation
- Date: 2026-10-24
- Continues ADR-0041 under the owner's requested next delivery.

## Decision and compatibility

New creative documents use bounded scene v2 with literal background, logo accent,
icon foreground, wordmark color and Arial font. New scenes copy the pinned brand
identity palette; later brand edits never rewrite saved scenes. Title/subtitle and
wordmark use the primary color when contrast against the background is at least
4.5, otherwise a black/white fallback. Logo accent retains primary; its icon gets
a contrasting foreground. User-edited text colors remain user-controlled. This
is not a guarantee that every manually edited design meets accessibility rules.

Existing scene v1 retains its prior rendering and exact stored shape; no automatic
rewrite, upgrade or downgrade occurs on read, save or restore. V1 seed remains
available for compatibility. V2 does not enable uploaded logos, custom fonts,
remote assets, new formats or edits to photographic product colors.

## Durable history

New documents record their initial snapshot. Each changed save atomically stores
a new immutable application snapshot and moves the document revision. Owner and
explicit brand scope are checked under the same brand/document locks. No-op saves
keep the revision and timestamp. Existing documents without history acquire only
their current baseline on the first changed save; unknown old edits are not
invented. GET does not create history or alter the document.

Restore reads a snapshot within that owned document, checks the expected current
revision and copies the old scene as a new revision. Later snapshots remain;
stale/repeated writes cannot duplicate a restore. A no-op restore does not append.
History lists the most recent50 entries; stored older entries are not pruned.
Snapshots record the acting owner and time of capture; a legacy baseline date is
its capture time, not a reconstructed original creation time. This is application
append-only history, not a tamper-proof SQL audit system or per-keystroke undo.

The browser uses CSRF-protected bounded JSON for restore, confirmation before
replacing unsaved work, and no automatic retry after network uncertainty. PNG
exports the current canvas; publication approval is still separate.

## Verification and release boundaries

Focused tests cover palette snapshots, strict v2 inputs, preserved v1, ownership,
no-op/replay/stale restore, immutable history and rollback after snapshot failure.
A PostgreSQL competing-restore case must pass in required CI. Chromium exercises
save, restore old/new snapshots and stale-tab refusal; decoded PNG pixels verify
v2 background/logo colors and unchanged v1 background. Mobile/desktop reviewed.
Migration0004 creates only the history table; no legacy scene data migration.
No provider, advertiser account, customer data, payment or publishing is enabled.
