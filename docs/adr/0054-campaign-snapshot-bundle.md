# ADR-0054: Campaign-selected design ZIP

- Status: Accepted for local synthetic implementation
- Date: 2026-10-25
- Continues ADR-0049/0052/0053 and Y07.

The read-only campaign preview adds a version-addressed ZIP download. It includes
the selected immutable scene/revision, pinned brand identity and material metadata,
and actual original/normalized PNGs when the fixed palette source is used.
`campaign_selection` in manifest.json identifies campaign, selection ID/version,
snapshot ID, document revision and brand ID. No customer brief, credentials,
provider payload or owner identity is included. Fixed illustration/logo metadata
still does not imply an original binary or rights/scan proof. Arial and the stated
fixed renderer remain required; the package is not a standalone editor/importer.

The document ZIP keeps exporting the current saved document. Both callers share
the bounded deterministic serializer; campaign ZIP explicitly supplies the old
snapshot scene/revision and selection manifest. Default document manifest/README
remain unchanged. Campaign README explains this distinction. Each included file
has measured size/hash in the manifest; deterministic ordering,12MiB package and
64KiB manifest limits are retained. There is no archive intake or extraction.

Current selection and owner/workspace/activity/archive/source eligibility are
validated before and after collection. A selection or permission change observed
during collection refuses, without substituting a newer record. No new draft or
source locks, write operations, financial approval or provider calls are added.
Checks describe the observed eligible selection, not a perpetual grant after bytes
have been returned. The application-owned immutable source/history contracts apply.

DEBUG, campaign-design and material-persistence flags are required; the preview
hides ZIP when material persistence is disabled. GET/HEAD only. Unsafe methods,
including multipart/leading-zero routes, reject before body parsing. All success,
authentication and error responses remain private/no-store/noindex; attachment
names use only typed numeric IDs and response is nosniff. No migration or configured
database change is needed.

Checks verify current document revision2 versus selected archive revision1,
deterministic repeated bytes, file hashes, exact palette original/normalized bytes,
portrait dimensions, scope/flags/preparse method refusal, and selection/ownership
change during collection. Actual browser downloads before and after editing the
live design must remain identical. Existing document ZIP and bundle rehearsal
checks must pass. This is local synthetic capability, not production readiness.

Next Y08: measure the synthetic campaign → brand/design → edit/save → explicit
selection → preview/PNG/ZIP journey, record observed duration/errors and fix
demonstrated friction. Automated rehearsal is not independent human usability
validation; the planned six consented observations remain open.
