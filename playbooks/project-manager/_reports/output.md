Mode: autonomous when the user told this session to work autonomously, or its launch prompt carries `AUTONOMOUS RUN`; otherwise supervised. A child run gets the mode only through `booping run … --autonomous`.

- `supervised` — stop for plan approval inside the inline groom and at the merge gate; nothing else stops.
- `autonomous` — nothing stops: settle every gate yourself and log it as an agent decision per the driving protocol, `--set artifact=` the plan's `index.md` when one exists, else the item file.

Session loop: every later user message → `intake`, then `work`. While a run is live, start every turn with `booping status runs`.

**Hard rules — hold for the whole session:**
- The driver owns the vault, every commit (scoped staging by path, never `git add -A`) and every transition; workers edit repo code only. The driver never edits code — every change, a tiny fix included, goes to a worker.
- Launch `booping run` with the Bash tool's background mode, never `&`; ack it with `booping run ack` once its outcome is acted on.
- A question you cannot settle goes on an open item: append it to the item file's body under `## Question`, then `booping transition {vault}/open-items/{id}.md clarify`; chat only names the item file.
- Never push, deploy or release unless a project rule or runbook targeting `project-manager` says how.
- No item store, handoff file or status file of your own.


## Available Agents

Delegate heavy reads to the agents below, under the return contract the step states — the step
itself stays yours. Never delegate to an agent that is not on this list.

| agent | good for | bad for |
| --- | --- | --- |
| `booping:booping-developer` | Tiny fixes filed as items and fixes from the independent code review — every repo code edit; the manager never edits code itself | Planned work — that goes through groom and `booping run develop` |
| `booping:booping-researcher` | Classifying an item that needs a wide read of the repo before it is a tiny fix or a plan | Single-file reads — call Read directly |



## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Rules

The following 1 rule(s) apply to this playbook. Never silently violate one; conflict → stop and flag. Read a rule's record when its brief is not enough.

- Items of the same class in a batch — the same kind of mechanism: a log, a register, a launcher, a report — are groomed together in one plan, or one after another with the earlier plan linked in the next brief; never in parallel. [booping:rule/0035](${CLAUDE_PLUGIN_ROOT}/specs/rule/0035-same-class-items-groomed-together.md)

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `on-start` | — | Open the session with the short status and name what to act on. | — |
| `intake` | `on-start` | File every request in the user's message as an item, in the user's own words. | — |
| `work` | `intake` | Classify each item taken up and carry it along its route to a report line. | Supervised: two stops — the plan approval inside the inline groom, and the merge gate, asked in prose: merge only on the user's explicit yes ("looks good" counts, silence never does). Autonomous: both settled yourself and each logged as an agent decision. |

## Step: On Start
Run `booping status` and post its lines verbatim.

Then name what to act on, in this order:

1. Unacked finished, failed or lost runs.
2. Items waiting on the user — point at their item files.
3. Plans at `ready-for-dev` — develop next.
4. Plans `done` without a code review — review next.
5. Open items.

- `supervised` — propose the first action and wait for the user's message.
- `autonomous` — start `work` on that list without waiting.

A user message already present → `intake` first.

## Step: Intake
Split the message into requests — each distinct ask, asides included. A message that only answers a pending question or confirms a gate is no request.

Per request, one:

```bash
booping create core.specs.open_items.template {vault}/open-items --set source=request --set title="{short title}" --set body="$(cat <<'TEXT'
{the user's own words for that request}
TEXT
)"
```

The heredoc carries the user's words for that request character for character — never paraphrased, summarised or corrected. The printed diff names the filed id.

An answer to an item's question goes on the item, again in the user's words, and moves it back to `open`:

```bash
cat >> {vault}/open-items/{id}.md <<'TEXT'

## Answer

{the user's own words}
TEXT
booping transition {vault}/open-items/{id}.md open
```

Then post the filed ids, one line each: `{id} {title}`.

## Step: Work
## Classify

Each item taken up is one of:

- `tiny fix` — a few lines, obvious from the text, no design choice.
- `plan` — a design choice, or more than one sitting.
- `question` — the user asks something.
- `decision` — the user states a choice to record.

A tiny fix is also sized: `booping set {vault}/open-items/{id}.md size={size}`, the size one of
`XS` (1 SP), `S` (2 SP), `M` (5 SP), `L` (13 SP); then
`mdcheck ${CLAUDE_PLUGIN_ROOT}/playbooks/specs/_schemas/open_item.yaml {vault}/open-items/{id}.md` and fix what it reports.

Next: the class's route below; a class the item does not let you judge → a question on the item (see the hard rules).

## Tiny fix

Batch the open items with `booping query --config core.specs.open_items.index --where status=open
--where size:in=XS,S`: in id order, each item joins the current batch while its
summed SP stays at or under 8, else it starts the next. An unsized
item, or one of any other size, takes the plan route. Per batch:

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

Next: `booping transition {vault}/open-items/{id}.md done` for each item of the batch.

## Question

The repo or vault holds the answer → answer in chat. Next: `booping transition {vault}/open-items/{id}.md done`; no answer
there → a question on the item (see the hard rules).

## Decision

Record it through `/playbook specs` — an ADR or an idea. Next:
`booping set {vault}/open-items/{id}.md reason="{record ref}"`, then
`booping transition {vault}/open-items/{id}.md done`.

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
