---
id: "07"
title: "Documentation, CLAUDE.md and config reference for budget, window and batches"
sp: 3
status: done
plan: "plans/202610152053_project-manager-autonomous-extras/index.md"
---

# M07: Documentation, CLAUDE.md and config reference for budget, window and batches

The public docs, the config reference and CLAUDE.md describe the budget gate, the time window, paused runs and item batches.

**Scope**: audience — a booping user running an autonomous project; only what they configure, run or read in `booping status`; no internal module names (rule/0008). `documentation/project_manager.md` — a "Budget and time window" section (what the gate checks, when it runs: at an autonomous launch and before each develop milestone group; the `pause` verdict; how a paused run shows in `booping status` and resumes; a generic cron line `booping run develop {plan} --autonomous` as the timer example, C11) and a "Batches" section (sizes, `booping items size`, `booping items batch`, what skips grooming). `documentation/project_config.md` — `core.budget` (all six keys) and `core.project_manager_playbook.batch` (three keys), defaults from `src/config.yaml`, not retyped elsewhere. `documentation/develop.md` — one line: each milestone group passes the budget gate. `CLAUDE.md` — `## Commands`: `budget` (`read`, `gate`) in the subcommand list, `items` gains `size`, `batch`; `## Config`: a `core.budget` bullet (shared key: the run launcher, develop and the manager read it; `run_pct`, `window`, `probe` named); `## Lifecycle` run-records bullet: `paused`, its three keys, resumed computed from a later record on the same plan.

Tests: none — docs; `just docs` builds them.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | User docs pages. | `documentation/project_manager.md`, `documentation/project_config.md`, `documentation/develop.md` | 2 | done |
| 7.2 | CLAUDE.md lines. | `CLAUDE.md` | 1 | done |

## Definition of Done

### Task 7.1

- [x] Every key and verb this plan adds is named on exactly one reference page; other pages link to it.
- [x] No module path, class name or test name in the user pages.
- [x] `just docs` builds with no new warning.

### Task 7.2

- [x] The three CLAUDE.md sections name the new surface; no other section changes.

Return: the list of changed files, nothing else.

## References

- `documentation/project_manager.md` — the page's existing section shape.
- `documentation/project_config.md` — an existing `core.run` entry to mirror.

## Verify

`just docs`
