# ADR-0049: Owned saved-design package and closed portability rehearsal

- Status: Accepted for local synthetic implementation/evidence
- Date: 2026-10-25
- Continues ADR-0047/0048 and Y06.

Add an owner-only, default-off/DEBUG ZIP download for a saved bound v2/v3 design.
The owned brand/document locks freeze one committed scene/revision. The package
contains scene.json, a version-one manifest, Turkish README and, for v3, the exact
original and normalized PNG read through the existing scoped/hash-checked service.
Manifest records pinned source and document identities, material versions, tool,
file SHA256/size, renderer contract and the unbundled Arial system requirement.
It excludes account/session/credential data, unsaved edits and revision history.

Fixed illustrations/logo remain renderer metadata, not invented original files
or hashes. Legacy unbound documents retain scene JSON download but cannot claim
unknown source provenance in a package. The normal source-delete protection and
v1/v2/v3 scene/history behavior remain unchanged.

ZIP names are fixed server values, stored without compression, deterministically
ordered/timestamped and capped at12 MiB with a64 KiB manifest. No archive extraction,
filesystem write, importer, provider call or state mutation occurs in export.
The HTTP response is private/no-store/nosniff with a fixed UUID-based filename.

The no-input `scripts/rehearse_design_bundle.py` creates a new private source DB,
fixed palette at identity1 and saved v3 work at identity2. It exports its own ZIP,
then recreates that known fixture in a second fresh DB/workspace with a new owner
and document/material UUIDs. It reads only that process-generated archive, never
extracts paths and accepts no input file or configured Django process. Original/
normalized bytes, catalog/identity metadata, scene, actual PNG pixels and reexport
are compared. Source DB and ZIP hashes stay unchanged. Exact private fixture
inventory is removed; unknown files, links or cleanup failure prevent success.

This proves a bounded synthetic data transfer, not a general customer importer,
independent offline editor, bundled font/license entitlement, configured DB
recovery, migration compatibility or full Y05/Y06 readiness. Recreating the fixed
fixture uses the compatible current Yaparo implementation; it is not production
restoration and never overwrites an existing workspace. ADR-0051 subsequently
extends the fixture to a format-pinned v4 portrait; the original v3 result remains
historical evidence. Upload/parser isolation,
production storage, rights/privacy and full portable editing remain open gates.

Verification covers deterministic archive/content/hash checks, saved revision,
legacy/owner/flag/body-method boundaries, size and corrupt-raster refusal, the
actual private Windows rehearsal plus subprocess CI proof and browser ZIP download.
Desktop/mobile package UI reviewed. No migration or configured DB mutation needed.

Next: per-action undo/redo for unsaved editor changes, distinct from committed
save/restore history; keyboard access and failed-save edit preservation required.
