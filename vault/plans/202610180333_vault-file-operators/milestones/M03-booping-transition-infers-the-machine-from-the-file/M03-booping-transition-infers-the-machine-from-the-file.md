---
id: "03"
title: "booping transition` infers the machine from the file"
sp: 4
status: done
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M03: booping transition` infers the machine from the file

## Tasks

**Goal**: `booping transition <file> <status>` moves a file along the one machine that matches it, or fails naming the candidates.
**Scope**: `booping-python/src/booping/commands/playbook_transition.py` → `transition.py` (CLI + the in-process `transition()` other code calls), `cli.py`, `specs/open_items.py` callers of `transition()`, e2e `cases/playbook-transition/` → `cases/transition/`, unit tests and script docstrings naming the old command.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Candidate resolution: machines across all playbooks whose `artifact` matches the file (instance from the path), filtered by an edge from the file's current status (or `initial` when it has none), narrowed by `--playbook`/`--state`; workdir implied from file + pattern; `--playbook` required for machines without `artifact:` | `booping-python/src/booping/commands/transition.py` | 3 | done |
| 3.2 | Move the e2e corpus to `cases/transition/` with rewritten argv; add cases: unique inference (open item, milestone instance), ambiguous `index.md` edge without `--playbook` exits 1 listing `groom/run` and `develop/run`, a no-artifact machine without `--playbook` exits 1, illegal target lists legal ones | `booping-python/e2e/cases/transition/` | 1 | done |

Tests: integration tier, txtar — the four inference cases above plus the moved corpus; the hook environment (`BOOPING_*`) unchanged.

## Definition of Done

- [x] Task 3.1: `booping transition {vault}/open-items/OI-0001.md clarify` moves the item without `--playbook`; `booping transition {plan}/index.md ready-for-dev` from `awaiting-approval` exits 1 naming both candidates; with `--playbook groom` it runs groom's hooks; the printed mutation report is unchanged in shape.
- [x] Task 3.2: `just e2e -k transition` passes; `booping playbook-transition` is unknown.

## References

- `booping-python/src/booping/commands/playbook_transition.py` — `transition()`, `implied_workdir()`, `_resolve_artifact()`.
- `booping-python/src/booping/context/lifecycle.py` — `resolve_edges`, `resolve_hooks`.
- `booping-python/e2e/cases/playbook-transition/` — case shape.

## Verify

`just e2e -k transition`
