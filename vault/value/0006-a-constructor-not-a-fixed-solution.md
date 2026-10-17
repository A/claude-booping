---
type: value
title: A framework for playbooks
summary: Booping is a framework a user digitises their own processes with — config, templates, primitives, the CLI, playbooks and evals for their steps.
kind: value
created_by: owner
created_at: 2026-10-14
updated_at: 2026-10-17
---

Booping is a framework for playbooks. A user extends it by digitising their own processes — writing user stories, designing an architecture, any procedure — with the tools booping gives: config, templates, primitives, the CLI, playbooks and evals for their steps. (owner, 2026-10-17)

## In practice

A project's config extends booping's logic: user playbooks, scripts and templates read their own config keys, and the core mechanics (state machines, hooks, queries, scaffolds, tiers) carry them.

## Trade-off

no schema gate on config: a mistyped key is not caught at load.
