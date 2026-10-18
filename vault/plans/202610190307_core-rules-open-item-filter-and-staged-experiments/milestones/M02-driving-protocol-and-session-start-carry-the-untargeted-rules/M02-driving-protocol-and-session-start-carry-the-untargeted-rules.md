---
id: "02"
title: "Driving protocol and session start carry the untargeted rules"
sp: 5
status: done
plan: "plans/202610190307_core-rules-open-item-filter-and-staged-experiments/index.md"
---

# M02: Driving protocol and session start carry the untargeted rules

## Tasks

**Goal:** every `/playbook` render carries the ids-with-titles and staged-experiments lines; every booping session's start block carries the staged-experiments line.
**Scope:** `src/templates/_partials/_playbook_driving.j2`, `src/templates/hooks/session_start.md.j2`, the two e2e render cases; no config keys.
**Tests:** surface `booping render` of the skill and the session-start template; cases — the skill render carries both new lines, the session-start block carries the experiments line; tier — e2e txtar contract.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add to the driving protocol one line: every id said in chat carries its short title, filed items listed `Создан {id}: {title}` / `Created {id}: {title}` in the user's language, linking M01's rule; and one line: an experiment, eval or benchmark matrix runs cheap screen → shortlist → significance, each stage's size (calls, rough cost) and what it decides named before launch, linking M01's rule. Place them where the protocol speaks of chat output (near the completion report / questions paragraph), one paragraph each, no restated rule body. | `src/templates/_partials/_playbook_driving.j2` | 2 | done |
| 2.2 | Add one line to the session-start block: experiments run in stages, size named before each stage, linking the rule record by `${CLAUDE_PLUGIN_ROOT}` path. | `src/templates/hooks/session_start.md.j2` | 1 | done |
| 2.3 | Rebaseline the session-start e2e case; add an e2e render case pinning the two new driving-protocol lines (grep-filtered like `driving-protocol-carries-both-modes.txtar`). | `booping-python/e2e/cases/render/session-start-block-lists-project-and-global-playbooks.txtar`, `booping-python/e2e/cases/render/driving-protocol-carries-ids-and-experiments.txtar` | 2 | done |

## Definition of Done

Task 2.1
- [x] `bin/booping render src/templates/skills/playbook.md.j2` shows both lines once each, links resolving to the M01 records.
- [x] No other line of the partial changed; `driving-protocol-carries-both-modes.txtar` passes unchanged.

Task 2.2
- [x] The block grows by one line; nothing else in it changes; silent-outside-a-project behaviour of `hooks/session-start.sh` untouched.

Task 2.3
- [x] The rebaselined case differs from its old baseline only by the new line.
- [x] The new case fails if either driving-protocol line is removed.

## References

- `booping-python/e2e/cases/render/driving-protocol-carries-both-modes.txtar` — grep-filtered render case shape.
- `specs/rule/0032-approval-asked-in-prose.md` — how a protocol-carried rule names its carrier.

## Verify

`just e2e -k "driving-protocol or session-start"`
