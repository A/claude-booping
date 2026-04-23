---
name: retro
description: Generate a sprint retrospective by reviewing session logs, gathering user feedback, and comparing plan vs built. Use after /develop reports a sprint DONE, or when the user explicitly asks to retro a plan.
argument-hint: [plan file path(s), space-separated; omit to pick interactively]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git show *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(ls *)
  - Bash(booping-plans *)
  - Agent
  - AskUserQuestion
effort: xhigh
---

# booping — /retro

Produce a retrospective grounded in session logs, code diff, and user feedback — not vibes.

This skill is **wide-domain** — it must work across very different projects. Project-specific concerns live in `_booping/skill_retro.md`, lessons, and the vault `CLAUDE.md`.

## Preflight

- Read and resolve project based on [project resolution principle](../../docs/partial_project_resolution.md).
- Read [plan statuses](../../docs/partial_plan_statuses.md).
- Read [research agents](../../docs/partial_agents_researcher_tiers.md) — researcher-middle is the sole delegation target here.
- Read [plan transitions for /retro](../../docs/partial_plan_transitions_retro.md).
- Read lessons per [read lessons](../../docs/partial_read_lessons.md).
- Read [retrospective template](../../docs/template_retrospective.md) — section spec for Phase 3.
- Read `~/Claude/{project_name}/lessons/` — full lesson set, loaded here for the Phase 3 cross-check.
- Read `~/Claude/{project_name}/_booping/skill_retro.md` if present — project-local overrides and extra instructions.
- Read the attached repo's `CLAUDE.md` — project conventions.

## High-level workflow

1. Intake — resolve `$ARGUMENTS` to 0/1/N plan paths; delegate session-log search.
2. Sprint analysis — read plan(s) + diff + session summary inline.
3. User feedback — targeted `AskUserQuestion` derived from Phase 1 findings.
4. Synthesize — draft using `template_retrospective.md`; run lesson cross-check.
5. Save & transition — write retrospective; apply transitions per `partial_plan_transitions_retro.md`; commit.

---

## Phase 0 Intake

Resolve `$ARGUMENTS` to plan paths.

**0 plans**: Run `booping-plans --status awaiting-retro` to list candidates. Present the list to the user via `AskUserQuestion` with `multiSelect: true`. Proceed once the user selects one or more.

**1 or more plans**: Validate that each plan's `status:` is `awaiting-retro`. On mismatch, STOP with this verbatim error:

> `/retro requires a plan in status 'awaiting-retro'; got '<current-status>' for <plan-path>. Run 'booping-plans --status awaiting-retro' to list candidates.`

Read each plan in full. Compute the combined git diff range (union of each plan's diff range — typically from `started:` to `completed:` across all plans).

Delegate session-log search to `booping-researcher-middle`. Brief: search `~/.claude/projects/` for references to each plan file and sprint topic; return a structured summary of user questions, blockers, and detours. Do not copy raw logs.

## Phase 1 Sprint analysis

The orchestrator performs sprint analysis **inline** — no sub-agent delegation. For each plan, extract:

- Decisions honored vs. deviated (from the plan's Decisions table).
- Tech debt introduced or carried forward.
- Test coverage delivered vs. planned.
- Per-plan business-goal verdict: `success | partial | fail`.

Hold the extracted facts in context for Phases 2–3.

## Phase 2 User feedback

Use `AskUserQuestion` with targeted prompts derived from Phase 1 findings — cite each finding, never ask open-ended "how did it go?". For multi-plan retros, include at least one prompt confirming each plan's goal verdict if Phase 1 left any ambiguous.

## Phase 3 Synthesize

Draft the retrospective using `../../docs/template_retrospective.md` as the section spec. Do not inline the template's body structure — follow its sections as written.

**Lesson cross-check**: For each problem identified in "What went wrong", scan the lesson set loaded at Preflight (from `~/Claude/{project_name}/lessons/`) and any extra instructions in `_booping/skill_retro.md`. No additional load — use only what's in context. Where a loaded rule should have prevented or caught a problem, add an entry under the template's `### Ignored / unapplied lessons` subsection citing the lesson path, the rule, and what happened instead.

Do not generate new candidate lessons — that is `/learn`'s responsibility.

Run the template's inline self-review checklist before Phase 4. Any `no` → fix before proceeding.

## Phase 4 Save & transition

Write the retrospective to `~/Claude/{project_name}/retrospectives/YYYYMMDD-{kebab-title}.md`.

Frontmatter always uses `plans:` as a YAML list (even for a single plan):

```yaml
plans:
  - plans/YYYYMMDD-{kebab-title}.md
date: YYYY-MM-DD
goal_summary: <cross-plan one-liner verdict>
```

Apply the transition per `../../docs/partial_plan_transitions_retro.md` to each plan in `plans:`.

`<retro-basename>` is the retrospective filename (`YYYYMMDD-{kebab-title}.md`); `<plan-basename-N>` is each plan file's basename. Commit the vault:

```bash
cd ~/Claude/{project_name}
git add retrospectives/<retro-basename>.md plans/<plan-basename-1>.md plans/<plan-basename-2>.md ... sprints.md
git commit -m "retro: {kebab-sprint-title}"
```

## What retro does NOT do

- Does **not** extract lessons — that is `/learn`'s responsibility.
- Does **not** generate candidate new lessons.
- Does **not** write a stale-`CLAUDE.md` impact analysis section.
- Does **not** edit any `CLAUDE.md`.
- Does **not** edit `sprints.md` directly — it is regenerated by `/chat`.
- Does **not** transition plans to `done`, `cancelled`, or `fail`.

## Hard rules

- **Orchestrator owns the retrospective write** — never route the synthesis or write through an agent.
- **Retrospective body is project-specific** — no cross-project generalization, no candidate lessons.
- **No blame language** — retrospective content targets decisions and processes, not people.
- **Never edit any `CLAUDE.md` here; never include a stale-`CLAUDE.md` analysis section in the retrospective body.**
