---
type: rule
title: Vault artefacts are plain markdown with YAML frontmatter
summary: Every artefact a run writes into the project vault is plain markdown with YAML frontmatter, readable in Obsidian.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [vault/docs/_specs/features.md]
---

## Rule

Every project-vault artefact is plain markdown with YAML frontmatter — no other
format and no database — so the vault opens as is in Obsidian.

## Follows from

- [Everything in one place](../value/0011-everything-in-one-place.md) — everything is plain
  files, easy to look at from one place.
- [Analysable history](../value/0004-analysable-history.md) — a stable plain shape stays
  comparable across projects.
