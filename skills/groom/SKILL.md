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
effort: max
---

# booping — /groom

Produce a plan that a fresh agent can execute with only the plan file as context.

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
| `booping-teamlead` | Coordinate the above, collate findings, draft the plan file |

For a **feature** run all four in this order:
1. `booping-product-manager` — confirm the problem and desired outcome
2. `booping-techlead` — codebase investigation (can run in parallel with PM once the problem is clear)
3. `booping-qa-lead` — testing strategy based on techlead's plan
4. `booping-teamlead` — synthesize into the plan document

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

Write to `~/Claude/{project}/plans/YYYYMMDD-{kebab-title}.md` using [template.md](template.md). The filename uses today's date and the lowercase-kebab form of the plan title.

Initial frontmatter at write time must include `status: backlog` — the grooming agents have not yet run:

```yaml
---
title: ...
type: feature | bug | refactoring
status: backlog
sp: null                    # filled after SP elicitation
source: <chat topic, issue URL, or 'ad-hoc'>
created: YYYY-MM-DD
planned: null
started: null
completed: null
retro: null
goal: null
business_goal: null         # features only; filled after business-goal elicitation
---
```

**After writing the file**, immediately run:

```bash
booping-plans set --project=<P> plans/YYYYMMDD-{kebab-title}.md status=in-spec
```

Full 9-state lifecycle + transition table: [docs/plan-schema.md](../../docs/plan-schema.md).

This marks the plan as actively being spec'd by the grooming agents (techlead, PM, QA).

**CLI fallback:**

- If `booping-plans set --project=<P> ... <key>=<value>` exits non-zero: hand-edit the plan frontmatter to match the intended transition. Then print `booping-plans set failed (exit N): <stderr>` verbatim to chat.
- If `booping-plans sync-sprints --project=<P>` exits non-zero: do NOT hand-edit `sprints.md`. Print `booping-plans sync-sprints failed (exit N): <stderr>` verbatim.

After writing, run [quality-checklist.md](quality-checklist.md) against the file. Fix any violations before presenting.

## Estimation (SP scale)

Use this scale verbatim. Present per-milestone and per-task estimates, then ask the user for adjustment before finalizing.

| SP | Meaning |
|----|---------|
| 1  | Simple text/config change, no risk |
| 2  | Simple task, predictable, no risk |
| 3  | Medium task, minor risks but predictable overall |
| 4  | Complex task, medium risk, may need small research but clear enough |
| 5  | Research task — developer needs to clarify and decompose further before proceeding |

A task estimated **5 SP must be re-decomposed** before `status: ready-for-dev`. Do not hand a 5-SP task to `/develop`. Project-local calibration (sprint-size thresholds, buffer factors) lives in `_booping/skill_groom.md`.

## Business goal elicitation (features)

Before finalizing a **feature** plan, explicitly ask the user:

> "What business goal does this sprint contribute to?"

This is distinct from the sprint title — it names the user-visible outcome (e.g. "Working events system", "Faster digest pipeline"). Capture the answer in `business_goal:` frontmatter and in the plan's **Business goal** section. `/develop` will copy it into `sprints.md`, and `/retro` will judge the sprint against it. No business goal → no `status: ready-for-dev`.

## Cross-validation (Gemini)

After the quality checklist passes, run the Gemini validator to surface execution risks and rule violations the orchestrator may have missed. Mandatory for features and refactorings, optional for single-file bugs.

```bash
booping-validate-plan ~/Claude/{project}/plans/YYYYMMDD-{kebab-title}.md
```

`booping-validate-plan` is shipped in the plugin's `bin/` and auto-added to PATH while the plugin is enabled. It derives the project from the plans path, loads `~/Claude/{project}/lessons/` as the rubric, and handles its own API-key check.

**Security:** never inspect the environment for `GEMINI_API_KEY` (no `env | grep`, no `printenv`, no reading `.env` files). The token stays out of the conversation context. Call the validator blind and let it report its own readiness.

Handle the validator by **exit code**, not output parsing:

| Exit code | Meaning | Action |
|-----------|---------|--------|
| `0` | Validation ran | Present the full stdout to the user verbatim under a "Gemini cross-validation" heading. Then address each **CRITICAL EXECUTION RISK** and **RULE VIOLATION** before finalizing the plan. **ARCHITECTURAL BLIND SPOTS** may be deferred with explicit user acceptance — record the deferral in the Risk register. |
| `2` | Skipped (no `GEMINI_API_KEY`) | Report to the user: "Gemini cross-validation skipped — `GEMINI_API_KEY` not set." Continue grooming. Optionally fall back to the `double-check` skill if installed. |
| `1` | Error (bad input, API failure) | Report the stderr message to the user. Continue grooming but flag that cross-validation did not complete. |

The validator's output **belongs to the user** — do not silently summarize or internalize it. Paste it in the chat as-is (fenced block is fine) so the user sees exactly what Gemini flagged.

## Acceptance

When the user accepts estimates and the quality checklist is clean:

```bash
booping-plans set --project=<P> plans/YYYYMMDD-{kebab-title}.md status=ready-for-dev
booping-plans sync-sprints --project=<P>
```

The `set` call auto-fills `planned` with today's date. `sync-sprints` regenerates `sprints.md` to include the newly accepted plan.

**CLI fallback:**

- If `booping-plans set --project=<P> ... <key>=<value>` exits non-zero: hand-edit the plan frontmatter to match the intended transition. Then print `booping-plans set failed (exit N): <stderr>` verbatim to chat.
- If `booping-plans sync-sprints --project=<P>` exits non-zero: do NOT hand-edit `sprints.md`. Print `booping-plans sync-sprints failed (exit N): <stderr>` verbatim.

### Split into sibling sprints

When the user's request maps to multiple sprints (e.g. a single feature request decomposes into a core sprint + a follow-up polish sprint), `/groom` produces one fully-spec'd primary plan and lightweight stubs for the others.

**For each sibling stub:**

1. Derive the stub filename: `plans/{YYYYMMDD}-{kebab-stub-title}.md` (same date + kebab convention as the primary plan).

2. Write the stub file via the Write tool with the following frontmatter and a Context-only body (≤200 words describing what the stub is about, why it was split off, and what is NOT in its scope):

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

3. Immediately after writing each stub, run:

```bash
booping-plans set --project=<P> plans/{stub-filename}.md status=backlog
```

   This is an idempotent validation pass — `backlog` is already set, so the status does not change. The purpose is to confirm that the CLI accepts the frontmatter shape. If the CLI exits non-zero, the stub has a frontmatter error; fix it before proceeding.

**After all stubs are written**, run exactly one sync covering the primary plan + all stubs:

```bash
booping-plans sync-sprints --project=<P>
```

**CLI fallback:**

- If `booping-plans set --project=<P> ... <key>=<value>` exits non-zero: hand-edit the plan frontmatter to match the intended transition. Then print `booping-plans set failed (exit N): <stderr>` verbatim to chat.
- If `booping-plans sync-sprints --project=<P>` exits non-zero: do NOT hand-edit `sprints.md`. Print `booping-plans sync-sprints failed (exit N): <stderr>` verbatim.

## Commit

After the user accepts the plan and estimates, commit the artifact to the project vault:

```bash
cd ~/Claude/{project}
git add plans/YYYYMMDD-{kebab-title}.md metrics/lesson-hits.md sprints.md  # sprints.md is the regenerated rollup
git commit -m "plans: {kebab-title}"
```

One commit per groom run. If `metrics/lesson-hits.md` was updated in the same run, include it. If sibling stubs were written, include their files in the same commit.

## What groom does NOT do

- Does **not** hand-edit `sprints.md`. State transitions flow through `booping-plans set` + `sync-sprints`.
- Does **not** start implementation — even the tempting 1-SP items.
- Does **not** duplicate content from lessons into the plan file. Reference lesson IDs instead: `Applies lesson: 0007_no-mocked-db`.

## Lesson hit tracking

After the plan file is written, for each lesson referenced, append a row to `~/Claude/{project}/metrics/lesson-hits.md` with today's date and the plan file path.

## Hard rules

- The orchestrator never edits files outside `~/Claude/{project}/plans/` and `~/Claude/{project}/metrics/`.
- Every task in a milestone lists exact files and a DoD with checkboxes.
- No "TBD", "handle edge cases", "TODO", or task spanning unrelated concerns.
