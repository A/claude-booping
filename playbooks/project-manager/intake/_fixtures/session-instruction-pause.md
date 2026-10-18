# Input — session-instruction-pause

The project is `taskflow`; the current working directory is its vault root. Run date: **2026-10-15**. This run covers the `intake` step only; `work` takes the filed items up later.

This run has no shell, so the `booping` commands were run for you; their outputs:

- `booping query --config core.specs.open_items.index` — no items; `open-items/` holds no item yet, so the first id is `OI-0001`.
- `booping create core.specs.open_items.template open-items --set source=request --set title="…" --set body="…"` — cannot run here; write the file it would create yourself, one per call, ids in filing order: `open-items/OI-NNNN.md` with frontmatter `id: OI-NNNN`, `title: "{title}"`, `status: open`, `direction: null`, `record: null`, `source: request`, `plan: null`, `created_at: 2026-10-15`, `closed_at: null`, `reason: null`, then `# {title}`, a blank line, and the stdin text as the body.

## Dialogue

**Manager:** The nightly load test on the `pi` host is running, two of five scenarios are done.

**User:** Пауза pi на 2 часа, сервер нужен мне под другое.
