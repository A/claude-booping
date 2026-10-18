---
id: "02"
title: "Scorer v3: rubric, agent body, the guide's Record scenario"
sp: 10
status: done
plan: "plans/202610190307_adr-scorer-v3/index.md"
---

# M02: Scorer v3: rubric, agent body, the guide's Record scenario

## Tasks

**Goal:** the specs guide scores a draft ADR with the v3 input and reply and gates on route and alt_score; the brief shows «Не взвешено:». **Scope:** `playbooks/specs/guide/adr-rubric.md`, `agents/adr-scorer.md`, `src/specs/README.md`, `playbooks/specs/guide/prompt.md`, the guide's eval fixtures; no other playbook reads the scorer.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Replace the rubric's body with the v3 task text quoted under References, verbatim below an `# ADR scorer task` heading — the text the experiment measured | `playbooks/specs/guide/adr-rubric.md` | 2 | done |
| 2.2 | Agent body: names the five pasted parts (task, guide excerpt, records, primitives, draft ADR), says it judges from them alone and has no tool to reach anything else, replies with the task's JSON line and nothing else; frontmatter `description` updated to route + alternatives; `tools: ListAgents` and its comment kept | `agents/adr-scorer.md` | 2 | done |
| 2.3 | Append the `open item` bullet to `## When a record is worth writing`: "**open item** — a piece of work or a question for the owner that must outlive the session (a bug, a feature, a gap between specs and code); not a decision, not a constraint." | `src/specs/README.md` | 1 | done |
| 2.4 | `## Record` step 1: spawn the scorer with, under fixed headings, the rubric's text, the format guide's `## Types` and `## When a record is worth writing` sections, the output of `booping specs ls --tier {tier} --type value --type rule --type adr --exclude adr/{NNNN} --titles`, the project's primitives (one line per command or building block the attached repo's CLAUDE.md names; none → the heading says so), the ADR's text — text, never paths. Gate per Decisions 11; brief per Decisions 12 (header from `alt_score`, «Не взвешено:» line, `overlaps` refs in «Задевает:») | `playbooks/specs/guide/prompt.md` | 3 | done |
| 2.5 | The guide's eval fixtures carry a v3 JSON reply in place of `score: 3`; record-adr-brief's canned reply has one `missing` entry and its brief asserts check the «Не взвешено:» line; one new fixture with `route: rule` checks no ADR file is written and the route is shown | `playbooks/specs/guide/_fixtures/record-adr-brief.md`, `playbooks/specs/guide/_fixtures/record-decision.md`, `playbooks/specs/guide/tests.yaml`, new `playbooks/specs/guide/_fixtures/record-adr-routed.md` | 2 | done |

Test surface: the specs guide step and the scorer agent; cases — v3 reply shape in the brief, «Не взвешено:» rendered, `route: rule` blocks the ADR; tier — the guide's promptfoo suite (smoke + regress), integration of the prompt with canned scorer replies.

Worker returns: the list of changed files and the Verify exit status.

## Definition of Done

Task 2.1
- [x] Rubric asks for exactly one JSON line with keys `route`, `route_why`, `overlaps`, `alt_score`, `missing`, the limits ≤ 3 and the route enum `adr|rule|value|story|reference|idea|open-item|none`.
- [x] No `score:` line contract remains.

Task 2.2
- [x] Body names the five inputs and the JSON reply; the phrase "you have no tools" is gone; `tools: ListAgents` unchanged.

Task 2.3
- [x] README section ends with the open item bullet; `just specs-check` clean.

Task 2.4
- [x] `## Record` names the five pasted parts and the `specs ls` line with `--exclude` of the draft's ref.
- [x] `route ≠ adr` → no ADR written, material recorded as the routed type per Decisions 11; `alt_score ≤ 1` → redraft from `missing`, at most two rounds.
- [x] Brief template has «Не взвешено: {missing}» (omitted when empty) and `overlaps` in «Задевает:».
- [x] `bin/booping render-playbook specs --step guide` renders clean.

Task 2.5
- [x] No fixture carries `score: N` as a scorer reply.
- [x] `just smoke specs/guide` passes.

## References

- The v3 task text for task 2.1, verbatim:

> You review one draft ADR before it is written to the project's specs. Judge it on two questions.
>
> 1. Routing — is this an ADR at all? Apply the guide's test. A choice already settled by a rule, a value restated, what the code, config or a state machine already says, a decision another existing record already makes, a scenario, a fact, or future work is not an ADR: name where it belongs.
> 2. Alternatives — if it is an ADR, were the options real? Check the cheap options where they apply: prose in a prompt or an existing tool, extending or generalising an existing primitive (look for one in the project's records and primitives below), building nothing. Each counts as weighed when it is a row, or one line in Context says why it does not apply. An option that is the decision's negation, a straw man, or the broken way nobody would return to is filler.
>
> Answer with one JSON object on one line and nothing else:
> {"route":"adr|rule|value|story|reference|idea|open-item|none","route_why":"one sentence","overlaps":["at most 3 bare refs like adr/0012, no prose: existing records that make this same decision or state this same constraint"],"alt_score":0-3,"missing":["at most 3: a cheap option not weighed, or the one obvious rival, naming the existing primitive or record when there is one"]}
>
> alt_score: 3 the cheap options that apply are weighed honestly; 2 the rivals are real but a cheap option is missing; 1 the alternatives are filler (negation, straw man), or the cheapest obvious option — building nothing or extending a named existing primitive — clearly applies and is ignored; 0 no real choice. List in missing only what a reader would want weighed before accepting — not every variation of the design.

- `playbooks/specs/guide/prompt.md` `## Record` (today's step 1–2) — the shape kept.
- `playbooks/specs/guide/_fixtures/record-adr-brief.md` — canned-output fixture shape.

## Verify

`just smoke specs/guide`
