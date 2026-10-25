# Y08: Measured local synthetic design journey

25 October2026. Continues ADR0052–0054 and delivery-plan Y07/Y08.
This is automated browser evidence on disposable synthetic fixtures. No customers,
independent human observations, production traffic or provider access were used.
Y08 human validation remains open: planned six consented observations and at least
five independent completions have not happened.

## Observed obstruction

Starting at an unbound campaign with existing synthetic brands but no designs,
the old chooser offered the global brand list. Brand → create → editor lost the
campaign return context. The actual baseline browser reached the editor with no
campaign return link: the task was blocked, not successfully completed. The
recorded1.501s baseline includes launch/login and reaching this obstruction; it is
NOT comparable to the post-login completed-task timings below. No human speed or
completion-rate improvement is inferred.

The chooser now offers direct new-design links only for active brands in the
same owned workspace. A typed optional campaign ID is preserved through brand,
create redirect, saved document and editor. Failed creation also keeps the return
and retry links. The ID is checked again against active ownership/workspace at each
step; flags/DEBUG, bounded positive integer and internal reversed routes apply.
It is never a free redirect URL, hidden POST authority, automatic selection or
publication approval. Existing general brand navigation remains available.

The saved-document introduction also now explains that full visual editing is in
the visual editor, instead of suggesting the product cannot produce visual files.

## Actual completed rehearsals

Chromium local runs after login measured nine checkpoints: chooser → same-workspace
brand → create saved design → edit/save → return still unselected → explicit
selection → read-only preview → decoded800x800 PNG → ZIP containing selected
revision2 and edited title. No horizontal overflow at any checkpoint; no browser
JavaScript errors. Separate scope/error tests confirm no implicit choice.

| Width | First completed run | Regression run | Outcome |
|---|---:|---:|---|
|1440px|1.174s|1.057s|All nine checkpoints completed|
|390px|1.067s|0.899s|All nine checkpoints completed|

These are automated interaction/wait/download timings on one local environment,
excluding browser launch/login in completed runs. They exclude human reading,
typing and decision time; they are not a production latency SLA or a comparison
benchmark. No timing threshold is enforced in tests. Raw optional reports and
screenshots live privately under the configured YAPARO_JOURNEY_REPORT_DIR; tests
write only explicit synthetic report fields, never credentials or browser state.
Mobile final screenshot was reviewed.

34 relevant HTTP/service/browser checks ran:31 passed,3 PostgreSQL-only local
skips. Typed/foreign/same-owner-other-workspace/disabled hints, failed creation,
document persistence and previous campaign selection journeys were included.
The broader changed workspace module also passed133 checks (128 pass/5 PostgreSQL
local skips). Ruff/format/migration-drift/diff checks passed. Required PR CI is
checked separately.

## Scope and next step

This rehearsal starts with an authenticated owner and existing synthetic brands.
New-account/brand onboarding, identity edits, material preparation/generation side
paths, general uploads, production and independent human usability are outside
this measured slice. It does not complete Y05/Y06 or release gates.

Next Y09: inspect the existing AI gateway/provider contracts and define a narrow
brand/source/version-bound capability profile before adding generation. Read
AI_PROVIDERS.md and relevant ADRs first; no new provider, model package, paid
service or real-data experiment is authorized by this rehearsal.
