---
id: "03"
title: "Booping e2e rewire onto pytest-txtar"
sp: 5
status: done
plan: "vault/plans/202608121206_txtar-runner-extraction/index.md"
---

# M03: Booping e2e rewire onto pytest-txtar

Goal: booping's e2e corpus runs through the pytest-txtar plugin — old runner deleted, all 38 cases green, `just e2e [pattern]` interface preserved — and the generic case-format spec lives in the package.

Scope: `booping-python/` (pyproject, e2e/), `justfile`, `CLAUDE.md`, `pytest-txtar/README.md` (spec moves in). Requires M02 complete. Cases in `booping-python/e2e/cases/` are not edited.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Wire the dependency and spec: add `pytest-txtar` to booping-python dev group with `[tool.uv.sources] pytest-txtar = { path = "../pytest-txtar", editable = true }`; write `e2e/conftest.py` implementing `pytest_txtar_spec` with booping's constants — `commands` mapping `booping` to the repo's `bin/booping`, roots `home`/`xdg`/`cwd`, env `HOME`→home + `XDG_CONFIG_HOME`→xdg, cwd root `cwd` | `booping-python/pyproject.toml`, `booping-python/e2e/conftest.py` | 2 | done |
| 3.2 | Delete the old runner and rewire entry points: remove `e2e/run.py` + `e2e/_txtar.py`; justfile `e2e` recipe becomes `cd booping-python && uv run pytest e2e` with `*patterns` mapped to `-k`; move the generic case-format spec from `e2e/README.md` into `pytest-txtar/README.md` (genericized: no booping paths, command-word substitution described via the `commands` mapping), leaving `e2e/README.md` as booping-specific notes (conftest spec, rebaseline command) plus a pointer to the package | `booping-python/e2e/run.py`, `booping-python/e2e/_txtar.py`, `justfile`, `booping-python/e2e/README.md`, `pytest-txtar/README.md` | 2 | done |
| 3.3 | Update repo docs: CLAUDE.md Commands bullet for `just e2e` (pytest runner, rebaseline via `uv run pytest e2e --txtar-update`) and Layout bullet for `booping-python/` (spec now in the package) | `CLAUDE.md` | 1 | done |

## Definition of Done

### Task 3.1

- [x] `cd booping-python && uv sync` resolves `pytest-txtar` from the local path source.
- [x] `conftest.py` computes the `booping` binary path from its own location (`Path(__file__).resolve()` up to the repo root), never from the process CWD.
- [x] `uv run pytest e2e` collects exactly the 38 `.txtar` cases and all pass, no `test_*.py` glue beyond `conftest.py`.

### Task 3.2

- [x] `e2e/run.py` and `e2e/_txtar.py` deleted; `git grep -l _txtar -- ':!*.lock'` returns nothing.
- [x] `just e2e` runs the corpus; the pattern form selects via `-k` and a single-case pattern (e.g. one case's filename stem) collects strictly fewer than 38 items; `just ci` still chains e2e unchanged.
- [x] `uv run pytest e2e --txtar-update` on the green corpus rewrites nothing (`git status` clean after).
- [x] `pytest-txtar/README.md` carries the full case-format spec with no booping reference. Genericization rules: the "leading `booping` word resolves to `bin/booping`" rule is restated as "a `cmd` word listed in the spec's `commands` mapping resolves to its configured binary path"; the worked example uses a neutral command name (e.g. `mytool`), not `booping`; sandbox roots/tokens are described as spec-supplied, with `home`/`xdg`/`cwd` shown only as an example configuration.
- [x] `e2e/README.md` keeps only booping-specific configuration (the conftest spec values, the rebaseline command) and points at the package spec.

### Task 3.3

- [x] CLAUDE.md `just e2e` bullet and the `booping-python/` layout bullet match the new commands and file set; no remaining mention of `e2e/run.py`.

## Verify

```
just e2e
just e2e {one-case-pattern}   # must collect < 38 items
cd booping-python && uv run pytest e2e --txtar-update && git status --short booping-python/e2e/cases
git grep -n "e2e/run.py" -- ':!vault' || echo clean
```
