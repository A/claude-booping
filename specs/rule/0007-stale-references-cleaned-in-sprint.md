---
type: rule
title: References a plan invalidates are cleaned up in the same sprint
summary: When a plan deletes or renames something others reference, the cleanup is a milestone task of the same sprint with its own DoD, never a follow-up sweep.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [groom/draft-plan]
brief: "When the plan deletes or renames partials, agents, CLAUDE.md lines or doc links, make the cleanup of every stale reference a milestone task with its own DoD in this sprint."
sources: [vault/retrospectives/20260425-migrate-retro-skill-to-template-pipeline.md]
---

## Rule

When a plan's work invalidates references — a deleted partial, a renamed agent, a
status line in `CLAUDE.md`, a broken doc link — cleaning them up is a milestone
task inside the same sprint, with its own DoD. A half-stale working tree at sprint
close is itself the documentation gap; a "sweep it up after" follow-up leaves the
repo inconsistent and gets dropped.

## Follows from

- [Single source](../../vault/specs/value/0003-single-source.md) — a stale reference is a second, wrong copy of
  a fact.
- [Retro: migrate retro skill to the template pipeline](../../vault/retrospectives/20260425-migrate-retro-skill-to-template-pipeline.md)
  — deleting a partial and updating a CLAUDE.md status block as their own
  milestone landed both inside the sprint.
