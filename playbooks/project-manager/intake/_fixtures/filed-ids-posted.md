# Input — filed-ids-posted

The project is `taskflow`; the current working directory is its vault root. Run date: **2026-10-15**. This run covers the `intake` step only; `work` takes the filed items up later.

This run has no shell, so the `booping` commands were run for you; their outputs:

- `booping query --config core.specs.open_items.index` — no items; `open-items/` holds no item yet, so the first id is `OI-0001`.
- `booping create core.specs.open_items.template open-items --set source=request --set title="…" --set body="…"` — cannot run here; write the file it would create yourself, one per call, ids in filing order: `open-items/OI-NNNN.md` with frontmatter `id: OI-NNNN`, `title: "{title}"`, `status: open`, `direction: null`, `record: null`, `source: request`, `plan: null`, `created_at: 2026-10-15`, `closed_at: null`, `reason: null`, then `# {title}`, a blank line, and the stdin text as the body. Its stdout is the written path.

## Dialogue

**User:** The nightly cleanup job deletes archives that are still being downloaded, it must skip any archive with an open download. Also rename the `Jobs` tab in the web UI to `Queue`.
