---
type: rule
title: A hermetic render repeats byte for byte
summary: With macros stubbed and the config merge pinned to core and project levels, a render is identical on any machine.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

## Rule

A hermetic render repeats byte for byte on any machine: macro stubs pin every
config-declared macro, and `--project` pins the config merge to the core and
project levels, so nothing from the machine or the global level leaks in. A change
that makes a render depend on anything else breaks this rule.

## Follows from

- [Proven to work](../value/0010-proven-to-work.md) — the committed snapshot reports can only
  hold behaviour if the render is reproducible.
