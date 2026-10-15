# project-manager playbook

The manager you talk to about a project: tell it what you want, in as many requests per message as you like, and it files each one as an **open item**, then carries it through groom, develop, an independent code review and the merge — stopping where your autonomy mode says it should.

```text
/playbook project-manager
```

## A session

**Opening.** The manager runs `booping status` and posts its lines as printed, then names what to act on, in this order:

1. runs that finished, failed or were lost and that nobody has acted on yet;
2. items waiting on you, with the file holding their questions;
3. plans at `ready-for-dev` — develop next;
4. finished plans without a code review — review next;
5. open items.

In `supervised` mode it proposes the first action and waits for you; in `autonomous` mode it starts on that list.

**Every message.** Each request in your message becomes one item, filed with `booping items add --source request` — asides included, in your own words, never paraphrased. A message that only answers a question or confirms a gate files nothing. The manager then lists the ids it filed, one line each.

**Working an item.** Each item it takes up is one of four kinds:

| Kind | What happens |
|------|--------------|
| tiny fix | A few lines, obvious from the text: the manager sizes it and works it in a [batch](#batches) — a worker agent makes the changes, the manager checks them, commits each naming its item id and closes the items. |
| plan | Anything with a design choice or more than one sitting: groom, develop, code review, merge — see [Runs](#runs). Several items you framed as one change share one plan. |
| question | You asked something: answered in chat when the repo or vault holds the answer, otherwise filed back to you as a question on the item. |
| decision | You stated a choice: recorded through the [specs playbook](specs_playbook.md) as an ADR or an idea, and the item closed with a reference to that record. |

**Reporting.** After each turn, one line per item it touched:

```text
{id} {title} — {outcome} — {pointer}
```

| outcome | pointer |
|---------|---------|
| `done` | the closing commit's short sha; with a plan, the plan's path |
| `planned` | the plan's path |
| `running` | the run record `runs/{run}.md` |
| `waiting on you` | the question, `open-items/questions/{id}.md#C{n}` |
| `dropped` | the reason it was closed |
| `paused` | the run record `runs/{run}.md`, or `gate closed` when no run started — see [Budget and time window](#budget-and-time-window) |

Then the next action, in one sentence.

## Modes

The mode is the project's `core.autonomy` setting (see [project config](project_config.md)).

- **`supervised`** (default) — two stops: approving the plan, which groom presents in the same session, and the merge. The merge happens only on your explicit yes; "looks good" counts, silence does not.
- **`autonomous`** — nothing stops. The manager settles both itself and logs each choice with `booping defaults add` — in the plan's `defaults.md` once there is a plan — so you can read afterwards what it decided for you.

## Questions on an item

A question the manager cannot settle itself goes on the item, never only in chat: chat names the file, the file keeps the question.

| Command | What it does |
|---------|--------------|
| `booping items ask ID --topic TEXT --question TEXT [--option TEXT]…` | Adds the next question `C{n}` to `open-items/questions/{ID}.md` on an open or planned item, with the candidate answers as options; prints `open-items/questions/{ID}.md#C{n}`. |
| `booping items answer ID C{n} --text TEXT` | Writes your answer verbatim (`--text -` reads stdin) and marks the question answered. |

The file uses the same format as a plan's clarifications: one `## C{n} — {topic} — open|answered` section per question. You can answer by telling the manager — it records your words with `booping items answer` — or by editing the file yourself.

An item with an unanswered question is **waiting on you**. `booping status` adds ` — {n} waiting on you` to its items line, and `booping status items` lists those items under `Waiting on you:` with their question count and file.

## Runs

Planned work runs headless, as registered runs you can follow with `booping status runs`:

- `booping run groom {items} --autonomous` — autonomous mode only; in supervised mode groom runs in the same session, so you can approve the plan there. A groom that parks on a question points you at the plan's `clarifications.md`.
- `booping run develop {plan} --autonomous` — once the plan is `ready-for-dev`, in both modes.
- `booping run code-review {plan} --autonomous` — once develop finishes the plan. The manager commits the fixes the review leaves, reads its findings, and turns an unfixed blocker into a question on the plan's items instead of merging.

One develop or code-review run per checkout at a time — a second item queues until the running one ends; groom runs may overlap. A develop run that fails is reported with its log, never retried silently. Once the manager has acted on a run's outcome it acknowledges it with `booping run ack`, which hides it from `booping status`.

## Budget and time window

An autonomous project spends your Claude subscription while you are away. The **budget gate** keeps it inside the limits you set:

```text
booping budget read    # 5-hour and 7-day usage, when each resets, and where the reading came from
booping budget gate    # allow (exit 0) or pause (exit 3)
```

The reading comes from the newest recent run log — a headless run already streams the subscription's usage — or, when there is none, from a one-line probe call. The gate pauses when:

- the time is outside your window;
- there is no usage reading at all;
- 5-hour or 7-day usage has reached its ceiling;
- the run has spent its own allowance of 7-day usage, counted from the reading it launched with.

A `pause` prints the reason and, when one is known, a second line `resume_after: {YYYY-MM-DD HH:MM}` — the next window start or the usage reset. The thresholds, the window and the probe are `core.budget` in the [project config](project_config.md#corebudget).

**When it runs.** At every `booping run … --autonomous` launch, and before each milestone group of a develop run. A supervised session at your keyboard is never gated.

- A launch that meets a closed gate prints the verdict, starts nothing and exits 3; the manager reports the item `paused` with `gate closed` and keeps it queued.
- A develop run that meets it between milestone groups stops there — never mid-milestone — and its run ends `paused`, recording why, when to resume and the plan's next milestone.

**Paused runs in `booping status`.** `booping status runs --detail` lists every paused run nobody resumed under `Paused:`, with its plan, items, next milestone, reason, resume time and the command that resumes it:

```text
booping run develop {plan} --autonomous
```

Develop picks up from the plan's first unfinished milestone. Once a later run on the same plan exists, the paused one is no longer listed. The manager relaunches a paused run itself on a later turn, once its resume time has passed — or, with none recorded, once the gate allows again.

**A timer.** booping ships no scheduler; point your own at the resume command. A cron line that tries every hour during the night:

```text
0 0-6 * * * cd /path/to/repo && booping run develop {plan} --autonomous
```

Outside the window, or over a ceiling, the launch exits 3 and nothing runs.

## Batches

A tiny fix gets a size when the manager classifies it — its judgement, written onto the item:

```text
booping items size ID SIZE    # SIZE is one of the sizes in core.project_manager_playbook.batch
```

`booping items list` shows it in the `size` column; an item filed before sizes existed simply has none. `booping items batch` packs the open items whose size skips grooming and that wait on no question, in id order, into batches under a story-point cap, one line each:

```text
B1 (8 SP): OI-0002 OI-0004 OI-0006 OI-0007
B2 (1 SP): OI-0009
```

or `no batch: no open item of a direct size`. Each batch passes the [budget gate](#budget-and-time-window), then goes to one worker briefing carrying every item's text; the manager checks the result and commits once per item, naming its id, then closes the items. An unsized item, or one of a size that does not skip grooming, takes the plan route. The sizes, their story points, which sizes skip grooming and the cap are `core.project_manager_playbook.batch` in the [project config](project_config.md#coreproject_manager_playbookbatch).

## Merge, push and deploy

The merge stays local: the branch develop worked on is merged with `git merge --no-ff` into the branch that was checked out when develop started, and nothing is pushed.

Pushing, opening a pull request, deploying or releasing happens only when the project says how. Add a [rule](specs.md) record with `targets: [project-manager]` and a `brief:` naming the step — "after the merge, push `main` to `gh`", "deploy with `just deploy` once merged" — or a runbook record the rule points at.

## Closing an item without a plan

`booping items close ID` closes an open item as `done` — the path a tiny fix, an answered question or a recorded decision takes. `--reason TEXT` says why; `--dropped` closes it without any work done.
