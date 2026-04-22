---
name: develop
description: Execute a groomed backlog item milestone-by-milestone via sub-agents. Owns sprints.md. Use after /groom produces a backlog file that is ready to implement.
argument-hint: [backlog file path]
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

Execute a backlog item. **The orchestrator does not edit application code.** Every task — even 1 SP — is delegated to a worker agent.

## Project resolution

Follow [docs/project-scoping.md](../../docs/project-scoping.md). After resolving, read `~/Claude/{project}/_booping/skill_develop.md` if present.

## Arguments

`$ARGUMENTS` — path to a backlog file in `~/Claude/{project}/backlog/`. If omitted, ask and list recent items with `ls -t ~/Claude/{project}/backlog/`.

## Phase 1: Load context

In parallel:

1. Read the backlog file. Extract milestones, tasks, decisions, DoD, verify commands.
2. Read **all** files in `~/Claude/{project}/lessons/`. Record each lesson ID you encountered.
3. Read `~/Claude/{project}/CLAUDE.md` and the project's in-repo `CLAUDE.md` if the backlog references files in a git repo.
4. Spot-check 2-3 key files named in the backlog to detect codebase drift since grooming.

If any lesson conflicts with a decision in the backlog, stop and flag it to the user before proceeding.

## Phase 2: Register the sprint

Update `~/Claude/{project}/sprints.md` — append a row if this backlog item is not yet listed, or update its status. Copy the `business_goal:` from the backlog frontmatter verbatim into the Business Goal column.

```markdown
| Goal | Backlog | SP | Status | Business Goal | Goal Status |
|------|---------|----|--------|---------------|-------------|
| ... | backlog/20260421-...md | 18 | IN PROGRESS | ... | |
```

`/develop` is the **only** skill that writes to `sprints.md` (except `/retro` which updates the `Goal Status` column only).

## Phase 2.5: Branch

In the attached repo (not the Claude vault), create a sprint branch before any worker agent writes code:

```bash
cd <repo-path>
git checkout -b <prefix>/<kebab-sprint-title>
```

Prefix by sprint type:

| Backlog `type` | Branch prefix |
|----------------|---------------|
| feature        | `feat/` |
| bug            | `fix/` |
| refactoring    | `refactor/` |
| other          | `chore/` |

One branch per sprint. Project-specific prefix overrides (e.g. `hotfix/`) may live in `_booping/skill_develop.md`. Never run worker agents against `main` or `master`.

## Phase 2.6: SP → agent seniority

Before delegating, resolve seniority from the task's SP:

| Task SP | Agent seniority |
|---------|-----------------|
| 1–2     | middle (briefing flag: `seniority: middle`) |
| 3–4     | senior (briefing flag: `seniority: senior`) |
| 5       | **refuse** — kick back to `/groom` for re-decomposition |

Encode the seniority in the briefing header passed to `booping-be-dev` / `booping-fe-dev`. Workers must read this flag and adjust care level (senior tasks get design-first thought; middle tasks stay mechanical). If/when dedicated `*-middle` / `*-senior` agents are added, route by sub-agent type instead of by briefing flag.

## Phase 3: Confirm scope

Present to the user:

- Total SP, milestone list, execution order
- Lessons that will apply (by ID and title)
- Any codebase drift found
- Ask: "Ready to start, or adjust?"

## Phase 4: Execute

For each milestone:

1. `TaskCreate` one task per backlog-task.
2. Delegate to the appropriate worker via the `Agent` tool:
   - `booping-be-dev` — Python/Django/Rust backend
   - `booping-fe-dev` — React/TypeScript/Leptos frontend
   - `booping-techlead` — coordination when a milestone spans both

   **Always delegate.** Even for a 1-line config change. The main context should never see the edited file contents.

3. Brief each agent using the canonical header — see [docs/agent-wiring.md](../../docs/agent-wiring.md):

   ```
   project_root: ~/Claude/{project}
   agent_extension: ~/Claude/{project}/_booping/agent_<agent-name>.md
   seniority: middle | senior

   Applicable lessons:
   - lessons/<id>_<title>.md
   - ...

   Milestone/task: <verbatim from backlog>
   Decisions that apply: ...
   Files you may touch: ...
   ```

   Filter `Applicable lessons:` by the worker's domain set (`code,tech,all` for be-dev/fe-dev/reviewer). Narrow further by task relevance — a Django-migration lesson doesn't go to a frontend-only task.

4. When the agent reports completion, verify:
   - Run the milestone's `Verify` command
   - Read the task DoD checkboxes in the backlog file — they should now be `[x]`
   - Update the milestone status in the backlog and in `sprints.md`

5. Before moving to the next milestone, spawn `booping-reviewer` on the milestone's diff. Address findings or document them in the backlog's Risk register.

6. **Commit on milestone close.** After the reviewer approves and the milestone row is flipped to `done`, commit the work in the attached repo using a Conventional Commits header that matches the sprint branch prefix:

   ```bash
   cd <repo-path>
   git add -A
   git commit -m "<prefix>(<scope>): M<n> <milestone summary>"
   ```

   Example: `feat(events): M2 event-pipeline workflow wrapper`. One commit per milestone minimum — finer-grained commits are fine. Commit message body may reference backlog `M2` task IDs.

Parallel milestones (marked as independent in the backlog) may run concurrently in separate Agent calls within the same message.

## Phase 5: Finalize

1. Run the backlog's `Final Verification` commands.
2. Confirm every DoD checkbox is `[x]` and every milestone status is `done`.
3. Update `~/Claude/{project}/sprints.md` → status `DONE`.
4. Append a row to `~/Claude/{project}/metrics/lesson-hits.md` for every lesson consulted during execution (one row per lesson, with the sprint's backlog path and today's date).
5. Commit the vault updates (backlog progress marks, `sprints.md`, `metrics/lesson-hits.md`) to the project vault:

   ```bash
   cd ~/Claude/{project}
   git add -A
   git commit -m "develop: {kebab-sprint-title} DONE"
   ```

6. Suggest `/retro <backlog-path>`.

## Multi-repo sprints

A single sprint may land changes across multiple repos (e.g. aurora-api + aurora-frontend). In that case:

- One sprint row, one branch per repo with the same sprint title.
- The sprint stays `IN PROGRESS` until the **last** repo lands. Do not mark `DONE` when the first one merges.
- Milestone close commits happen in each repo independently; `/develop` tracks them in the backlog status table.

## Hard rules

- **Always delegate.** The orchestrator's edits are limited to the backlog file (progress marks), `sprints.md`, and `metrics/lesson-hits.md`. Any other file touched in the main context is a bug.
- **No worktree isolation.** Never invoke Agent with `isolation: "worktree"`. This project mounts the main worktree into Docker for tests; a worktree copy cannot run the test suite. Agents work directly in the attached repo on the sprint branch.
- **No scope additions.** If a worker agent suggests "while I'm here, I'd also…", reject and ask the user.
- **Stop on Verify failure.** Diagnose the root cause. Never skip, `xfail`, or monkey-patch a test to make it green. If Verify still fails after two fix attempts, stop and ask the user.
- **Monkey-patch smell.** If a worker reports they needed to monkey-patch a dependency, patch a module attribute at runtime, or add a `mock.patch` in non-test code to get a test green, stop — that is an injection-seam failure. Re-plan the injection before continuing.
- **Flag unexpected test behavior.** If a test passes that you expected to fail, or produces output that contradicts the implementation, stop and investigate. Do not accept "good enough" green.
- **Boy Scout Rule.** Worker agents may fix a small, obviously-broken thing in a file they touch (a typo in a nearby comment, a dead import), but only in files already within the task's scope, and only if the fix is smaller than the task itself. Anything bigger becomes a separate backlog item.
- **Lessons are load-bearing.** If mid-task you notice a lesson would be violated, stop the agent and re-plan.
