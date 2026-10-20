---
type: story
title: Develop
summary: Develop executes a groomed plan one milestone group at a time through a worker agent and closes it at done or fail.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P0
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want a groomed plan executed one milestone group at a time by a worker
agent, so that the plan is carried to the end while the runner checks every milestone.

## Scenarios

1. The user runs `/playbook develop`, naming a plan or picking one from the table of
   plans ready for development; `intake` checks the plan against the repo's current
   shape.
2. `provision` proposes the sprint branch and waits for the user's confirmation before
   touching git, then settles the milestone groups.
3. For each group the runner briefs the worker with the milestone files by path; the
   worker implements them, runs each milestone's Verify and leaves the work
   uncommitted.
4. The runner validates the working tree against the DoD, commits the milestone, ticks
   its checkboxes and takes its transition.
5. `verify` runs the project's gates and the plan's Final Verification; `wrap-up` closes
   the plan at `done` and hands off to `/playbook retro`.

Resuming: the user invokes develop on a plan already `in-progress`; the run picks up at
the first milestone not `done`.

## Edge cases

- A tree short of the DoD or a red Verify: the runner writes `feedback.md` beside the milestone and briefs a fresh worker with it; after two attempts the run asks the user to approve the abort and the plan ends at `fail`.
- A sprint branch that already exists: it is reused rather than recreated.
- The user corrects the runner mid-sprint: the correction is logged verbatim under `corrections/`.

## Criteria

- Resolves the plan from the invocation, or offers a table of plans ready for
  development.
- Hands the configured worker one briefing per SP group of milestones, the milestone files by path as the whole work contract ([adr/0022](../adr/0022-group-milestones-by-sp.md)); the runner never writes application code.
- The worker runs its milestone's Verify and leaves the work uncommitted; the runner
  validates it against the DoD and makes the repo commit.
- Works one milestone group at a time on the sprint branch, never two workers at once.
- Verifies the definition of done and the project guardrails, closes the plan at `done`
  or `fail`, and hands off to `/playbook retro`.
