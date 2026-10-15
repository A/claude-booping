---
id: "02"
title: "Closing an open item and the waiting-on-you status"
sp: 3
status: done
plan: "plans/202610152006_project-manager-playbook/index.md"
---

# M02: Closing an open item and the waiting-on-you status

`booping items close` closes an `open` item as `done`, and `booping status` counts and lists the items waiting on the user.

**Scope**: in `playbooks/specs/playbook.yaml`'s `open_item` machine add `open → done` with `when:` "`booping items close` on an open item — a tiny fix, an answered question or a recorded decision closed without a plan" and the same `frontmatter-update closed_at=…` hook as `planned → done`. Make `booping items close ID` on an `open` item take that edge in `booping-python/src/booping/specs/open_items.py` / `commands/items.py` (today it is rejected). Replace `booping-python/e2e/cases/items/close-on-an-open-item-is-rejected.txtar` with `close-on-an-open-item-marks-it-done.txtar`. In `booping-python/src/booping/status.py` compute, through `booping.specs.questions.open_count`, the items in `open` or `planned` with at least one open question; `_items_summary` appends ` — {n} waiting on you` when `n > 0`; `_items_detail` appends the `Waiting on you:` table the I/O contract in `index.md` locks.

Tests (integration tier, e2e corpus, hand-derived): close on an open item → `status: done`, `closed_at` stamped; status short line with one open item holding one open and one answered question → ` — 1 waiting on you`; a `done` item with an open question is not counted; `status items --detail` prints the table with `open questions` 1 and the sidecar path; zero waiting → the line and the detail unchanged (the existing status cases still pass untouched).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `open → done` edge; `items close` takes it; the rejected-case replaced. | `playbooks/specs/playbook.yaml`, `booping-python/src/booping/specs/open_items.py`, `booping-python/src/booping/commands/items.py`, `booping-python/e2e/cases/items/close-on-an-open-item-*.txtar` | 1 | done |
| 2.2 | Waiting-on-you count and table in status. | `booping-python/src/booping/status.py` | 1 | done |
| 2.3 | e2e cases for the status line and detail. | `booping-python/e2e/cases/status/*waiting*.txtar` | 1 | done |

## Definition of Done

### Task 2.1

- [x] `bin/booping render-playbook specs` shows the `open → done` row in the `open_item` state table.
- [x] `close-on-an-open-item-is-rejected.txtar` is gone; its replacement passes.

### Task 2.2

- [x] `status.py` reads questions only through `booping.specs.questions`; no answered-test logic of its own.
- [x] The items line and detail equal the I/O contract.

### Task 2.3

- [x] The status cases above exist and pass; every pre-existing status case passes unchanged.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/items/close-a-planned-item-stamps-closed-at.txtar` — close case shape.
- `booping-python/e2e/cases/status/short-report-counts-items-by-status-and-source.txtar`, `booping-python/e2e/cases/status/items-detail-is-the-items-list-table.txtar` — status case shapes.

## Verify

`cd booping-python && uv run pytest e2e/cases/items e2e/cases/status -q`
