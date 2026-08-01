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

| Step    | Summary                          | Inputs                                                      | Artifact                     | Gate             | Model           | Spec                           |
| ------- | -------------------------------- | ----------------------------------------------------------- | ---------------------------- | ---------------- | --------------- | ------------------------------ |
| sweep   | collect findings per file        | module the user points at; which files changed; one changed file's contents | `_review/<file>.md` findings | none             | sonnet-5:medium | [spec](steps/sweep/index.md)   |
| compose | compose findings into the report | every file's collected findings; the module and its changed-file list | `_review/review.md` report   | confirm findings | opus-5:medium   | [spec](steps/compose/index.md) |

## Decisions

- `[2026-07-29 12:10]` Findings stay per-file on disk; only the composed report is gated.
```

The procedure, as the user described it: "Point the playbook at a module. For every changed
file, collect findings — defects, risks, fix sketches. Then compose the findings into one
review report I sign off. Findings stay on disk per file; I only want to gate the final
report."
