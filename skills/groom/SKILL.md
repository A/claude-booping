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
  - Bash(booping-validate-plan:*)
  - Bash(booping-plans:*)
  - Agent
  - AskUserQuestion
  - WebSearch
  - WebFetch
effort: xhigh
---

# booping — /groom

Produce a plan that a fresh agent can execute with only the plan file as context.

This skill is **wide-domain** — it must work across very different projects (backends, frontends, content sites, CLIs). Project-specific concerns (frameworks, stack patterns, SOLID enforcement, lint/test commands, etc.) live in lessons, `CLAUDE.md`, and `_booping/skill_groom.md`. Do **not** bake them into this skill.

## Preflight

- Read and resolve project based on [project resolution principle](../../docs/partial_project_resolution.md).
- Read [plan statuses](../../docs/partial_plan_statuses.md).
- Classify the task per [task classification](../../docs/partial_task_classification.md) — ask the user or infer with confirmation.
  Read detailed guidance when you understand which task type user is planning.
- Read [research agents](../../docs/partial_agents_researchers_delegator.md) — delegate research to researchers to keep this skill's context clean.
- Read [sprint planning](../../docs/partial_sprint_planning.md) — full estimation framework: scale, totals, sizing thresholds, defensive buffer.
- Read `~/Claude/{project_name}/_booping/skill_groom.md` per [extra instructions](../../docs/partial_extra_instructions.md) — silent-skip if absent.
- Read lessons per [read lessons](../../docs/partial_read_lessons.md).
- Read [plan transitions for /groom](../../docs/partial_plan_transitions_groom.md) for the valid transitions and how to apply them.

## High-level workflow

1. Save the user request.
2. Build the plan (Phase 1 understand → Phase 2 design → Phase 3 write).
3. The plan is born in `status: backlog`.
4. Validate the plan.
5. Show plan to user, gather feedback, iterate.
6. On **explicit** user confirmation: transition to `ready-for-dev`. If user shelves the work: transition to `cancelled`. Otherwise stays in `backlog` for further iteration.

---

## Phase 0 — Save the user request

Write the request to `~/Claude/{project_name}/requests/{YYYYMMDD}-{kebab-title}.md` using the [user request template](../../docs/template_user_request.md). The body is a compact summary of what the user asked for. If the user re-scopes during planning, update this file so it reflects the agreed intent. The `plan:` field is filled in Phase 3 once the plan file exists.

## Phase 1 — Understand

Before drafting anything, build the picture:

- **Ask upfront**: *"What new components, dependencies, APIs, or workflow changes will this likely require?"* Use the answer to scope research. Project-specific framings (e.g. registries / builders / harnesses for codebases that have those) live in `_booping/skill_groom.md` and stack on top of this generic question.
- **Map the blast radius**: which files, modules, integrations, and external surfaces will change. Delegate the codebase read to a researcher (default `booping-researcher-middle`).
- **Check for prior art**: existing patterns to reuse. Researcher returns paths + brief descriptions, not full file dumps.
- **Re-read constraints**: the relevant `CLAUDE.md` sections, project extensions, and applicable lessons.
- **Verify external references**: any package version, image tag, API endpoint, CLI flag, or config option named in the plan must be verified against current docs. Delegate to a researcher with web access. Never assume — always verify.

## Phase 2 — Design

Present design decisions to the user **before** writing the plan file:

- Architecture: how the change fits in; integration points.
- Pattern choices and rejected alternatives.
- Data / API / config surface changes.
- Open trade-offs you can't decide alone.

Wait for user feedback. Iterate on the design until aligned. Only then write the plan.

## Phase 3 — Write the plan

Write to `~/Claude/{project_name}/plans/{YYYYMMDD}-{kebab-title}.md` using the [plan template](../../docs/template_plan.md).

- Initial frontmatter sets `status: backlog` and `source: requests/{YYYYMMDD}-{kebab-title}.md`.

**After the plan file exists**, set the request file's `plan:` field to `plans/{YYYYMMDD}-{kebab-title}.md`. This closes the cross-reference: plan → request via `source:`, request → plan via `plan:`.

Each milestone must:

- Be executable in a fresh session with only the plan file as context.
- List exact files to touch, per task.
- Carry a verifiable DoD with checkboxes.
- Reference applicable lessons by ID — never duplicate lesson content into the plan.

Apply the [sprint planning](../../docs/partial_sprint_planning.md) framework to estimate, total, and size the sprint. If the threshold check suggests splitting, follow [Split into sibling sprints](#split-into-sibling-sprints).

### Split into sibling sprints

When a request maps to multiple sprints, write one fully-spec'd primary plan + lightweight stubs for the others.

For each stub:

1. Filename: `plans/{YYYYMMDD}-{kebab-stub-title}.md` (same date convention).
2. Write via the Write tool with a Context-only body (≤200 words: what the stub is about, why it was split off, what is NOT in scope) and frontmatter:

```yaml
---
title: {{Stub Title}}
type: {{feature|bug|refactoring}}
status: backlog
source: split-from:plans/<primary-plan-filename>.md
created: YYYY-MM-DD
---
```

No `sp`, no `planned` — stubs are parked drafts, not committed work.

## Phase 4 — Validate

Run the quality checklist before showing the plan to the user. Run cross-validation too unless its own rules say to skip (e.g. single-file bugs).

### Quality checklist

Run [quality checklist](../../docs/partial_plan_quality_checklist.md). Fix every violation before showing the plan.

### Cross-validation (Gemini)

See [cross-validation](../../docs/partial_cross_validation.md).

## Phase 5 — Present to user

Show:

1. Brief approach summary.
2. Milestone overview.
3. SP per milestone and total.
4. Final plan file path.
5. Ask: *"Ready for development, or want changes?"*

Iterate on plan edits until the user explicitly confirms.

## Phase 6 — Acceptance

On **explicit** user confirmation, apply the appropriate transition per [plan transitions for /groom](../../docs/partial_plan_transitions_groom.md). Then commit all artifacts written during this groom run:

```bash
cd ~/Claude/{project}
git add requests/{YYYYMMDD}-{kebab-title}.md plans/{YYYYMMDD}-*.md
git commit -m "plans: {kebab-title}"
```

The `plans/{YYYYMMDD}-*.md` glob picks up the primary plan plus any sibling stubs written in the same run. One commit per groom run.

## What groom does NOT do

- Does **not** start implementation — even tempting 1-SP items.
- Does **not** duplicate lesson content. Reference by ID: `Applies lesson: 0007_no-mocked-db`.
- Does **not** bake project-specific patterns, framework rules, or stack details into this skill. Those live in `_booping/skill_groom.md`, lessons, and `CLAUDE.md`.

## Hard rules

- The orchestrator never edits files outside `~/Claude/{project}/requests/` and `~/Claude/{project}/plans/`.
- Every task in a milestone lists exact files and a DoD with checkboxes.
- No "TBD", "handle edge cases", "TODO", or task spanning unrelated concerns.
- Each milestone executable in a fresh session with only the plan as context.
- External references (versions, tags, endpoints) must be verified against current docs — never assume.
- User confirmation for `ready-for-dev` must be **explicit**. "Looks good" is enough; silence is not.
