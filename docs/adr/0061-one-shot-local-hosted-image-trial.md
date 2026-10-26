# ADR-0061: One-shot owned local AI image trial

- Status: Accepted local fictional-data trial, defaults disabled
- Date:2026-10-26
- Continues ADR0060; no general upload, production provider or publishing grant.

Add a separate image page linked from the admitted text trial. It sends only the
existing fixed fictional Duru Studio IMAGE_PROMPT. It does not send editable brand
metadata, customer files or images. DEBUG, text workspace admission and a separate
default-off LOCAL_HOSTED_IMAGE_TRIAL_ENABLED flag are required. Text job1 remains
unchanged. A fresh unique HostedImageTrial row commits before reservation/call;
workspace/owner references use PROTECT. Existing intents never dispatch again.

Move the existing bounded image transport from the operator script into the AI
gateway, preserving the script's exports/calling behavior. Pin the same single
Google Vertex route, no fallback, ZDR and data-collection denial. The fixed request
asks for1K,9:16,n=1. Parse an at-most24MB response with duplicate/finite-number
checks. The shared JSON loader's default64KiB remains unchanged for text; image
explicitly supplies the larger bound. The API provides bytes and usage cost, not
independently returned model/provider identity: UI labels these as requested model
and route. Never infer exact aspect ratio from the request; show measured pixels.

Use the existing shared USD16 ledger, with a USD0.10 image reservation. Preserve
the text runner's USD0.01 limit and the historical unresolved hold. Commit known
cost before decoding; accept at most3MiB of original bytes, verify format and
retain original/hash before normalization. Reuse the existing4MP/4096-edge bounded
single-frame raster validator to create a metadata-free PNG, at most8MiB. Store
both objects, hashes, measured dimensions and tool provenance in the private DB.
Structural validation is not malware scanning or commercial rights clearance.

Persist image/metadata before settlement; reservation and settlement acknowledgment
ambiguity is unknown until verified. Completion follows confirmed settlement only.
Crashes, decode failures or ambiguous storage/accounting block repeat calls; no
delete, retry, worker, reset or reconciliation endpoint. Original bytes never have
an HTTP route. Owned GET/HEAD returns only a completed PNG after hash, size, source,
dimension and accounting checks. Download returns the same PNG, not a fresh call.
Private/no-store/noindex headers cover redirects and framework/CSRF errors. Closed
small URL-encoded POSTs are enforced before CSRF; no file, URL or raw prompt intake.
No result changes a brand identity, editor document, campaign choice or publication.

The one additive workspaces0007 migration was applied only to the existing private
preview after a fresh backup. Every preexisting row compared unchanged; additions
were the image table, one migration/content type and four permissions. Integrity
passed. After actual generation, a separate consistent backup was read without
replacing the source DB: original and PNG hashes, full decode/dimensions and the
existing completed text job were verified. This is local backup readback, not
configured PostgreSQL/Heroku restore or disaster-recovery qualification.

Evidence:80 focused checks (78 pass/2 PostgreSQL-only skips), plus14 raster/parser/
browser checks all passed. Actual browser normal login clicked the real image
button once:768×1376 JPEG,98,295 original bytes;592,509-byte PNG; USD0.033625.
The image matches the requested olive/sand mugs, natural light and clear top area;
agent visual review found no visible text/logo/person. It is an invented product,
not a faithful real product photograph. Reopen, explicit repeated POST and download
preserved one job and unchanged cost; existing text row was compared exactly.
Temporary test password was restored to its original hash after QA; no value was
retained. Cumulative local spent USD0.19523655, historical hold USD0.00078075 intact.
No account balance/credit usage inspected. Fresh public catalog route/capabilities/
pricing/ZDR and key cap USD16/no reset were checked before the call. Independent
source review passed; required CI/actual PostgreSQL race must pass before merge.
The first CI run's only failure was the browser checking image dimensions before
decode completed. Explicit auto-waiting complete/naturalWidth assertions replace
the immediate check; targeted browser rerun passed without a paid provider call.

Next: explicitly combine a selected saved real text and this owned image into a
new editable ad draft, with true image/task provenance and preserved originals.
Do not label the AI image as a fixed palette fixture or silently replace an old
design/campaign selection. This next slice should not require more provider calls.
