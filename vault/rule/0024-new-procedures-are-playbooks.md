---
type: rule
title: A new procedure is a playbook, not a skill
summary: Anything procedural is added as a playbook driven by /playbook; a new skill is added only for a surface /playbook cannot drive.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: accepted
sources: [CLAUDE.md]
---

## Rule

A new procedure is written as a playbook that the one shipped skill,
`/playbook`, drives. A new skill is added only for a surface `/playbook` cannot
drive.

## Follows from

- [adr/0002](../adr/0002-procedures-are-playbooks.md) — every procedure ships as a playbook driven by the single `/playbook` skill, carrying run state and loading step bodies one at a time.
- [value/0002](../value/0002-minimal-effective-context.md) — a step gets only what it needs.
- [value/0005](../value/0005-stack-agnostic-core.md) — the core stays stack-agnostic; specifics live in the global and the project tiers.
