---
id: "07"
title: "Specs import guidance \u2014 init with a language set, splitting an area file into value records"
sp: 2
status: pending
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M07: Specs import guidance — init with a language set, splitting an area file into value records

The specs playbook guides bringing existing specs into a tier — the language set via `init --schemas`, and an area-file `values` record split into one `value` record per value.

**Scope**: create `docs/specs-import.md` (lazy-linked, value/0002): when the source specs use another language, `booping specs init --tier project --schemas {set}` first (sets: the `schemas-*` directories under `core.specs.format`, named by `booping specs init --help`), then a tier-owned override for any shape that still differs, then the records; an area file (one file, `## Ценности`/`## Values` with an `###` per value, bold `**На практике:**`/`**Чем жертвуем:**` labels or the source's own) becomes one `value` record per `###` — the heading the title, its paragraph the statement, each label's text the matching section, `kind: value` unless the source marks a non-value; numbers from `booping specs next value`; links into the area file rewritten to the new records; `booping specs check` last. Which `###` is one value and the wording stay the model's judgement, settled with the owner; never a schema for the area form. `playbooks/specs/guide/prompt.md` gains an `## Import` scenario (≤ 3 lines, links the doc) and one sentence in `## Init` naming `--schemas {set}` for a project writing in another language. Then `just snapshots` drifts in `playbooks/specs/_reports/output.md` only — the runner accepts it under the owner's snapshot policy.

Tests: none new — prose guidance; the snapshot holds the render. The specs/guide eval suite is not re-run (owner-run, subscription auth).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | The import doc. | `docs/specs-import.md` | 1 | pending |
| 7.2 | `Import` scenario and the `Init` sentence. | `playbooks/specs/guide/prompt.md` | 1 | pending |

## Definition of Done

### Task 7.1

- [ ] The doc names no project (no swarmlight, no hermes-pet) and restates no schema literal beyond the example labels.

### Task 7.2

- [ ] `bin/booping render-playbook specs --step guide` shows the `## Import` scenario and the link resolves under `${CLAUDE_PLUGIN_ROOT}`.

Return: the list of changed and created files, nothing else.

## References

- `docs/specs-alignment.md` — a lazy-linked specs doc to copy the tone and length of.
- `playbooks/specs/guide/prompt.md` — the scenario shape.

## Verify

`bin/booping render-playbook specs --step guide | grep -n "specs-import.md"`
