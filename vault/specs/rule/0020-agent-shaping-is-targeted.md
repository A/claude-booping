---
type: rule
title: Project shaping of an agent or skill is a targeted record
summary: A project adjusts a core agent or skill through a targeted lesson or rule (agent:<id>, skill:<name>), never through a separate extension file.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [CLAUDE.md]
---

## Rule

When a project needs a core agent or skill to behave differently, it writes a
record targeted at it — `agent:<id>` or `skill:<name>` — which is injected into
that agent's or skill's body. It does not add a separate extension file beside the
agent or skill. Today the record is a targeted lesson; with
[rule/0001](0001-lessons-are-rules.md) it becomes a rule with `targets:`.

## Follows from

- [Single source](../values/0001-booping.md#single-source) — one record per adjustment, no second
  extension mechanism restating it.
- [Stack-agnostic core](../values/0001-booping.md#stack-agnostic-core) — the core agent stays generic;
  the project tier adds.
