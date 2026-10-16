---
id: "04"
title: "booping plan check — the milestone contract as code"
sp: 4
status: done
plan: "plans/202610161319_groom-one-pass-and-plan-split/index.md"
---

# M04: booping plan check — the milestone contract as code

**Goal**: `booping plan check PLAN_DIR` reports every milestone that breaks the contract, per the I/O contract in `index.md`.

**Scope**: new `booping-python/src/booping/plan/check.py`, the `check` verb in `booping-python/src/booping/commands/plan.py`, tests `booping-python/tests/plan/check_test.py`, e2e `booping-python/e2e/cases/plan/check-*.txtar`. Reads `core.plans.milestones.glob`, `core.sprint.redecompose_threshold` and `core.groom_playbook.split.sections`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `check_milestone(text, sections, redecompose_threshold) -> list[Finding]`, sections located by the configured names: `verify` — exactly one command in Verify: one fenced block whose non-blank lines number one, or one non-blank line that is a single inline code span; zero or several → finding naming the count. `files` — Tasks names at least one path: a backticked token containing `/` or ending in `.{ext}`. `dod` — DoD `- [ ]`/`- [x]` items ≥ tasks, where tasks are the data rows of the first table in Tasks whose header has a cell `Task` (case-insensitive), else Tasks' top-level list items; zero tasks → finding. `sp` — frontmatter `sp` missing/null, or ≥ the threshold → finding. | `booping-python/src/booping/plan/check.py` | 2 | done |
| 4.2 | `check` verb: glob the milestone files in `id` order, print `{milestone dir}: {check}: {finding}` lines, exit 0/1/2 as the contract states. | `booping-python/src/booping/commands/plan.py` | 1 | done |
| 4.3 | Unit tests per check, each with a passing and a failing milestone text (two fenced Verify commands; Verify with `cmd1 && cmd2` on one line passes; a fenced Verify block holding two command lines fails; a task table with three rows and two checkboxes fails `dod`; list-style tasks; `sp: 5` with threshold 5 fails); e2e cases: a clean plan dir (exit 0, empty stdout), a plan dir with two failing milestones (exit 1, lines in id order), an empty dir (exit 2). | `booping-python/tests/plan/check_test.py`, `booping-python/e2e/cases/plan/check-clean.txtar`, `check-findings.txtar`, `check-no-milestones.txtar` | 1 | done |

Tests: surface `check_milestone` and `bin/booping plan check`; cases above; tiers unit + e2e.

## Definition of Done

### Task 4.1

- [x] Each of the four checks has a test that fails when the check is removed.

### Task 4.2

- [x] `bin/booping plan check --help` names the checks and the exit codes.

### Task 4.3

- [x] `uv run pytest tests/plan/check_test.py` and `just e2e -k check-` pass.

## References

- `booping-python/src/booping/plan/split.py` — section location and fence handling written in M01.
- `playbooks/_partials/milestone_contract.md` — the prose rules this check replaces (deleted in M05).

## Verify

```
cd booping-python && uv run pytest tests/plan/check_test.py -q
```
