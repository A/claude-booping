---
name: retro
title: Retro
summary: Generate a project- and plan-specific sprint retrospective — mine 
  session logs, gather the user's raw feedback, triage issues, then save it and 
  hand off to /learn.
trigger: retro a plan after /develop reports a sprint done; write a sprint 
  retrospective (playbook variant, parallel to /retro)
jinja: true
inline_steps: true
requires_project: true
reviewed_at: 20260802 14:43
---
Produce a project- and plan-specific retrospective grounded in session logs, code diff, and user feedback — not vibes. No cross-project generalization, no candidate lessons. One run produces one retrospective, grounded in the session record, the plan as written, and the user's own words — never in vibes, and never in cross-project generalization.

## Guidance

- Retro is based on the plan `plans/{slug}/index.md`
- Retro statuses are sub-path of the plan state-machine and they live on `plans/{primary-slug}/index.md`
- Retro is saved to `plans/{primary-slug}/retro.md`
- Retro handles plans in `{{ config.core.retro_playbook.status }}` status.
- Retro playbook only produces retro files and link them to the plan in frontmatter under `retro` key.

## Plans awaiting retro

{% set _retro_plans = 'core.retro_playbook.queries.candidates' | query -%}
{% if _retro_plans -%}
| Status | SP | Title | Created | Completed | Path |
| --- | --- | --- | --- | --- | --- |
{% for plan in _retro_plans -%}
| {{ plan.status }} | {{ plan.sp if plan.sp is not none else "—" }} | {{ plan.title }} | {{ plan.created if plan.created is not none else "—" }} | {{ plan.completed if plan.completed is not none else "—" }} | {{ plan.path }} |
{% endfor -%}
{%- else -%}
_No plans at `{{ config.core.retro_playbook.status }}`._
{%- endif %}

## High-level workflow

1. Input — select / load the plan(s) for retrospective.
2. Prepare — review sessions and plan(s); extract the issue list.
3. User feedback — open-ended overall feedback first, then per-issue triage (refine / accept / dismiss).
4. Per-issue research and analysis — code reading, web research, prevention design for each accepted issue.
5. Synthesize — draft using the retrospective template; run lesson cross-check.
6. Save & transition — write retrospective; apply transitions per the transitions table above; commit.

{% set playbook_agents = config.core.retro_playbook -%}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
