# /develop

Claim a `ready-for-dev` plan and execute its milestones, delegating coding to `booping-developer` and orchestrating verification, commits, and status transitions on the way to `awaiting-retro`.

## What it does

`/develop` walks a plan through `ready-for-dev → in-progress → awaiting-retro`. It claims exactly one plan, picks the right branch from `git.branches`, groups consecutive milestones into agent briefings, runs each briefing through `booping-developer`, verifies milestone DoDs, runs the project's lint / typecheck / test gates at Final Verification, and flips the plan's status when every checkbox is `[x]` and Final Verification is green.

`/develop` does not edit application code from the orchestrator — all coding is delegated. The orchestrator owns reads/writes against the vault, briefing assembly, verification, and commits.

By default `/develop` runs all milestone groups in **one session**. Stopping after each milestone is a user-prompt-level instruction, not default behaviour (see Best practices).

## Command

```text
/develop
/develop plans/20260423-refactor-chat-skill-to-groom-pattern.md
/develop ~/Claude/claude-booping/plans/20260430-src-files-build-pipeline.md pause after each milestone
/develop ~/Claude/claude-booping/plans/20260429-skill-runtime-template-rendering.md re-implement from master, don't toggle todos in the plan
continue to develop plans/20260428-snippet-pre-filter-pipeline.md
```

Bare `/develop` claims the oldest plan in `ready-for-dev`; the queue-empty case is reported and the skill exits — no silent fallback to `in-progress` plans. Pass a plan path (absolute, `~/Claude/...`, or vault-relative) to claim a specific one. Free-text after the path reaches the skill verbatim — useful for stop-after-each-milestone or model-comparison runs.

To resume a plan already in `in-progress` (e.g. after a stopped session), invoke `/develop` with the explicit path; the skill picks up at the first milestone whose DoDs are not all `[x]`. "continue to develop &lt;plan&gt;" works as a natural-language equivalent.

## Best practices

### Run code review in a fresh session

When you want a [/code-review](code_review.md) pass, do it from a **fresh session**, not the same one that ran `/develop`. `/code-review` reads the diff and the plan, which is unaffected by orchestrator context, but the reviewer benefits from a clean slate without any of `/develop`'s execution traces in scope.

### Try alternative models for implementation

Because plans are reproducible files, you can run the same plan with different models — for example use a cheaper or faster model (Sonnet, GLM) for the implementation pass under `/develop`, and reserve Opus for [/code-review](code_review.md) afterward. The plan file is the controlled input; the diff is the controlled output. Swap models, compare diffs, calibrate which model gives you acceptable quality on your codebase.

### Review the code-review feedback list

After `/code-review` produces its findings, work the list explicitly:

- **BLOCKER** — must be applied before merge. Trivial fixes happen inline in the review session; non-trivial fixes go back through `booping-developer` via a follow-up briefing.
- **SUGGESTION** — apply if the cost is low; defer with an explicit one-liner in the plan otherwise. Do not silently drop.
- **NIT** — apply or skip on judgment; no record needed.

Treat the feedback list the same way `/groom` treats Gemini's cross-validation output: every BLOCKER must be addressed, deferrals are explicit, no item is silently dropped.

## Config

`/develop` reads the following keys from `src/config.yaml`. See [Project config](project_config.md) for the deep-merge override mechanics; per-project tweaks live in `~/Claude/{project}/config.yaml`.

- **`sprint.max_milestones_per_agent`** — maximum number of consecutive milestones grouped into a single `booping-developer` briefing. `/develop` only groups when the milestones share enough context that one agent handling them in sequence is cheaper than spinning a fresh agent per milestone; otherwise it stays one milestone per briefing. Default `2`.
- **`git.branches`** — list of `{branch, when}` entries that map plan `type` (or freeform descriptors) to a branch prefix. `/develop` picks the branch prefix from this list before starting work.
- **`git.commit_message`** — conventional-commit format string used for in-plan commits. Override per-project to enforce a different commit shape.
- **`skills.develop.agents`** — the agents `/develop` is allowed to delegate to, with `good_for` / `bad_for` guidance rendered into the skill body. `booping-developer` is the implementation channel; `booping-researcher` is reserved for Phase 0 drift spot-checks across many plan-named files.
