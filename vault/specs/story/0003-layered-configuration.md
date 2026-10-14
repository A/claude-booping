---
type: story
title: Layered configuration
summary: Config is a deep merge over the core, global and project levels, and any mapping in it can be a query spec or a scaffold tree.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want to override any config key at the global or project
level, so that booping fits my machine and my codebase without touching the plugin.

## Criteria

- Any key can be overridden in `~/.config/booping/config.yaml` or the Project Vault's
  `config.yaml`, later levels winning.
- Query specs declared at any config path run with `booping query --config` or the
  `| query` filter; scaffold trees materialise with `booping scaffold`, skipping an
  existing target unless `--force`.
- `booping scaffold` and `booping frontmatter-update` print every write as a unified
  diff, silent when a file is unchanged.
- Argv macros under `core.macros` carry a `command:` and a `cwd: repo|vault`, and can be
  stubbed for reproducible renders.
- `booping config-get` reads any merged value and `booping marker-set` sets marker
  keys; `core.plans.glob` and `core.research_agent` are ordinary overridable keys.
