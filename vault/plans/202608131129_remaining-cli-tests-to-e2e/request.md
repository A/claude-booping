---
title: "Migrate the remaining CLI command tests to the txtar e2e corpus"
---

# Request

> can you groom what left to migrate to e2e?

# Task type

`refactoring` — test-suite restructuring with no user-visible behaviour change; the CLI's observable contract is what the corpus pins, and it stays identical before and after. Not `feature`: no new capability reaches a user, and no new CLI surface is added. Not `bug`: nothing diverges from expected behaviour today; the units pass, they simply live at the wrong tier.

# Problem

Five commands already have txtar contract cases (`scaffold`, `frontmatter-update`, `config-get`, `marker-set`, `query`) and their CLI-shaped units were deleted. The remaining CLI surfaces — `render`, `render-playbook`, `playbook-state`, `playbook-transition`, `session-stats`, `build`, `debug-context`, `debug-template` — are still covered only by Python unit tests that drive internals rather than the `bin/booping` boundary (`tests/commands/` ~1.4k lines, `tests/test_render_playbook.py` 1.8k lines, `tests/test_session_stats.py` 372 lines). What must change: every remaining CLI-boundary assertion moves into `e2e/cases/<command>/`, and the unit files shrink to the pure-logic coverage that genuinely belongs at the unit tier (context assembly, YAML handling, playbook graph resolution, template rendering).

# Clarifications and Decisions

- Scope is `render-playbook` and `playbook-transition` only; the other unmigrated commands (`playbook-state`, `session-stats`, `render`, `build`, `debug-*`) stay for later runs.
- `tests/context/**`, `tests/templates/**`, `tests/scripts/**` are out of scope — not CLI-boundary tests.
- Goal after landing: no CLI-boundary behaviour of these two commands is pinned by a Python unit test; the txtar corpus is the single contract surface, units keep only pure-logic coverage.
- Deletion rule follows the prior migrations: unit coverage moves case-by-case, the unit file is deleted after a cross-check that every assertion has a corpus home.
