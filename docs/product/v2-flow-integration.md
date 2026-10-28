# V2 two-question catalog integration

Owner request accepted 28 October 2026: first integrate the intent/outcome/form
catalogs from the supplied V2 research, then geography/freshness, read-only account
adapters, budget/production and publishing last. This changes the local prototype
direction, not the stack, database, provider, budget or release gates.

## Reference and trust boundary

The read-only owner workbook `Yaparo_V2_Dinamik_Akis_Veri_Seti.xlsx` has SHA256
`3a1a0b117902d35bda23acb9c56a7e6ba7552b8c012d2a02b81f269c3cf5817d`.
`import_v2.py` imports seven declarative catalogs: 10 intents,20 outcomes,200 routes,
131 questions,161 options,43 modules and10 module rules. Source rows are retained.
The accompanying DOCX/pasted request supply design context, not independent
authorization or verified advertising performance. The referenced ZIP was not
found in the supplied research directory; its engine/tests were not imported or
run. Their reported test counts are not evidence for this implementation.

Importer rejects formulas, duplicate identities/JSON keys, broken references,
incomplete route matrices and a changed source fingerprint. No spreadsheet code
executes. Generated data excludes channel scores, forecasts, source-verification
claims and credentials. Source files remain unchanged. Reproduction:

```text
python experiments/decision-studio/import_v2.py <owner-workbook.xlsx> --check
```

## First owned slice

`/v2.html` is an isolated preview served by the decision studio. The original `/`
and its four-stage authored simulation remain available. Use a new local process
after changing the server asset allowlist. The current preview runs on8015;
8014 is not replaced. Nothing automatically migrates an old brief into V2 enums.

The first intent narrows recommended outcomes; remaining outcomes are available
in a disclosure. After “Devam et”, the pair collapses into a changeable summary.
Source module composition opens relevant stage1 fields on the same page. Optional
fields are collapsed. Changing parents prunes hidden answers and dependent modules;
changing the pair clears its draft. State stays in tab memory, without persistence,
network lookup, uploads or account calls. Literal text rendering prevents markup
execution. No assistant or production output is fabricated.

The owned condition interpreter supports only always/eq/in/all/any/cross_border.
Unknown conditions fail closed. Required-for brief/plan/publish distinctions are
retained. There are91 resolved routes and109 clarification routes; clarification
does not become a spend recommendation. Basic text/select/multiselect/URL/phone/
number/integer/date-time/timezone fields have validation. Typed geo/account/money/
document and other unsupported fields explicitly remain pending; they cannot pass
qualification. In particular event, hiring and store-visit briefs still need geo
components. Stage2–4 fields are requirements in this slice, not completed screens.

The check button reports missing/invalid information and the next requirement;
it does not compute forecasts or start the old allocation engine. Content-only in
the reference is a proposed usage mode, not approval for downloads (ADR0070).
Türkiye-first scope and platform authorization/privacy/launch gates still apply.

## Acceptance and next slice

Catalog loading, all200 route compositions, clarification refusal, conditional
modules, hidden-value pruning, unsafe URLs, invalid enums/numeric boundaries and
mobile overflow are checked. Browser coverage includes pair→form, website link
pruning, invalid URL and a mismatched hiring/donation pair. Desktop/mobile images
must also be viewed; runtime evidence is recorded in STATE.md.

Next: implement owned typed location/destination components and stage2 requirement
collection. Distinguish user-entered locations from verified platform geographic
IDs. No silent geographic expansion, invented reach, score-derived allocation or
publish readiness may bridge missing account/source data.
