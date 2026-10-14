---
type: rule
title: A lesson is a rule
summary: What a run teaches is recorded as a rule with targets and a brief; only the brief reaches the targeted step, the body is read on demand.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [learn]
brief: "Write every accepted learning as a rule record in the project specs tier (targets, a self-sufficient one-or-two-line brief, Rule and Follows from) or as a repo CLAUDE.md bullet; never as a lesson file."
---

## Rule

A lesson the user takes from a retro or a review is written as a rule: a record
in `specs/rule/` of its tier (project, user or core) with `targets:` — the
playbooks, steps, agents or skills it applies to — and `brief:`, one or two
lines. Only the brief is injected into a targeted step, with a link to the
record. The brief is enough for most of the work on its own: an agent reads the
record only for an edge case or the reason, never for every rule; and the brief
does not restate what the agent checks or knows anyway. `## Follows from`
links a value, or the source the lesson came from (the retro, the review, the
incident) when no value names it.

## Follows from

- [Curated self-learning](../value/0001-curated-self-learning.md) — a lesson becomes a
  rule only when the user takes it, and a rule is where taken knowledge lives.
- [Minimal effective context](../value/0002-minimal-effective-context.md) — a step gets
  the brief, not the whole record.
- [Single source](../value/0003-single-source.md) — one record carries the rule and its
  reason; no second lesson file restates it.
