---
id: "02"
title: "booping config` replaces config-get"
sp: 2
status: done
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M02: booping config` replaces config-get

## Tasks

**Goal**: `booping config <key>` prints what `config-get` printed, with the same exit codes.
**Scope**: `booping-python/src/booping/commands/config_get.py` → `config.py`, `cli.py`, `booping-tracker/src/booping_tracker/config.py` + its tests and README, `playbooks/develop/_scripts/refresh-milestone-table`, `vault/_playbooks/docs/_scripts/commit-docs`, `playbooks/setup/**`, `playbooks/project-manager/work/prompt.md`, `migrations/004_lessons_to_rules/migration.md`, `migrations/005_project_specs_to_vault_root/migration.md`, e2e `cases/config-get/` → `cases/config/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Rename the command and its module; switch booping-tracker's shell-out and every script, prompt and migration caller | `booping-python/src/booping/commands/config.py`, `booping-tracker/src/booping_tracker/config.py`, `migrations/004_lessons_to_rules/migration.md` | 1 | done |
| 2.2 | Move e2e cases to `cases/config/`; update booping-tracker tests | `booping-python/e2e/cases/config/`, `booping-tracker/tests/config_test.py` | 1 | done |

Tests: integration tier — existing cases under the new name; booping-tracker's config test against the renamed call.

## Definition of Done

- [x] Task 2.1: `booping config core.plans.glob` prints `plans/*/index.md`; `booping config-get` is unknown; `grep -rn 'config-get'` outside history returns nothing.
- [x] Task 2.2: `just e2e -k config` and booping-tracker's pytest pass.

## References

- `booping-python/src/booping/commands/config_get.py` — the behaviour kept.

## Verify

`just e2e -k config`
