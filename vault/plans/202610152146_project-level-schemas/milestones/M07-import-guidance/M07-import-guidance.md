---
id: "07"
title: "Specs import guidance — init with a language set, splitting an area file into
  value records"
sp: 2
status: done
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M07: Specs import guidance — init with a language set, splitting an area file into value records

The specs playbook guides bringing existing specs into a tier — renaming structural headings to the shipped English ones, and splitting an area-file `values` record into one `value` record per value.

**Scope** (amended by the owner's decision of 2026-10-15 — English structural headings everywhere, no translated schema sets): create `docs/specs-import.md` (lazy-linked, value/0002) for importing specs written elsewhere: rename every structural heading, bold label and table column to the shipped English one (a mechanical rename — e.g. `## Правило` → `## Rule`, `## Следует из ценностей` → `## Follows from`, `**На практике:**` → In practice, `**Чем жертвуем:**` → Trade-off, `Вариант|Статус|Сложность|Обратимость|Вердикт` → `Option|Status|Complexity|Reversibility|Verdict`, values `низкая/средняя/высокая` → `low/medium/high`) while the content keeps its language; a tier-owned schema only for a type the shipped set lacks (e.g. `mechanic`); an area file (one file, `## Ценности`/`## Values` with an `###` per value) becomes one `value` record per `###` — the heading the title, its paragraph the statement, the labels' text the In practice / Trade-off sections, `kind: value` unless the source marks a non-value; numbers from `booping specs next value`; links into the area file rewritten; `booping specs check` last. Which `###` is one value and the wording stay the model's judgement, settled with the owner. `playbooks/specs/guide/prompt.md` gains an `## Import` scenario (≤ 3 lines, links the doc). Then `just snapshots` drifts in `playbooks/specs/_reports/output.md` only — accepted under the owner's snapshot policy.

Tests: none new — prose guidance; the snapshot holds the render. The specs/guide eval suite is not re-run (owner-run, subscription auth).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | The import doc. | `docs/specs-import.md` | 1 | done |
| 7.2 | `Import` scenario and the `Init` sentence. | `playbooks/specs/guide/prompt.md` | 1 | done |

## Definition of Done

### Task 7.1

- [x] The doc names no project (no swarmlight, no hermes-pet) and restates no schema literal beyond the example labels.

### Task 7.2

- [x] `bin/booping render-playbook specs --step guide` shows the `## Import` scenario and the link resolves under `${CLAUDE_PLUGIN_ROOT}`.

Return: the list of changed and created files, nothing else.

## References

- `docs/specs-alignment.md` — a lazy-linked specs doc to copy the tone and length of.
- `playbooks/specs/guide/prompt.md` — the scenario shape.

## Verify

`bin/booping render-playbook specs --step guide | grep -n "specs-import.md"`
