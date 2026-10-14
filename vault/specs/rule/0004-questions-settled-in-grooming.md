---
type: rule
title: Open questions are settled in grooming, not in develop
summary: Grooming hunts for open questions and settles them with the user before ready-for-dev; develop stops only for force majeure.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [groom, develop]
brief: Settle every open question with the user during grooming; in develop, stop only for force majeure, not for what grooming should have asked.
---

## Rule

Grooming looks for what could stop the run — unclear scope, an undecided
choice, a missing access — and settles it with the user in the grooming
session before the plan reaches `ready-for-dev`. Develop carries the plan to
the end on its own and stops only for force majeure: what grooming could not
have known.

## Follows from

- [Plans run to the end](../values/0001-booping.md#plans-run-to-the-end) — a plan runs to the end
  only when its questions are answered before it starts.
- [Effective human review](../values/0001-booping.md#effective-human-review) — the user answers in
  one planning session, not in ad-hoc interruptions.
