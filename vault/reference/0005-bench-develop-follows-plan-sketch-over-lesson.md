---
type: reference
title: Bench finding — develop follows the plan's code sketch over a lesson
summary: In claude-booping-bench, /develop copied the casing of the plan's code sketch instead of a loaded naming lesson in 3 of 3 reps (judgment 0.2).
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: live
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/claude-booping-bench.md
---

## Facts

- 2026-07-09, case `fastify-naming-lesson` in `claude-booping-bench`: `/develop` followed
  the casing in the plan's code sketch over a loaded lesson that named a different
  convention, in 3 of 3 reps; judgment score 0.2.
- Bench runs used booping's native agents only; pi-developer was deregistered from the
  vault config on 2026-07-09.
- The booping version and model under test are not named in the source; the run was then
  the skill-based `/develop`, before the develop playbook.

## How to check

- In a local clone of the bench harness: `uv run booping-bench run --case
  fastify-naming-lesson --reps 3`, then `uv run booping-bench report <run-id>`.
