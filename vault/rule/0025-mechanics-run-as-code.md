---
type: rule
title: Whatever can be computed runs as code, not as model reasoning
summary: State transitions, their hooks and config-rendered values execute as code; the model never re-derives them, and a transition's printed mutation report is trusted without re-reading.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: accepted
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

## Rule

Wherever a step can be computed, it runs as code: rendering known playbooks,
skills and agent bodies, injecting rules and config-rendered values, queries,
state transitions and their hooks (frontmatter stamps, named scripts, vault
commits). The model never re-derives them. A transition's printed
mutation report is authoritative, so the runner does not re-read frontmatter to
verify it.

## Follows from

- [Deterministic where it can be](../value/0015-deterministic-where-it-can-be.md) — a
  computed result does not depend on the model that runs the step.
- [Quality at a rational cost](../value/0012-quality-at-a-rational-cost.md) — code does the
  mechanics without spending tokens on them.
- [Proven to work](../value/0010-proven-to-work.md) — code can be tested; a model re-deriving a
  transition cannot be held by a check.
