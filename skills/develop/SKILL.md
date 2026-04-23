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
- Read [research agents](../../docs/partial_agents_researchers_delegator.md) — delegate heavy reading to researchers to keep context clean.
- Read [plan transitions for /develop](../../docs/partial_plan_transitions_develop.md) — the only transitions this skill owns.
- Read [agent delegator](../../docs/partial_agent_developers_delegator.md) — the active delegation strategy, including the SP→agent mapping, batching rules, and briefing template.
- Read [project quality checks](../../docs/partial_development_quality_checks.md) — how to detect and run the project's own lint / typecheck / test tooling during the sprint.
- Read lessons per [read lessons](../../docs/partial_read_lessons.md).
- Read `~/Claude/{project_name}/_booping/skill_develop.md` per [extra instructions](../../docs/partial_extra_instructions.md) — silent-skip if absent.
- Read the attached repo's `CLAUDE.md` — project conventions for the code under development.

## High-level workflow

1. Intake — load plan, validate entry status, spot-check codebase.
2. Confirm scope — present SP, milestones, lessons; wait for explicit user go.
3. Branch — create the sprint branch in the attached repo.
4. Execute — transition plan, run the milestone loop.
5. Finalize — Final Verification, transition to `awaiting-retro`, commit vault.

## Phase 0 Intake

Resolve the plan path from `$ARGUMENTS`; if missing, ask and list recent plans with `ls -t ~/Claude/{project_name}/plans/`.

Read the plan file, the vault `CLAUDE.md`, and the repo `CLAUDE.md`. (Lessons are already loaded in Preflight per [read lessons](../../docs/partial_read_lessons.md).) Spot-check 2–3 key files named in the plan to detect codebase drift; delegate to `booping-researcher-middle` when the set is large (see the research-agents partial).

**Validate entry status**: the plan's `status:` must be `ready-for-dev` or `backlog`. Any other status means `/develop` has no claim — stop and report clearly.

Classify the project's quality tooling per [project quality checks](../../docs/partial_development_quality_checks.md): which tools are hook-enforced (let them run naturally at commit time) and which are configured-but-manual (the skill will run them per milestone).

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
2. Build the `Contract:` block before composing any briefing: read the bodies of `../../docs/partial_agents_developer_rules.md`, `../../docs/partial_agents_developer_workflow.md`, and `../../docs/partial_extra_instructions.md`; concatenate them under a `Contract:` heading. Prepend an `Extra instructions file: ~/Claude/{project}/_booping/agent_booping-developer.md` line. Include the resulting block at the top of every `Agent()` call's prompt argument.
3. Group and delegate per the active strategy in [agent delegator](../../docs/partial_agent_developers_delegator.md); use the briefing template from that partial. Always delegate — even a 1-line change.
4. When the worker reports done:
   - Run the milestone's `Verify` command.
   - Run the configured-but-manual quality commands identified in Phase 0 (see [project quality checks](../../docs/partial_development_quality_checks.md)).
   - Flip each completed task's DoD checkboxes in the plan: `- [ ]` → `- [x]`.
   - Flip each task row in the milestone's status table: `pending` → `done`.
5. Delegate a milestone-diff review to a researcher per [research agents](../../docs/partial_agents_researchers_delegator.md). Ask it to read the diff on the sprint branch and return a bulleted summary covering: plan adherence, scope creep, and regression risk. The orchestrator decides what to action; project-specific triage rules, if any, live in `_booping/skill_develop.md`.
6. Flip the milestone status to `done`, then commit in the attached repo: `<prefix>(<scope>): M<n> <summary>`.
7. Report milestone completion to the user with a one-paragraph summary (what shipped, reviewer verdict, any deferred items) before starting the next milestone.

Parallelism: dispatch tasks (within a milestone or across milestones) in parallel `Agent` calls in the same message only when their briefings touch disjoint files/components. The skill judges disjointness from the plan's file lists — no plan marker required. Sequential otherwise. Parallel agents share the sprint branch; never use `isolation: "worktree"` (see Hard rules).

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
