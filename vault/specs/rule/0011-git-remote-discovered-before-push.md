---
type: rule
title: The git remote is discovered before a push
summary: Before any git push, the remote name is read from git remote -v; origin is never assumed.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [develop]
brief: "Before any git push, run git remote -v and push to the remote it names; never assume origin."
sources: [vault/_lessons/0011_discover_the_git_remote_before_pushing.md]
---

## Rule

Before any `git push`, `git remote -v` is run to find the actual remote name.
`origin` is never assumed: the user's repos often name the remote differently, and
a push to a guessed name fails or goes to the wrong place.

## Follows from

- [Lesson 0011](../../_lessons/0011_discover_the_git_remote_before_pushing.md) — the
  source names no retro; the reason is the user's remote naming.
