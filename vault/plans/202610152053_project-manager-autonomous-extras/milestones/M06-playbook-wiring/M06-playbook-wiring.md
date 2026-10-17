---
id: "06"
title: "Develop-loop gate and project-manager batches, pauses and resumes"
sp: 3
status: done
plan: "plans/202610152053_project-manager-autonomous-extras/index.md"
---

# M06: Develop-loop gate and project-manager batches, pauses and resumes

develop checks the budget gate before each milestone group, and the project-manager sizes tiny fixes, works them in batches, and reports and resumes paused runs.

**Scope**: `playbooks/develop/develop-loop/base.md` "## Delegating a group" — a new first step: run `booping budget gate`; exit 3 → take no transition, end the run with the verdict as its report (the gate already stamped the run record); exit 0 → continue. `playbooks/project-manager/work/prompt.md` — "## Classify": a tiny fix is also sized, `booping items size {id} {size}` with the sizes `booping config-get core.project_manager_playbook.batch` lists; "## Tiny fix" becomes batch-driven: `booping items batch`, then per batch line: `booping budget gate` (exit 3 → stop the turn, report), one worker briefing — `## Task` (fix the items below, uncommitted), one `## Item {id}` block per item holding its verbatim text from the item file, `## Return` (per item: files touched and its check's verdict, nothing else) — verify, one commit per item by path naming its id, `booping items close` each; "## Runs": `booping run … --autonomous` exiting 3 means the gate is closed — the item stays queued and is reported `paused`; a `Paused:` row in `booping status runs --detail` whose `resume after` has passed (or is empty and the gate now allows) → run its `resume` command; "## Report": one new row, outcome `paused`, pointer the run record `runs/{run}.md` (or `gate closed` when no run started). No literal sizes, thresholds or statuses in prose (rule/0017) — the bodies name the command that prints them.

Drift: `just snapshots` drifts in `playbooks/develop/_reports/output.md` and `playbooks/project-manager/_reports/output.md` with exactly these edits; the runner accepts them per the owner's snapshot policy.

Tests: none new — prompt prose; the committed snapshot reports hold it (`just snapshots`).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Gate step in develop-loop. | `playbooks/develop/develop-loop/base.md` | 1 | done |
| 6.2 | Sizing, batches, paused outcome and resume in the work step. | `playbooks/project-manager/work/prompt.md` | 2 | done |

## Definition of Done

### Task 6.1

- [x] `bin/booping render-playbook develop --step develop-loop` shows the gate as the first step of "Delegating a group", with no STOP or Note notice.

### Task 6.2

- [x] `bin/booping render-playbook project-manager --step work` shows the four section changes, no STOP or Note notice.
- [x] No size letter, SP number, threshold or run status literal appears in the changed prose.

Return: the list of changed files, nothing else.

## References

- `playbooks/project-manager/work/prompt.md` — the existing route sections whose shape the changes keep ("Next:" line per section).

## Verify

`bin/booping render-playbook develop --step develop-loop | grep -c 'booping budget gate' && bin/booping render-playbook project-manager --step work | grep -c 'booping items batch'` — both counts ≥ 1.
