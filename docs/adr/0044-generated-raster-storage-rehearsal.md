# ADR-0044: Generated raster storage rehearsal

- Status: Accepted for isolated synthetic evaluation
- Date: 2026-10-25
- Continues ADR-0009/0043; owner delegated local implementation.

## Decision

Y05-B starts with an internal rehearsal of three code-generated64×48 JPEG/PNG/
WebP examples using an owned synthetic brand's palette. Its switch defaults False
and DEBUG must also be True. No route, customer-byte/path/URL input, durable
asset write or provider operation is introduced. Existing catalog/editor behavior
is unchanged.

Pillow13.0.0 is pinned in development dependencies for evaluation. PyPI records
Python3.13 support and MIT-CMU licensing; CI audits the installed package. Sources:
[PyPI](https://pypi.org/project/pillow/13.0.0/),
[Pillow Image API](https://pillow.readthedocs.io/en/stable/reference/Image.html).

## Validation and provenance

Sources are capped at3 MiB. Declared type must match the actual decoder format;
dimensions must each be1–4096 and total pixels≤4,000,000. Animation, truncation,
unknown types and decompression-bomb warnings/errors are rejected. Verify, reopen,
fully decode, apply EXIF orientation and copy RGBA pixels into a fresh PNG capped
at8 MiB. EXIF/comments/profiles are not copied; color-profile fidelity is not
claimed. Original and derivative use separate files. Readback verifies original
bytes and derivative SHA256. Scalar evidence records measured byte sizes, both
hashes, dimensions and exact normalization tool version.

`structure_verified` is not a malware CLEAN result, READY customer asset, rights
proof or publication permission. No scanner outcome is fabricated.

## Private disposable storage

Fresh temporary directory, no supplied roots or names; POSIX0700/0600 permissions.
Windows establishes and verifies a protected current-user-only directory ACL
before bytes are written. Failure refuses the run. UUID filenames, exclusive
writes, six-file quota and8 MiB per-file cap apply. No public URLs or file routes.
Root identity/reparse and regular-file/link checks detect accidental replacement.
These are best-effort checks, not atomic protection from a hostile same-user
process. Decoding runs in the test process without a CPU sandbox; only internally
generated images may use this rehearsal. Untrusted intake requires separate
enforceable time/memory isolation and scanning.

Brand ownership is checked before storage and again before reporting. Exact
inventoried files are deleted individually on success/failure. Unexpected files
or links prevent cleanup success; no recursive cleanup is performed. A crash can
leave an orphan private directory, so durable deletion/retention/restore is not
proven. No migration, configured database, cloud storage or paid service.

## Next slice

Durable original/derivative records, private storage adapter, crash/orphan
reconciliation and backup/restore. Customer files stay closed under ADR-0009's
scanning, isolation, rights, privacy and tenant gates. Y05 remains incomplete.
