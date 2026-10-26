# Yaparo — current handoff

Verified: 2026-10-26 19:55 Europe/Istanbul (+03:00). Recheck mutable facts.

## Objective and preferences

Owned-core/open-source plan (ADR0040, Y01–Y32). Current local synthetic journey:
brand/material/editor → reviewed real AI → saved creative/campaign planning.
Usage monitoring is disabled; never query usage or restart monitors. Reviewed
green PRs may merge under standing authorization; never push main directly.
Existing approved OpenRouter evaluation pool USD16; owner handles balance checks.
No new service/recharge, customer data, real account, media spend or publishing.

## Repository and current milestone

Checkout: C:\Users\ugrkb\OneDrive\Masaüstü\yaparo
Remote: https://github.com/ugurkbcgl-hub/yaparo
Private Python: %USERPROFILE%\.yaparo\.venv; secrets remain outside OneDrive.
Base main bd877ff / PR364 merged; main CI40327599783 passed.
Current branch codex/brand-bound-ai-generation, not yet committed/PR at snapshot.
Task issue328. Recheck head/PR/required CI before merge.

ADR0068 adds default-off LOCAL_BRAND_AI_ENABLED plus exact reviewed synthetic
request UUID/fingerprint admission, independent of ADR0067's unauthorized envelope.
workspaces0011 BrandGenerationAttempt commits one intent before budget/provider;
conditional transitions, capture-before-settlement, bound readback and no retry.
New per-brand copy adapter1024 tokens preserves old512 trials. Image adapter now
validates extension against bytes and supplies detected MIME to normalization.
No source pixels/logo binary supplied. Private CSRF POST/result/image reads.

Actual normal website generation against brand1 Duru identity2, bound source
4b2de5c5-17bd-4835-a928-25f7a0588efc revision1:
- request3 dd955529-bdd0-43d5-bc32-05f3eac71ca9:3 Turkish variants, GPT-6 Luna/Azure,
  513 input/1010 output, USD0.00055630, completed/settled.
- request4 78885b7c-0412-4ce9-b8c6-debc5a5cd61d:768×1376 JPEG128201 bytes,
  normalized PNG854996 bytes, requested Gemini3.1 Flash Lite Image/Google Vertex,
  USD0.03364200, completed/settled. Blue/terracotta cups, no text/logo, natural light.
- successful total USD0.03419830. Local cumulative settled spent USD0.22943485;
  holds USD0.10170650 including historical0.00078075. NOT account balance.
- initial request1 text HTTP200 truncated at512 tokens; request2 image HTTP200/
  complete rejected by initial extension/MIME bug. Both preserved unverified/held,
  no output/precise receipt; visible rounded provider charges0.000305/0.0336.
  Never delete/reset/retry or release holds ad hoc. Safe stage/category diagnostics
  now added. Exact historical billing reconciliation remains separate work.

Checks:19 focused tests17 pass/2 PG skips before final two new guard cases;
subsequent12 generation checks11 pass/1 PG skip, including JPEG/mismatch and HTTP
method/CSRF/intake/fingerprint. Browser mock journey/reload/repeatedPOST/mobile
passed; actual user browser generation and key-free restart/readback passed.
Ruff and drift passed; final formatting/full required PostgreSQL CI pending.
Independent source re-review found no blocker. This is smoke, not quality benchmark.

## Same private preview — preserve it

%TEMP%\yaparo-public-preview-q2ql3pkq / preview.sqlite3 / loopback8002.
Schema workspaces0011 / campaigns0010. Forward0011 backup:
preview-before-brand-ai-20261026T163458Z.sqlite3. All old rows across36 prior
non-auth/non-framework tables preserved; four requests/four attempts now exist.
Old fixed trials/drafts/source/history/campaign choices remain independent.
Current known serve_design_preview.py process restarted WITHOUT provider key or
hard-cap assertion. Exact private brand-ai-approved.json permits only requests1–4;
no new request automatically gets paid permission. Normal repo flags stay off.
Verify exact listener command before restarting. Never recreate/replace DB or
reset intent/history. Private evidence brand-ai-live-evidence.json,
brand-ai-image-iab.png, brand-bound-real-image.png. Saved results survive restart.
Normal IAB test login renewed with existing protected credential, no rotation:
%USERPROFILE%\.yaparo\preview-test-login.dpapi, prepare_preview_login.py READ mode.
Never print helper output or use default mode just to log in. Provider key remains
in existing Windows protected store; never print or copy into repo/docs/chat.

Established previous milestones: ADR0060/61 fixed Duru text/image trials;
ADR0062 editable independent draft; ADR0063 square/portrait; ADR0064 saved ZIP;
ADR0065 pinned campaign choice; ADR0066 campaign ZIP; ADR0067 immutable owned
brand brief/source context. None is retroactively rebound to new requests.
General upload/rights/scan/isolation/font/production editor gates remain open.

## Preserved integration and release gates

Rename: docs/continuity/RENAMING.md. Keep stable Python/migration labels, UUIDs,
DB/DPAPI/OAuth IDs; no global replacement or identity/credential reset.
Actual scoped Google candidate remains quarantined; token/account proof is not
established here. Origin session/process secret was lost. Private root:
%TEMP%\gwt-scoped-preparation-_jafwrsl / synthetic.sqlite3. Completed PREPARE and
forward0007 APPLY MUST NOT rerun. No new permit/retry/reset/activation/refresh.
See recovered-inspection-exercise-preparation.md / windows-inspection-fixture.md
under docs/product. Fabricated fixture proof is not actual candidate evidence.
Historical Google PAUSED TEST evidence is not live delivery/performance proof.
Fresh staging E2E, configured DB/files restore, code/schema rollback, privacy/
domain, upload isolation, tenant token controls, real platform metrics/permissions,
payments and financial consent remain release gates. No production-ready claim.
Old usage/time monitors remain disabled. A15-minute heartbeat's actual execution
was not verified by this product task; scheduling is not proof of work.

## Next action

Compose the owned completed brand text/image results into an explicitly selected,
identity-pinned editable creative with immutable request/source/cost provenance.
Preserve old drafts/campaign choices and failures/holds; use saved outputs without
another provider call. Keep general customer/provider/publishing gates closed.
