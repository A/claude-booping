---
id: "07"
title: "Smoke suite for project-manager on-start"
sp: 2
status: pending
plan: "plans/202610152006_project-manager-playbook/index.md"
---

# M07: Smoke suite for project-manager on-start

A deterministic smoke suite holds `on-start`'s contract: the status first, then the act-on order, and writing nothing.

**Scope**: create `playbooks/project-manager/on-start/promptfooconfig.yaml`, `tests.yaml`, `_fixtures/`, the shape of M06's suite (`output_mode: files`, `allow_no_files: true`). Each fixture states the `booping status` output a live run would print and `Autonomy: supervised`. Cases, all `tier: smoke`:

1. `finished-run-first` — status with one unacked finished run, one item waiting on the user and one `ready-for-dev` plan → the return carries the status lines verbatim and names the run id before the waiting item and the plan; no file written.
2. `waiting-item-points-to-sidecar` — status with only an item waiting → the return names `open-items/questions/{id}.md`; no file written.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Suite config, two fixtures, `tests.yaml`. | `playbooks/project-manager/on-start/promptfooconfig.yaml`, `playbooks/project-manager/on-start/tests.yaml`, `playbooks/project-manager/on-start/_fixtures/*.md` | 2 | pending |

## Definition of Done

### Task 7.1

- [ ] `just suites` lists `project-manager/on-start`; every case carries the smoke metadata.
- [ ] The suite passes.

Return: the list of changed and created files and the suite's pass count, nothing else.

## References

- `playbooks/project-manager/intake/promptfooconfig.yaml` (M06), `playbooks/specs/guide/tests.yaml` (the `what-is-open` case) — suite and no-write case shapes.

## Verify

`EVAL_PR=0 just smoke project-manager/on-start`
