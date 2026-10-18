---
id: "03"
title: "ADR scorer"
sp: 7
status: pending
plan: "plans/202610190033_specs-acceptance-and-session-entry/index.md"
---

# M03: ADR scorer

## Tasks

**Goal:** a new ADR is scored 0–3 by a context-free subagent on a cheap model chosen by measurement, before the brief.
**Scope:** a rubric file beside the guide step, the `## Record` scenario, a measurement script, a reference record with the result.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Rubric: the audit rubric verbatim from `adr-audit-ground-truth.md`, plus the three cheap options by name and the output contract — first line `score: {0-3}`, then one line per finding | `playbooks/specs/guide/adr-rubric.md` | 1 | pending |
| 3.2 | Measurement: a script runs the rubric over the ground-truth ADRs unchanged since `2597086`, each ADR alone, through `claude -p --model {model}` for haiku, sonnet and opus, twice per model; it prints per model the exact-match rate and the count of 1↔3 swaps against the ground truth | `scripts/adr-scorer-bench.sh` | 3 | pending |
| 3.3 | Run it; record the table and the pick in a reference record — the cheapest model with exact-match ≥ 70 % and no 1↔3 swap; none passes → Opus | `vault/reference/{next}-adr-scorer-model.md` | 1 | pending |
| 3.4 | `## Record`: before the brief, spawn a `general-purpose` subagent on the picked model with only the ADR path and the rubric path; ≤ 1 → redraft, at most two rounds; the brief's header carries the score | `playbooks/specs/guide/prompt.md` | 2 | pending |

Test surface: the measurement itself is the test of the scorer (real model calls, ground truth hand-derived yesterday); the guide's eval fixture from M02 gains the score in the header.

## Definition of Done

Task 3.1
- [ ] The rubric file holds the four score lines, the three cheap options and the output contract.

Task 3.2
- [ ] The script exits 0 and prints one row per model with the two numbers.

Task 3.3
- [ ] The reference record holds the table, the threshold and the pick; `just specs-check` passes.

Task 3.4
- [ ] `## Record` names the model from the reference, the inputs (two paths only), the threshold and the round limit.

Return: the files changed, the measurement table and the Verify verdict, nothing else.

## References

- `vault/plans/202610190033_specs-acceptance-and-session-entry/adr-audit-ground-truth.md` — rubric and scores.
- `scripts/eval-*.sh` — how scripts call `claude -p` on subscription auth.

## Verify

`bash scripts/adr-scorer-bench.sh --dry-run && just specs-check`
