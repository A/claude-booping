---
type: rule
title: A hermetic render repeats byte for byte
summary: With macros stubbed and the config merge pinned to core and project levels, a render is identical on any machine.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [vault/docs/_specs/features.md]
---

## Rule

A hermetic render repeats byte for byte on any machine: macro stubs pin every
config-declared macro, and `--project` pins the config merge to the core and
project levels, so nothing from the machine or the user tier leaks in. A change
that makes a render depend on anything else breaks this rule.

## Follows from

- [Proven to work](../values/0001-booping.md#proven-to-work) — the committed snapshot reports can only
  hold behaviour if the render is reproducible.
