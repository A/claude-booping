# develop playbook

Execute a groomed plan's milestones, delegating coding to `booping-developer` and orchestrating verification, commits, and status transitions on the way to `done`.

Development is a **playbook**, not a skill — driven by [`/playbook`](playbook.md):

```text
/playbook develop
```

## What it does

The playbook walks one plan through `awaiting-approval → ready-for-dev → in-progress → done`. Three outcomes are terminal: `done`, `fail` (the abort branch), and `cancelled` — a run you call off cancels formally from any non-terminal status, not by being abandoned. `done` closes the plan **immediately**: the plan track ends there, with no waiting status after it. Retro runs afterwards as its own track — start it with [`/playbook retro`](retro.md); it, like [code-review](code_review.md), picks the plan up through the `retro:` / `code_reviews:` frontmatter seams, each keeping its own run state in its own artifact, without moving the plan's status again. That vocabulary is develop's own, declared in `playbooks/develop/playbook.yaml`'s `states:` block, not in a shared lifecycle. Run state lives in the plan's own `index.md`, so a stopped sprint is **resumable**.

Five steps, in dependency order:

| Step | What it does |
|------|--------------|
| `intake` | Resolve the plan — one entering at `awaiting-approval` is advanced to `ready-for-dev` without asking, since handing it to develop is the approval — and check the plan against the repo's current shape (drift) |
| `provision` | Pick and confirm the sprint branch, then settle the milestone groups the briefings will cover |
| `develop-loop` | Brief `booping-developer` per group, verify each milestone's DoD, commit as it goes |
| `verify` | Run the project's lint / typecheck / test gates plus the plan's Final Verification |
| `wrap-up` | Closing commit, sprint report, transition to `done` |

The runner edits no application code — all coding is delegated; it owns reads/writes against the vault, briefing assembly, verification, and commits.

Every milestone group runs in **one session** by default. Stopping after each milestone is a request you make at invocation time.

## Starting a run

```text
/playbook develop
/playbook develop — plans/202604301120_src-files-build-pipeline/index.md, pause after each milestone
```

Bare invocation resolves the plan from what the session just groomed or from the vault's queue. Name a plan path to target a specific one. Free-text reaches `intake` verbatim — useful for stop-after-each-milestone or model-comparison runs.

To resume a sprint already `in-progress`, invoke the playbook against the same plan: `playbook-state` reports the frontier and the run picks up at the first milestone whose DoDs are not all `[x]`.

## Branch

`provision` picks the branch prefix from `core.develop_playbook.git.branches` using the plan's `type`, proposes a kebab-case name, and asks through `AskUserQuestion` — **nothing touches git until you answer**, and a name you rewrite is used verbatim. A branch that already exists for the sprint is reused rather than recreated. In multi-repo projects the same branch name is reused across repos unless you say otherwise.

That confirmation is the playbook's single review gate.

## Best practices

### Run code review in a fresh session

Run a [code-review](code_review.md) pass from a **fresh session**, not the one that ran the sprint. It reads the diff and the plan, which runner context does not affect, but the reviewer benefits from a slate free of the sprint's execution traces.

### Try alternative models for implementation

Plans are reproducible files, so the same plan runs with different models — a cheaper or faster model for the implementation pass, Opus for [code-review](code_review.md) afterward. The plan is the controlled input, the diff the controlled output: swap models, compare diffs, calibrate which model gives acceptable quality on your codebase.

### Review the code-review feedback list

The [code-review playbook](code_review.md) puts its findings in front of you and asks for a verdict on each one, then applies what you approved. Rule on the list explicitly:

- **BLOCKER** — must be applied before merge. Trivial fixes happen inline in the review session; non-trivial fixes go back through `booping-developer` via a follow-up briefing.
- **SUGGESTION** — apply if the cost is low; drop it explicitly otherwise. Do not silently drop.
- **NIT** — apply or skip on judgment.

The discipline is the [groom playbook](groom.md)'s for cross-review findings: every BLOCKER addressed, deferrals explicit, no item silently dropped.

## Config

The playbook reads these keys from `src/config.yaml`. See [Project config](project_config.md) for the deep-merge override mechanics; per-project tweaks live in `~/Claude/{project}/config.yaml`.

- **`core.sprint.max_milestones_per_agent`** — maximum consecutive milestones grouped into a single `booping-developer` briefing. Grouping happens only when the milestones share enough context that one agent handling them in sequence is cheaper than a fresh agent per milestone. Default `2`.
- **`core.develop_playbook.git.branches`** — list of `{branch, when}` entries that map plan `type` (or freeform descriptors) to a branch prefix; `provision` picks from this list.
- **`core.develop_playbook.git.commit_message`** — message format string used for in-sprint commits. Override per-project to enforce a different commit shape.
- **`core.develop_playbook.agents`** — the agents the playbook may delegate to, with `good_for` / `bad_for` guidance. `booping-developer` is the implementation channel; `booping-researcher` is reserved for the intake drift spot-check across many plan-named files.
