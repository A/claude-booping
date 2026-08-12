---
id: "02"
title: "Standalone corpus runner"
sp: 6
status: done
plan: "plans/202608111422_e2e-contract-corpus-pilot/index.md"
---

# M02: Standalone corpus runner

**Goal**: `uv run python e2e/run.py` discovers, sandboxes and executes txtar cases against `bin/booping` and reports pass/fail per the I/O contract in `index.md`.

**Scope**: `booping-python/e2e/run.py` (new), one smoke case, `justfile`, `.github/workflows/ci.yml`. Depends on M01's `_txtar.py` and format spec. Callers affected: `just ci` gains a step.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Discovery + sandbox + exec: collect `e2e/cases/**/*.txtar` filtered by positional patterns (substring on the path relative to `cases/`); per case build a tmp sandbox `{home/, xdg/, cwd/}`, materialize `fixtures/**` into it, run each `cmd` line via `subprocess` with `HOME`/`XDG_CONFIG_HOME` pointed into the sandbox, cwd = `cwd/`, the leading word `booping` resolved to the repo-absolute `bin/booping`; capture stdout, stderr, exit code per line. Add one hand-written smoke case: `fixtures/xdg/booping/config.yaml` defines a tree at `core.e2e_smoke.tree` with one dir and one file whose body uses a `--set` global; `cmd` scaffolds it into `out/`; case asserts the diff receipt (`created dir`, one `/dev/null` hunk, summary line `scaffolded 2 paths — 1 dirs created, 1 files created, 0 files overwritten`), exit 0, and the file's content via `expected/cwd/out/...`. | `booping-python/e2e/run.py`, `booping-python/e2e/cases/scaffold/smoke.txtar` | 2 | done |
| 2.2 | Compare + report: normalize actual output (`{CWD}`/`{HOME}`/`{XDG}` token substitution, then `[..]` wildcard), enforce multi-line `cmd` semantics (non-final lines must exit 0), compare `stdout`/`stderr`/`exit`/`expected/**` sections (absent = not asserted), print `PASS`/`FAIL` lines with labeled unified diffs and the `{N} passed, {M} failed` summary, exit 0/1/2 per the I/O contract. `[..]` semantics: line-by-line compare; an expected line containing `[..]` is matched as a full-line regex built from `re.escape`d literal segments joined by `.*?` (non-greedy, may match empty, several `[..]` per line allowed); lines without `[..]` compare by string equality, so literal `[..]` in actual output can never satisfy a non-wildcard expectation. Malformed case (parse error, missing `cmd`, unknown section, no pattern match) → stderr message + exit 2. | `booping-python/e2e/run.py` | 2 | done |
| 2.3 | `--update`: rewrite the selected cases' `stdout`/`stderr`/`exit`/`expected/**` sections in place from the actual normalized run via M01's `serialize`, leaving `cmd`/`fixtures/**` and the leading comment untouched; print `updated {case}` per rewritten file; running it twice produces no second diff. | `booping-python/e2e/run.py` | 1 | done |
| 2.4 | Wiring: `just e2e` recipe (`cd booping-python && uv run python e2e/run.py`), append `e2e` to the `just ci` chain, add the step to the CI python job. | `justfile`, `.github/workflows/ci.yml` | 1 | done |

## Definition of Done

### Task 2.1

- [x] Smoke case passes end-to-end through a real `bin/booping` subprocess; no `booping` import appears anywhere in `run.py`.
- [x] Sandbox is fresh per case and removed afterwards; the host `$HOME` is never read or written.
- [x] A pattern selecting zero cases exits 2 with a stderr message naming the pattern.

### Task 2.2

- [x] Failure output matches the I/O contract: labeled diff per mismatched stream/file, summary line, exit 1.
- [x] `[..]` matches any span within its line; a literal `[..]` in actual output cannot false-positive an assert of different surrounding text.
- [x] Exit-code semantics: 0 all pass, 1 any fail, 2 malformed/no-match — no other codes.

### Task 2.3

- [x] `--update` on an already-green corpus is a byte-level no-op (verified via `git diff --exit-code`).
- [x] Updated sections are written in normalized form (tokens, not sandbox paths).

### Task 2.4

- [x] `just e2e` green locally; `just ci` runs it after `mdcheck`; CI workflow step added.
- [x] `run.py` passes `ruff` and `basedpyright` under the project config.

## Verify

```
just e2e                                # smoke passes
just e2e nosuchpattern; echo $?         # → 2
# break smoke.txtar's expected stdout, run, confirm labeled diff + exit 1, restore
cd booping-python && uv run python e2e/run.py --update && git diff --exit-code e2e/
```
