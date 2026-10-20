---
type: story
title: Layered configuration
summary: Config is a deep merge over the core, global and project levels, and any mapping in it can be a query spec or a template tree.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P0
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want to override any config key at the global or project
level, so that booping fits my machine and my codebase without touching the plugin.

## Scenarios

1. The user sets a key in `~/.config/booping/config.yaml`, and it applies to every
   project on the machine.
2. The user sets the same key in the Project Vault's `config.yaml`, and the project's
   value wins for that project.
3. The user reads the merged value back with the CLI to see what a run will use.
4. The user declares a query spec or a template tree at a config path, then runs it
   with `booping query --config` or writes it with `booping create`, each write printed
   as a unified diff.

## Edge cases

- A list is overridden at a later level: it replaces the earlier list wholesale, it is not merged.
- `booping create` meets an existing target: it skips it unless `--force`.
- A write leaves a file unchanged: nothing is printed.
- A render needs to be reproducible: the macros are stubbed instead of run.

## Criteria

- Any key can be overridden in `~/.config/booping/config.yaml` or the Project Vault's
  `config.yaml`, later levels winning.
- Query specs declared at any config path run with `booping query --config` or the
  `| query` filter; template trees are written with `booping create`, skipping an
  existing target unless `--force`.
- `booping create` and `booping frontmatter-update` print every write as a unified
  diff, silent when a file is unchanged.
- Argv macros under `core.macros` carry a `command:` and a `cwd: repo|vault`, and can be
  stubbed for reproducible renders.
- `booping config-get` reads any merged value and `booping marker-set` sets marker
  keys; `core.plans.glob` and `core.research_agent` are ordinary overridable keys.
