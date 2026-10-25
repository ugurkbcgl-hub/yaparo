# ADR-0043: Closed synthetic material catalog

- Status: Accepted for local synthetic implementation
- Date: 2026-10-24
- Continues ADR-0009 and ADR-0042.

## Context

The owned Fabric editor already renders two fixed synthetic sources per example:
an illustration and a logo. They previously had stable scene keys but no durable,
owner-scoped source/version record. Product work needs that connection before a
future editor can reference assets by a portable manifest.

ADR-0009 keeps customer upload, binary storage, scanning, extraction and provider
transfer closed. A catalog must not make those operations appear ready merely
because the application has a table called "material".

## Decision

1. Store only metadata for the two code-owned synthetic sources of each brand.
   A server-authorized POST creates those records from a closed catalog; request
   fields, files, URLs and client-supplied metadata are ignored.
2. Bind each catalog item permanently to the owner-scoped Brand and the identity
   version current when the kit is first prepared. Existing records are never
   rebound after a later brand change. A catalog item and its version metadata
   are append-only application records, not a tamper-proof SQL vault.
3. Record display name, declared MIME type, byte/pixel bounds, source label,
   synthetic-use label and a digest of canonical catalog metadata. The digest is
   **not a binary file hash**, scanner result, rights proof or advertising claim.
4. Keep type and byte/pixel caps explicit for future JPEG/PNG/WebP design work.
   This slice catalogs only the existing PNG-rendered examples; it does not
   accept, persist, decode, expose or transform JPEG, PNG or WebP bytes.
5. Keep the catalog private: access resolves the brand through the authenticated
   owner and no public URL, static/media file, download endpoint, provider call,
   virus scan, OCR, extraction or publication path is introduced.
   Its POST boundary rejects multipart, unknown and oversized bodies before the
   CSRF layer can invoke Django's upload handlers; the browser's small CSRF form
   is the only accepted request shape.

## Consequences

- The editor's existing v1/v2 scenes and their raster rendering stay unchanged.
  The next editor schema work can add an explicit material-version reference
  without guessing an old brand or replacing a source key.
- The catalog is a bounded **Y05-A** foundation, not completion of Y05. It does
  not satisfy private binary storage, quarantine/scanning, deletion/backup,
  real rights declarations or customer material readiness.
- Future real-file work still needs an approved storage/scanner/parser threat
  model, exact format/size/pixel checks on bytes, deletion/restore evidence,
  tenant tests and the data/legal/provider gates in ADR-0009.
