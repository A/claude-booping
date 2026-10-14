---
type: rule
title: The content of a user-facing output is locked in grooming
summary: When a plan defines a user-facing output or log format, its exact content — fields, truncation, trailers — is settled with the user in grooming, not iterated in develop.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [groom/draft-plan]
brief: "When the plan defines a user-facing output or log format, lock its exact content with the user now — line fields, truncation rules, trailers — not just the format in prose."
sources: [vault/_lessons/0010_lock-output-content-during-grooming.md]
---

## Rule

When a plan defines a user-facing output or a log format, its exact content — the
fields of a line, the truncation rules, the trailers — is agreed with the user
during grooming, not only the format described in prose. This is one case of
[rule/0004](0004-questions-settled-in-grooming.md): an output contract settled in
develop is iterated live instead of decided up front.

## Follows from

- [Plans run to the end](../values/0001-booping.md#plans-run-to-the-end) — develop does not stop to
  settle what grooming should have asked.
- [Lesson 0010](../../_lessons/0010_lock-output-content-during-grooming.md) — the
  source names no retro.
