Target model: `opus:medium`. Destination root: the global `_playbooks/`.

The confirmed decomposition:

```markdown
---
reviewed_at: 20260730 09:00
---

# mod-review — Decomposition

Review a module: findings gathered per changed file, composed into one report the user signs
off.

## Graph

    graph:
      sweep: []
      compose: [sweep]

## Steps

| Step    | Summary                          | Artifact                     | Gate             | Model           | Spec                           |
| ------- | -------------------------------- | ---------------------------- | ---------------- | --------------- | ------------------------------ |
| sweep   | collect findings per file        | `_review/<file>.md` findings | none             | sonnet-5:medium | [spec](steps/sweep/index.md)   |
| compose | compose findings into the report | `_review/review.md` report   | confirm findings | opus-5:medium   | [spec](steps/compose/index.md) |

## Decisions

- `[2026-07-29 12:10]` Findings stay per-file on disk; only the composed report is gated.
```
