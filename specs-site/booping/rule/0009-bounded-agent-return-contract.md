---
type: rule
title: An agent briefing bounds what the agent returns
summary: Every agent briefing states the exact shape of the agent's reply, limited to what the orchestrator needs; groom bounds it in the task so develop's briefings inherit it.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [groom/draft-plan]
brief: "When folding DoD and Verify into tasks, state the exact return shape the worker replies with — only what the orchestrator needs (e.g. the list of changed files)."
---

## Rule

Every agent briefing states the exact shape the agent returns, limited to what the
orchestrator needs — for example "the final reply contains only the list of changed
files". Groom bounds the shape while folding DoD and Verify into the tasks, so
develop's briefings inherit it. An unbounded contract lets the agent return surplus
prose into the orchestrator's context.

## Follows from

- [Minimal effective context](../../vault/value/0002-minimal-effective-context.md) — the orchestrator's
  context holds only what it acts on. In the retro on CLI logging and agent namespacing,
  mid-sprint the user had to tell the agent to return only the changed files.
