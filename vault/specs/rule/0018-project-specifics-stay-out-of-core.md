---
type: rule
title: Project specifics stay out of the core
summary: Core skills and playbooks stay stack-agnostic; whatever is specific to a project is written into that project's tier, never into the core or a user-level scope by a run.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [CLAUDE.md, playbooks/learn/playbook.md]
---

## Rule

Core skills and playbooks name no stack and no project. A project's specifics —
its conventions, commands, the shaping of an agent for it — live in the project's
own destinations: today its vault `_lessons/` and the attached repo's
`CLAUDE.md`, the only two places `learn` writes. A run never writes a project
specific into the core or into a user-level scope such as `~/.claude/CLAUDE.md`.
Lessons are moving into project-tier rules ([rule/0001](0001-lessons-are-rules.md)).

## Follows from

- [Stack-agnostic core](../value/0005-stack-agnostic-core.md) — specifics live in the global and
  the project's tiers.
