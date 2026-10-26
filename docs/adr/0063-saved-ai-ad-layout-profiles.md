# ADR0063 — Explicit saved-output ad layouts

Accepted 26 October 2026 for the default-off local synthetic trial.

Extend ADR0062 with two independent versioned profiles: square1080×1080 and
portrait1080×1350. The original overlay-v1 remains768×1376. Explicit creation
selects the profile; immutable source manifests include the new profile's exact
geometry, fit mode and label. Existing manifests remain byte-equivalent in their
data and are not backfilled. Geometry never changes on save or replay.

Uniqueness now includes profile as well as text/image/candidate. Each format has
its own UUID, content, revision and history; repeated creation reopens that exact
format's edits. Profiles accept only the existing checked768×1376 source. A source
fingerprint from another profile, unknown profile, altered layout or save-time
profile field refuses. Old chooser forms without a profile retain legacy creation.
Fresh ownership, source validation, locking, private image checks and default-off
admission stay unchanged. No inference, ledger operation, campaign association,
brand binding, advertising, paid service or production deployment is introduced.

New layouts use a768-unit design scaled to the exact output canvas. A fixed header
holds editable text/CTA; the complete source photo is fitted proportionally into
the remaining area, centered with cream side space. No crop, distortion, invented
image fill or automatic text shortening. This is a deliberately bounded layout,
not an optimized creative for every channel. Text fit remains client-measured;
the server retains ADR0062's semantic/length bounds. Original overlay draw order
and transparent pixels stay unchanged. Download requires unchanged saved content
and verified source bytes; filename binds UUID and revision. No channel suitability
or policy approval is inferred from dimensions alone.

Migration0009 only replaces the uniqueness constraint and does not rewrite draft
or history rows. Once multiple profiles exist for one source/candidate, reversing
to the old uniqueness can fail. Do not automatically reverse0009, delete profiles
or restore an old backup over later user work. Schema rollback requires a separate
reviewed data-preserving plan; ordinary app recovery should retain the new schema.

Evidence:19 targeted local tests,17 passed/2 PostgreSQL-only race skips. Tests cover
separate formats/history/replay, profile/fingerprint/geometry tamper refusal, fixed
format saves, exact PNG dimensions, fitted source regions, mobile overflow and old
alpha pixels. Existing provider/ledger spies forbid all calls. Independent read-only
source review found and then verified the legacy alpha regression fix; no blockers
remain. Required CI still must verify PostgreSQL races and broader tests before merge.

The same known private preview DB was consistently backed up before forward0009.
All existing rows were compared unchanged; only a migration recorder row was added.
No protected Google fixture or configured database was accessed. Normal test login
then created a new square draft from actual previously saved text/image sources.
No provider credential was loaded or added to the preview server.

Next: export a saved formatted draft as an owned source-manifest package, keeping
the PNG/profile/content revision together for later explicit campaign selection.
Do not silently associate this independent trial with a BrandIdentity or campaign.
