---
name: develop
description: Execute a groomed plan milestone-by-milestone via sub-agents. Use after /groom produces a plan file that is ready to implement.
argument-hint: [plan file path]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
effort: high
---




# booping — /develop

Execute a plan by delegating every task to a worker agent. The orchestrator never edits application code.

## Project Context

!`bin/booping-project-name`

On skill load, report the resolved project context back to the user verbatim so they can see which project and vault the skill is operating on.


## Plan Transitions

This table is the contract: the valid moves and their requirements — `Gates` (must hold before the move) and `On exit` (must be fulfilled when taking the move). Both are strict. When an internal action matches a `When` trigger, verify every `Gate` holds, fulfill every `On exit` requirement, update `status:` to the `To` value, then commit the change to the vault:

```bash
cd ~/Claude/{project}
git add plans/<plan-file>.md   # plus any sibling artifacts written in the same run
git commit -m "<to-status>: <kebab-title>"
```

One commit per transition. Sibling stubs written in the same run go in the same commit.

### `ready-for-dev` — Approved by user. Queued for /develop to claim.

| To | When | Gates | On exit |
|----|------|-------|---------|
| `in-progress` | /develop claims the plan at the start of its execute phase | — | set `started: yyyymmdd hh:mm` |


### `in-progress` — /develop has claimed the plan and is executing milestones.

**Artifacts**
- Code changes per milestone on the sprint branch
- DoD checkboxes flipped to [x] as tasks complete


| To | When | Gates | On exit |
|----|------|-------|---------|
| `awaiting-retro` | All milestones done | Every DoD checkbox marked [x]; Final Verification green | set `completed: yyyymmdd hh:mm`; suggest `/retro <plan-path>` |
| `fail` | Unrecoverable blocker on the same milestone | Two fix attempts documented in the plan; User has approved the abort | set `completed: yyyymmdd hh:mm` |




## Available Agents


### `booping-developer-middle`

**Good for:**
- 1–2 SP tasks; batch related tasks up to ~10 SP combined per briefing
- Mechanical or predictable changes: config edits, simple additions, low-risk refactors


**Bad for:**
- 3+ SP — route to senior
- Design-judgment work — architectural decisions, non-trivial trade-offs
- 5+ SP — refuse, route back to /groom for re-decomposition


### `booping-developer-senior`

**Good for:**
- 3–4 SP tasks — one per briefing (no batching)


**Bad for:**
- 1–2 SP — cost-effective to route to middle
- 5+ SP — refuse, route back to /groom for re-decomposition


### `booping-researcher`

**Good for:**
- Phase 0 drift spot-check: given a large set of plan-named files, determine whether actual file shape matches the plan's assumptions


**Bad for:**
- Milestone-diff review — that stays in the skill
- Single-file reads — call Read directly



## Git

Branches always live in the attached repo. Always ask the user before switching or creating a branch. Branch names use kebab-case (lowercase, hyphenated).

### Branches

| Branch | When |
|--------|------|
| `feat/` | feature |
| `fix/` | bug |
| `refactor/` | refactoring |
| `chore/` | other; tooling, dependency bumps, formatting |


### Commit messages

Format: `<agent>: <plan title> <message>`


## Plan selection

If `$ARGUMENTS` is empty, run `booping-plans --status ready-for-dev` and `booping-plans --status awaiting-plan-review` in parallel, combine the results, and present them to the user via `AskUserQuestion` (single-select) with each entry showing the plan title and its status. Use the selected plan path as the plan for this session. If both lists are empty, stop and tell the user there are no plans ready.

## High-level workflow

1. Intake — load plan, validate entry status, spot-check codebase.
2. Plan groupings — propose batched task groups per milestone, confirm with user.
3. Branch — create the sprint branch in the attached repo.
4. Execute — transition plan, run the milestone loop.
5. Finalize — Final Verification, apply the exit transition, commit vault.

## Phase 0 Intake

Load the plan and the repo `CLAUDE.md`. If the plan was created more than 1h ago, double-check for codebase drift against the files it names.

**Validate entry status**: the plan's `status:` must match an entry transition in the table above. Otherwise stop and report clearly.

## Phase 1 Plan groupings

For each milestone, propose task groupings: tasks **≤ 1 SP** can be batched into a single agent briefing (subject to the agent roster's batching limits). Larger tasks stay one-per-briefing.

Then present total SP, milestone list, execution order, and the proposed groupings. Include any drift findings from Phase 0. Ask the user to confirm (and adjust scope if drift was raised).

## Phase 2 Branch

Decide which branch the sprint goes on (see [Git](#git)) and confirm with the user.

One branch per sprint. In multi-repo projects, reuse the same branch name across repos unless the user asks otherwise.

## Phase 3 Execute

**Apply the entry transition** per the transitions table above.

For each milestone:

1. `TaskCreate` one task per task group from Phase 1.
2. Compose the briefing from task/DoD/Verify.
3. Delegate each group per the agent roster above; always delegate — even a 1-line change.
4. When the worker reports done:
   - Verify developer work.
   - Flip each completed task's DoD checkboxes in the plan: `- [ ]` → `- [x]`.
   - Flip each task row in the milestone's status table: `pending` → `done`.
5. Flip the milestone status to `done`, then commit in the attached repo per the [Git](#git) guide.
6. Report milestone completion to the user with a one-paragraph summary (what shipped, any deferred items) before starting the next milestone.

Within a milestone, run tasks in parallel when their files don't overlap and they don't depend on each other. Otherwise run them sequentially. Don't use worktrees — parallel agents share the sprint branch.

## Phase 4 Finalize

1. Run the plan's Final Verification commands **plus** the project's own lint / typecheck / test commands (see below). Once, at sprint end.
2. Confirm every DoD checkbox is `[x]` and every milestone status is `done`.
3. Apply the `All milestones done` exit transition from the transitions table above; verify with `booping-plans`.
4. Commit the vault updates.

If Final Verification fails, delegate the fix to a worker agent; two failed fix attempts on the same issue trigger the failure exit transition from the transitions table.

### Project quality commands

The project's own lint / typecheck / formatter / test tooling runs once at Phase 4, alongside the plan's Final Verification. If you already know the commands, skip discovery. Otherwise infer them from the repo `CLAUDE.md` or typical signals: `package.json` scripts, `pyproject.toml` / `ruff.toml` / `pyright` config, `Justfile` / `Makefile` targets, `.eslintrc`, `tsconfig.json`, `cargo.toml` dev-dependencies.

## What develop does NOT do

- Does **not** write application code itself — every task delegates to a worker.
- Does **not** accept scope additions — changes are limited to the plan scope.

!`bin/booping-extra-instructions skill_develop.md`
