The confirmed brief:

```markdown
---
reviewed_at: 20260730 09:00
---

# mod-review — Brief

## Goal

Review a module file by file: findings collected per changed file, then composed into one
review report the user signs off.

## Success result

A run ends with `_review/review.md` confirmed by the user, every finding grounded in the
module's files with a fix sketch.

## Artifact home

`_review/`

## Wishes

- findings stay per-file on disk
- only the composed report is gated
```

The procedure, as the user described it: "Point the playbook at a module. For every changed
file, collect findings — defects, risks, fix sketches. Then compose the findings into one
review report I sign off. Findings stay on disk per file; I only want to gate the final
report."
