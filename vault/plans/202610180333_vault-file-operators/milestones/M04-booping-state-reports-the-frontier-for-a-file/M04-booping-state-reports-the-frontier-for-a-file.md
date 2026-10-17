---
id: "04"
title: "booping state` reports the frontier for a file"
sp: 2
status: done
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M04: booping state` reports the frontier for a file

## Tasks

**Goal**: `booping state <file>` prints today's frontier report for the playbook(s) whose machines match the file.
**Scope**: `booping-python/src/booping/commands/playbook_state.py` → `state.py`, `cli.py`, e2e `cases/playbook-state/` → `cases/state/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Resolve the playbook(s) from the file with M03's matcher (`--playbook` narrows, required without `artifact:`), run dir from the file; report every machine of each, instances included | `booping-python/src/booping/commands/state.py` | 1 | done |
| 4.2 | Move e2e cases to `cases/state/` with rewritten argv; add one case where `index.md` reports groom and develop without `--playbook` | `booping-python/e2e/cases/state/` | 1 | done |

Tests: integration tier — the moved corpus plus the two-playbook case.

## Definition of Done

- [x] Task 4.1: `booping state {plan}/index.md --playbook groom` prints the same report `playbook-state groom --workdir {plan}` printed; `booping playbook-state` is unknown.
- [x] Task 4.2: `just e2e -k state` passes.

## References

- `booping-python/src/booping/commands/playbook_state.py` — the report kept.

## Verify

`just e2e -k state`
