# ADR-0053: Read-only campaign snapshot preview and PNG

- Status: Accepted for local synthetic implementation
- Date: 2026-10-25
- Continues ADR-0052 and Y07.

The campaign's explicitly selected immutable revision now has an authenticated,
read-only preview and logical-size PNG download. URLs name the selection version;
when that selection has changed, a new read of the old URL refuses with409 rather
than silently following the new choice. An already loaded page remains the shown
immutable snapshot. It is not an authorization to publish or a live selection check
at the instant of client PNG generation.

The same workspace/owner/active/archive/source checks as selection apply. A
separate version-addressed private endpoint reads only the pinned palette source
and verifies its immutable material version and raster hashes through the existing
gateway. Missing/inaccessible/contradictory sources fail closed. No arbitrary URL,
customer file, external request, upload, AI call or write endpoint is added.

Shared scene-renderer.js holds the existing fixed bitmap drawing, bounded private
PNG loader, Fabric object construction and exact-size PNG export. The editable
document still owns its controls, validation, save/restore and undo. The campaign
page uses StaticCanvas with no edit/restore/save controls or write URLs. PNG export
restores the display dimensions/viewport in finally. Existing v1-v4 rendering is
preserved; Fabric and system Arial remain prerequisites. Package verification now
requires the shared renderer, preview client and style assets.

GET/HEAD only; other methods are rejected before CSRF/body parsing, including
multipart and leading-zero paths. Success/auth/error responses are private,
no-store and noindex. Preview CSP limits scripts, images and connections to the
existing local contract. Normal flag remains off and DEBUG is required. There is
no new migration or configured database change. Approval/dispatch/stop, budget,
Search text, provider tokens and protected TEST fixtures remain separate.

HTTP checks cover exact old snapshot after live edit, no write bootstrap, stale
selection URLs, flags/auth/archive/same-owner-other-workspace/transfer refusal,
preparse write rejection and exact private palette bytes. Actual browser checks
compare downloaded800x1000 PNG pixels before/after editing the live document and
at mobile width, for illustration and palette sources. Palette request failure
keeps download disabled. Existing editor save/reopen/undo/export checks also run.

Next: extend owned ZIP export to the campaign-selected immutable snapshot, with
an explicit selection/revision manifest. The existing document ZIP still exports
the current saved document, not the campaign snapshot. No general importer,
standalone editor, production quality claim or publishing approval is implied.
