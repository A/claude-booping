---
id: "06"
title: "Groom partials, present check and snapshot"
sp: 2
status: done
plan: "plans/202610161319_groom-one-pass-and-plan-split/index.md"
---

# M06: Groom partials, present check and snapshot

**Goal**: groom's shared partials and present match the one-file draft, every stale reference to the removed steps and partial is gone, and groom's snapshot report is accepted.

**Scope**: delete `playbooks/_partials/milestone_contract.md`, edit `playbooks/_partials/plan_templates.md` and `playbooks/groom/present/sonnet-5.md`, accept `playbooks/groom/_reports/output.md` (runner). `playbooks/groom/_specs/` is design history — not touched.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Delete `_partials/milestone_contract.md`; in `_partials/plan_templates.md` replace the checklist-walk bullet with "`# Quality Checklist` — constraints the plan meets; read with the body, not walked as a separate pass", and replace the "two surfaces … one file per milestone" paragraph with one line: the draft is one file, cut by `booping plan split`. Grep the repo (`playbooks/`, `src/`, `docs/`, `agents/`, `skills/`) for `milestone_contract`, `research-codebase`, `research-web`; every hit outside `_specs/`, `_reports/` and `vault/` is fixed (rule/0007). | `playbooks/_partials/milestone_contract.md`, `playbooks/_partials/plan_templates.md` | 1 | done |
| 6.2 | `present/sonnet-5.md`: run `booping plan check {plan-dir}` and show its output (or "milestone contract: clean") on the approval screen under the table, so findings left after the fix rounds reach the gate from code, not from memory. | `playbooks/groom/present/sonnet-5.md` | 1 | done |

Tests: surface `bin/booping render-playbook groom --step present` and `just snapshots`; cases — present carries the check, the only drift is groom's report; tier render + snapshot.

## Definition of Done

### Task 6.1

- [x] `grep -rn -E 'milestone_contract|research-codebase|research-web' playbooks src docs agents skills --include='*.md' --include='*.j2' --include='*.yaml' | grep -v -E '/_specs/|/_reports/'` prints nothing.
- [x] Runner: `just snapshots` drifts only `playbooks/groom/_reports/output.md`, and every hunk is a change this milestone describes; the runner then runs `just snapshots-accept groom` and appends the report and why to `plans/202610161319_groom-one-pass-and-plan-split/develop-defaults.md` (owner's standing permission, clarifications C12). Any other drift stops the run.

### Task 6.2

- [x] `bin/booping render-playbook groom --step present` contains `booping plan check`.

## References

- `playbooks/groom/present/sonnet-5.md` — the approval screen being extended.
- `scripts/snapshots.py` — what `just snapshots` / `just snapshots-accept groom` compare and write.

## Verify

```
bin/booping render-playbook groom --step present
```
