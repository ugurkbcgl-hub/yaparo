# ADR0064 — Saved AI ad source package

Accepted 26 October 2026 for the existing default-off synthetic trial.

An admitted owner can download the current saved HostedAdDraft as a ZIP containing
ad.png (the browser-rendered saved canvas), source.png (the verified normalized AI
source), draft.json (saved content, profile, revision, source manifest and renderer
requirements), manifest.json (file byte lengths/SHA256), and README.txt. No original
JPEG, account credentials, user-uploaded file or arbitrary URL is read. No inference,
ledger mutation, campaign association, new dependency or database migration is added.

A private read-only version-addressed JSON endpoint rechecks current ownership,
default-off admission, both saved source jobs, source bytes/manifests and current
history. It locks source/draft rows in existing order and refuses a stale revision;
there is no silent latest-version substitution. Auth, errors and method refusals
receive private/no-store/noindex headers. Unknown query options refuse. HEAD is safe.

Only unchanged saved fields and a verified source enable the ZIP button. The browser
captures that canvas, reads bounded same-origin JSON without redirects, compares
UUID/revision/profile/source fingerprint/content/dimensions/mode/source PNG hash,
and rechecks fields before download. Edits while fetching refuse rather than pair
new pixels with old metadata. After a consistent snapshot is read, another tab may
later save a new revision; the package remains the explicitly captured saved one.
It is not a live link or a guarantee that it is still the newest revision forever.

A narrow ZIP_STORED writer accepts exactly five fixed ASCII filenames and bounded
byte arrays (8MiB each,20MiB aggregate). CRC32, local/central headers and offsets are
verified by Python's independent ZipFile reader. No decompression, path handling,
general archive API or importer is exposed. File hashes cover the four data files;
manifest.json cannot hash itself. Stored filenames, UUID and revision identify the
download; the archive stays in browser memory until handed to the download manager.

This is client-assembled provenance/integrity information, not a digital signature,
server attestation of rendered pixels, rights certificate or advertising/legal
approval. Private contents may be shared only at the owner's choice; no third-party
transmission is added. There is no general package import or standalone editor.
Re-rendering requires the matching Canvas2D renderer/system Arial; different fonts
or browsers can change pixels. The exact exported ad.png is preserved in the ZIP.

Evidence:23 focused tests,21 passed/2 PostgreSQL-only race skips. Six browser tests
include all three profile ZIPs, CRC, exact equality to the separate saved PNG,
source bytes, every manifest hash/length, unsaved edits, stale other-tab refusal,
malformed/oversized/mismatched responses and edits while fetching. Endpoint tests
cover ownership, flags, corrupt sources, current revision, HEAD/method/query/auth
and private headers. Provider/ledger spies deny all calls. Ruff/format/migration
drift/diff checks and independent read-only source review passed. Required broad
PostgreSQL/browser CI still must pass before merge.

Actual in-app normal test login on the existing portrait draft revision1 produced
the package-ready message. An independent Chromium development QA session then
downloaded that actual ZIP, verified CRC/all hashes/source hash/1080×1350 PNG, and
compared37 non-auth DB tables unchanged. Artifact and evidence stay in the known
private preview root as duru-portrait-source-package.zip/ad-package-evidence.json.
No source/history/hold change, configured DB/Google fixture access or AI cost.

Next: explicitly select a saved HostedAdDraft revision for a local campaign's visual
planning reference, with ownership/source checks and a pinned read-only preview.
Do not infer BrandIdentity binding or change existing Search dispatch/publishing.
