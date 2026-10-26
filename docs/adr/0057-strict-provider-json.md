# ADR-0057: Shared unambiguous provider JSON boundary

- Status: Accepted for existing synthetic evaluation adapters
- Date: 2026-10-25
- Continues ADR0055/0056.

The typed-output experiment exposed an ignored unknown-root-field case in the
direct parser. Add a small owned `provider_json` helper to all three existing
OpenAI/OpenRouter/Ollama adapters, without adding a runtime library or changing
provider/model selection, request body, credentials, accounting limits or routes.

Outer provider envelopes retain varying metadata fields, but must be bounded
UTF-8 JSON objects with unique decoded keys at every level. Reject NaN/Infinity,
overflowing floats, malformed/trailing/deep JSON and non-object roots. Character
and encoded byte checks cap input at64KiB before unbounded conversion. Generic
errors never echo raw provider fields/values; recursion/encoding failures become
the existing adapter rejection type. A malformed response does not grant budget
settlement or retry authority; existing accounting/uncertain handling remains.

Generated inner output must contain exactly `variants`, a list of1–5 objects with
exactly key/angle/headline/body/call_to_action fields. Text must be bounded,
nonblank and UTF-8 encodable. Existing domain validation still checks distinct
keys/angles, source fingerprint and non-publishable candidate semantics. Varying
provider envelope metadata is not confused with the closed inner content schema.
This is structural/ambiguity validation, not factual/claim/policy clearance.

53 offline new-parser/existing-gateway/brand-task checks passed, including all
three actual adapters with mocked HTTP, valid Unicode, unknown fields, duplicate
decoded/escaped keys, ambiguous outer metadata, nonfinite/overflow numbers,
size/depth/type errors and safe failure/connection closure. No live API calls or
secret lookup occurred; no provider data is logged.

The isolated experiment now has16 controlled cases and288 executions per normal
and optimized run. Direct parsing rejects unknown root fields and duplicate
root/variant keys. The strict typed schema rejects unknown fields but its JSON
decoding accepts duplicate keys in these fixtures. Both still accept shaped
unsupported claims. The earlier13-case/234-run ADR0056 baseline remains dated
evidence; this is an explicit regression-suite extension, not a model-quality
comparison. Required CI recreates the pinned experiment separately.

Next: expose the owned brand-bound offline template candidate path in the local
creative journey with explicit review/selection and preserved user edits. Do not
connect a hosted provider or grant publish/spend authority through this parser.
