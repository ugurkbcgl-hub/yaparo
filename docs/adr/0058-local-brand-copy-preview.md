# ADR-0058: Read-only local brand-copy candidate preview

- Status: Accepted local synthetic slice; no hosted AI/product promotion
- Date: 2026-10-26
- Continues ADR0055/0057 and the first local Y11 journey slice.

Expose the existing owned brand-bound task envelope through a GET/HEAD-only
candidate preview. It calls only SyntheticTemplateGenerator, then reconstructs
and validates the server-owned request/result again. No OpenAI/OpenRouter/Ollama
adapter, provider credential or live inference is involved. Normal settings keep
the new SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED flag off; DEBUG and the existing
campaign-design flag are also required. No database migration or new SDK.

The page displays three fixed-fixture text candidates, pinned brand identity,
selected design revision and the fixed source facts. Candidate cards use the
validated brand color; tone is identity metadata, not a measured output-quality
score. The UI clearly labels these as fictional template examples, not AI output
or publishing approval. No candidate/task result is persisted and each read uses
an ephemeral task ID. This is not a durable job, audit trail or API authorization.

The selected immutable snapshot is retained even if the live editor document has
new user edits. No candidate replaces a title/body, selects a design, restores a
revision, updates campaign copy or grants spend/publication authority. The page
links back to selection/selected preview and separately to the current editor.
Applying a candidate requires a later explicit, stale-safe action and field-fit
contract; no silent truncation is accepted. Y11 is not declared complete.

Owner/workspace/activity/archive and task/source/selection checks apply before
and after template construction. Changed selection or revoked scope refuses;
failed/invalid output is not displayed. Unsafe/multipart requests reject before
CSRF/body parsing, including leading-zero paths. Auth/success/error responses are
private/no-store/noindex. CSP disables page scripts; output is HTML-escaped and
no save/apply form is exposed in the task area. The existing header logout form
remains available and is not mistaken for a candidate write action.

Eight focused service/HTTP/browser checks passed. They verify read-only records,
user edit preservation, flags/scope/reselection/archive refusal, mid-build selection
change, escaping and preparse refusal. A real browser follows the choice link,
checks three cards at desktop/mobile widths without overflow and opens the editor
with the user's revision2/title unchanged. Mobile screenshot reviewed. Another58
gateway/task/design-view checks passed. Ruff/format/migration-drift/diff checks
pass; required PR CI is checked separately. No real provider/quality/claim-safety
evaluation is inferred from these fixed examples.

Next: define and implement explicit application of a selected offline candidate
to a new saved document revision, with ownership/selection/current revision checks,
field-fit validation and preserved history. Keep hosted generation, real data,
financial execution and production publishing behind their separate gates.
