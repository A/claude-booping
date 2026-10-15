---
id: "04"
title: "Paused runs in booping status with next milestone and resume command"
sp: 3
status: pending
plan: "plans/202610152053_project-manager-autonomous-extras/index.md"
---

# M04: Paused runs in booping status with next milestone and resume command

`booping status` shows each paused run that nothing has resumed yet, with its next milestone and the command that resumes it.

**Scope**: `booping-python/src/booping/status.py` — only develop runs pause (develop-loop is the only step that calls the gate inside a run; a refused launch writes no record), so a paused run always has a `plan`; it counts as **resumed** when a later run record (by id) of any playbook names the same `plan`; resumed runs leave the summary count and the detail like acked ones. `booping status runs --detail`, after the existing table, when any unresumed paused run exists: a blank line, `Paused:`, a blank line and `| id | plan | items | next milestone | reason | resume after | resume |`, rows by id, `resume` the backticked `booping run develop {plan} --autonomous`. The summary line needs nothing new: `paused` is in `runs.STATUSES` after M03 and is counted with them.

Tests (integration tier, `booping-python/e2e/cases/status/`, hand-derived): short report counts a paused run; detail lists it in the `Paused:` table with the resume command; a paused run followed by a later develop record on the same plan → absent from both.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Resumed computation and the `Paused:` table. | `booping-python/src/booping/status.py` | 2 | pending |
| 4.2 | The three e2e cases above. | `booping-python/e2e/cases/status/*paused*.txtar` | 1 | pending |

## Definition of Done

### Task 4.1

- [ ] No paused run → the detail output is byte-identical to today's; every existing `status` case passes unchanged.

### Task 4.2

- [ ] The three cases exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/status/runs-detail-lists-unacked-runs-by-id.txtar`, `booping-python/e2e/cases/status/items-detail-lists-items-waiting-on-you.txtar` — a detail table and a trailing sub-table.

## Verify

`cd booping-python && uv run pytest e2e/cases/status -q`
