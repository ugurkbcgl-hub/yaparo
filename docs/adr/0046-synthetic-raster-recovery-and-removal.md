# ADR-0046: Synthetic raster recovery and removal

- Status: Accepted for local synthetic implementation/evidence
- Date: 2026-10-25
- Continues ADR-0045 under delegated implementation authority.

## Removal

Add an internal, default-off/DEBUG-only owner service to delete an explicitly
identified palette material. Brand/workspace locking serializes it with creation.
It checks the existing byte pair before deleting the material, its version and
both binaries in one DB transaction. A failed cascade rolls back every row.
Absent scoped ID is a no-op; an old ID cannot delete a newly recreated sample.
Metadata-only source-kit items, other brands and identity/history stay intact.
No HTTP removal route or customer retention/deletion policy is added. Direct
immutable child-row mutation stays forbidden; the parent cascade is intentional.
Future editor references must protect referenced versions before integration.

## Recovery proof

`python scripts/rehearse_raster_recovery.py` accepts no arguments. It refuses an
already configured Django process, creates a fresh private directory, migrates
a fresh SQLite DB and seeds only one unusable-password generated fixture account,
brand and palette pair. No existing/configured DB is opened. It creates a native
SQLite backup and restores it into another fresh file, never over source history.

Recovered owner/material/version/identity, both byte hashes/sizes and tool version
must match; the PNG is decoded and an actual pixel checked. Removing the restored
material must remove original, derivative, version and material; replay is a
no-op. Whole source and backup hashes must remain unchanged. Exact inventory
cleanup then removes the three generated DB files and private directory.

Windows uses the evaluated current-user-only ACL helper; POSIX uses0700. Native
SQLite connections explicitly close before deletion. Unknown files/reparse/link
or cleanup errors prevent success. Checks remain active under Python optimization.
Only scalar evidence is printed. A crash may leave a private synthetic fixture;
there is no recursive cleanup or automatic recovery retry.

This is isolated SQLite backup/restore evidence and transaction rollback
evidence, not configured PostgreSQL/Heroku backup, process-crash durability,
backup-retention erasure or customer privacy readiness. Those release gates stay
open. No migration, live preview mutation, provider, paid service or deployment.

## Verification and next action

Tests cover complete removal, scoped denial, old-ID replay after recreation,
rollback after partial cascade failure, corrupt-pair refusal and real recovery
CLI execution/cleanup. The recovery runner refuses reuse within a configured
Django process. Independent review found no blocker; final CI verifies PostgreSQL
application tests and the isolated SQLite runner on Linux.

Next: explicit owned material-version linkage in new editor documents while
preserving existing v1/v2 scenes and protecting all referenced source versions.
