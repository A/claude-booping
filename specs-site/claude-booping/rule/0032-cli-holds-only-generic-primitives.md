---
type: rule
title: The booping CLI holds only generic primitives
summary: A booping CLI command is a primitive any playbook can use; behaviour of one playbook's domain is that playbook's script, run through its hooks.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: accepted
---

## Rule

A command in the booping CLI is a generic primitive any playbook could use — render, query, create, set, transition, state, config. Behaviour that belongs to one playbook's domain, such as cutting a groom draft into milestone files, is a script in that playbook's `_scripts/` (or the shared `playbooks/_scripts/` when several core playbooks use it) and runs through the playbook's hooks, the same mechanism a user's own playbook gets (owner, 2026-10-18).

## Follows from

- [A framework for playbooks](../value/0006-a-constructor-not-a-fixed-solution.md) — the CLI is the framework's primitive set, not a home for one procedure.
- [A core set for development and self-learning](../value/0018-a-core-set-for-development-and-self-learning.md) — a core playbook uses only mechanics a user playbook gets too.
