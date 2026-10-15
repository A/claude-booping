---
type: rule
title: Deterministic mechanics run as code, not as model reasoning
summary: State transitions, their hooks and config-rendered values execute as code; the model never re-derives them, and a transition's printed mutation report is trusted without re-reading.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

## Rule

Wherever a mechanic can be deterministic, it runs as code: state transitions,
transition hooks (frontmatter stamps, named scripts, vault commits) and
config-rendered values. The model never re-derives them. A transition's printed
mutation report is authoritative, so the runner does not re-read frontmatter to
verify it.

## Follows from

- [Quality at a rational cost](../value/0012-quality-at-a-rational-cost.md) — code does the
  mechanics without spending tokens on them.
- [Proven to work](../value/0010-proven-to-work.md) — code can be tested; a model re-deriving a
  transition cannot be held by a check.
