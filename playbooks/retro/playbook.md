---
name: retro
title: Retro
summary: Generate a project- and plan-specific sprint retrospective — mine session logs, gather the user's raw feedback, triage issues, then save it and hand off to `/playbook learn`.
trigger: retro a plan after `/playbook develop` reports a sprint done; write a sprint retrospective
jinja: true
inline_steps: true
requires_project: true
reviewed_at: 20260802 14:43
---
Produce a project- and plan-specific retrospective grounded in session logs, code diff, and user feedback — not vibes. No cross-project generalization, no candidate lessons. One run produces one retrospective, grounded in the session record, the plan as written, and the user's own words — never in vibes, and never in cross-project generalization.

{% from "_partials/timestamps.md" import slug_ts, human_ts -%}
## Guidance

- Date & time: {{ human_ts }}
- The run's artifact is a standalone retrospective, `retrospectives/{{ slug_ts }}_{kebab-title}.md` — one file per run, whatever the size of the working set.
- The run workdir is the **vault root**; every `booping playbook-state` / `booping playbook-transition` call passes `--target retrospectives/{slug}.md`, since the machine declares no `artifact:`.
- The retrospective carries `plan:` (the primary plan's path); each covered plan is linked back by the `retro:` key the exit hook stamps. Plan `status:` is never touched here.
- Candidate plans are the ones the table below lists — the `core.retro_playbook.queries.candidates` query.

## Plans awaiting retro

{% set _retro_plans = 'core.retro_playbook.queries.candidates' | query -%}
{% if _retro_plans -%}
| Status | SP | Title | Created | Completed | Path |
| --- | --- | --- | --- | --- | --- |
{% for plan in _retro_plans -%}
| {{ plan.status }} | {{ plan.sp if plan.sp is not none else "—" }} | {{ plan.title }} | {{ plan.created if plan.created is not none else "—" }} | {{ plan.completed if plan.completed is not none else "—" }} | {{ plan.path }} |
{% endfor -%}
{%- else -%}
_No plans awaiting retro._
{%- endif %}

{% set playbook_agents = config.core.retro_playbook -%}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
