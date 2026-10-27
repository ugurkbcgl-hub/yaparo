# Yaparo unified journey prototype

Local-only UX draft; see `../../docs/product/unified-journey-draft.md` for scope.
No Django/database/provider integration, storage, download or publishing.
All sample cards and helper replies are local deterministic examples.

Run with the existing Python environment:

```text
python experiments/unified-journey/serve.py --port 8013
```

Open `http://127.0.0.1:8013/`. Use fictional requests and synthetic PNG/JPEG files
only. Data stays in open-tab memory and disappears on refresh. No registration,
keys, dependency installation or paid infrastructure is needed.

With the repository's existing Playwright development environment:

```text
python experiments/unified-journey/check.py
```

The focused check starts its own ephemeral loopback server/browser, checks flow
continuity,1..800km point-radius/invalid/stale-summary handling and safety boundaries, saves screenshots to a printed private temp
directory, and closes its test processes. It never loads the application DB.
These checks are explicit/manual for this isolated draft; existing CI does not
discover this experiment automatically.

Turkey clipping and channel scenarios use tracked offline data/bundle; no CDN,
map/GPS/geocoder or forecast API. Data/dependency provenance and update procedure:
`third-party/README.md`. `../../docs/product/turkey-channel-catalog-draft.md`
records the14 channel candidates, actual/unknown capability distinctions and
hypothetical formulas. None is a connected production channel.

Current mixer: checked channels above with percentages; unchecked compact catalog
below without visible bars. All14 can be added manually as hypothetical scenarios;
unknown geo is flagged and never becomes production permission. The AI suggestion
button is an explicit LOCAL SIMULATION: fresh form context each press, fixed
rules, no model/platform/price request. Real fresh-query integration is still
pending. Wide view preserves values and returns invalid hidden campaign fields
for validation. Run check.py for8 current focused prototype tests.
