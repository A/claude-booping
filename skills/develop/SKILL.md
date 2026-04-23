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
effort: xhigh
---

# booping — /develop

Execute a plan by delegating every task to a worker agent. The orchestrator never edits application code.

This skill is **wide-domain** — it must work across very different projects. Project-specific concerns (deploy checklists, SP thresholds, stack conventions) live in `_booping/skill_develop.md`, lessons, and the vault `CLAUDE.md`. Do not bake them into this skill.

## Preflight

- Read and resolve project based on [project resolution principle](../../docs/partial_project_resolution.md).
- Read [plan statuses](../../docs/partial_plan_statuses.md).
- Read [research agents](../../docs/partial_agents_researcher_tiers.md) — delegate heavy reading to researchers to keep context clean.
- Read [plan transitions for /develop](../../docs/partial_plan_transitions_develop.md) — the only transitions this skill owns.
- Read [agent delegation](../../docs/partial_develop_agent_delegation.md) — the active SP→agent mapping and batching rules for this skill.
- Read all lessons in `~/Claude/{project_name}/lessons/`.
- Read `~/Claude/{project_name}/_booping/skill_develop.md` — project-local overrides, if present.
- Read the attached repo's `CLAUDE.md` — project conventions for the code under development.

## High-level workflow

1. Intake — load plan, validate entry status, spot-check codebase.
2. Confirm scope — present SP, milestones, lessons; wait for explicit user go.
3. Branch — create the sprint branch in the attached repo.
4. Execute — transition plan, run the milestone loop.
5. Finalize — Final Verification, transition to `awaiting-retro`, commit vault.

## Phase 0 Intake

Resolve the plan path from `$ARGUMENTS`; if missing, ask and list recent plans with `ls -t ~/Claude/{project_name}/plans/`.

Read the plan file, all lessons in `~/Claude/{project_name}/lessons/`, the vault `CLAUDE.md`, and the repo `CLAUDE.md`. Spot-check 2–3 key files named in the plan to detect codebase drift; delegate to `booping-researcher-middle` when the set is large (see the research-agents partial).

**Validate entry status**: the plan's `status:` must be `ready-for-dev` or `backlog`. Any other status means `/develop` has no claim — stop and report clearly.

If any lesson conflicts with a decision in the plan, stop and flag it to the user before proceeding.

## Phase 1 Confirm scope

Present to the user:

- Total SP, milestone list, execution order.
- Applicable lessons by ID and title.
- Drift findings from Phase 0.

Ask: "Ready to start, or adjust?" Wait for explicit confirmation.

## Phase 2 Branch

Create the sprint branch per [branch naming](../../docs/partial_branch_naming.md) before spawning any worker.

## Phase 3 Execute

**Apply the entry transition per [../../docs/partial_plan_transitions_develop.md](../../docs/partial_plan_transitions_develop.md):**
- Picked up from `ready-for-dev`: set `status: in-progress`, `started: <today>`.
- Picked up from `backlog`: set `status: in-progress`, `planned: <today>`, `started: <today>` in the same edit.

For each milestone:

1. `TaskCreate` one task per plan task.
2. Group and delegate per [agent delegation](../../docs/partial_develop_agent_delegation.md). Always delegate — even a 1-line change. Brief each agent using the header documented in [docs/agent-wiring.md](../../docs/agent-wiring.md); do NOT re-embed the template here. Filter `Applicable lessons:` by the worker's domain set (`code`, `tech`, `all` for developer agents).
3. When the worker reports done:
   - Run the milestone's `Verify` command.
   - Flip each completed task's DoD checkboxes in the plan: `- [ ]` → `- [x]`.
   - Flip each task row in the milestone's status table: `pending` → `done`.
4. Spawn `booping-reviewer` on the milestone's diff. Apply **lesson 0003 per-item triage** (S0/S1 fix-now; S2+ defer to Risk register; cap defers at three before promoting to a follow-up stub plan).
5. Flip the milestone status to `done`, then commit in the attached repo: `<prefix>(<scope>): M<n> <summary>`.
6. Report milestone completion to the user with a one-paragraph summary (what shipped, reviewer verdict, any deferred items) before starting the next milestone.

Task-level parallelism: tasks within a milestone are sequential by default. If the plan marks tasks as independent AND the delegation strategy does not batch them, dispatch them in parallel `Agent` calls in the same message.

Parallel milestones (marked independent in the plan) may run concurrently.

## Phase 4 Finalize

1. Run the plan's Final Verification commands.
2. Confirm every DoD checkbox is `[x]` and every milestone status is `done`.
3. Apply the `in-progress → awaiting-retro` transition per [../../docs/partial_plan_transitions_develop.md](../../docs/partial_plan_transitions_develop.md): set `status: awaiting-retro`, `completed: <today>`. Run `booping-plans --status awaiting-retro` to confirm.
4. Append one row per lesson consulted to `~/Claude/{project_name}/metrics/lesson-hits.md` (lesson path + plan path + today's date).
5. Commit the vault updates:

```bash
cd ~/Claude/{project_name}
git add plans/<plan-filename>.md metrics/lesson-hits.md sprints.md
git commit -m "develop: <kebab-sprint-title> awaiting-retro"
```

Suggest `/retro <plan-path>`.

## What develop does NOT do

- Does **not** write application code itself — every task delegates to a worker.
- Does **not** transition plans to `done`, `cancelled`, or `awaiting-learning`. `/retro` moves `awaiting-retro → awaiting-learning`; `/learn` moves to `done`; the user marks `cancelled`.

A sprint may span multiple repos; one branch per repo under the same sprint title; the sprint stays `in-progress` until the last repo lands. Per-project orchestration detail lives in `_booping/skill_develop.md`.

## Hard rules

- **Always delegate.** The orchestrator writes nothing except the plan file (progress marks + frontmatter) and `metrics/lesson-hits.md`. Any other file touched in the main context is a bug.
- **No worktree isolation.** Never invoke `Agent` with `isolation: "worktree"`. Agents work directly in the attached repo on the sprint branch.
- **No scope additions.** If a worker suggests "while I'm here, I'd also…", reject and ask the user.
- **Lessons are load-bearing.** If mid-task you notice a lesson would be violated, stop the agent and re-plan.
