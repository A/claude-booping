---
id: "03"
title: "Runs section in booping status"
sp: 3
status: done
plan: "plans/202610151936_run-registry/index.md"
---

# M03: Runs section in booping status

`booping status` prints a `runs:` line after `plans:`, and `booping status runs` prints the table of runs not yet acked.

**Scope**: in `booping-python/src/booping/status.py` add a `runs` `Section` between `plans` and `records` in `SECTIONS`, reading records through `booping.runs` only (`effective_status`, the record reader) via one `@cached_property` on `StatusContext`. Records with a non-null `acked_at` are skipped. Summary and detail are exactly the I/O contract's. Update every existing `booping-python/e2e/cases/status/*.txtar` whose expected stdout is the short report or `--detail` to the six-section shape.

Tests (integration tier, e2e `booping-python/e2e/cases/status/`, hand-derived): a vault with one running record whose pid cannot exist (counted `lost`), one finished, one failed and one acked → `runs: 1 finished, 1 failed, 1 lost`; no `runs/` directory → `runs: none`; `status runs` detail table for the same fixture, rows by id, acked row absent.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `runs` section in `status.py`. | `booping-python/src/booping/status.py` | 2 | done |
| 3.2 | New status cases; existing status cases moved to six sections. | `booping-python/e2e/cases/status/*.txtar` | 1 | done |

## Definition of Done

### Task 3.1

- [x] `bin/booping status --help` lists `runs` between `plans` and `records`.
- [x] `status.py` holds no run-status literal; every status comes from `booping.runs`.

### Task 3.2

- [x] All `booping-python/e2e/cases/status/` cases pass, the new ones included.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/status.py` — `_items_summary`/`_items_detail`, `_table`, `StatusContext`.
- `booping-python/e2e/cases/status/short-report-counts-items-by-status-and-source.txtar` — case shape.

## Verify

`cd booping-python && uv run pytest e2e/cases/status -q`
