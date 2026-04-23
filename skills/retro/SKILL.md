---
name: retro
description: Generate a sprint retrospective by reviewing session logs, gathering user feedback, and comparing plan vs built. Use after /develop reports a sprint DONE, or when the user explicitly asks to retro a plan.
argument-hint: [plan file path]
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
  - WebSearch
effort: xhigh
---

# booping — /retro

Produce a retrospective grounded in session logs, code diff, and user feedback — not vibes.

## Project resolution

Follow [docs/partial_project_resolution.md](../../docs/partial_project_resolution.md). After resolving, read `~/Claude/{project}/_booping/skill_retro.md` if present.

## Arguments

`$ARGUMENTS` — plan file path for the sprint being reviewed. If omitted, ask; default to the most recent `awaiting-retro` plan (find it via `booping-plans list --project=<P> --status=awaiting-retro`).

## Phase 1: Session research

Delegate to `booping-teamlead`:

> Search session logs for references to `plans/<file>` or the sprint's topic. Summarize what the user asked about, what blocked them, and any tinkering / detours. Return a structured summary — do not copy raw logs.

The teamlead reads session data from wherever it's stored on this machine (typically `~/.claude/projects/`) and returns a concise findings report.

## Phase 2: Tech, product, QA feedback (parallel)

In a single message, spawn three agents in parallel using the canonical briefing header — see [docs/agent-wiring.md](../../docs/agent-wiring.md):

- `booping-techlead` — compare the code diff against the plan's Decisions. Flag execution gaps, shortcuts taken, and tech debt introduced.
- `booping-product-manager` — verify the business goal was met. If not, why: deprioritized, discovered infeasible, partial?
- `booping-qa-lead` — verify testing strategy was executed. Any missing regression coverage, skipped test cases, or shortcuts?

Each returns a short findings doc. Include under `Applicable lessons:` only the lessons relevant to each agent's role — a SOLID lesson does not go to the product manager.

## Phase 3: User feedback

`booping-teamlead` asks the user targeted questions derived from the three reports above (not open-ended "how did it go?"). Examples:

- "Techlead flagged that migration X skipped the off-peak rollout pattern we discussed in grooming — was that a deliberate choice?"
- "QA lead noted no regression test for the fallback path. Do you want that captured as a lesson or a follow-up task?"

Use `AskUserQuestion` to gather answers.

## Phase 3.5: CLAUDE.md impact review

Before synthesizing the retro, the teamlead asks the three role agents one extra question:

> "Did this sprint introduce a registry/builder/harness, change a public data shape, or relocate a 'how to add X' procedure? If yes, name the exact section of `~/Claude/{project}/CLAUDE.md` (or the in-repo `CLAUDE.md`) that's now stale and what it should say."

Capture the answers in the retrospective's **CLAUDE.md impact** section (new; see below). This is **analysis only** — do not edit any CLAUDE.md file here. `/learn` handles the actual edit with user confirmation.

## Phase 4: Synthesize

`booping-teamlead` merges findings + user feedback into the retrospective document. Structure:

```markdown
---
plan: plans/YYYYMMDD-title.md
date: YYYY-MM-DD
---

# Retrospective: {{title}}

## What went well
...

## What went wrong
### {{Issue}}
**What happened**: ...
**Why**: ...
**Impact**: ...

## Root causes
...

## Action items
| # | Action | Owner | Status |
|---|--------|-------|--------|

## Takeaways
...

## Lessons review
### Existing lessons that applied
- `lessons/0007_...md` — followed / violated (why)

### Candidate new lessons
- ...

## CLAUDE.md impact
- `~/Claude/{project}/CLAUDE.md` — section "X" is stale because ...; should say ...
- `<repo>/CLAUDE.md` — ...
- (or) None required.
```

The `plan:` field holds the project-relative path to the plan file (e.g. `plans/20260422-plans-as-data-refactor.md`).

## Phase 4.5: Self-review

Before saving, the teamlead runs this checklist against the draft. Any `no` → fix before Phase 5.

- [ ] Every "what went wrong" item traces to a specific cause (plan decision, blind spot, carried debt — not "we should have tried harder")
- [ ] Root causes are **patterns**, not restatements of individual issues
- [ ] Action items are specific and actionable (owner + concrete next step — not "improve testing")
- [ ] Takeaways are heuristics a developer could apply next sprint (not platitudes)
- [ ] "What went well" is honest — not inflated to balance criticism
- [ ] No blame language — decisions and processes, not people
- [ ] Lessons review section is present and cross-references existing lesson file paths
- [ ] CLAUDE.md impact section is present — either concrete stale sections or explicit "None required"
- [ ] `goal` field set in the plan frontmatter (via manual edit) matches the action-item / root-cause narrative (success | partial | fail)

## Phase 5: Save & commit

1. Write to `~/Claude/{project}/retrospectives/YYYYMMDD-{kebab-title}.md`.
2. Transition the plan to `awaiting-learning` via a manual frontmatter edit (see [plan transitions for /retro](../../docs/partial_plan_transitions_retro.md)).

   The `goal` value reflects the PM's verdict on the business goal — see [docs/plan-schema.md](../../docs/plan-schema.md) for the enum definition.

3. Commit:

   ```bash
   cd ~/Claude/{project}
   git add retrospectives/YYYYMMDD-{kebab-title}.md plans/YYYYMMDD-{kebab-title}.md sprints.md  # sprints.md is the regenerated rollup
   git commit -m "retro: {kebab-sprint-title}"
   ```

4. Suggest `/learn <retro-path>` to extract lessons and apply the CLAUDE.md impact edits.

## Anti-patterns to avoid

- **Vague praise**: "Good teamwork" tells you nothing. Be specific: "ModelRef round-trip parsing works correctly for all 30+ model strings."
- **Blame**: "X should have done Y" focuses on people. Reframe as "the decision at grooming time to defer Y produced Z."
- **Laundry lists**: Don't enumerate every small issue. Group into themes and root causes.
- **Missing the systemic**: Individual bugs are implementation; *patterns* that produce bugs are retrospective material.
- **Happy-path retros**: If the tech lead gave substantial feedback, the retro should reflect that honestly.
- **Generic takeaways**: "Write more tests" is useless. "Add an injection-seam check to the grooming quality checklist" is actionable.

## Hard rules

- The orchestrator never writes the retro body itself — the teamlead agent does, based on the other agents' reports.
- Never inflate "What went well" to balance criticism.
- Never use blame language. Focus on decisions and processes.
- Do not hand-edit `sprints.md`. It is regenerated by /chat via `booping-plans --format=md`; plan status transitions are manual frontmatter edits per [plan transitions for /retro](../../docs/partial_plan_transitions_retro.md).
- **Never edit a CLAUDE.md here.** Analyze impact only; `/learn` writes with user confirmation.
