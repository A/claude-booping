---
id: "05"
title: "project-manager work step \u2014 classify, route, review, merge, report"
sp: 4
status: pending
plan: "plans/202610152006_project-manager-playbook/index.md"
---

# M05: project-manager work step — classify, route, review, merge, report

The `work` step carries each item from classification to the report line, routing by class and by `core.autonomy`.

**Scope**: create `playbooks/project-manager/work/prompt.md` — frontmatter `summary:` and `review_gate:` naming the two supervised stops (the plan approval inside the inline groom; the merge gate — merge only on the user's explicit yes, "looks good" counts, silence never does), stating that autonomous mode settles both and logs each with `booping defaults add`. Body, one short block per class, each ending in its next command (rule/0005):

- **Classify** each item taken up: `tiny fix` (a few lines, obvious from the text, no design choice), `plan` (anything with a design choice or more than one sitting), `question` (the user asks something), `decision` (the user states a choice to record). A class that cannot be judged from the item → `booping items ask`.
- **tiny fix** — brief the worker agent from the preamble's agents table with the item text, verify its change, commit it by path with a conventional message naming the item id, `booping items close {id}`.
- **question** — answer in chat when the repo or vault holds the answer, then `booping items close {id}`; otherwise `booping items ask`.
- **decision** — record it through `/playbook specs` (an ADR or an idea), then `booping items close {id} --reason "{record ref}"`.
- **plan** — one groom per item, or one for several items the user framed as one change. Supervised: drive `/playbook groom` inline in this session with the item ids; autonomous: `booping run groom {ids} --autonomous`. A groom parked at `awaiting-clarification` → point at the plan's `clarifications.md` (supervised: ask its questions in this session; autonomous: leave it parked and report `waiting on you`). At `ready-for-dev` → note `git branch --show-current` (the merge target), then `booping run develop {plan} --autonomous`. When develop ends `done` → `booping run code-review {plan} --autonomous`; when it ends, commit the fixes it left uncommitted (scoped staging) and read the findings in its artefact (`codereviews/{plan-dirname}/{ts}.md`, `## Findings` and `## Verdict`): an unfixed blocker → `booping items ask` on the plan's items (the `booping items list` rows whose `plan` is this plan), no merge. Then the merge gate: supervised asks in prose and waits; autonomous logs the default. Merge: the branch develop left checked out `--no-ff` into the merge target noted at launch, locally, never pushed; the same branch → nothing to merge. A develop `fail` → report it with the run log path, never retry silently.
- **Runs** — one develop or code-review run per checkout at a time: before launching one, `booping status runs --detail`; a `running` develop or code-review row → the item queues until it ends. Groom runs may overlap. A run that ends → act on its outcome, then `booping run ack {id}`.
- **Report** — after each turn's work, one line per item touched, exactly the manager-report content the I/O contract in `index.md` locks, then the next action in one sentence.

Corrections the user makes during the session → `booping correction add` per `booping:rule/0031` with `--target` the plan's `index.md` (no plan → the item file).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Classification and the tiny-fix, question and decision routes. | `playbooks/project-manager/work/prompt.md` | 1 | pending |
| 5.2 | The plan route: groom per mode, develop, code-review, fixes, merge gate, merge. | `playbooks/project-manager/work/prompt.md` | 2 | pending |
| 5.3 | Runs, report and corrections blocks; IA pass (rule/0006) over the three step prompts and the preamble. | `playbooks/project-manager/work/prompt.md`, `playbooks/project-manager/playbook.md`, `playbooks/project-manager/on-start/prompt.md`, `playbooks/project-manager/intake/prompt.md` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] Each of the four classes has one route ending in a named command; none offers two ways to do one thing.

### Task 5.2

- [ ] Every launch is `booping run {groom|develop|code-review} … --autonomous`, except the supervised groom, which is `/playbook groom` inline.
- [ ] Merge is local `--no-ff`, never pushed; push/deploy are left to project rules and runbooks.

### Task 5.3

- [ ] The report block matches the I/O contract's manager-report line word for word in its fields and outcome vocabulary.
- [ ] No sentence in the four files restates another file's or config's content (rule/0006); no motivation or "you are" preamble.

Return: the list of changed and created files, nothing else.

## References

- `playbooks/specs/guide/prompt.md` — scenario blocks, each ending in its next command.
- `src/templates/_partials/_playbook_driving.j2` — how gates and questions behave per `core.autonomy`; do not restate it.
- `vault/adr/0028-one-project-manager.md`, `vault/adr/0027-autonomy-modes.md` — the decisions this step carries.

## Verify

`bin/booping render-playbook project-manager`
