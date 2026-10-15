---
id: "03"
title: "Source column and collision-safe ids"
sp: 3
status: pending
plan: "plans/202610151825_user-request-items/index.md"
---

# M03: Source column and collision-safe ids

`booping items list` shows each item's source, and two `items add` calls racing for the same id never write one file twice — the loser takes the next id.

**Scope**:

- `src/config.yaml` `core.specs.open_items.index.columns` becomes `[id, status, source, direction, record, title, plan]`; the e2e `list` cases' expected tables follow.
- `booping-python/src/booping/specs/open_items.py`: item creation allocates its id by creating the file exclusively (`open(path, "x")` / `O_CREAT|O_EXCL`); on `FileExistsError` it takes the next id and retries, at most 100 times, then fails with `error: could not allocate an item id under {dir}` (exit 1). The directory listing that picks the starting id is injectable (a parameter defaulting to the real glob), so a test can hand it a stale answer. If `write_item` goes through `booping scaffold`'s writer, the exclusive create replaces only the final file write; the scaffold stays the sole definition of the content.

Tests:
- Integration tier, e2e: the moved `list-shows-open-and-planned-items.txtar`, `list-all-adds-closed-items.txtar` and `list-on-an-empty-vault-prints-no-open-items.txtar` expect the `source` column (expected tables hand-edited).
- Unit tier, `booping-python/tests/specs/open_items_test.py` (new): a vault holding `OI-0001.md` and `OI-0002.md` while the injected listing reports only `OI-0001` → the new item is `OI-0003.md`, and `OI-0002.md` is byte-identical afterwards. No mocks — a real temp directory and a plain function as the stale listing.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `source` index column and the three list cases. | `src/config.yaml`, `booping-python/e2e/cases/items/list-*.txtar` | 1 | pending |
| 3.2 | Exclusive-create id allocation with the injectable listing and its unit test. | `booping-python/src/booping/specs/open_items.py`, `booping-python/tests/specs/open_items_test.py` | 2 | pending |

## Definition of Done

### Task 3.1

- [ ] `bin/booping items list` prints a table whose header is `| id | status | source | direction | record | title | plan |`.

### Task 3.2

- [ ] The unit test in Tests passes; a pre-existing item file is never overwritten.
- [ ] The retry bound and its error message are as in Scope.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/tests/specs/tiers_test.py` — unit test shape with real temp directories.
- `booping-python/e2e/cases/items/list-shows-open-and-planned-items.txtar` (after M01) — the case to extend.

## Verify

`cd booping-python && uv run pytest tests/specs/open_items_test.py e2e/cases/items -q`
