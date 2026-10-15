---
id: "03"
title: "Paused runs — launch gate, the gate stamps the run record, the paused status"
sp: 4
status: pending
plan: "plans/202610152053_project-manager-autonomous-extras/index.md"
---

# M03: Paused runs — launch gate, the gate stamps the run record, the paused status

A registered run that meets a closed gate ends as `paused`, with its reason, its resume time and its plan's next milestone on the run record; an autonomous launch is refused up front when the gate is already closed.

**Scope**: `booping-python/src/booping/commands/run.py` — the child's environment gains `BOOPING_RUN_ID={run id}`; a launch with `--autonomous` runs M02's verdict first (gated by definition — the launch is a registered run) and on `pause` prints the verdict lines, writes no record and exits 3; with `core.budget.run_pct` set, the record gets `usage_baseline_7d` (the 7-day percent of the reading the launch gate used). `booping-python/src/booping/runs.py` — `STATUSES` gains `paused`; `finish()` records `paused` when the child exits 0 and the record carries `paused_reason`, else as today; `ack` accepts `paused`. `booping-python/src/booping/budget.py` / `commands/budget.py` — `gate` inside a registered run (`BOOPING_RUN_ID` set) that returns `pause` stamps that run's record with `paused_reason` (the verdict line without its `pause — ` prefix), `resume_after` (or null) and `next_milestone`: the stem of the first milestone file under the record's `plan` directory (glob `core.plans.milestones.glob`, ordered by `id`) whose `status` is not `done`, null when the record has no plan. The stamp goes through `booping.context._yaml.update_frontmatter`, the way `runs.finish` writes.

Tests (integration tier, e2e corpora `booping-python/e2e/cases/run/` and `.../budget/`, hand-derived, fakes as in M01/M02): a fake child that runs `booping budget gate` against a closed window and exits 0 → record `status: paused`, the three keys, `next_milestone` the first `pending` milestone of a two-milestone fixture plan whose first is `done`; `run develop --autonomous` under a closed window → exit 3, the verdict on stdout, no `runs/*.md`; the child sees `BOOPING_RUN_ID` (the fake echoes it into the log); `run_pct` set → record carries `usage_baseline_7d`; `ack` on a paused run stamps `acked_at`; a fake child that pauses then exits 1 → `failed`, the three keys kept.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `BOOPING_RUN_ID`, launch gate, baseline. | `booping-python/src/booping/commands/run.py` | 1 | pending |
| 3.2 | `paused` status in `finish` and `ack`; gate stamps the record and computes `next_milestone`. | `booping-python/src/booping/runs.py`, `booping-python/src/booping/budget.py`, `booping-python/src/booping/commands/budget.py` | 2 | pending |
| 3.3 | The six e2e cases above. | `booping-python/e2e/cases/run/*paused*.txtar`, `booping-python/e2e/cases/run/*gate*.txtar` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] `bin/booping run develop --help` notes that `--autonomous` passes the budget gate first and exits 3 on `pause`.
- [ ] A launch without `--autonomous` is never gated; every existing `run` case passes unchanged.

### Task 3.2

- [ ] `gate` outside a registered run writes nothing.
- [ ] A paused child that exits non-zero records `failed`, keeping the stamped keys.

### Task 3.3

- [ ] The six cases exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/run/develop-over-a-plan-directory-records-a-finished-run.txtar` — a plan fixture plus a fake child.
- `booping-python/e2e/cases/run/ack-a-finished-run-stamps-acked-at.txtar` — the ack case to mirror.

## Verify

`cd booping-python && uv run pytest e2e/cases/run e2e/cases/budget -q`
