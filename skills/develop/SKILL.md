---
name: develop
description: Execute a groomed plan milestone-by-milestone via sub-agents. Manages sprints.md via booping-plans sync-sprints. Use after /groom produces a plan file that is ready to implement.
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
effort: max
---

# booping — /develop

Execute a plan. **The orchestrator does not edit application code.** Every task — even 1 SP — is delegated to a worker agent.

## Project resolution

Follow [docs/project-scoping.md](../../docs/project-scoping.md). After resolving, read `~/Claude/{project}/_booping/skill_develop.md` if present.

## Arguments

`$ARGUMENTS` — path to a plan file in `~/Claude/{project}/plans/`. If omitted, ask and list recent items with `ls -t ~/Claude/{project}/plans/`.

## Phase 1: Load context

In parallel:

1. Read the plan file. Extract milestones, tasks, decisions, DoD, verify commands.
2. Read **all** files in `~/Claude/{project}/lessons/`. Record each lesson ID you encountered.
3. Read `~/Claude/{project}/CLAUDE.md` and the project's in-repo `CLAUDE.md` if the plan references files in a git repo.
4. Spot-check 2-3 key files named in the plan to detect codebase drift since grooming.

If any lesson conflicts with a decision in the plan, stop and flag it to the user before proceeding.

## Phase 2: Sprint registration

The sprint is registered by the CLI automatically. On pickup (Phase 4 start), `/develop` transitions the plan to `in-progress` and regenerates `sprints.md` via `booping-plans sync-sprints`; that single action registers the sprint. No manual sprints.md edit.

## Phase 2.5: Branch

In the attached repo (not the Claude vault), create a sprint branch before any worker agent writes code:

```bash
cd <repo-path>
git checkout -b <prefix>/<kebab-sprint-title>
```

Prefix by sprint type:

| Plan `type` | Branch prefix |
|-------------|---------------|
| feature        | `feat/` |
| bug            | `fix/` |
| refactoring    | `refactor/` |
| other          | `chore/` |

One branch per sprint. Project-specific prefix overrides (e.g. `hotfix/`) may live in `_booping/skill_develop.md`. Never run worker agents against `main` or `master`.

## Phase 2.6: SP → agent

Before delegating, resolve the agent from the task's SP:

| Task SP | Agent |
|---------|-------|
| 1       | `booping-developer-junior` (haiku) |
| 2–3     | `booping-developer-middle` (sonnet) |
| 4       | `booping-developer-senior` (opus, reasoning high) |
| 5       | **refuse** — kick back to `/groom` for re-decomposition |

## Phase 3: Confirm scope

Present to the user:

- Total SP, milestone list, execution order
- Lessons that will apply (by ID and title)
- Any codebase drift found
- Ask: "Ready to start, or adjust?"

## Phase 4: Execute

### CLI state transitions

**At the start of Phase 4** (before the milestone loop), transition the plan to `in-progress`:

```bash
booping-plans set --project=<P> <plan-path> status=in-progress
booping-plans sync-sprints --project=<P>
```

Do NOT pass `started=...` — the CLI auto-fills it on the `→ in-progress` transition.

**CLI fallback (applies to every `booping-plans` call below):**

- If `booping-plans set --project=<P> ... <key>=<value>` exits non-zero: hand-edit the plan frontmatter to match the intended transition (flip the `status:` field; for transitions that auto-fill dates, also fill the matching date field with today's ISO date). Then print `booping-plans set failed (exit N): <stderr>` verbatim to chat so the user sees the CLI error.
- If `booping-plans sync-sprints --project=<P>` exits non-zero: do NOT hand-edit `sprints.md` — leave it alone. Print `booping-plans sync-sprints failed (exit N): <stderr>` verbatim. The user can re-run the CLI after diagnosing.

---

For each milestone:

1. `TaskCreate` one task per plan task.
2. Delegate to the appropriate worker via the `Agent` tool:
   - `booping-developer-junior` | `booping-developer-middle` | `booping-developer-senior` — pick by SP tier per Phase 2.6 table
   - `booping-techlead` — when a milestone spans multiple concerns and needs coordination

   **Always delegate.** Even for a 1-line config change. The main context should never see the edited file contents.

3. Brief each agent using the canonical header — see [docs/agent-wiring.md](../../docs/agent-wiring.md):

   ```
   project_root: ~/Claude/{project}
   agent_extension: ~/Claude/{project}/_booping/agent_booping-developer.md

   Applicable lessons:
   - lessons/<id>_<title>.md
   - ...

   Milestone/task: <verbatim from plan>
   Decisions that apply: ...
   Files you may touch: ...
   ```

   Filter `Applicable lessons:` by the worker's domain set (`code,tech,all` for developer agents/reviewer). Narrow further by task relevance.

4. When the agent reports completion, verify:
   - Run the milestone's `Verify` command
   - Read the task DoD checkboxes in the plan file — they should now be `[x]`
   - Update the milestone status in the plan file

5. Before moving to the next milestone, spawn `booping-reviewer` on the milestone's diff. Address findings or document them in the plan's Risk register.

6. **Commit on milestone close.** After the reviewer approves and the milestone row is flipped to `done`, commit the work in the attached repo using a Conventional Commits header that matches the sprint branch prefix:

   ```bash
   cd <repo-path>
   git add -A
   git commit -m "<prefix>(<scope>): M<n> <milestone summary>"
   ```

   Example: `feat(events): M2 event-pipeline workflow wrapper`. One commit per milestone minimum — finer-grained commits are fine. Commit message body may reference plan `M2` task IDs.

Parallel milestones (marked as independent in the plan) may run concurrently in separate Agent calls within the same message.

## Phase 5: Finalize

1. Run the plan's `Final Verification` commands.
2. Confirm every DoD checkbox is `[x]` and every milestone status is `done`.
3. Transition the plan to `awaiting-retro` via CLI:

   ```bash
   booping-plans set --project=<P> <plan-path> status=awaiting-retro
   booping-plans sync-sprints --project=<P>
   ```

   Apply the CLI fallback block from Phase 4 if either command exits non-zero. The plan is now in `awaiting-retro` — the terminal state for `/develop`. (`/retro` moves it to `awaiting-learning`; `/learn` moves it to `done`.)

4. Append a row to `~/Claude/{project}/metrics/lesson-hits.md` for every lesson consulted during execution (one row per lesson, with the sprint's plan path and today's date).
5. Commit the vault updates (plan progress marks, regenerated `sprints.md`, `metrics/lesson-hits.md`) to the project vault:

   ```bash
   cd ~/Claude/{project}
   git add -A
   git commit -m "develop: {kebab-sprint-title} awaiting-retro"
   ```

6. Suggest `/retro <plan-path>`.

## Multi-repo sprints

A single sprint may land changes across multiple repos (e.g. aurora-api + aurora-frontend). In that case:

- One sprint row, one branch per repo with the same sprint title.
- The sprint stays `in-progress` until the **last** repo lands. Do not transition to `awaiting-retro` when the first one merges. See [docs/plan-schema.md](../../docs/plan-schema.md) for the full lifecycle.
- Milestone close commits happen in each repo independently; `/develop` tracks them in the plan status table.

## Hard rules

- **Always delegate.** The orchestrator's edits are limited to the plan file (progress marks in milestone tables, plus frontmatter via `booping-plans set`) and `metrics/lesson-hits.md`. Any other file touched in the main context is a bug.
- **No worktree isolation.** Never invoke Agent with `isolation: "worktree"`. This project mounts the main worktree into Docker for tests; a worktree copy cannot run the test suite. Agents work directly in the attached repo on the sprint branch.
- **No scope additions.** If a worker agent suggests "while I'm here, I'd also…", reject and ask the user.
- **Stop on Verify failure.** Diagnose the root cause. Never skip, `xfail`, or monkey-patch a test to make it green. If Verify still fails after two fix attempts, stop and ask the user.
- **Monkey-patch smell.** If a worker reports they needed to monkey-patch a dependency, patch a module attribute at runtime, or add a `mock.patch` in non-test code to get a test green, stop — that is an injection-seam failure. Re-plan the injection before continuing.
- **Flag unexpected test behavior.** If a test passes that you expected to fail, or produces output that contradicts the implementation, stop and investigate. Do not accept "good enough" green.
- **Boy Scout Rule.** Worker agents may fix a small, obviously-broken thing in a file they touch (a typo in a nearby comment, a dead import), but only in files already within the task's scope, and only if the fix is smaller than the task itself. Anything bigger becomes a separate plan.
- **Lessons are load-bearing.** If mid-task you notice a lesson would be violated, stop the agent and re-plan.
