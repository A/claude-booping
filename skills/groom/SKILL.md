---
name: groom
description: Deep-research a feature, bug, or refactor and produce a specified, estimated plan with Definition of Done. Cross-validates architecture with a second model when useful. Use when the user describes a new piece of work that needs to be shaped before implementation.
argument-hint: [task description or issue reference]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash(ls *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(booping-external-llm-call:*)
  - Bash(booping-plans:*)
  - Bash(booping-project-name:*)
  - Bash(booping-sprint-threshold:*)
  - Bash(booping-extra-instructions:*)
  - Bash(booping-lessons:*)
  - Bash(booping-plan-templates:*)
  - Agent
  - AskUserQuestion
  - WebSearch
  - WebFetch
effort: high
---





# booping — /groom

Produces a development plan across domains (backend, frontend, Claude Code skills, CLI tools, etc.) and task types (bugs, features, refactorings, etc.). Plans are written so an agentic tool such as Claude Code can execute them with only the plan file as context.

## Project Context

!`booping-project-name`

On skill load, report the resolved project context back to the user verbatim so they can see which project and vault the skill is operating on.


## Plan Transitions

This table is the contract: the valid moves and their requirements — `Gates` (must hold before the move) and `On exit` (must be fulfilled when taking the move). Both are strict. When an internal action matches a `When` trigger, verify every `Gate` holds, fulfill every `On exit` requirement, update `status:` to the `To` value, then commit the change to the vault:

```bash
cd ~/Claude/{project}
git add plans/<plan-file>.md   # plus any sibling artifacts written in the same run
git commit -m "<to-status>: <kebab-title>"
```

One commit per transition. Sibling stubs written in the same run go in the same commit.

### `backlog` — Parked plan — not actively being worked on. Sibling stubs from split sprints and user-filed ideas not yet in grooming live here.

**Artifacts**
- Plan stub at ~/Claude/{project}/plans/{YYYYMMDD}-{kebab-title}.md (split siblings or parked ideas)


| To | When | Gates | On exit |
|----|------|-------|---------|
| `in-spec` | User asks /groom to shape a parked plan, or /groom is invoked on a fresh request | — | — |
| `cancelled` | User shelves the request before grooming | — | set `completed: yyyymmdd hh:mm` |


### `in-spec` — /groom is actively specifying — researching, designing, drafting the plan.

**Artifacts**
- Plan at ~/Claude/{project}/plans/{YYYYMMDD}-{kebab-title}.md with all milestones, SP estimates, and DoDs
- Sibling stub plans (one per split sprint) under the same plans/ path


| To | When | Gates | On exit |
|----|------|-------|---------|
| `awaiting-plan-review` | Draft is complete and ready to present to the user | Cross-validation run (see [cross-validation](${CLAUDE_PLUGIN_ROOT}/src/docs/cross_validation.md)) — single-file-bug skip acceptable; Every task estimated; any task ≥ redecompose_threshold SP has been re-decomposed | set `planned: yyyymmdd hh:mm` |
| `backlog` | User parks the work mid-grooming to revisit later | — | — |
| `cancelled` | User shelves the work mid-grooming | — | set `completed: yyyymmdd hh:mm` |


### `awaiting-plan-review` — Plan drafted; /groom is presenting to the user and awaiting explicit approval, change request, or cancellation.

| To | When | Gates | On exit |
|----|------|-------|---------|
| `ready-for-dev` | User explicitly approves the plan ('looks good', 'ship it'). Silence does not count. | Explicit user approval captured | — |
| `in-spec` | User requests changes that require re-research or re-design | — | — |
| `cancelled` | User shelves the plan instead of approving | — | set `completed: yyyymmdd hh:mm` |




## Available Agents


### `booping-researcher`

**Good for:**
- Wide read or web search where results must be aggregated outside this skill's context and returned as a summary
- Map blast radius across many files (which modules and integrations a change touches)
- Extract patterns from a corpus too large to read directly (e.g. 'common shapes across 30 test files')
- Verify package versions, image tags, API endpoints, CLI flags against current docs when many sources need to be checked
- Cross-system architecture investigation across multiple repos or services
- Compare framework/library options with deep tradeoff analysis


**Bad for:**
- Small checks — single-file reads, one-off greps, existence checks
- When the information cannot be meaningfully compressed without losing signal the caller needs to decide
- When the skill already needs to read the same few files for other reasons
- When the question fits in a few lines of `ls`/`grep` output



## Plan editing

After modifying any plan's SPs or status, run:

```bash
booping-plans --format=md > ~/Claude/{project}/sprints.md
```


## Task Classification

Pick one. Load the linked doc for the matched type before proceeding.

- **feature** — New user-facing capability. Needs business goal, design, milestones, DoD. [detailed guidance](${CLAUDE_PLUGIN_ROOT}/src/docs/task_feature.md)
- **bug** — Defect — observed behavior diverges from expected. Needs triage, reproduction, root-cause hypothesis, minimal fix, and a regression test. [detailed guidance](${CLAUDE_PLUGIN_ROOT}/src/docs/task_bug.md)
- **refactoring** — Internal structure change with no user-visible behavior change. Needs current-vs-target design, migration steps, and a no-behavior-change DoD. [detailed guidance](${CLAUDE_PLUGIN_ROOT}/src/docs/task_refactoring.md)


## Sprint planning

A plan is estimated as a single sprint — the plan's `sp` field is the sprint total, summed up from milestone SPs, which are summed up from task SPs.

Storypoints measure the **complexity and review burden** of getting a task to a merged, accepted state: design judgment, blast radius, ambiguity, integration surface, and how much careful reading the diff demands. AI does implementation cheaply; this is what remains.

### Scale

| SP | Meaning |
|----|---------|
| 1 | Simple text/config change, no risk |
| 2 | Simple task, predictable, no risk |
| 3 | Medium task, minor risks but predictable overall |
| 4 | Complex task, medium risk, may need small research but clear enough |
| 5 | Research task — developer needs to clarify and decompose further before proceeding |


A task estimated **≥ 5 SP must be re-decomposed** before leaving /groom. Do not promote such a task to `ready-for-dev`.

Group tasks **≤ 1 SP** so /develop can hand a batch to a single agent rather than spinning one agent per trivial change.
### Estimation flow

1. Estimate per task on the 1–5 scale.
2. Sum per milestone; show per-milestone totals alongside per-task estimates.
3. Sum per sprint; show the total before promoting.
4. Ask the user for adjustment before finalizing.

### Split threshold

Split threshold: !`booping-sprint-threshold` SP. This is not a velocity — there is no fixed cadence. It's the point past which a plan is too large to hold together as one coherent iteration. If the total exceeds the threshold, flag it and propose splitting into sibling plans.

Project-specific overrides (different threshold, extra sizing rules) live in `~/Claude/{project}/_booping/skill_groom.md` and take precedence.

## Plan Structure

A plan is a markdown file at `~/Claude/{project}/plans/{YYYYMMDD}-{kebab-title}.md` (date = first-written date). Three parts in order:

### Frontmatter

```yaml
---
title: {{Descriptive Title}}
type: feature | bug | refactoring
status: in-spec                  # active groom runs write directly here; parked ideas and split stubs start in `backlog`
sp: {{total}}
split_from: null                 # sibling stubs only: path to the primary plan this was split from
created: YYYY-MM-DD              # date this file was first written
planned: null                    # set when transitioning in-spec → awaiting-plan-review (draft finalized)
started: null                    # set when transitioning ready-for-dev → in-progress (/develop claims)
completed: null                  # set on terminal transition (done/fail/cancelled) or entry to awaiting-retro
retro: null                      # path to retrospective file, set by /retro
goal: null                       # success | partial | fail — set by /retro
business_goal: ""                # features and refactorings: user/internal-visible outcome
---

```

### Title

Top-level heading matching `title:` from the frontmatter:

```
# {{Descriptive Title}}
```

### Body + Quality Checklist

Pick a plan template whose name + description matches the dominant surface of the work. Each template is one file with two top-level sections:

- `# Plan Body` — the structure to follow while drafting the plan.
- `# Quality Checklist` — the rules the plan must pass before moving out of `in-spec`.

Read the selected template, write the plan against its `# Plan Body`, then verify against its `# Quality Checklist`.

!`booping-plan-templates`


!`booping-lessons`

## Craft

Groom produces a specified, estimated, user-reviewed plan. The transitions table governs *when* each step is required; this list is *what* must be performed.

- **Challenge scope**: ask upfront what new components, dependencies, APIs, or workflow changes this likely needs.
- **Review the codebase**: map the blast radius — files, modules, integrations, external surfaces; check prior art.
- **Research when uncertain**: for complex, novel, or non-obvious work, search the web for current best practices, competing approaches, and known pitfalls before locking design decisions.
- **Verify external references**: every package version, image tag, API endpoint, CLI flag, or config option named in the plan is checked against current docs. Never assume.
- **Draft design with the user**: architecture, pattern choices, data / API / config surface changes, open trade-offs. Iterate until aligned before writing.
- **Write the plan**: pick a plan template from [Plan Structure](#plan-structure) whose name + description matches the work, then produce the plan against its `# Plan Body`.
- **Present and iterate**: show approach summary, milestones, SP totals, plan file path. Ask *"Ready for development, or want changes?"* Iterate on changes until the user explicitly approves.

## Hard rules

- The orchestrator never edits files outside `{project}/plans/`.
- Each milestone executable in a fresh session with only the plan as context.
- User approval is **explicit** — "looks good" is enough; silence is not.

## What groom does NOT do

- Does **not** start implementation — even tempting 1-SP items.
- Does **not** duplicate lesson content. Reference lessons by ID.

!`booping-extra-instructions skill_groom.md`
