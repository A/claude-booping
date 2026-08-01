---
status: spec-ing
---

# record-decision

[← index](../../index.md)

## Contract

- **Needs** —
  - zero or more user decisions as short summaries, relayed verbatim by the runner
- **Value** — one append-only, timestamped log of every decision made during the run, in one
  place regardless of which step or gate produced it; the raw material a later human pass
  narrows to what stays valuable.
- **Output files** —
  - `[CREATED|UPDATED] <slug>/_specs/DECISIONS.md`:
    - created when missing with the heading `# Decisions` (the wave-1 bootstrap call does
      only this)
    - one appended line per decision: `` `[YYYY-MM-DD HH:MM]` <summary> `` — timestamp taken
      from `date -u +"%Y-%m-%d %H:%M"`, never omitted or invented; summaries verbatim, no
      rewording, merging or filtering; existing lines never edited or deleted
- **Harness return** — `## Changed:` with the one path; `## Notes:` the recorded count or
  the bootstrap note.
- **Review gate** —
  - none — mechanical log; the user narrows the file later

## Example artifact

```markdown
# Decisions

- `[2026-07-31 14:02]` findings stay per-file on disk; only the composed report is gated
- `[2026-07-31 14:02]` state machine: minimal —  single deliverable, one confirm gate
- `[2026-07-31 15:40]` target model opus-5:medium, destination root global _playbooks/
```

## Return Format

```markdown
## Changed:
- [UPDATED] mod-review/_specs/DECISIONS.md

## Notes:
- 2 decision(s) recorded
```
