---
type: rule
title: Code review covers code files only
summary: A code review surfaces findings on code files only; documentation, plans and other prose in the diff pass unreviewed.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
---

## Rule

A code review is scoped to code files. Documentation, plans and other prose in the
diff are out of scope and get no findings — a diff touching `src/` modules, a
plan's `index.md` and a README gets findings on the `src/` files only. The reason
is not named in the source; it is the owner's preference.

## Follows from

- `_lessons/0015_review-only-code-files.md` (removed by [migration 004](https://github.com/A/claude-booping/blob/master/migrations/004_lessons_to_rules/migration.md)) — the source names no
  retro.
