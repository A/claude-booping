---
id: "01"
title: "Package core — txtar parser and pytest-free runner core"
sp: 8
status: done
plan: "vault/plans/202608121206_txtar-runner-extraction/index.md"
---

# M01: Package core — txtar parser and pytest-free runner core

Goal: a new uv package `pytest-txtar/` at the repo root holds the txtar parser and the full pytest-free runner core (case model, sandbox execution, normalization, comparison, update), parameterized by a spec object with zero booping references.

Scope: new directory `pytest-txtar/` only (src layout, module `pytest_txtar`); source material is `booping-python/e2e/run.py` and `booping-python/e2e/_txtar.py`, which are read but not modified — booping's e2e keeps running on the old runner until M03.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Package skeleton: pyproject (hatchling, name `pytest-txtar`, `requires-python >=3.12`, MIT, dev group pytest/ruff/basedpyright), MIT LICENSE with BSD-3-Clause attribution block for the txtar port (Google LLC copyright + license text), README stub, src layout with empty `pytest_txtar/__init__.py` | `pytest-txtar/pyproject.toml`, `pytest-txtar/LICENSE`, `pytest-txtar/README.md`, `pytest-txtar/src/pytest_txtar/__init__.py` | 2 | done |
| 1.2 | Move the txtar parser: copy `booping-python/e2e/_txtar.py` to `pytest_txtar/txtar.py` unchanged in behavior, add a BSD-3 attribution header naming `golang.org/x/tools/txtar`; test the public parse/serialize surface — parse→serialize roundtrip, comment handling, empty archive, trailing-newline normalization | `pytest-txtar/src/pytest_txtar/txtar.py`, `pytest-txtar/tests/test_txtar.py` | 2 | done |
| 1.3 | Extract the runner core from `run.py`, parameterized by `TxtarSpec`: `case.py` (Case model, `load_case`, tree-path validation), `sandbox.py` (sandbox build, env, `run_case`), `compare.py` (normalizer, wildcard line matching, `Mismatch`, diff rendering), `update.py` (`updated_archive`). No pytest import anywhere in core; no `booping` string, no fixed binary path, no module-constant roots/tokens. Unit-test the pure logic: normalizer token substitution, `[..]` wildcard matching, update-roundtrip idempotence | `pytest-txtar/src/pytest_txtar/case.py`, `pytest-txtar/src/pytest_txtar/sandbox.py`, `pytest-txtar/src/pytest_txtar/compare.py`, `pytest-txtar/src/pytest_txtar/update.py`, `pytest-txtar/tests/test_core.py` | 4 | done |

## Definition of Done

### Task 1.1

- [x] `cd pytest-txtar && uv sync` succeeds; `uv build` produces sdist + wheel.
- [x] LICENSE contains the MIT text and a separate BSD-3-Clause block crediting Google LLC for the txtar format port.
- [x] `uv run ruff check .` and `uv run basedpyright` clean on the skeleton.

### Task 1.2

- [x] `pytest_txtar.txtar` exposes the same parse/serialize behavior as `e2e/_txtar.py` (Archive dataclass, parse, serialize).
- [x] File header carries the BSD-3 attribution naming `golang.org/x/tools/txtar`.
- [x] `uv run pytest tests/test_txtar.py` passes; tests cover roundtrip, comment text, empty archive, missing trailing newline.

### Task 1.3

- [x] Spec object interface (final field names free, shape fixed):

  ```
  @dataclass(frozen=True)
  class TxtarSpec:
      commands: Mapping[str, Path]      # command word -> binary path substitution
      roots: tuple[str, ...]            # sandbox subdirs, first-listed conventions preserved
      cwd_root: str                     # which root the process runs in
      env: Mapping[str, str]            # env var -> root name, resolved against the sandbox
      tokens: Mapping[str, str] | None  # root -> normalization token; default derived from roots
  ```

- [x] `grep -ri booping pytest-txtar/src/` returns nothing.
- [x] Core modules import cleanly without pytest installed (no `import pytest` in `case/sandbox/compare/update/txtar`).
- [x] `run_case(case, spec)` executes a case in a fresh sandbox and returns an outcome object comparable via `compare`; behavior matches `run.py` for the same inputs.
- [x] `uv run pytest tests/test_core.py` passes; parametrized cases cover token substitution, wildcard `[..]` matching (full-segment and infix), and `updated_archive` idempotence on an already-passing case.

## Verify

```
cd pytest-txtar && uv sync && uv run pytest && uv run ruff check . && uv run basedpyright && uv build
grep -ri booping src/ || echo clean
```
