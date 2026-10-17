---
summary: Classify each item taken up and carry it along its route to a report line.
review_gate: "Supervised: two stops — the plan approval inside the inline groom, and the merge gate, asked in prose: merge only on the user's explicit yes (\"looks good\" counts, silence never does). Autonomous: both settled yourself and each logged as an agent decision."
---

## Classify

Each item taken up is one of:

- `tiny fix` — a few lines, obvious from the text, no design choice.
- `plan` — a design choice, or more than one sitting.
- `question` — the user asks something.
- `decision` — the user states a choice to record.

A tiny fix is also sized: `booping items size {id} {size}`, one of the sizes
`booping config core.project_manager_playbook.batch` lists.

Next: the class's route below; a class the item does not let you judge → a question on the item (see the hard rules).

## Tiny fix

`booping items batch` prints one line per batch; an item it leaves out takes the plan route. Per
batch line:

1. Brief the worker from the agents table, exactly this block:

   ```markdown
   ## Task

   Fix the items below. Leave the work uncommitted.

   ## Item {id}

   {the item's text, verbatim from its item file}

   ## Return

   Per item: the files touched and its check's verdict, nothing else.
   ```

   One `## Item {id}` block per item in the batch, in the batch's order.
2. Verify each item's change; commit each by path with a conventional message naming its id.

Next: `booping items close {id}` for each item of the batch.

## Question

The repo or vault holds the answer → answer in chat. Next: `booping items close {id}`; no answer
there → a question on the item (see the hard rules).

## Decision

Record it through `/playbook specs` — an ADR or an idea. Next:
`booping items close {id} --reason "{record ref}"`.

## Plan

One groom per item, or one for several items the user framed as one change.

1. Groom — supervised: `/playbook groom {ids}` inline in this session; autonomous:
   `booping run groom {ids} --autonomous`.
2. Parked at `awaiting-clarification` → the plan's `clarifications.md`. Supervised: ask its
   questions in this session; autonomous: leave it parked, report `waiting on you`.
3. At `ready-for-dev` → note `git branch --show-current` as the merge target, then
   `booping run develop {plan} --autonomous`.
4. Develop ends `fail` → report it with the run log path; never retry silently. Ends `done` →
   `booping run code-review {plan} --autonomous`.
5. Review ends → commit the fixes it left uncommitted (scoped staging), then read `## Findings` and
   `## Verdict` in its artefact, `codereviews/{plan-dirname}/{ts}.md`. An unfixed blocker →
   report the plan's items `waiting on you`, the blocker as the pointer; no merge.
6. Merge gate (the review gate above). Supervised: list first, numbered, every decision the
   autonomous runs settled — each row of `booping query --config core.agent_decisions.open`
   — one plain line each, marked `(proposal)`; once the user answers, mark each listed file
   with `booping set {vault}/{path} state=reviewed`.
7. Merge the branch develop left checked out into the merge target with `git merge --no-ff`,
   locally, never pushed; develop left the merge target itself checked out → nothing to merge.

Next: the report line for each of the plan's items.

## Runs

One develop or code-review run per checkout at a time; groom runs may overlap. Before launching
one: `booping status runs --detail` — a `running` develop or code-review row → the item queues
until it ends. A run that ends → act on its outcome. Next: `booping run ack {id}`.

## Report

After each turn's work, one line per item touched:

`{id} {title} — {outcome} — {pointer}`

| outcome | pointer |
|---|---|
| `done` | the closing commit's short sha; with a plan, the plan's vault path |
| `planned` | the plan's vault path |
| `running` | the run record `runs/{run}.md` |
| `waiting on you` | the item file `open-items/{id}.md`, or the review's blocker |
| `dropped` | the close reason |

Next: the next action, in one sentence.

## Corrections

A correction from the user → a correction file per `booping:rule/0031`, `--set artifact=` the
plan's `index.md`, or the item file when there is no plan.
