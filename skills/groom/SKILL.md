---
name: groom
description: Deep-research a feature, bug, or refactor and produce a specified, estimated backlog item with Definition of Done. Cross-validates architecture with a second model when useful. Use when the user describes a new piece of work that needs to be shaped before implementation.
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
  - Agent
  - AskUserQuestion
  - WebSearch
  - WebFetch
effort: max
---

# booping — /groom

Produce a backlog item that a fresh agent can execute with only the backlog file as context.

## Project resolution

Follow [docs/project-scoping.md](../../docs/project-scoping.md). After resolving, read `~/Claude/{project}/_booping/skill_groom.md` if present — those are project-local rules that override defaults. Also read all files in `~/Claude/{project}/lessons/` so the spec respects known constraints.

## Task classification

Ask the user (or infer with confirmation) which type:

- **feature** — new capability, needs business goal + design + milestones + DoD
- **bug** — triage, reproduction, root-cause hypothesis, minimal fix plan, regression test
- **refactoring** — current-vs-target design, migration steps, no behavior change DoD

## Orchestration

The orchestrator (this skill) does **not** read the codebase or write code itself. Delegate to sub-agents:

| Agent | Role |
|-------|------|
| `booping-techlead` | Read codebase, identify existing patterns, map blast radius, flag tech risk |
| `booping-product-manager` | Validate / challenge requirements, web-research alternatives, define business goal |
| `booping-qa-lead` | Propose testing strategy, regression concerns, QA plan |
| `booping-teamlead` | Coordinate the above, collate findings, draft the backlog file |

For a **feature** run all four in this order:
1. `booping-product-manager` — confirm the problem and desired outcome
2. `booping-techlead` — codebase investigation (can run in parallel with PM once the problem is clear)
3. `booping-qa-lead` — testing strategy based on techlead's plan
4. `booping-teamlead` — synthesize into the backlog document

For a **bug** skip PM unless the bug has product-impact ambiguity.
For a **refactoring** skip PM; put techlead in the lead role.

### Briefing template

Every `Agent()` call uses the canonical briefing header — see [docs/agent-wiring.md](../../docs/agent-wiring.md) for the full spec and the per-agent domain filter. In short:

```
project_root: ~/Claude/{project}
agent_extension: ~/Claude/{project}/_booping/agent_<agent-name>.md

Applicable lessons:
- lessons/<id>_<title>.md
- ...

Task / goal: ...
```

Filter the `Applicable lessons:` list by the agent's domain set (`tech,code,all` for techlead; `product,all` for PM; `qa,all` for qa-lead) before writing the briefing. Do **not** hand a techlead's SOLID lesson to the product manager.

## Output

Write to `~/Claude/{project}/backlog/YYYYMMDD-{kebab-title}.md` using [template.md](template.md). Frontmatter must include:

```yaml
---
type: feature | bug | refactoring
title: ...
created: YYYY-MM-DD
source: <chat topic, issue URL, or 'ad-hoc'>
status: groomed
sp: <total>
business_goal: <one-sentence user-facing outcome>   # features only
---
```

After writing, run [quality-checklist.md](quality-checklist.md) against the file. Fix any violations before presenting.

## Estimation (SP scale)

Use this scale verbatim. Present per-milestone and per-task estimates, then ask the user for adjustment before finalizing `status: groomed`.

| SP | Meaning |
|----|---------|
| 1  | Simple text/config change, no risk |
| 2  | Simple task, predictable, no risk |
| 3  | Medium task, minor risks but predictable overall |
| 4  | Complex task, medium risk, may need small research but clear enough |
| 5  | Research task — developer needs to clarify and decompose further before proceeding |

A task estimated **5 SP must be re-decomposed** before `status: groomed`. Do not hand a 5-SP task to `/develop`. Project-local calibration (sprint-size thresholds, buffer factors) lives in `_booping/skill_groom.md`.

## Business goal elicitation (features)

Before finalizing a **feature** backlog item, explicitly ask the user:

> "What business goal does this sprint contribute to?"

This is distinct from the sprint title — it names the user-visible outcome (e.g. "Working events system", "Faster digest pipeline"). Capture the answer in `business_goal:` frontmatter and in the backlog's **Business goal** section. `/develop` will copy it into `sprints.md`, and `/retro` will judge the sprint against it. No business goal → no `status: groomed`.

## Cross-validation (Gemini)

After the quality checklist passes, run the Gemini validator to surface execution risks and rule violations the orchestrator may have missed. Mandatory for features and refactorings, optional for single-file bugs.

```bash
booping-validate-plan ~/Claude/{project}/backlog/YYYYMMDD-{kebab-title}.md
```

`booping-validate-plan` is shipped in the plugin's `bin/` and auto-added to PATH while the plugin is enabled. It derives the project from the backlog path, loads `~/Claude/{project}/lessons/` as the rubric, and handles its own API-key check.

**Security:** never inspect the environment for `GEMINI_API_KEY` (no `env | grep`, no `printenv`, no reading `.env` files). The token stays out of the conversation context. Call the validator blind and let it report its own readiness.

Handle the validator by **exit code**, not output parsing:

| Exit code | Meaning | Action |
|-----------|---------|--------|
| `0` | Validation ran | Present the full stdout to the user verbatim under a "Gemini cross-validation" heading. Then address each **CRITICAL EXECUTION RISK** and **RULE VIOLATION** before finalizing the backlog. **ARCHITECTURAL BLIND SPOTS** may be deferred with explicit user acceptance — record the deferral in the Risk register. |
| `2` | Skipped (no `GEMINI_API_KEY`) | Report to the user: "Gemini cross-validation skipped — `GEMINI_API_KEY` not set." Continue grooming. Optionally fall back to the `double-check` skill if installed. |
| `1` | Error (bad input, API failure) | Report the stderr message to the user. Continue grooming but flag that cross-validation did not complete. |

The validator's output **belongs to the user** — do not silently summarize or internalize it. Paste it in the chat as-is (fenced block is fine) so the user sees exactly what Gemini flagged.

## Commit

After the user accepts the backlog item and estimates, commit the artifact to the project vault:

```bash
cd ~/Claude/{project}
git add backlog/YYYYMMDD-{kebab-title}.md metrics/lesson-hits.md
git commit -m "backlog: {kebab-title}"
```

One commit per groom run. If `metrics/lesson-hits.md` was updated in the same run, include it.

## What groom does NOT do

- Does **not** update `~/Claude/{project}/sprints.md`. That happens in `/develop` when the backlog item is picked up.
- Does **not** start implementation — even the tempting 1-SP items.
- Does **not** duplicate content from lessons into the backlog file. Reference lesson IDs instead: `Applies lesson: 0007_no-mocked-db`.

## Lesson hit tracking

After the backlog file is written, for each lesson referenced, append a row to `~/Claude/{project}/metrics/lesson-hits.md` with today's date and the backlog file path.

## Hard rules

- The orchestrator never edits files outside `~/Claude/{project}/backlog/` and `~/Claude/{project}/metrics/`.
- Every task in a milestone lists exact files and a DoD with checkboxes.
- No "TBD", "handle edge cases", "TODO", or task spanning unrelated concerns.
