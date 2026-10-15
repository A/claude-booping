---
type: value
title: A constructor, not a fixed solution
summary: Booping is a constructor — a framework for playbooks with a set of core mechanics — not a ready solution fixed to one task.
kind: value
created_by: owner
created_at: 2026-10-14
updated_at: 2026-10-14
---

Booping is a constructor — a framework for playbooks with a set of core mechanics —
not a ready solution fixed to one task.

## In practice

A project's config extends booping's logic: user playbooks, scripts and templates read their own config keys, and the core mechanics (state machines, hooks, queries, scaffolds, tiers) carry them.

## Trade-off

no schema gate on config: a mistyped key is not caught at load.
