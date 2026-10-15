---
id: "01"
title: "Open-item machine, config and the specs playbook skeleton"
sp: 3
status: done
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M01: Open-item machine, config and the specs playbook skeleton

`bin/booping render-playbook specs` renders a `specs` playbook whose `## State` section shows the `open_item` machine, and `bin/booping config-get core.specs.open_items` prints the open-items config.

**Scope**: `src/config.yaml` gains `core.specs.open_items` with `dir: open-items`, `scaffold` (a scaffold tree writing one `{{ id }}.md` item file with exactly the frontmatter and body of `index.md` `## Architecture` → "Open item file", values from `--set id/title/direction/record/source/created_at`, `status: open`, `plan`/`closed_at`/`reason` null, optional `--set body`) and `index` (a query spec over `{dir}/OI-*.md`, columns `id, status, direction, record, title, plan`, sorted by id) — comment each key as the surrounding block does. `playbooks/specs/` is created: `playbook.yaml` with `graph: {guide: []}` and `states.open_item` exactly as `index.md` `## Architecture` → "`open_item` machine" (artifact `open-items/{instance}.md`, initial `open`, `done`/`dropped` terminal, `frontmatter-update` hooks stamping `closed_at` with `core.macros.date '+%Y-%m-%d'` and clearing `plan` on `planned → open`, gate on `open → planned`: "`plan` names an existing plan file"); `playbook.md` with frontmatter `name: specs`, `title`, `summary`, `trigger`, `jinja: true`, `inline_steps: true`, `requires_project: true` and a preamble of one paragraph: the run keeps no state of its own; the `open_item` machine's workdir is the vault and only `booping specs open-items` moves it; then the agents and shared-instructions includes. `guide/prompt.md`: frontmatter `summary` (one line: act on the user's specs request from the dialogue) and `review_gate: null`, body the single line "Read the user's specs request and act on it." — M07 grows both bodies.

Tests: integration tier — one txtar case moving a scaffolded item `open → dropped` through `booping playbook-transition specs dropped --state open_item --instance OI-0001 --workdir {vault}`, asserting `status: dropped` and a stamped `closed_at`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `core.specs.open_items` — dir, item scaffold tree, index query spec. | `src/config.yaml` | 1 | done |
| 1.2 | `specs` playbook skeleton with the `open_item` machine, plus the transition case. | `playbooks/specs/playbook.yaml`, `playbooks/specs/playbook.md`, `playbooks/specs/guide/prompt.md`, `booping-python/e2e/cases/playbook-transition/the-open-item-machine-drops-an-open-item.txtar` | 2 | done |
| 1.3 | Engine: a `standalone: true` key on a `states:` entry loads a per-instance machine no graph scope references (moved only by `--state {name} --instance {id}` invocations), exempt from the subgraph-reference `bad_state` check and the `orphan_state` note; `open_item` sets it; the `## State` render names it standalone instead of a referencing scope. Added at develop (develop-defaults D6). | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/`, `booping-python/e2e/cases/render-playbook/`, `documentation/playbook.md` | 1 | done |

## Definition of Done

### Task 1.1

- [x] `bin/booping scaffold core.specs.open_items.scaffold /tmp/oi --set id=OI-0001 --set title=t --set direction=clarify --set record=null --set source=manual --set created_at=2026-10-15` writes `/tmp/oi/OI-0001.md` matching the "Open item file" shape key for key.
- [x] `bin/booping query --config core.specs.open_items.index` runs (empty result on a vault with no items).
- [x] No status literal outside the machine: the scaffold's `status: open` is the machine's `initial`, commented as such.

### Task 1.2

- [x] `bin/booping render-playbook specs` exits 0 with no STOP notice and a `## State` section for `open_item`.
- [x] Every edge of the Architecture table exists, no other edge; `done` and `dropped` are terminal.
- [x] The transition case passes.

### Task 1.3

- [x] A `standalone: true` state with `{instance}` in `artifact` and no referencing scope loads with no `bad_state` and no `orphan_state`; without the key both checks still fire (unit or e2e cases for both).
- [x] `documentation/playbook.md` documents the key in its states reference.

Return: the list of changed files, nothing else.

## References

- `playbooks/setup/playbook.md`, `playbooks/setup/playbook.yaml` — the ephemeral, stateless playbook shape.
- `/home/anton/Dev/@A/notes/projects/_playbooks/backlog-manage/playbook.yaml` — `states.task`, a per-file machine (`artifact: tasks/{instance}.md`) the graph's run does not own.
- `src/config.yaml` `core.groom_playbook.milestone_scaffold` — a templated one-file scaffold tree.

## Verify

`just e2e -k "open-item-machine"`
