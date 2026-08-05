---
name: groom
title: Groom
summary: Shape a feature, bug, or refactor into a specified, estimated, 
  user-approved plan.
trigger: groom a request into a plan — spec out a feature, bug, or refactor 
  before development (playbook variant, parallel to /groom)
jinja: true
inline_steps: true
requires_project: true
reviewed_at: 20260731 19:10
---
Groom playbook takes user feature-development request, clarifies it if it's needed and builds
a development plan based on it.

{% set stamp = macro('macros.now') -%}
**Context:**
- Date & Time: {{ stamp }}
- Plan dir: `plans/{{ stamp }}_{kebab-title}/`

**High Level Execution**
- Understand user request and create an empty `plans/{{ stamp }}_{kebab-title}/index.md` main artifact
- Research codebase
- Research web
- Draft a solution into `index.md`
- Cross-check the solution
- Write and present the final solution to a user

The groom playbook ends on `ready-for-dev` states, you need to give a note to user to approve the
created plan by mentioning plan path in the final response.

**Cross-review**
{%- if config.get('cross_review') %}
- `cross-review` runs detached in `{{ config.cross_review.agent }}` and returns findings only. Dispose of them
  yourself before advancing: `CRITICAL` folded into the plan or recorded as a deferral in
  `## Risk register`, `RISK` folded in unless it reopens a call the user settled, `NOTE` at your
  discretion. A finding that reopens a settled design call is folded in nowhere — it sends the run
  back to `drafting`.
{%- else %}
- No `cross_review` agent is configured: **skip the `cross-review` step** and transition straight
  past it. Nothing reviewer-flavoured enters the plan — no findings list, no severity vocabulary,
  no risk register.
{%- endif %}

{% set agents_skill = "groom" %}
{% include "_partials/available_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}