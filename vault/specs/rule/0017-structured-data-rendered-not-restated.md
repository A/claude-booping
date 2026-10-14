---
type: rule
title: Structured data is rendered from config, never restated in prose
summary: Statuses, queues, agent ids, globs and other structured values live in config or query specs and are rendered into bodies; prose never copies a literal.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [CLAUDE.md, vault/docs/_specs/features.md]
---

## Rule

Structured data — statuses, queues, agent ids, plan and milestone globs, table
columns — lives in `src/config.yaml` (or a tier above it) and in query specs, and
reaches a skill or step body by rendering. Body prose names the source and never
restates the literal value, because a copied literal decays while the schema does
not.

## Follows from

- [Single source](../value/0003-single-source.md) — config is the source; prose never restates it.
