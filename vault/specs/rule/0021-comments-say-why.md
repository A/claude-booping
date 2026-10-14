---
type: rule
title: Comments say why, never restate the code
summary: A code comment explains a non-obvious reason; a comment that restates what the code does is not written.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [CLAUDE.md]
---

## Rule

Comments are written only for the why of a non-obvious bit. A comment that
restates what the code already says is not written.

## Follows from

- [Single source](../values/0001-booping.md#single-source) — a comment restating code is a second copy
  that drifts from it.
