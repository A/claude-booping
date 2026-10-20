---
type: story
title: Migration shipping
summary: The plugin ships Project Vault migrations, and every render surface is gated on a vault's applied watermark.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P1
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a contributor**, I want to ship a vault migration with the plugin, so that a change
to the vault shape reaches every existing Project Vault.

## Scenarios

1. A contributor changes the vault shape and declares a migration at
   `migrations/NNN_<slug>/migration.md`, its `id` frontmatter the authority.
2. The contributor authors it against the shipped primitives: query specs over core
   files, numeric `--where` ordering, the vault's applied watermark in templates, and
   marker writes.
3. A user updates the plugin; every render surface sees the vault's watermark below the
   new migration and gates on it.
4. The migration is applied and the watermark advances, and the render surfaces stop
   gating.

## Edge cases

- With `core.auto_migrate` on, the default, the notice orders the agent to run the migration unattended and resume; with it off, the run stops for the user.

## Criteria

- A migration is declared at `migrations/NNN_<slug>/migration.md`, its `id`
  frontmatter authoritative.
- Every render surface is gated on the Project Vault's applied watermark until the
  migration lands.
- A migration is authored against the primitives: numeric `--where` ordering, query
  specs over core files (`root: core`), `{{ booping.latest_migration }}` in templates,
  and marker writes via `booping marker-set`.
