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
continuity and safety boundaries, saves screenshots to a printed private temp
directory, and closes its test processes. It never loads the application DB.
These checks are explicit/manual for this isolated draft; existing CI does not
discover this experiment automatically.
