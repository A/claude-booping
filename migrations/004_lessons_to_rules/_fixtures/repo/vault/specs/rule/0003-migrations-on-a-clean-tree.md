---
type: rule
title: Migrations run on a clean working tree
summary: A vault migration is applied only after every pending change is committed, so its diff stands alone.
created_by: claude
created_at: 2026-09-02
updated_at: 2026-09-02
status: accepted
sources: [vault/_lessons/0004_commit-the-generated-client.md, vault/_lessons/0001_commit-scope.md]
---

## Rule

Commit every pending change before applying a vault migration, so the migration's
diff stands alone and can be reverted on its own.

## Follows from

- [Lesson 0004](../../_lessons/0004_commit-the-generated-client.md) — the sprint that lost a day.
- [Lesson 0001](../../_lessons/0001_commit-scope.md) — the source names no retro.
