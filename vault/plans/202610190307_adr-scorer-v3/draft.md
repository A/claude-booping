# ADR scorer v3 — routing, overlaps and missing options from the guide and the record inventory

## Context

Request: [request.md](request.md), open item [OI-0035](../../open-items/OI-0035.md).

`booping:adr-scorer` today gets an ADR and the v1 rubric (`playbooks/specs/guide/adr-rubric.md`) pasted into its prompt and replies `score: {0-3}` plus findings; the specs guide's `## Record` scenario redrafts on a score ≤ 1. Judging the text alone, it cannot tell an ADR that should have been a rule, a value or nothing, and its score barely moves when a cheap option is cut. The owner's experiment (private note, not published) settled the fix: give the scorer the specs guide excerpt, the tier's record inventory and the project's primitives, ask it for route, overlaps, alt_score and missing in one JSON line, and gate on route and alt_score.

Outcome after it ships: when the owner records an ADR, a draft that is really a rule, a value or nothing is stopped before it is written as an ADR and routed where it belongs; a real ADR reaches the brief with the cheap options it never weighed listed under «Не взвешено:» and the records it touches under «Задевает:».

Values in play: value/0012 (quality at a rational cost — Opus with the inventory pasted, ≈ 7K tokens in, not repo read access at ×6), value/0002 (the scorer gets the guide excerpt and a one-line-per-record inventory, never the records themselves), value/0015 (the inventory is a slice of many files filled into a prompt, so a CLI produces it), value/0003 (the guide excerpt is pasted from `src/specs/README.md`, not copied into the rubric), value/0010 (an eval suite with labelled fixtures proves routing and missing). No departure from a value or rule.

## Decisions

1. Scorer input = the v3 task text (the rubric file) + the format guide's `## Types` and `## When a record is worth writing` sections + the tier's value/rule/adr inventory + the project's primitives + the draft ADR; Opus, no tools beyond `ListAgents`. (user)
2. Reply = one JSON object on one line: `route` (`adr|rule|value|story|reference|idea|open-item|none`), `route_why` (one sentence), `overlaps` (≤ 3 bare refs), `alt_score` (0–3), `missing` (≤ 3, each naming the existing primitive or record when there is one) — the experiment's prompt v3 text, verbatim. (user)
3. Gate: `route ≠ adr` or `alt_score ≤ 1` blocks; otherwise the brief carries `missing` as «Не взвешено:» and `overlaps` inside «Задевает:». (user)
4. The inventory holds only records that exist when the ADR is written: live, that is every value/rule/adr record of the tier except the draft itself; in eval fixtures, the records whose `created_at` is not after the fixture ADR's. (user)
5. The agent keeps `tools: ListAgents`; its body stops claiming it has no tools. (user)
6. Eval fixtures are booping-only: ADRs deleted on 2026-10-18 recovered from git (0012 → rule, 0013 → none, 0005 → value), the kept 0019/0024/0003, and mutants of 0003/0007/0030/0033 with one cheap option cut. (user)
7. The inventory comes from `booping specs ls`, extended with a repeatable `--type`, `--exclude {ref}` and `--titles` (line `{type}/{NNNN}  {status}  {title}: {summary}`) — extending the existing primitive rather than a new command, and the title keeps the tested `title: summary` shape. (proposal)
8. The inventory's tier is the one the ADR is written to; other tiers stay out, as in the experiment. (proposal)
9. "The project's primitives" are supplied by the driver as prose: one line per command or building block the attached repo's `CLAUDE.md` names, nothing when it names none — only a model reads them, so prose (rule/0025). (proposal)
10. The guide excerpt is the README's two sections verbatim; the excerpt's one extra line (the `open item` bullet) is added to README's `## When a record is worth writing`, so the shipped guide and the scorer's input are the same text. (proposal)
11. `route ≠ adr` blocks the ADR outright: the material is recorded as the routed type instead (a value as an owner draft, `open-item` filed as an item, `none` dropped and reported) — supervised the route and `route_why` are shown to the user first, autonomous it is logged as an agent decision. `alt_score ≤ 1` keeps today's loop: redraft the alternatives from `missing`, at most two rounds, then the brief carries the score as it stands. (proposal)
12. The brief header keeps «оценка альтернатив {alt_score}/3»; «Не взвешено:» is a new line after «Ключевые моменты», omitted when `missing` is empty; `overlaps` refs merge into «Задевает:». (proposal)
13. Eval tiers: smoke asserts zero tool calls and the JSON contract; regress asserts `route` exactly, `alt_score` within ±1 on the kept fixtures, the 0019 < 0003 order on `alt_score`, and, per mutant, an llm-rubric judge that `missing` names the cut option. Eval runs stay advisory, never CI. (proposal)

## Architecture

- `playbooks/specs/guide/prompt.md` `## Record` is the only caller. It assembles the scorer prompt from: the rubric file's text, the two README sections, `booping specs ls --tier {tier} --type value --type rule --type adr --exclude adr/{NNNN} --titles`, the primitives list, the ADR text — all pasted, no paths, under fixed headings.
- `agents/adr-scorer.md` — static body (no render line), reads the five pasted parts and replies per the rubric's contract.
- `playbooks/_agents/adr-scorer/agent_provider.py` mirrors the caller: `config.paste` gains section extraction (`{file}#{heading}`), and per-test vars `inventory` and `primitives` are pasted under the caller's headings, so each fixture carries its own frozen inventory.
- `booping specs ls` stays one command; the flags are additive, default output unchanged.

## Milestones

### M01 — Inventory flags on booping specs ls

sp: 5
depends_on: []

#### Tasks

**Goal:** `booping specs ls` prints a tier's value/rule/adr inventory without the draft, with titles. **Scope:** `booping-python/src/booping/commands/specs.py`, its e2e corpus, `documentation/specs.md`; default output unchanged for every existing caller.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `--type` becomes repeatable (`action="append"`), each value checked as today; `--exclude REF` (repeatable, `{type}/{NNNN}`) drops those records; `--titles` prints `{type}/{NNNN}  {status}  {title}: {summary}`. Help line of `ls` names the `--titles` shape | `booping-python/src/booping/commands/specs.py` | 2 | pending |
| 1.2 | e2e txtar case(s) under the existing specs cases: two types plus an exclude plus `--titles` over a small tier; an unknown type in a repeated `--type` still errors as today | `booping-python/e2e/cases/specs/` | 2 | pending |
| 1.3 | The `specs ls` entry in the public docs names the three flags | `documentation/specs.md` | 1 | pending |

Test surface: the `booping specs ls` CLI; cases — repeated type, exclude, titles line, unknown type; tier — e2e (txtar, integration).

Worker returns: the list of changed files and the Verify exit status.

#### Definition of Done

Task 1.1
- [ ] `booping specs ls --type value --type adr` lists both types, sorted by type then number.
- [ ] `--exclude adr/0003` removes exactly that record; a ref not in the tier is ignored.
- [ ] `--titles` line is `{type}/{NNNN}  {status}  {title}: {summary}`; without it output is byte-identical to today.

Task 1.2
- [ ] New txtar case passes; existing specs cases pass unchanged.

Task 1.3
- [ ] `documentation/specs.md` names `--type` (repeatable), `--exclude`, `--titles` and the titles line shape; no internal churn (rule booping:rule/0008).

#### References

- `booping-python/src/booping/commands/specs.py` `_run_ls` (line ~215) and the `ls` parser (line ~46).
- An existing case in `booping-python/e2e/cases/specs/` for the txtar shape.

#### Verify

`just e2e -k specs`

### M02 — Scorer v3: rubric, agent body, the guide's Record scenario

sp: 10
depends_on: [M01]

#### Tasks

**Goal:** the specs guide scores a draft ADR with the v3 input and reply and gates on route and alt_score; the brief shows «Не взвешено:». **Scope:** `playbooks/specs/guide/adr-rubric.md`, `agents/adr-scorer.md`, `src/specs/README.md`, `playbooks/specs/guide/prompt.md`, the guide's eval fixtures; no other playbook reads the scorer.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Replace the rubric's body with the v3 task text quoted under References, verbatim below an `# ADR scorer task` heading — the text the experiment measured | `playbooks/specs/guide/adr-rubric.md` | 2 | pending |
| 2.2 | Agent body: names the five pasted parts (task, guide excerpt, records, primitives, draft ADR), says it judges from them alone and has no tool to reach anything else, replies with the task's JSON line and nothing else; frontmatter `description` updated to route + alternatives; `tools: ListAgents` and its comment kept | `agents/adr-scorer.md` | 2 | pending |
| 2.3 | Append the `open item` bullet to `## When a record is worth writing`: "**open item** — a piece of work or a question for the owner that must outlive the session (a bug, a feature, a gap between specs and code); not a decision, not a constraint." | `src/specs/README.md` | 1 | pending |
| 2.4 | `## Record` step 1: spawn the scorer with, under fixed headings, the rubric's text, the format guide's `## Types` and `## When a record is worth writing` sections, the output of `booping specs ls --tier {tier} --type value --type rule --type adr --exclude adr/{NNNN} --titles`, the project's primitives (one line per command or building block the attached repo's CLAUDE.md names; none → the heading says so), the ADR's text — text, never paths. Gate per Decisions 11; brief per Decisions 12 (header from `alt_score`, «Не взвешено:» line, `overlaps` refs in «Задевает:») | `playbooks/specs/guide/prompt.md` | 3 | pending |
| 2.5 | The guide's eval fixtures carry a v3 JSON reply in place of `score: 3`; record-adr-brief's canned reply has one `missing` entry and its brief asserts check the «Не взвешено:» line; one new fixture with `route: rule` checks no ADR file is written and the route is shown | `playbooks/specs/guide/_fixtures/record-adr-brief.md`, `playbooks/specs/guide/_fixtures/record-decision.md`, `playbooks/specs/guide/tests.yaml`, new `playbooks/specs/guide/_fixtures/record-adr-routed.md` | 2 | pending |

Test surface: the specs guide step and the scorer agent; cases — v3 reply shape in the brief, «Не взвешено:» rendered, `route: rule` blocks the ADR; tier — the guide's promptfoo suite (smoke + regress), integration of the prompt with canned scorer replies.

Worker returns: the list of changed files and the Verify exit status.

#### Definition of Done

Task 2.1
- [ ] Rubric asks for exactly one JSON line with keys `route`, `route_why`, `overlaps`, `alt_score`, `missing`, the limits ≤ 3 and the route enum `adr|rule|value|story|reference|idea|open-item|none`.
- [ ] No `score:` line contract remains.

Task 2.2
- [ ] Body names the five inputs and the JSON reply; the phrase "you have no tools" is gone; `tools: ListAgents` unchanged.

Task 2.3
- [ ] README section ends with the open item bullet; `just specs-check` clean.

Task 2.4
- [ ] `## Record` names the five pasted parts and the `specs ls` line with `--exclude` of the draft's ref.
- [ ] `route ≠ adr` → no ADR written, material recorded as the routed type per Decisions 11; `alt_score ≤ 1` → redraft from `missing`, at most two rounds.
- [ ] Brief template has «Не взвешено: {missing}» (omitted when empty) and `overlaps` in «Задевает:».
- [ ] `bin/booping render-playbook specs --step guide` renders clean.

Task 2.5
- [ ] No fixture carries `score: N` as a scorer reply.
- [ ] `just smoke specs/guide` passes.

#### References

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

#### Verify

`just smoke specs/guide`

### M03 — Scorer eval suite on v3

sp: 11
depends_on: [M02]

#### Tasks

**Goal:** `playbooks/_agents/adr-scorer/` proves routing, overlaps-free contract, alt_score and missing on booping-only fixtures. **Scope:** the suite directory only.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Provider: a `config.paste` value may be `{file}#{heading}[,{heading}]` and pastes those H2 sections; per-test vars `inventory` and `primitives` are pasted under the headings `## Record` uses, in its order; config preamble and headings mirror `## Record` | `playbooks/_agents/adr-scorer/agent_provider.py`, `playbooks/_agents/adr-scorer/promptfooconfig.yaml` | 2 | pending |
| 3.2 | Fixtures from git: ADRs 0012, 0013, 0005 at `19a984f^`; each fixture's inventory = `bin/booping specs ls --type value --type rule --type adr --titles --exclude adr/{NNNN}` run against a worktree of the commit that holds the ADR, lines whose record `created_at` is after the ADR's dropped; same for the kept 0019/0024/0003; one primitives file from this repo's CLAUDE.md `## Commands` per Decisions 9. A header comment in `tests.yaml` names the commit and the command | `playbooks/_agents/adr-scorer/_fixtures/` | 3 | pending |
| 3.3 | Mutants of 0003, 0007, 0030, 0033: each with one cheap-option row (prose, an existing primitive, or building nothing) cut, and its Context line about it; its inventory as in 3.2; the cut option named in the test's metadata | `playbooks/_agents/adr-scorer/_fixtures/` | 3 | pending |
| 3.4 | Asserts and tests: `contract` (one JSON line, the keys, enum, ≤ 3 lists, `alt_score` 0–3), `route` (exact), `alt_score` (±1), `order` on `alt_score`; smoke = tools + contract on every fixture; regress = route on all, alt_score on the kept, order 0019 < 0003, an llm-rubric judge per mutant "`missing` names {cut option}"; the old `score` check goes | `playbooks/_agents/adr-scorer/asserts.js`, `playbooks/_agents/adr-scorer/tests.yaml` | 3 | pending |

Test surface: the `booping:adr-scorer` agent through the live caller's prompt shape; cases — deleted ADRs route to rule/none/value, kept route to adr, alt_score ±1, order, mutants' missing; tier — promptfoo smoke (deterministic) + regress (llm-rubric), integration against the real agent, no mocks.

Worker returns: the list of changed files, the smoke result line, and whether regress ran.

#### Definition of Done

Task 3.1
- [ ] Provider builds the prompt in `## Record`'s order with the two README sections, the fixture's inventory and primitives; stdlib-only, `call_api` never raises.

Task 3.2
- [ ] Each fixture has its frozen inventory with no record newer than the ADR and without the ADR itself; no fixture or inventory names another project (rule/0033).

Task 3.3
- [ ] Four mutant fixtures, each with exactly one cheap option cut and the cut named in metadata.

Task 3.4
- [ ] No assert parses `score: N`; `just smoke _agents/adr-scorer` passes.

#### References

- `playbooks/_agents/adr-scorer/tests.yaml`, `asserts.js` — today's shape.
- `playbooks/_lib/grader.yaml` — llm-rubric judge config.

#### Verify

`just smoke _agents/adr-scorer`

### M04 — Stale descriptions of scorer v1

sp: 2
depends_on: [M02]

#### Tasks

**Goal:** no shipped text describes the 0–3 `score:` scorer. **Scope:** `CLAUDE.md`, `CHANGELOG.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | CLAUDE.md Layout bullet on `agents/adr-scorer.md`: static body and allowlist kept, "reads nothing beyond its prompt" kept, nothing on the score contract added | `CLAUDE.md` | 1 | pending |
| 4.2 | CHANGELOG unreleased entry: the scorer routes a draft ADR, names what it overlaps and the cheap options it misses; a draft that is not an ADR is routed, «Не взвешено:» joins the brief — user-facing only (booping:rule/0008); the v1 line on this release amended | `CHANGELOG.md` | 1 | pending |

Test surface: none — text only.

Worker returns: the list of changed files.

#### Definition of Done

Task 4.1
- [ ] `git grep -n "score: {0-3}\|score of 1 or less"` over shipped files returns nothing outside `vault/`.

Task 4.2
- [ ] CHANGELOG names routing, «Не взвешено:» and the inventory input; no internal file names.

#### References

- `CHANGELOG.md:10` — the v1 line.

#### Verify

`git grep -n "score: {0-3}" -- ':!vault' ; test $? -eq 1`

## Final Verification

- [ ] `just ci` passes, except `just snapshots` reporting drift in `playbooks/specs/_reports/output.md` limited to the guide step — the owner accepts it.
- [ ] `bin/booping render-playbook specs --step guide` renders clean, no `{{placeholder}}` leaks.
- [ ] `just smoke _agents/adr-scorer` and `just smoke specs/guide` pass; regress run reported, advisory.

## Out of scope

- Re-running the private cross-project experiment.
- Scoring records other than ADRs; cross-tier inventories.
- Any caller of the scorer besides the specs guide's `## Record`.

## CLAUDE.md impact

Layout bullet on `agents/adr-scorer.md` — M04 task 4.1.
