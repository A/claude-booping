---
type: story
title: Develop
summary: Develop executes a groomed plan one milestone group at a time through a worker agent and closes it at done or fail.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want a groomed plan executed one milestone group at a time by a worker
agent, so that the plan is carried to the end while the runner checks every milestone.

## Criteria

- Resolves the plan from the invocation, or offers a table of plans ready for
  development.
- Hands the configured worker one briefing per SP group of milestones, the milestone files by path as the whole work contract ([adr/0022](../adr/0022-group-milestones-by-sp.md)); the runner never writes application code.
- The worker runs its milestone's Verify and leaves the work uncommitted; the runner
  validates it against the DoD and makes the repo commit.
- Works one milestone group at a time on the sprint branch, never two workers at once.
- Verifies the definition of done and the project guardrails, closes the plan at `done`
  or `fail`, and hands off to `/playbook retro`.
