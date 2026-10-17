---
id: "07"
title: "Item callers move onto the operators"
sp: 4
status: pending
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M07: Item callers move onto the operators

## Tasks

**Goal**: no prompt, hook or doc calls `booping items`; every item operation runs through `create`, `query`, `set`, `transition`, and batching is prose.
**Scope**: `playbooks/specs/playbook.yaml` (open_item `when:` texts and header comment), `playbooks/specs/guide/prompt.md`, `playbooks/specs/playbook.md`, `playbooks/project-manager/{work,intake}/prompt.md` + fixtures + `tests.yaml`, `playbooks/groom/intake/fable-5.md`, `playbooks/_scripts/open-items-follow-plan`, new `playbooks/specs/_schemas/open_item.yaml`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Rewrite the open_item `when:` texts and every prompt: add → `create` tree, list → `query --config core.specs.open_items.index`, plan → `set plan=` + `transition planned`, close/reopen → `transition`, size → `set size=` + `mdcheck` with the schema | `playbooks/specs/playbook.yaml`, `playbooks/specs/guide/prompt.md`, `playbooks/groom/intake/fable-5.md` | 2 | pending |
| 7.2 | Project-manager batching as prose over `query`, sizes/direct/cap rendered from `core.project_manager_playbook.batch`; its eval fixtures and asserts follow | `playbooks/project-manager/work/prompt.md`, `playbooks/project-manager/intake/prompt.md`, `playbooks/project-manager/intake/tests.yaml` | 1 | pending |
| 7.3 | `open-items-follow-plan` as `query … --output paths` + `transition` per item, failures absorbed; the size schema; its e2e case rewritten | `playbooks/_scripts/open-items-follow-plan`, `playbooks/specs/_schemas/open_item.yaml`, `booping-python/e2e/cases/transition/` | 1 | pending |

Tests: integration tier — follow-plan hook closes a planned item on develop `done` and reopens it on `fail`; the size schema rejects `XL`.

## Definition of Done

- [ ] Task 7.1: `grep -rn 'booping items'` in `playbooks/`, `src/` and `specs/` returns nothing.
- [ ] Task 7.2: `bin/booping render-playbook project-manager` shows the sizes, direct sizes and cap from config in the batching paragraph.
- [ ] Task 7.3: `mdcheck playbooks/specs/_schemas/open_item.yaml` flags an item with `size: XL`; the follow-plan case passes.

## References

- `playbooks/groom/_schemas/milestone.yaml` — schema shape and the restated-config comment.
- `playbooks/_scripts/open-items-follow-plan` — failure absorption kept.

## Verify

`just e2e -k "transition and follow"`
