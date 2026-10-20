---
type: rule
title: Project shaping of an agent or skill is a targeted record
summary: A project adjusts a core agent or skill through a targeted rule (agent:<id>, skill:<name>), never through a separate extension file.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: accepted
sources: [CLAUDE.md]
---

## Rule

When a project needs a core agent or skill to behave differently, it writes a
record targeted at it — `agent:<id>` or `skill:<name>` — which is injected into
that agent's or skill's body. It does not add a separate extension file beside the
agent or skill. The record is a rule with `targets:`
([booping:rule/0001](../../specs/rule/0001-lessons-are-rules.md)).

## Follows from

- [Single source](../value/0003-single-source.md) — one record per adjustment, no second
  extension mechanism restating it.
- [Stack-agnostic core](../value/0005-stack-agnostic-core.md) — the core agent stays generic;
  the project tier adds.
