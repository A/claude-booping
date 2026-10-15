---
type: rule
title: Project specifics stay out of the core
summary: Core skills and playbooks stay stack-agnostic; whatever is specific to a project is written into that project's tier, never into the core or a user-level scope by a run.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: accepted
sources: [CLAUDE.md, playbooks/learn/playbook.md]
---

## Rule

Core skills and playbooks name no stack and no project. A project's specifics —
its conventions, commands, the shaping of an agent for it — live in the project's
own destinations: rule records in the project specs tier and the attached repo's
`CLAUDE.md`, the only two places `learn` writes ([booping:rule/0001](../../specs/rule/0001-lessons-are-rules.md)).
A run never writes a project specific into the core or into a user-level scope such
as `~/.claude/CLAUDE.md`.

## Follows from

- [Stack-agnostic core](../value/0005-stack-agnostic-core.md) — specifics live in the global and
  the project's tiers.
