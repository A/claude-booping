---
type: rule
title: Step bodies are fetched on demand, not pasted into spawn prompts
summary: A step's body is fetched when the step runs rather than pasted into a spawn prompt, so a run's context grows with its graph, not with the sum of its step bodies.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

## Rule

Every step body is fetched on demand by whoever runs the step; it is never pasted
into a spawn prompt. A run's context stays proportional to its graph, not to the
sum of its step bodies.

## Follows from

- [Minimal effective context](../value/0002-minimal-effective-context.md) — detail is read on
  demand, never inlined in case it helps.
