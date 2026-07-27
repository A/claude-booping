---
name: groom
title: Groom
summary: Turn a request into a specified, estimated, user-approved development plan.
trigger: groom a request into a plan; spec out a feature, bug, or refactoring before development starts
jinja: true
requires_project: true
graph:
  intake: []
  research-codebase: [intake]
  research-web: [intake]
  design: [research-codebase, research-web]
  draft: [design]
  present: [draft]
---
{% import "_partials/_plan_transitions.j2" as plan_transitions with context %}
# Groom

Produce a development plan across domains (backend, frontend, Claude Code skills, CLI tools, etc.) and task types (bugs, features, refactorings, etc.). Plans are written so an agentic tool such as Claude Code can execute them with only the plan file as context.

{{ plan_transitions.render("groom") }}

{% include "_partials/_shared_instructions.j2" %}

## Hard rules

- Never edit files outside `{project}/plans/`.
- Each milestone must be executable in a fresh session with only the plan as context.
- User approval is **explicit** — "looks good" is enough; silence is not.

## What groom does NOT do

- Does **not** start implementation — even tempting 1-SP items.
- Does **not** duplicate lesson content. Reference lessons by ID.

## Conditional research wave

`research-web` is skippable. `intake` ends its output with a single literal line:

```
web-research: yes
```
or
```
web-research: no
```

Parse that last line exactly:

- Last line is exactly `web-research: yes` → wave 2 runs both `research-codebase` and `research-web` in parallel.
- Last line is exactly `web-research: no` → wave 2 runs `research-codebase` alone; `research-web` is skipped and `design` proceeds without it.
- Anything else (line missing, reworded, extra text after it) → ask the user whether web research is warranted; do not guess.

No looser matching: an in-body mention of web research is not the flag.

## Resuming a groom run

On invocation, check `{project}/plans/` for an existing plan matching this request (statuses per the Plan Transitions table above):

- Status `in-spec` — a groom run is already underway. Read the plan, judge how complete it is, and re-enter at the earliest wave whose output is missing or stale: no research recorded → `research-codebase` (asking the user whether `research-web` is warranted); research present but design undecided → `design`; design settled but milestones/SPs missing or stale → `draft`. Do not re-run earlier waves whose output the plan already carries.
- Status `awaiting-plan-review` — the draft is finished and awaiting the user. Re-enter at `present`; do not re-draft before the user asks for changes.
- Status `backlog` — a parked plan. Start at `intake` and fire the `backlog → in-spec` move once grooming actually begins.
- No matching plan — start at `intake`.

{{ tools.render('src/templates/_partials/_lessons.j2') }}

{{ tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='skill_groom') }}
