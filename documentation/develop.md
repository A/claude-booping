# develop playbook

Execute a groomed plan's milestones, delegating coding to `booping-developer` and orchestrating verification, commits, and status transitions on the way to `awaiting-retro`.

Development is a **playbook**, not a skill — it is driven by [`/playbook`](playbook.md):

```text
/playbook develop
```

## What it does

The playbook walks one plan through `awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro`. Its run state lives in the plan's own `index.md`, so a stopped sprint is **resumable**.

Five steps, in dependency order:

| Step | What it does |
|------|--------------|
| `intake` | Resolve the plan, capture explicit approval when it entered at `awaiting-plan-review`, and check the plan against the repo's current shape (drift) |
| `provision` | Pick and confirm the sprint branch, then settle the milestone groups the briefings will cover |
| `develop-loop` | Brief `booping-developer` per group, verify each milestone's DoD, commit as it goes |
| `verify` | Run the project's lint / typecheck / test gates plus the plan's Final Verification |
| `wrap-up` | Closing commit, sprint report, transition to `awaiting-retro` |

No application code is edited by the runner — all coding is delegated. The runner owns reads/writes against the vault, briefing assembly, verification, and commits.

By default every milestone group runs in **one session**. Stopping after each milestone is a request you make at invocation time, not default behaviour.

## Starting a run

```text
/playbook develop
/playbook develop — plans/20260430-11-20_src-files-build-pipeline/index.md, pause after each milestone
```

Bare invocation resolves the plan from what the session just groomed or from the vault's queue. Name a plan path to target a specific one. Free-text reaches `intake` verbatim — useful for stop-after-each-milestone or model-comparison runs.

To resume a sprint already in `in-progress` (e.g. after a stopped session), invoke the playbook against the same plan: `playbook-state` reports the frontier and the run picks up at the first milestone whose DoDs are not all `[x]`.

## Branch

`provision` picks the branch prefix from `git.branches` using the plan's `type`, proposes a kebab-case name, and asks through `AskUserQuestion` — **nothing touches git until you answer**, and a name you rewrite is used verbatim. A branch that already exists for the sprint is reused rather than recreated. In multi-repo projects the same branch name is reused across repos unless you say otherwise.

That confirmation is the playbook's single review gate.

## Best practices

### Run code review in a fresh session

When you want a [/code-review](code_review.md) pass, do it from a **fresh session**, not the one that ran the sprint. `/code-review` reads the diff and the plan, which are unaffected by runner context, but the reviewer benefits from a clean slate without the sprint's execution traces in scope.

### Try alternative models for implementation

Because plans are reproducible files, you can run the same plan with different models — a cheaper or faster model for the implementation pass, Opus for [/code-review](code_review.md) afterward. The plan is the controlled input; the diff is the controlled output. Swap models, compare diffs, calibrate which model gives acceptable quality on your codebase.

### Review the code-review feedback list

After `/code-review` produces its findings, work the list explicitly:

- **BLOCKER** — must be applied before merge. Trivial fixes happen inline in the review session; non-trivial fixes go back through `booping-developer` via a follow-up briefing.
- **SUGGESTION** — apply if the cost is low; defer with an explicit one-liner in the plan otherwise. Do not silently drop.
- **NIT** — apply or skip on judgment; no record needed.

Treat the feedback list the way the [groom playbook](groom.md) treats cross-review findings: every BLOCKER is addressed, deferrals are explicit, no item is silently dropped.

## Config

The playbook reads these keys from `src/config.yaml`. See [Project config](project_config.md) for the deep-merge override mechanics; per-project tweaks live in `~/Claude/{project}/config.yaml`.

- **`sprint.max_milestones_per_agent`** — maximum number of consecutive milestones grouped into a single `booping-developer` briefing. Grouping only happens when the milestones share enough context that one agent handling them in sequence is cheaper than spinning a fresh agent per milestone. Default `2`.
- **`git.branches`** — list of `{branch, when}` entries that map plan `type` (or freeform descriptors) to a branch prefix; `provision` picks from this list.
- **`git.commit_message`** — conventional-commit format string used for in-sprint commits. Override per-project to enforce a different commit shape.
- **`skills.develop.agents`** — the agents the playbook may delegate to, with `good_for` / `bad_for` guidance. `booping-developer` is the implementation channel; `booping-researcher` is reserved for the intake drift spot-check across many plan-named files.
