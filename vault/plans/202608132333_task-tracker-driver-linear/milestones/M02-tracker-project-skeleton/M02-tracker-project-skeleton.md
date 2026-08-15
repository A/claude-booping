---
id: "02"
title: "booping-tracker project and cli provider"
sp: 3
status: done
plan: "plans/202608132333_task-tracker-driver-linear/index.md"
---

# M02: booping-tracker project and cli provider

`bin/booping-tracker` exists as a second uv project with the full verb surface parsed, config resolved and the `cli` provider answering every verb as a receipt-printing no-op.

**Scope**: new `booping-tracker/` uv project (`pyproject.toml`, `src/booping_tracker/{cli,config,facade,logging}.py`, `providers/cli.py`, `tests/`, `e2e/`), new `bin/booping-tracker` shell wrapper, `justfile`. The Linear provider is M03; hooks are M04. `booping-python` is not modified.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Create the uv project and its entry point: `pyproject.toml` (name `booping-tracker`, `requires-python >=3.12`, dependency `pyyaml`, dev group `pytest`, `pytest-txtar`, `ruff`, `basedpyright`, script `booping-tracker = "booping_tracker.cli:main"`, ruff/basedpyright config copied from `booping-python/pyproject.toml`), and `bin/booping-tracker` exec'ing `uv run --project booping-tracker booping-tracker "$@"` in the shape of `bin/booping`. | `booping-tracker/pyproject.toml`, `bin/booping-tracker` | 1 | done |
| 2.2 | Write the facade and the `cli` provider: `facade.py` declares the seven operations (`states`, `show`, `comment`, `issue_create`, `issue_update`, `relate`, `sync`) as a typed Protocol plus the result dataclasses each returns; `providers/cli.py` implements every one as a no-op returning a receipt whose text ends `cli driver, no-op`. | `booping-tracker/src/booping_tracker/facade.py`, `booping-tracker/src/booping_tracker/providers/cli.py` | 1 | done |
| 2.3 | Write config resolution and the argument parser: `config.py` shells to `bin/booping config-get core.tracker` and parses the YAML, honouring `--config-file PATH` instead and erroring with exit 1 on a missing block, an unknown driver name or an unset `api_key_env` variable when the driver needs it; `cli.py` parses the verbs and flags of the plan's I/O contract, dispatches to the selected provider, prints receipts to stdout in `--output text` or JSON in `--output json`, honours `--dry-run`, and appends one `[tracker {verb}]` line to `{vault}/.booping.log` when a vault resolves. | `booping-tracker/src/booping_tracker/config.py`, `booping-tracker/src/booping_tracker/cli.py`, `booping-tracker/src/booping_tracker/logging.py` | 1 | done |
| 2.4 | Wire the tooling: `just lint`, `just typecheck` and `just pytest` run in both projects; add a `booping-tracker/e2e/conftest.py` with a `TxtarSpec` mapping `booping-tracker` to `bin/booping-tracker` (mirroring `booping-python/e2e/conftest.py`), have `just e2e` run both corpora, and add the corpus cases for the `cli` provider: each verb's receipt and exit 0, `--help`, unknown verb exit 1, unknown driver exit 1, a `--body-file` that does not exist exit 1, and a verb invoked without its required flag (`show` with no `--issue`) exit 1. | `justfile`, `booping-tracker/e2e/conftest.py`, `booping-tracker/e2e/cases/**` | 1 | done |

Tests: the txtar corpus is the contract surface for every verb under the `cli` driver — receipts, exit codes and `--output json` shape — with unit tests only for `config.py`'s resolution branches (config-file vs `config-get`, unknown driver, unset env var), which are pure logic with tricky branching.

## Definition of Done

### Task 2.1

- [x] `bin/booping-tracker --help` prints the verb list and exits 0 from a clean checkout with no manual install step.
- [x] `cd booping-tracker && uv run ruff check .` and `uv run basedpyright` both pass on the new project.

### Task 2.2

- [x] Every one of the seven operations is declared in `facade.py` and implemented in `providers/cli.py`; no operation exists on one side only.
- [x] Each `cli` provider receipt names the verb and its target and ends `cli driver, no-op`.

### Task 2.3

- [x] `bin/booping-tracker comment --issue LIN-1 --body hi` run inside the vault resolves config through `booping config-get`, prints one receipt, exits 0.
- [x] `--config-file` bypasses `booping config-get` entirely — verifiable by running outside any vault.
- [x] `--driver linaer` exits 1 with `error:` on stderr naming the unknown driver; stdout is empty.
- [x] `--output json` prints one JSON object per invocation and nothing else on stdout.
- [x] `--dry-run` prints the intended call and performs no write.
- [x] stdout and stderr never carry the same message.

### Task 2.4

- [x] `just lint`, `just typecheck`, `just pytest` and `just e2e` each cover both projects, and `just ci` still runs the same six phases in order.
- [x] The tracker corpus has at least one case per verb plus the five failure cases, all passing.

## Verify

```
bin/booping-tracker --help
bin/booping-tracker states --team ENG
bin/booping-tracker comment --issue LIN-1 --body hi --output json
bin/booping-tracker --driver linaer states --team ENG; echo "exit=$?"
cd booping-tracker && uv run pytest e2e
```

Expected: help lists every verb; the `cli` provider receipts end `cli driver, no-op` at exit 0; the JSON form is a single object; the unknown driver prints `error:` on stderr at exit 1; the tracker corpus passes.
