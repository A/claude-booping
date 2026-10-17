---
id: "08"
title: "booping items` removed; scan is `booping specs scan"
sp: 3
status: done
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M08: booping items` removed; scan is `booping specs scan

## Tasks

**Goal**: `booping items` no longer exists; `booping specs scan` files the same items `items scan` did.
**Scope**: `booping-python/src/booping/commands/items.py` (removed), `commands/specs.py` (scan), `specs/open_items.py` (pruned to what `status.py`, `commands/run.py`, `commands/status.py`, scan and tests import), `cli.py`, e2e `cases/items/`, `tests/specs/open_items_test.py`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Move `_run_scan` into `booping specs scan [--tier]`, writing items through the M06 tree | `booping-python/src/booping/commands/specs.py` | 1 | done |
| 8.2 | Remove `commands/items.py` and its registration; prune `open_items.py` (allocator, `move`, `set_size`, `pack`, `sized_open_items`, bulk close/reopen) | `booping-python/src/booping/commands/items.py`, `booping-python/src/booping/specs/open_items.py`, `booping-python/src/booping/cli.py` | 1 | done |
| 8.3 | e2e: move the scan cases to `cases/specs/` as `specs scan`; delete the other `cases/items/` cases, keeping one `query`-based list case under `cases/query/` | `booping-python/e2e/cases/specs/`, `booping-python/e2e/cases/query/` | 1 | done |

Tests: integration tier — the moved scan cases; status cases still pass.

## Definition of Done

- [x] Task 8.1: `booping specs scan` on the scan fixtures prints what `items scan` printed.
- [x] Task 8.2: `booping items` is unknown; `just typecheck` is clean.
- [x] Task 8.3: no `cases/items/` directory remains; `just e2e` passes.

## References

- `booping-python/src/booping/commands/items.py` — `_run_scan`.
- `booping-python/e2e/cases/items/` — scan case shapes.

## Verify

`just e2e -k "scan or status or query"`
