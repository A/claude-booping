---
id: "03"
title: "ADR scorer"
sp: 7
status: pending
plan: "plans/202610190033_specs-acceptance-and-session-entry/index.md"
---

# M03: ADR scorer

## Tasks

**Goal:** a new ADR is scored 0–3 before the brief by an Opus agent that gets the ADR text and the rubric inline and has no tool to read anything else.
**Scope:** a rubric file beside the guide step, a new internal agent, the `## Record` scenario, an eval suite for the agent.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Rubric: the audit rubric verbatim from `adr-audit-ground-truth.md`, plus the three cheap options by name and the output contract — first line `score: {0-3}`, then one line per finding | `playbooks/specs/guide/adr-rubric.md` | 1 | pending |
| 3.2 | Agent `adr-scorer`: model opus, no tools at all — check the Claude Code agent frontmatter for how a definition grants zero tools and use that; a static body (no render step, it could not run one) saying it scores only the text in its prompt against the rubric there and returns the output contract | `agents/adr-scorer.md` | 2 | pending |
| 3.3 | `## Record`: before the brief, spawn `booping:adr-scorer` with the ADR file's text and the rubric's text pasted into the prompt — no paths; ≤ 1 → redraft, at most two rounds; the brief's header carries the score | `playbooks/specs/guide/prompt.md` | 2 | pending |
| 3.4 | Eval suite for the agent: three ground-truth ADRs scored 1, 2 and 3; smoke asserts the output contract and that the agent made no tool call, regress asserts each score within ±1 of the ground truth | `agents/_evals/adr-scorer/` or the repo's existing place for agent evals | 2 | pending |

Test surface: the scorer agent, eval smoke (contract, zero tool calls) and regress (score against the hand-derived ground truth).

## Definition of Done

Task 3.1
- [ ] The rubric file holds the four score lines, the three cheap options and the output contract.

Task 3.2
- [ ] The agent definition grants no tool and names `model: opus`; its body names no file to read.

Task 3.3
- [ ] `## Record` passes the ADR and the rubric as text, names the threshold and the round limit, and never passes a path.

Task 3.4
- [ ] The smoke tier passes; the regress tier result is reported.

Return: the files changed, the regress scores and the Verify verdict, nothing else.

## References

- `vault/plans/202610190033_specs-acceptance-and-session-entry/adr-audit-ground-truth.md` — rubric and scores.
- `agents/booping-researcher.md` — agent frontmatter shape.

## Verify

`just smoke adr-scorer || just suites | grep -i scorer`
