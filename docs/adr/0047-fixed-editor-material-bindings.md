# ADR-0047: Fixed editor material-version bindings

- Status: Accepted for local synthetic implementation
- Date: 2026-10-25
- Continues ADR-0043/0046 and the Y04–Y07 creative journey.

New saved scenes keep their v2 rendering/schema and gain permanent server-side
hero/logo bindings to the brand's two fixed catalog material versions. Creation
prepares missing fixed catalog items and commits document, both bindings and
initial history together under the existing owned-brand lock. No caller-supplied
material ID, URL, file, raster or provider input is accepted.

The binding format marker distinguishes new documents from old v1/v2 scenes.
Migration0005 adds marker0 to old records without inventing historical provenance;
replay/save/restore never backfills them. New records use marker1 and require
exactly two matching immutable bindings. Read/save/replay/history/restore deny
missing, foreign or contradictory source metadata. A PROTECT foreign key prevents
deleting any referenced material version through its parent cascade. Application
immutability is not a SQL tamper-proof vault.

A source catalog item may predate the document's identity: its original identity
remains pinned while the scene retains the newer brand palette literals. The
detail page shows each source identity/version separately. These fixed source
metadata records are not raster files, file hashes, rights or scan evidence.
Scene JSON download is unchanged and is not yet a complete portable asset bundle.
Generated palette PNGs remain separate, not silently substituted for illustrations.

Verification covers atomic failure after the first binding, owner/brand scope,
source retention, immutable bindings, legacy save/replay, new save/restore and
metadata mismatch refusal. The existing browser workflow also checks source
details at desktop/mobile sizes then reopens, edits/restores and decodes exported
PNG pixels. Migration runs only in disposable test databases in this slice;
configured local preview, PostgreSQL/staging, protected Google fixture and
production remain untouched.

Next: a separately versioned, explicitly chosen owned palette-image layer and
private byte load/export, preserving old scene rendering and source provenance.
