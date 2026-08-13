---
id: "02"
title: "Pytest plugin layer"
sp: 8
status: done
plan: "vault/plans/202608121206_txtar-runner-extraction/index.md"
---

# M02: Pytest plugin layer

Goal: `*.txtar` files are collected and run as native pytest items — pytest is the runner (selection, reporting, exit codes), with a `--txtar-update` rebaseline flag and a conftest hook through which a consumer supplies its `TxtarSpec`.

Scope: `pytest-txtar/` only — `src/pytest_txtar/plugin.py` + `hooks.py` on top of the M01 core, `pyproject.toml` entry point, plugin tests via pytester. Requires M01 complete.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Collection and execution: `pytest_collect_file` collects `*.txtar` into a `TxtarFile`/`TxtarItem`; `runtest` builds the sandbox via the core and raises on mismatch; failure repr renders the core's unified diff (per-stream and per-file sections, as `run.py` reports today); malformed case surfaces as a collection/usage error, not a pass. Register `pytest11` entry point `pytest_txtar = pytest_txtar.plugin` | `pytest-txtar/src/pytest_txtar/plugin.py`, `pytest-txtar/pyproject.toml` | 3 | done |
| 2.2 | Spec wiring and update flow: declare a `pytest_txtar_spec(config) -> TxtarSpec` hookspec via `pytest_addhooks`, resolved once per session from the consumer's conftest, missing implementation = usage error naming the hook; add `--txtar-update` option — on mismatch rewrite the case file via `updated_archive` and report the item as passed-with-rewrite | `pytest-txtar/src/pytest_txtar/hooks.py`, `pytest-txtar/src/pytest_txtar/plugin.py` | 3 | done |
| 2.3 | Plugin behavior tests with `pytester`: passing case passes; mismatching case fails with the diff in the failure output; `-k` selects by case name; `--txtar-update` rewrites the file so the next run passes; missing spec hook errors out with the hook name | `pytest-txtar/tests/test_plugin.py` | 2 | done |

## Definition of Done

### Task 2.1

- [x] A directory of `.txtar` files under pytest's testpaths is collected without any `test_*.py` glue; item ids are the case paths.
- [x] A failing case's output contains the same unified-diff content the M01 `compare` module renders — no bare AssertionError.
- [x] A malformed case (bad section, illegal tree path) reports as an error naming the case file, not a pass or silent skip.
- [x] Entry point registered; `uv run pytest --trace-config` in a scratch project lists `pytest_txtar`.

### Task 2.2

- [x] Hook interface:

  ```
  # hooks.py
  def pytest_txtar_spec(config):
      """Return the TxtarSpec for this test session."""
  ```

- [x] Consumer conftest implementing the hook is the only configuration needed; no ini keys, no env vars.
- [x] Session with collected txtar items and no hook implementation aborts with a usage error that names `pytest_txtar_spec`.
- [x] `--txtar-update` rewrites only mismatching case files, byte-identical rerun passes, and passing cases are left untouched (file mtime/content unchanged).

### Task 2.3

- [x] `uv run pytest tests/test_plugin.py` passes; every behavior in the task description has a pytester test deriving expected values by hand (literal case files in the test body).

## Verify

```
cd pytest-txtar && uv run pytest tests/test_plugin.py && uv run ruff check . && uv run basedpyright
```
