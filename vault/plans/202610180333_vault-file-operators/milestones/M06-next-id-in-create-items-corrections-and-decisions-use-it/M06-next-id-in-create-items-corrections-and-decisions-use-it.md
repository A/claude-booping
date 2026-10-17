---
id: "06"
title: "next_id` in create; items, corrections and decisions use it"
sp: 3
status: done
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M06: next_id` in create; items, corrections and decisions use it

## Tasks

**Goal**: a template tree can name a file `{{ next_id('OI-') }}.md` and get the next free id in the destination.
**Scope**: `booping-python/src/booping/commands/create.py` (`dest` into the env), `booping-python/src/booping/rendering.py` if the global lives there, `src/config.yaml` (`core.specs.open_items.template`, `core.corrections.template`, `core.agent_decisions.template`), prompts that pass `--set name=$(date …)` (`_playbook_driving.j2`, `specs/rule/0031-corrections-are-logged.md`, `playbooks/code-review/resolve/opus-5.md`, project-manager prompts), e2e `cases/create/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | `next_id(prefix, width=4)` bound to the destination: max `{prefix}(\d+)` over its file names + 1, padded; usable in names and contents | `booping-python/src/booping/commands/create.py` | 1 | done |
| 6.2 | Key the three trees by `next_id` (`OI-`, `R`, `D`), the item tree stamping `created_at` by macro; switch the callers' `--set name=` to a step slug | `src/config.yaml`, `src/templates/_partials/_playbook_driving.j2`, `specs/rule/0031-corrections-are-logged.md` | 1 | done |
| 6.3 | e2e: empty dir → `OI-0001`, existing `OI-0007` → `OI-0008`, a correction gets `R0001-{slug}.md` | `booping-python/e2e/cases/create/` | 1 | done |

Tests: integration tier, txtar — the three cases with stubbed date/session macros.

## Definition of Done

- [x] Task 6.1: a tree keyed `"{{ next_id('OI-') }}.md"` writes `OI-0001.md` in an empty destination and `OI-0008.md` beside `OI-0007.md`.
- [x] Task 6.2: `bin/booping render src/templates/skills/playbook.md.j2` shows the agent-decision call without `$(date`.
- [x] Task 6.3: `just e2e -k create` passes.

## References

- `booping-python/src/booping/specs/open_items.py` — `create_item` id rule.
- `booping-python/e2e/cases/create/core-correction-entry-stamps-session-and-time.txtar` — case shape.

## Verify

`just e2e -k create`
