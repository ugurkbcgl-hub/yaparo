# ADR-0051: Explicit square and portrait scene v4

- Status: Accepted for local synthetic implementation
- Date: 2026-10-25
- Continues Y06–Y07 and ADR-0048/0049/0050.

New UI creation forms explicitly choose square800×800 or portrait800×1000. Both
fixed illustration and owned palette sources use scene v4, with exact `format`
and `hero_source` keys. Width stays800; format fixes height and vertical position
limit (height minus100). The portrait fixture places its hero100 units lower.
No arbitrary dimensions, source URL, file or existing-document conversion exists.
These are local canvas formats, not platform delivery/policy certification.

The optional service/form parameter preserves older cached forms and callers:
omitting it still creates v2/v3 squares. Existing v1–v3 data/rendering is unchanged.
Create replay must match format and exact source; save/restore rejects schema,
dimensions, format or hero-source changes. The shared palette predicate keeps
model bindings, metadata checks, private URL bootstrap and bundle bytes aligned.
No model schema or migration is required; no stored scene is rewritten.

The preview uses the saved aspect ratio, proportional viewport and height-aware
controls. PNG export temporarily uses exact logical dimensions/identity viewport,
then restores display dimensions/viewport in a finally block. This prevents
fractional mobile display sizes from rounding output to999/1001 pixels. Export
does not modify scene/local undo or committed history. Old PNG colors/dimensions
and post-export pointer transforms are regression-tested.

V4 bundles declare renderer contract yaparo-scene-v1-v4; older scenes keep the
previous contract. The no-input private bundle rehearsal now transfers a fixed
v4 portrait through its manifest to a fresh workspace and reexports it, preserving
source identities/bytes/pixels and the source DB/archive. Prior v3 evidence remains
historical. This is still not a general importer or configured DB recovery.

Verification: strict shape/types/limits, replay/source/format refusal, HTTP choice,
save/restore/bundle, actual desktop/mobile800×1000 PNG and bottom/palette pixels,
responsive999/390 viewports, export then drag/undo and legacy v1/v2/v3 PNGs.
Desktop/mobile screenshots reviewed. New services/dependencies/provider calls,
customer inputs and production deployment remain outside this slice.

Next: first owned synthetic campaign → explicit brand/design selection journey,
pinning a saved design revision. Do not infer a brand for older drafts, cross
workspace boundaries or treat selection as publishing approval.
