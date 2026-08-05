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

{% set slug_ts = macro('macros.date', '+%Y%m%d%H%M') -%}
{% set human_ts = macro('macros.date', '+%Y-%m-%d %H:%M') -%}
**Context:**
- Date & Time: {{ human_ts }}
- Plan dir: `plans/{{ slug_ts }}_{kebab-title}/`

**High Level Execution**
- Understand user request and create an empty `plans/{{ slug_ts }}_{kebab-title}/index.md` main artifact
- Research codebase
- Research web
- Draft a solution into `index.md`
- Cross-check the solution
- Write and present the final solution to a user

{% set playbook_agents = config.core.groom_playbook -%}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}