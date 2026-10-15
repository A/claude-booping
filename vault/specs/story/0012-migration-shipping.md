---
type: story
title: Migration shipping
summary: The plugin ships Project Vault migrations, and every render surface is gated on a vault's applied watermark.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a contributor**, I want to ship a vault migration with the plugin, so that a change
to the vault shape reaches every existing Project Vault.

## Criteria

- A migration is declared at `migrations/NNN_<slug>/migration.md`, its `id`
  frontmatter authoritative.
- Every render surface is gated on the Project Vault's applied watermark until the
  migration lands.
- A migration is authored against the primitives: numeric `--where` ordering, query
  specs over core files (`root: core`), `{{ booping.latest_migration }}` in templates,
  and marker writes via `booping marker-set`.
