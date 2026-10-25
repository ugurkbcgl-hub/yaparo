# ADR-0048: Explicit owned palette image in scene v3

- Status: Accepted for local synthetic implementation
- Date: 2026-10-25
- Continues ADR-0045/0047, Y05–Y07.

An owner may explicitly open a new design from an already generated palette PNG
on the brand page. The form carries the exact palette material UUID, current
brand identity version and a new document request UUID. The owned service checks
the default-off persistence flag and DEBUG, current brand scope and both stored
byte hashes/sizes before creation. No file, URL, provider or arbitrary raster ID
is accepted. Foreign/missing/stale/corrupt input fails closed.

This creates scene v3: the hero uses the fixture's fixed palette source key; logo,
text, styling and transform bounds retain v2 behavior. Two permanent server-side
bindings pin the exact palette and logo material versions. Source palette colors
may predate the new document's style; the old source identity/bytes remain pinned.
Replay must name the same source. Existing v1/v2 documents are never converted;
save/restore cannot switch schema or source. A v3 document cannot claim the legacy
unbound marker. PROTECT preserves the referenced version and original/derived
bytes against parent removal. No migration or existing document rewrite is needed.

Only a binding-derived private image URL enters the editor bootstrap. The browser
accepts the fixed same-origin route, refuses redirects, fetches with same-origin
credentials/no-store and a10-second deadline, bounds streamed bytes at8 MiB and
checks PNG MIME/signature and320×200 decoded dimensions. The in-memory data URL
is rendered locally by Fabric; no external image/editor/AI fetch is needed.
Failed image read leaves save/export disabled, with no substitute illustration.
Immutable image data is reused for history restores within the page.

Scene JSON download remains a scene-only artifact, not a complete portable bundle.
Production storage, customer intake/rights/scanning/isolation/privacy, arbitrary
photos, source replacement and general image editing remain separate gates.
The palette example demonstrates the binary journey, not advertising quality.

Verification includes exact source replay, brand/owner boundaries, source/style
identity separation, marker/schema protections, source retention, HTTP creation,
actual browser save/reopen/restore, decoded exported PNG pixels and mobile layout.
Browser negative cases cover denied/missing/truncated/invalid/oversized/wrong-size
or wrong-MIME PNG and cross-origin redirect refusal. An initial local browser
failure served stale collected JS; rebuilding static assets resolved it. Local
browser evidence requires current collectstatic output, as CI already builds it.

Next: a versioned owned portable bundle carrying scene, bound source manifest and
the actual palette derivative, with a fresh-workspace recovery/import rehearsal.
Keep v1/v2 rendering and fixed source metadata semantics explicit in that design.
