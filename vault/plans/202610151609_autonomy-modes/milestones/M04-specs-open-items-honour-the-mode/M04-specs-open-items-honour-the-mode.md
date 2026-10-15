---
id: "04"
title: "The specs open-items scenario honours the mode"
sp: 3
status: in-progress
plan: "plans/202610151609_autonomy-modes/index.md"
---

# M04: The specs open-items scenario honours the mode

The specs playbook shows the project's mode and its open-items scenario follows it: supervised stops at groom's plan review as today, autonomous takes items through groom and develop without stopping.

**Scope**: `playbooks/specs/playbook.md` gains the `Autonomy:` preamble line of `index.md` `## Output contract`, after the tier list. `playbooks/specs/guide/prompt.md` `## Open items` keeps its first two sentences and replaces its `Next:` sentence with the two mode lines of `### Specs open-items scenario`. A fourth smoke case, `autonomous-open-items`, under `playbooks/specs/guide/`: a fixture in the shape of `what-is-open.md` whose preamble lines state `Autonomy: autonomous`, two open items, and a user line "work the open items"; asserts — nothing written under `specs/`, the reply names `/playbook groom` with both ids and `/playbook develop`, and asks the user nothing. `what-is-open.md` gains the `Autonomy: supervised` line so both arms are pinned. Then run `just snapshots` and report its drift; accepting it is the runner's, per the run's snapshot policy, never the worker's: the specs report drifts in the preamble line and the scenario only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Preamble line and the scenario's two mode lines. | `playbooks/specs/playbook.md`, `playbooks/specs/guide/prompt.md` | 1 | pending |
| 4.2 | The autonomous smoke case, its fixture, and the supervised line in `what-is-open.md`. | `playbooks/specs/guide/tests.yaml`, `playbooks/specs/guide/_fixtures/autonomous-open-items.md`, `playbooks/specs/guide/_fixtures/what-is-open.md` | 2 | pending |

## Definition of Done

### Task 4.1

- [ ] `bin/booping render-playbook specs` shows `Autonomy: \`supervised\`` in this repo; `--set core.autonomy=autonomous` shows `autonomous`.
- [ ] The scenario restates nothing groom or develop own (gates, defaults logging) — the driving protocol carries that.
- [ ] `just snapshots` drift is limited to `playbooks/specs/_reports/output.md`, in these two places.

### Task 4.2

- [ ] The new case follows `tests.yaml`'s existing case shape: `metadata` with `tier: smoke`, asserts through `_lib/asserts/files.js` and `_lib/asserts/return.js`.
- [ ] `just smoke specs/guide` passes all four cases.

Return: the list of changed files and the smoke result line, nothing else.

## References

- `playbooks/specs/guide/_fixtures/what-is-open.md` — fixture shape.
- `playbooks/specs/guide/tests.yaml` — `what-is-open` case, the assert shape to copy.

## Verify

`just smoke specs/guide`
