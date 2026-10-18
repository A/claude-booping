# project-manager playbook

The manager you talk to about a project: tell it what you want, in as many requests per message as you like, and it files each one as an **open item**, then carries it through groom, develop, an independent code review and the merge — stopping where its mode says it should.

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

**Every message.** Only what must outlive the session becomes an item — work for later, or a question waiting on you — filed in your own words, never paraphrased. An instruction for this session ("ping me when the release is out", "pause for two hours"), an answer to a question or a gate confirmation files nothing and is handled in the session; a standing policy becomes a rule and a decision an ADR, through the `specs` playbook. The manager then lists the items it filed, one line each with its title: `Created OI-0007: {title}`, in your language.

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
| `waiting on you` | the item file `open-items/{id}.md`, or the review's blocker |
| `dropped` | the reason it was closed |

Then the next action, in one sentence.

## Modes

The manager is autonomous when you tell it to work autonomously; otherwise it is supervised (see [supervised and autonomous runs](playbook.md#supervised-and-autonomous-runs)). It passes the mode on to the runs it launches only through `booping run … --autonomous`.

- **`supervised`** (default) — two stops: approving the plan, which groom presents in the same session, and the merge. The merge happens only on your explicit yes; "looks good" counts, silence does not.
- **`autonomous`** — nothing stops. The manager settles both itself and logs each choice as one file under the vault's `agent-decisions/`, so you can read afterwards what it decided for you. In a supervised session the merge gate lists the `open` ones and marks them `reviewed` once you answer.

## Questions on an item

A question the manager cannot settle itself goes on the item, never only in chat: chat names the item file, the file keeps the question. The manager appends it to the item's body under `## Question` and moves the item to `clarify` with `booping transition {vault}/open-items/{ID}.md clarify`.

You answer by telling the manager — it appends your words verbatim under `## Answer` and moves the item back to `open` — or by editing the file and making the same transition yourself.

An item in `clarify` is **waiting on you**. `booping status` adds ` — {n} waiting on you` to its items line, and `booping status items` lists those items under `Waiting on you:`.

## Runs

Planned work runs headless, as registered runs you can follow with `booping status runs`:

- `booping run groom {items} --autonomous` — autonomous mode only; in supervised mode groom runs in the same session, so you can approve the plan there. A groom that parks on a question points you at the plan's `clarifications.md`.
- `booping run develop {plan} --autonomous` — once the plan is `ready-for-dev`, in both modes.
- `booping run code-review {plan} --autonomous` — once develop finishes the plan. The manager commits the fixes the review leaves, reads its findings, and turns an unfixed blocker into a question on the plan's items instead of merging.

One develop or code-review run per checkout at a time — a second item queues until the running one ends; groom runs may overlap. A develop run that fails is reported with its log, never retried silently. Once the manager has acted on a run's outcome it acknowledges it with `booping run ack`, which hides it from `booping status`.

## Batches

A tiny fix gets a size when the manager classifies it — its judgement, written onto the item:

```text
booping set {vault}/open-items/ID.md size=SIZE    # one of the sizes in core.project_manager_playbook.batch
```

`mdcheck playbooks/specs/_schemas/open_item.yaml` rejects any other size, and `booping query --config core.specs.open_items.index` shows it in the `size` column; an item filed before sizes existed simply has none. The manager then packs the open items whose size skips grooming, listed with `booping query`, in id order into batches under a story-point cap: each item joins the current batch while its summed points stay within the cap, else it starts the next. Each batch goes to one worker briefing carrying every item's text; the manager checks the result and commits once per item, naming its id, then closes the items. An unsized item, or one of a size that does not skip grooming, takes the plan route. The sizes, their story points, which sizes skip grooming and the cap are `core.project_manager_playbook.batch` in the [project config](project_config.md#coreproject_manager_playbookbatch).

## Merge, push and deploy

The merge stays local: the branch develop worked on is merged with `git merge --no-ff` into the branch that was checked out when develop started, and nothing is pushed.

Pushing, opening a pull request, deploying or releasing happens only when the project says how. Add a [rule](specs.md) record with `targets: [project-manager]` and a `brief:` naming the step — "after the merge, push `main` to `gh`", "deploy with `just deploy` once merged" — or a runbook record the rule points at.

## Closing an item without a plan

`booping transition {vault}/open-items/ID.md done` closes an open item — the path a tiny fix, an answered question or a recorded decision takes; `dropped` instead closes it without any work done. `booping set {vault}/open-items/ID.md reason=…` beforehand says why.
