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

The retrospective artifact is the sole output. If the retro surfaces work that belongs in `lessons/` or `_booping/skill_*.md`, the skill records the implication in the retro body and instructs the user to run `/learn` — it does not do that work itself.

This skill is **wide-domain** — it must work across very different projects. Project-specific concerns live in `_booping/skill_retro.md`, lessons, and the vault `CLAUDE.md`.

## Preflight

- Read and resolve project based on [project resolution principle](../../docs/partial_project_resolution.md).
- Read [plan statuses](../../docs/partial_plan_statuses.md).
- Read [research agents](../../docs/partial_agents_researchers_delegator.md) — researcher-middle is the sole delegation target here.
- Read [plan transitions for /retro](../../docs/partial_plan_transitions_retro.md).
- Read lessons per [read lessons](../../docs/partial_read_lessons.md).
- Read [retrospective template](../../docs/template_retrospective.md) — section spec for Phase 4.
- Read `~/Claude/{project_name}/lessons/` — full lesson set, loaded here for the Phase 4 cross-check.
- Read from `~/Claude/{project}/_booping/skill_retro.md`. Silently skip, if file doesn't exist.
- Read the attached repo's `CLAUDE.md` — project conventions.

## High-level workflow

1. Intake — resolve `$ARGUMENTS` to 0/1/N plan paths; delegate session-log search.
2. Initial user feedback — open-ended `AskUserQuestion` before orchestrator analysis.
3. Sprint analysis — read plan(s) + diff + session summary inline, informed by Phase 1 answers.
4. Follow-up feedback — targeted `AskUserQuestion` on gaps Phase 1 did not cover.
5. Synthesize — draft using `template_retrospective.md`; run lesson cross-check.
6. Save & transition — write retrospective; apply transitions per `partial_plan_transitions_retro.md`; commit.

---

## Phase 0 Intake

Resolve `$ARGUMENTS` to plan paths.

**0 plans**: Run `booping-plans --status awaiting-retro` to list candidates. Present the list to the user via `AskUserQuestion` with `multiSelect: true`. Proceed once the user selects one or more.

**1 or more plans**: Validate that each plan's `status:` is `awaiting-retro`. On mismatch, STOP with this verbatim error:

> `/retro requires a plan in status 'awaiting-retro'; got '<current-status>' for <plan-path>. Run 'booping-plans --status awaiting-retro' to list candidates.`

Read each plan in full. Compute the combined git diff range (union of each plan's diff range — typically from `started:` to `completed:` across all plans).

Delegate session-log search to `booping-researcher-middle`. Brief: search `~/.claude/projects/` for references to each plan file and sprint topic; return a structured summary of user questions, blockers, and detours. Do not copy raw logs.

## Phase 1 Initial user feedback

Once plan(s) are selected and read, ask the user for open feedback on the sprint(s) via `AskUserQuestion` — before orchestrator analysis runs. The goal is to capture the user's raw experience (what felt right, what felt wrong, what surprised them) before any findings from the orchestrator can bias the framing.

For a single-plan retro, one open-ended prompt. For a multi-plan retro, one prompt per plan (or one combined prompt if the plans are tightly related). This is the only place in the skill where open-ended prompts are correct — Phase 3 is targeted.

Hold the user's answers in context for Phases 2 and 4. May run in parallel with the session-log researcher from Phase 0.

## Phase 2 Sprint analysis

The orchestrator performs sprint analysis **inline** — no sub-agent delegation. For each plan, extract:

- Decisions honored vs. deviated (from the plan's Decisions table).
- Tech debt introduced or carried forward.
- Test coverage delivered vs. planned.
- Per-plan business-goal verdict: `success | partial | fail`.

Incorporate the user's Phase 1 answers into the analysis — a finding that contradicts user feedback gets a second pass.

Hold the extracted facts in context for Phases 3–4.

## Phase 3 Follow-up feedback

Use `AskUserQuestion` with targeted prompts narrowed to gaps Phase 1 left open — cite each finding, do not repeat the open-ended ask from Phase 1. For multi-plan retros, include at least one prompt confirming each plan's goal verdict if Phase 2 left any ambiguous.

## Phase 4 Synthesize

Draft the retrospective using `../../docs/template_retrospective.md` as the section spec. Do not inline the template's body structure — follow its sections as written.

**Lesson cross-check**: For each problem identified in "What went wrong", scan the lesson set loaded at Preflight (from `~/Claude/{project_name}/lessons/`) and any extra instructions in `_booping/skill_retro.md`. No additional load — use only what's in context. Where a loaded rule should have prevented or caught a problem, add an entry under the template's `### Ignored / unapplied lessons` subsection citing the lesson path, the rule, and what happened instead.

When the synthesis surfaces something that ought to become a new lesson, or a change to an existing `lessons/` or `_booping/skill_*.md` file, record the implication in the retro body and flag `/learn` as the follow-up skill. Do not write or edit those files from within `/retro`.

Run the template's inline self-review checklist before Phase 5. Any `no` → fix before proceeding.

## Phase 5 Save & transition

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

- Does **not** edit `lessons/` or `_booping/skill_*.md`. Implications from retro findings are recorded in the retro body with a `/learn` follow-up; the write belongs to `/learn`.
- Does **not** generate candidate new lessons.
- Does **not** write a stale-`CLAUDE.md` impact analysis section.
- Does **not** edit any `CLAUDE.md`.
- Does **not** edit `sprints.md` directly — it is regenerated by `/chat`.
- Does **not** transition plans to `done`, `cancelled`, or `fail`.

## Hard rules

- **Single output**: the retrospective artifact plus the plan-frontmatter transitions per `partial_plan_transitions_retro.md`. Nothing else written, nothing else edited.
- **Lessons and extensions are out of scope**: updating `lessons/` or `_booping/skill_*.md` as a consequence of retro findings is forbidden. Surface the implication in the retro body and instruct the user to run `/learn`.
- **Orchestrator owns the retrospective write** — never route the synthesis or write through an agent.
- **Retrospective body is project-specific** — no cross-project generalization, no candidate lessons.
- **No blame language** — retrospective content targets decisions and processes, not people.
- **Never edit any `CLAUDE.md` here; never include a stale-`CLAUDE.md` analysis section in the retrospective body.**
