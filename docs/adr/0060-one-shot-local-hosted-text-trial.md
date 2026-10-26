# ADR-0060: One-shot owned local hosted text trial

- Status: Accepted local fictional-data trial; normal defaults disabled
- Date:2026-10-26
- Continues ADR0055/0058/0059 and the real samples in PR356.

The owner requested real AI production through the website. Add a separate trial
page at `/workspace/brands/ai-trial/`, linked from the admitted owner's brand list.
It uses the exact fixed fictional Duru Studio request already evaluated in PR356.
It does not send editable brand/workspace names, campaign text, files or customer
data. Display this distinction explicitly; do not claim the result belongs to the
current brand identity or campaign. The offline template envelope remains unchanged.

Admission requires DEBUG, a separate default-off flag, one explicitly configured
workspace, fresh active ownership, a protected process credential and independently
verified key cap assertion. This is an operator-admitted local test, not a general
production AI feature. No model quality promotion follows from a successful call.

An explicit CSRF-protected POST carries only a fixed confirmation. One durable
HostedTextTrial row per workspace is committed before reservation or inference.
Reject ambient transactions; the view opts out of ATOMIC_REQUESTS. Serialize intent
creation using the existing workspace lock and a database OneToOne constraint.
Only the creator dispatches. Any existing row, including an uncertain/crashed one,
blocks a second call. Workspace/owner references use PROTECT. There is no delete,
reset, retry or reconciliation endpoint, background worker or automatic polling.

Reserve at most USD0.01 through the existing shared USD16 local ledger. Record
reservation intent as unknown before invoking the separate ledger; record held
only after confirmed reservation. Persist validated response/source/model/provider/
usage/cost/candidates before settlement. Mark settlement unknown durably before
calling it; settled/completed follows only normal return. This explicitly covers
commit followed by lost acknowledgment. A process crash can still leave uncertain
state across the two databases, so no automatic retry or release is allowed. A
later controlled reconciliation design must inspect evidence instead of rerunning
inference. This is one request-bound trial, not a general durable job scheduler.

GET/HEAD only read saved state. Repeat POSTs never dispatch again. Serve completed
results only after accounting and stored-result revalidation. Fixed error pages
omit provider exceptions/tracebacks even under DEBUG. Unknown outcomes say the
result is not yet verified, without promising a live worker. Pre-CSRF middleware
rejects multipart/JSON/oversized forms, denies unsafe methods, and applies private,
no-store/noindex headers to success, auth, CSRF and framework errors. Result output
is escaped and page scripts are disabled. No result is applied, selected or published.

One additive workspaces0006 migration creates only the trial table. The known
private SQLite preview was backed up before applying it. All old rows were compared
unchanged; the only standard additions were one migration, one content type and
four permissions. New trial table was initially empty and integrity_check passed.
No configured PostgreSQL, staging or protected Google candidate was changed.

Local evidence:222 related tests (216 passed/6 PostgreSQL-only skipped) before the
final settlement-ack regression; final trial suite13 tests (12 passed/1 PostgreSQL
skip). A mocked real-browser workflow and desktop/mobile screenshots passed.
Actual browser login with the existing disposable test owner then clicked the
real generation button:3 candidates,486 input/455 output tokens, GPT-6 Luna/Azure,
USD0.00027610. Reload and explicit repeated POST preserved one job and unchanged
cost/hold totals. Screenshots reviewed; no mobile overflow. Local spent is now
USD0.16161155; historical unresolved USD0.00078075 hold remains unchanged. No account
balance/credit usage was inspected. Fresh key hard cap USD16/no reset and an eligible
priced Azure ZDR route were verified before this call. Test credentials remained
in memory; no credential or generated binary was committed. Independent source
review completed, including settlement-ack fix; PostgreSQL race/required CI must
still pass before merge.

Next: add a separate one-shot image trial using the same fixed fictional brief,
with bounded bytes, durable source/hash/cost and owned readback. General brand-bound
generation, queued jobs, customer intake, editing AI images and publishing remain
later slices. No new infrastructure or deployment is introduced here.
