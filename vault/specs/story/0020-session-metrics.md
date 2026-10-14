---
type: story
title: Session metrics
summary: A plan carries measured active minutes, tokens and models computed from Claude Code session logs.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **a user**, I want each plan's real effort measured from the session logs, so that I
can see what a sprint cost in time, tokens and models.

## Criteria

- `booping session-stats` computes a plan's active work minutes, discounting time spent
  waiting on a human.
- Each session's tokens (input, output, cache-creation, cache-read) are accounted beside
  the model ids that ran the work.
- The totals are stamped as `metrics_*` plan frontmatter on groom and develop
  transitions.
- Active minutes and models show as `sprints.md` and query columns.
