---
type: rule
title: Python imports are top-level
summary: Python code uses top-level imports only; a function-local import is allowed only when there is no other way.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [agent:booping-developer]
brief: "Python imports are top-level; no lazy function-local imports unless there is genuinely no other way."
sources: [vault/_lessons/0014_code-style-guide.md]
---

## Rule

Python code does not use lazy, function-local imports; imports sit at the top of
the module unless there is genuinely no other way. The reason is not named in the
source; it is the owner's code-style preference.

## Follows from

- [Lesson 0014](../../_lessons/0014_code-style-guide.md) — the source names no retro.
