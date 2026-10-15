---
id: "05"
title: "Item sizes and batches \u2014 booping items size and items batch"
sp: 4
status: pending
plan: "plans/202610152053_project-manager-autonomous-extras/index.md"
---

# M05: Item sizes and batches — booping items size and items batch

An item carries a size the manager judged, and `booping items batch` packs the small open items into batches that skip grooming.

**Scope**: `src/config.yaml` — the item scaffold (`core.specs.open_items.scaffold`) gains `size: null` after `source`; the index `columns` gain `size` after `source`; `core.project_manager_playbook` gains `batch:` with `sizes: {XS: 1, S: 2, M: 5, L: 13}`, `direct: [XS, S]` and `max_sp: 8`, commented. `booping-python/src/booping/commands/items.py` (+ `booping-python/src/booping/specs/open_items.py` for the reads and writes) — `booping items size ID SIZE` writes `size:` on an `open` or `planned` item, `SIZE` one of the `sizes` keys; `booping items batch` takes the `open` items whose `size` is in `direct` and that wait on no question (the answered test `booping items ask|answer` already runs), in id order, and packs them greedily: the current batch takes the next item while its summed SP stays ≤ `max_sp`, else a new batch starts. An item file written before this change has no `size:` key and reads as null — no migration. Output lines locked in `index.md`'s I/O contract.

Tests (integration tier, `booping-python/e2e/cases/items/`, hand-derived): `size` writes the key and prints its line; an unknown size → exit 1 naming the allowed ones; `size` on a `done` item → exit 1; `batch` over OI-0001 XS, OI-0002 S, OI-0003 M, OI-0004 S, OI-0005 S (with an open question), OI-0006 S, OI-0007 XS, OI-0008 unsized, cap 8 → `B1 (7 SP): OI-0001 OI-0002 OI-0004 OI-0006` and `B2 (1 SP): OI-0007`; no direct-size item → the `no batch` line, exit 0. Existing `items list` cases gain the `size` column — rebaseline them with `just e2e -k items --txtar-update` and check every changed hunk is only that column.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Scaffold field, index column, `batch` config. | `src/config.yaml` | 1 | pending |
| 5.2 | `items size` and `items batch`. | `booping-python/src/booping/commands/items.py`, `booping-python/src/booping/specs/open_items.py` | 2 | pending |
| 5.3 | The five new cases; rebaselined `items list` cases. | `booping-python/e2e/cases/items/size-*.txtar`, `booping-python/e2e/cases/items/batch-*.txtar` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] `bin/booping config-get core.project_manager_playbook.batch` prints the three keys.

### Task 5.2

- [ ] `bin/booping items --help` lists `size` and `batch`; each verb's `--help` matches the contract.
- [ ] Batch packing is a pure function of (items in id order with sizes, sizes map, direct list, cap).

### Task 5.3

- [ ] The five cases pass; the rebaselined cases differ from before only by the `size` column.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/items/add-request-with-a-title-and-argv-text.txtar` — an items case.
- `booping-python/e2e/cases/status/items-detail-lists-items-waiting-on-you.txtar` — an item with an open question in its sidecar.
- `/home/anton/Dev/@A/notes/projects/_playbooks/backlog-run/_scripts/picking.py` lines 155–198 — the packing this ports; its repo and deliver keys are not ported.

## Verify

`cd booping-python && uv run pytest e2e/cases/items -q`
