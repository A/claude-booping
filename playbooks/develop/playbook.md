---
name: develop
title: Develop
summary: Execute a groomed plan by delegating every task to a worker agent, one 
  milestone group at a time, then hand off a verified sprint to retro.
trigger: execute a groomed plan; run the sprint after /groom; implement the 
  plan's milestones (playbook variant, parallel to /develop)
jinja: true
inline_steps: true
requires_project: true
reviewed_at: 20260802 09:43
---
Your goal is one finished sprint per run: every milestone `done`, every DoD checkbox `[x]`,
work committed on the sprint branch in the attached repo, the project's guardrails green, and
the plan handed off to `/retro`.

**Plan resolution.** Take the plan from the invocation argument; with none given, build a
candidate table of plans in the vault currently at `ready-for-dev` or `awaiting-plan-review` and
let the user pick. The plan's own directory, `plans/{slug}/`, is the run workdir — `index.md` is
both the plan document and the machine's artifact. The machine attaches to whatever status is
already on the file; it never bootstraps or creates it.

**Hard rules — hold for the whole run:**
- The runner never writes application code. Every task is delegated to a worker agent, even a
  one-line change.
- No scope additions: the sprint delivers exactly the plan's milestones and tasks, nothing more.
- `develop-loop` works one milestone group at a time — brief a worker, close the group, then
  move to the next. Never two workers on one sprint branch at once.
- `/develop` stays canonical: this playbook runs alongside it as an experiment and does not
  replace it.

Eval runs are proposed, never launched — the user triggers them.

{% set agents_skill = "develop" %}
{% include "_partials/available_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
