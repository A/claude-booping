---
title: "Migrate frontmatter-update tests from units to txtar e2e corpus"
type: "refactoring"
status: in-progress
sp: 8
related_to: null
created: 2026-08-12 14:17
planned: null
started: 2026-08-12 14:37
completed: null
code_reviews: []
sessions:
- 74d0d09f-c620-44da-a2e5-ee30fc87e079
- 07f92faa-63c3-4b72-acac-434a41369dbb
retro: null
summary: frontmatter-update units become txtar e2e cases; stub + real echo macro
  coverage; unit file deleted after cross-check
commit: e0d1796ff568c6b4a0d242069e6102e1a294e00a
reviewed_at: 2026-08-12 14:36
---

# Migrate frontmatter-update tests from units to txtar e2e corpus

## Context

`booping frontmatter-update` is covered by 571 lines of unit tests (`booping-python/tests/commands/frontmatter_update_test.py`) that assert through Python internals — direct calls to `parse_pairs`, `interpolate`, and private YAML helpers — making them fragile against refactors. The e2e pilot (plan 202608111422) established the txtar contract-corpus pattern for `scaffold`, and the runner extraction (plan 202608121206) moved the runner into the published `pytest-txtar` 0.1.0 plugin. This plan ports frontmatter-update's CLI-observable behaviors into txtar cases under `booping-python/e2e/cases/frontmatter-update/` and deletes the unit file wholesale. No user-visible behavior change.

## Decisions

- **Unit fate**: delete `frontmatter_update_test.py` wholesale once the corpus covers every CLI-observable behavior — the corpus is the contract, same call as the scaffold pilot.
- **Hook-tokenising tests**: `TestHookTokenising` exercises `playbook_transition.dispatch_frontmatter_update`, not this CLI; its intent is already covered by `playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`). Dropped, not ported.
- **Macro coverage**: stubbed macros (vault `macro_stubs:` / fixture config) for deterministic interpolation cases, plus one case with a real macro defined in fixture config as a shell command (`echo 1`) — proving live macro execution through the subprocess boundary. Live-git macro coverage consciously abandoned (user call: shell execution guarantee suffices).
- **Gap cases**: add cases the units never had — newline/tab-bearing values through coercion, macro interpolation across the subprocess boundary.
- **Corpus layout**: one kebab-named `.txtar` per behavior, existing `e2e/conftest.py` spec unchanged — no runner or config work in this plan.

## Architecture

Cases live in `booping-python/e2e/cases/frontmatter-update/*.txtar`, discovered by the `pytest-txtar` plugin via the existing `e2e/conftest.py` spec (`roots=(home, xdg, cwd)`, `cwd_root=cwd`, env-mapped `HOME`/`XDG_CONFIG_HOME`). Each case seeds fixture trees, runs one or more `booping frontmatter-update …` lines, and asserts stdout (unified diff), stderr (summary/error lines), exit code, and resulting file bytes under `expected/`. Volatile spans (log timestamps) use `[..]` wildcards. Rebaseline flow: `cd booping-python && uv run pytest e2e --txtar-update -k frontmatter`. Runner: `just e2e`. The one Python-internal consumer of this module (`playbook_transition.py:19` importing `interpolate`/`parse_pairs`) keeps its own coverage in `playbook_transition_test.py` and is untouched.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Core CLI corpus cases — set, coercion, errors, diff, stderr, log](milestones/M01-core-cli-cases/M01-core-cli-cases.md) | 3 | done |
| 02 | [List-op and macro corpus cases — remove, append, stubbed and real macros, gap cases](milestones/M02-list-ops-and-macro-cases/M02-list-ops-and-macro-cases.md) | 3 | done |
| 03 | [Delete superseded unit tests after coverage cross-check](milestones/M03-delete-superseded-units/M03-delete-superseded-units.md) | 2 | done |

## I/O contract

The CLI surface under test — unchanged by this plan, restated as the corpus contract:

- **Arguments**: `booping frontmatter-update <plan> [key=value ...] [--remove key]... [--append key=value]...`
- **stdout**: unified diff (`--- {path}` / `+++ {path}` / `@@`) of the mutated file; empty on no-op.
- **stderr**: `updated {plan}: k=v, -removed, k+=appended` summary on success; error message on failure.
- **Exit codes**: `0` success (including no-op diff), `1` user error (missing plan, malformed pair, nothing to do, append onto scalar), `2` macro/Jinja error or unexpected exception.
- **Side effect**: appends one line to the vault's `.booping.log` when a vault is attached.

## Final Verification

- [ ] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck, e2e).
- [ ] `uv run pytest e2e -k frontmatter` passes with no `--txtar-update` needed on a clean run.
- [ ] `frontmatter_update_test.py` deleted; `grep -rn frontmatter_update_test` returns nothing.
- [ ] Unit-vs-corpus coverage cross-check recorded in the deletion milestone's DoD — every CLI-observable unit behavior maps to a named case.

## Out of scope

- Other commands' test migrations (`marker-set`, `query`, `playbook-*`) — own grooming runs.
- Any change to `pytest-txtar`, the e2e conftest spec, or the case format.
- Any behavior change to `frontmatter-update` itself — bugs found while porting are recorded, not fixed here.
- `playbook_transition`'s reuse of `interpolate`/`parse_pairs` and its tests.

## CLAUDE.md impact

No CLAUDE.md changes required — `just e2e`, the corpus layout, and the rebaseline flow are already documented from the pilot and runner-extraction sprints; this plan only adds cases under the existing structure.
