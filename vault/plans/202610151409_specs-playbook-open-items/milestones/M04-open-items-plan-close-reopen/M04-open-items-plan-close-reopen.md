---
id: "04"
title: "plan, close and reopen move items through the machine"
sp: 4
status: done
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M04: plan, close and reopen move items through the machine

`booping specs open-items plan|close|reopen` move items through the `open_item` machine and print one transition report per item.

**Scope**: the transition logic of `booping-python/src/booping/commands/playbook_transition.py` is exposed as one function the specs CLI calls in-process (playbook `specs`, state `open_item`, instance the id, workdir the vault), printing the same report `playbook-transition` prints; the command itself keeps its behaviour. Verbs per `index.md` `## I/O contract`: `plan ID… --plan PATH` writes `plan:` (vault-relative; the path must exist, else exit 1) through the frontmatter-update module then transitions to `planned`; `close ID… [--dropped] [--reason TEXT]` writes `reason` when given, then transitions to `done` (or `dropped`); `close --plan PATH` and `reopen --plan PATH` select every `planned` item whose `plan:` equals PATH; `reopen ID…` → `open`. A machine-refused edge (e.g. `close` on an `open` item) is exit 1 with the message of `index.md` `## Architecture`. IDs are processed in order; the first failure stops the run.

Tests: integration tier, txtar cases — plan then close (`done`, `closed_at` stamped); close `--dropped --reason` on an open item; close on an open item without `--dropped` is exit 1; close `--plan` closes only that plan's planned items; reopen `--plan` returns them to `open` with `plan` cleared; `--plan` with no match prints `no planned items for …`; plan with a missing plan path is exit 1.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Expose the transition engine as an in-process function; `playbook-transition` unchanged. | `booping-python/src/booping/commands/playbook_transition.py` | 2 | done |
| 4.2 | `plan`, `close`, `reopen` verbs. | `booping-python/src/booping/commands/specs.py`, `booping-python/src/booping/specs/open_items.py` | 1 | done |
| 4.3 | The seven cases. | `booping-python/e2e/cases/specs/open-items-plan-*.txtar`, `open-items-close-*.txtar`, `open-items-reopen-*.txtar` | 1 | done |

## Definition of Done

### Task 4.1

- [x] Every existing `booping-python/e2e/cases/playbook-transition/` case passes unchanged.

### Task 4.2

- [x] No verb writes `status:` itself; every status change goes through the engine.
- [x] Each verb's `--help` lists its flags.

### Task 4.3

- [x] Seven cases, one per behaviour named in Tests.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/commands/playbook_transition.py` — the engine to expose.
- `/home/anton/Dev/@A/notes/projects/_playbooks/backlog-manage/_scripts/backlog-undo` — a caller moving a per-file machine by `--state` and `--instance`.
- `booping-python/e2e/cases/playbook-transition/a-machine-without-an-artifact-moves-with-a-target.txtar` — transition case shape.

## Verify

`just e2e -k "open-items-plan or open-items-close or open-items-reopen"`
