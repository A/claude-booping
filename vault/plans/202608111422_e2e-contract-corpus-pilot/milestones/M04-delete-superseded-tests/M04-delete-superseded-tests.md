---
id: "04"
title: "Delete superseded tests, wire docs"
sp: 2
status: pending
plan: "plans/202608111422_e2e-contract-corpus-pilot/index.md"
---

# M04: Delete superseded tests, wire docs

**Goal**: the corpus is the only verifier of scaffold behavior — superseded test files gone, stale references cleaned, repo guide updated.

**Scope**: deletions under `booping-python/tests/`, `CLAUDE.md`. Depends on M03's coverage cross-check being accepted.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Delete `tests/commands/scaffold_test.py` and `tests/context/scaffold_test.py`; sweep for stale references with: `grep -rn "context.scaffold" booping-python/tests/`, `grep -rn "scaffold_test" booping-python/ CLAUDE.md docs/ documentation/`, and for each fixture dir the deleted files referenced via `get_fixture_path` — `grep -rn "{fixture-name}" booping-python/tests/` — delete the dir when no other test names it. | `booping-python/tests/commands/scaffold_test.py`, `booping-python/tests/context/scaffold_test.py`, `booping-python/tests/__fixtures__/*` (orphans only) | 1 | pending |
| 4.2 | Update `CLAUDE.md`: Commands section gains `just e2e` (+ `just ci` chain note), Layout's `booping-python/` bullet gains `e2e/` (corpus + runner, format spec at `e2e/README.md`). | `CLAUDE.md` | 1 | pending |

## Definition of Done

### Task 4.1

- [ ] Both files deleted; no orphaned fixture dirs remain under `tests/__fixtures__/`.
- [ ] `grep -r "context.scaffold" booping-python/tests/` and `grep -rn "scaffold_test" booping-python/ CLAUDE.md docs/ documentation/` return nothing.
- [ ] No other test file lost a shared helper it imported.

### Task 4.2

- [ ] Commands and Layout sections updated; wording matches the surrounding style, one line each.
- [ ] No other CLAUDE.md section still implies scaffold has pytest coverage.

## Verify

```
ls booping-python/tests/commands/scaffold_test.py booping-python/tests/context/scaffold_test.py 2>&1  # both missing
grep -r "context.scaffold" booping-python/tests/ || echo clean
just e2e scaffold
```
