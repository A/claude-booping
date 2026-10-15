# Input — two-requests-and-an-aside

The project is `taskflow`; the current working directory is its vault root. Run date: **2026-10-15**. This run covers the `intake` step only; `work` takes the filed items up later.

This run has no shell, so the `booping` commands were run for you; their outputs:

- `booping items list` — no items; `open-items/` holds no item yet, so the first id is `OI-0001`.
- `booping items add --source request --title "…" --text -` — cannot run here; write the file it would create yourself, one per call, ids in filing order: `open-items/OI-NNNN.md` with frontmatter `id: OI-NNNN`, `title: "{title}"`, `status: open`, `direction: null`, `record: null`, `source: request`, `plan: null`, `created_at: 2026-10-15`, `closed_at: null`, `reason: null`, then `# {title}`, a blank line, and the stdin text as the body.

## Dialogue

**User:** Two things for today. First, the CSV export drops the header row when the report is empty, please make it always write the header. Second, add a `--since` flag to `taskflow jobs list` so I can filter jobs by their creation date. Oh, and by the way, the README still says Python 3.9 is the minimum version, it should say 3.12.
