# ADR-0045: Durable generated palette rasters

- Status: Accepted for local synthetic implementation
- Date: 2026-10-25
- Continues ADR-0043/0044 under delegated local development authority.

## Decision

Add one fixed `product:palette:v1` or `service:palette:v1` material per brand,
created explicitly from its current identity palette. It is a new source, not a
replacement for the existing illustrated scene keys. Its identity never rebinds;
later identity edits do not change its bytes. The two metadata-only source-kit
records remain unchanged and can coexist with the palette material.

Use the existing database as the first private bounded binary adapter: one
immutable pair per material version holds original PNG, normalized PNG, measured
sizes, both SHA256 values and tool provenance. All material/version/pair rows
commit in one transaction under the owned brand/workspace locks. Failure rolls
back all rows; replay reads and validates the existing pair. No filesystem/object
store write creates an orphan outside that transaction. Small fixed320×200
generated samples avoid new infrastructure and recurring services; this does not
select database blobs for future large customer media. Original cap3 MiB,
derivative cap8 MiB; bytes and hash/size metadata must agree.

The persistence flag defaults False and DEBUG is required. Pillow13.0.0 remains
a development dependency; enabling this local feature requires that dev runtime.
The POST accepts only the normal bounded CSRF form; multipart is refused before
parsing. No customer bytes, URL, filename or AI/provider inputs are accepted.
The generated source has a measured catalog size; old metadata-only sources keep
null size. Reads check the owner again in the SQL query returning the byte pair,
including active owner and unarchived brand, then validate both byte hashes/sizes.
The PNG route is authenticated/private/no-store/nosniff with fixed image/png MIME.
List pages read only pair metadata, not binary content. Editor scenes v1/v2 do
not reference this new source yet.

This supersedes ADR-0043's metadata-only boundary only for this fixed generated
palette material. Arbitrary customer files, scan CLEAN/READY states and production
publishing stay closed. Records are application-immutable, not a SQL vault.
Configured DB+binary backup/restore, privacy deletion and process-crash/recovery
evidence remain required; transactional rollback tests are not those proofs.

## Verification

Owner isolation, identity pinning, measured readback, repeat behavior, atomic
rollback after pair failure, immutable/hash checks, CSRF/multipart, PNG pixels
and ownership change between queries are tested. PostgreSQL competing-create
test must pass in CI. Browser proof creates, reopens and repeats the same image;
mobile screenshot reviewed without horizontal overflow. No configured DB or
deployment migration is authorized by this implementation alone.
