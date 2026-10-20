---
type: story
title: Session metrics
summary: A plan carries measured active minutes, tokens and models computed from Claude Code session logs.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P2
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want each plan's real effort measured from the session logs, so that I
can see what a sprint cost in time, tokens and models.

## Scenarios

1. The user grooms and develops a plan; each transition records the session ids that
   worked on it in the plan's frontmatter.
2. Develop closes the plan; `booping session-stats` mines those session logs and the
   plan gets its `metrics_*` keys: active minutes, models and token counts.
3. The user opens `sprints.md` and sees each sprint's cost in its columns, without
   opening the plans.
4. The user runs `booping session-stats` directly to see the same numbers broken down
   per session.

## Edge cases

- Time spent waiting on the user — a question unanswered, a tool call rejected — is not counted as active.
- One API message logged as several lines, one per content block: its tokens are counted once.
- A plan that ends at `fail` is stamped too; no other edge stamps the totals.

## Out of scope

- Sub-agent transcripts: only the main thread is measured.

## Criteria

- `booping session-stats` computes a plan's active work minutes, discounting time spent
  waiting on a human.
- Each session's tokens (input, output, cache-creation, cache-read) are accounted beside
  the model ids that ran the work.
- Groom and develop stamp their session ids on the plan; `stamp-active-time` stamps the totals as `metrics_*` plan frontmatter on develop's `done` and `fail` edges only.
- Active minutes and models show as `sprints.md` and query columns.
