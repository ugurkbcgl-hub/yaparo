# ADR0066 — Selected campaign AI source package

Accepted 26 October 2026 for the existing default-off local trial.

The read-only ADR0065 preview can download its selected revision as a separate
six-file ZIP: ad.png,source.png,draft.json,manifest.json,README.txt,campaign.json.
The independent ADR0064 five-file draft package stays unchanged. A closed campaign
mode in the existing bounded ZIP_STORED writer accepts exactly the sixth fixed
ASCII filename; per-file8MiB/aggregate20MiB limits and CRC verification remain.
No general archive API, importer, uploaded PNG, dependency or migration is added.

A private safe-method version-addressed package.json route calls the existing
selected() reader: current owner/workspace/flags/source/history and selection
version are rechecked under the campaign-first lock graph. Stale selections refuse
rather than substitute the latest one. Normal draft edits retain the pinned old
revision; explicit reselection is still required. Unknown query parameters refuse.
Auth/errors/method refusals receive private/no-store/noindex headers.

The response wraps exact canonical UTF8 ad_json plus selection metadata. Campaign,
workspace, choice and revision PKs are strings, avoiding JavaScript integer rounding.
Selection version, selected_at, ad identity/revision/profile/source fingerprint and
the canonical snapshot SHA256 are pinned in the preview bootstrap. The browser
compares every selection field, hashes the exact ad_json bytes (no cross-language
reserialization), and applies existing content/geometry/source checks before ZIP.
campaign.json records that selection; manifest.json binds each of the five data
files by size/hash and labels the client render. The manifest does not hash itself.
Campaign display names are not presented as immutable selection data. README
explains the extra file, name omission and planning-only status.

Readonly form/save behavior stays unchanged. Only a server-provided selection
enables the campaign package control. The button captures the current saved canvas,
checks fields after async work, refuses malformed/oversized/mismatched responses
and never pairs an old selection with a new revision. A successful captured package
remains that historical export; it is not a live latest-version link, a digital
signature, server-render attestation, brand match or publishing/rights approval.
General package import/standalone editing remain open. Font/browser portability
limits from ADR0064 still apply.

Evidence:36 focused tests,32 passed/4 PostgreSQL-only skips. The two new HTTP cases
check exact canonical hash and pinned snapshot after later edit/campaign rename,
scope/flag/auth/corrupt source, HEAD/method/query and stale reselection. Two new
browser cases verify all six files/CRC/every hash, PNG equality, old selected text,
wrong campaign context, raw JSON metadata tampering and stale download refusal.
The previous campaign/source/independent five-file regressions also pass. Ruff,
format/migration drift/diff checks and independent read-only review passed. Required
full PostgreSQL/browser CI must pass before merge. Provider/ledger spies forbid calls.

Actual normal in-app login on campaign1/selection1 produced a package-ready message.
Independent Chromium downloaded the existing portrait revision1 ZIP and verified
CRC/all hashes/source hash/canonical snapshot-selection hash and1080×1350 pixels.
All38 non-auth DB tables compared unchanged. Known private root holds
campaign-selected-source-package.zip,campaign-ai-package-evidence.json and
campaign-ai-package-{1440,390}.png. No DB/source/history/choice/hold write, provider
credential, new AI charge, protected Google fixture or deployment.

Next: define and test an immutable brand/brief/material-version contract for the
next brand-aware hosted-generation slice using synthetic mocked transport first.
The fixed Duru trial must remain separate and must not be retroactively labelled
as generated against an existing BrandIdentity. General production jobs stay gated.
