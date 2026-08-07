---
name: learn
title: Learn
summary: Turn retrospective findings into durable behavior changes routed to
  exactly one target each — extract atomic candidates, sweep for duplicates,
  confirm a review table with the user, write the accepted items, close the
  plans out.
trigger: absorb lessons from a retrospective after `/playbook retro`; fold retro findings into lessons and extensions
jinja: true
inline_steps: true
requires_project: true
---
Turn retrospective findings into durable behavior changes routed to exactly one target each.

## Guidance

- The run's unit of work is a standalone retrospective, `retrospectives/{slug}.md`; its `plans:` frontmatter lists the plans it covers, for context only.
- The run workdir is the **vault root**; every `booping playbook-state` / `booping playbook-transition` call passes `--target retrospectives/{slug}.md`, since the machine declares no `artifact:`.
- Plans are already `done` when learn runs and are never re-read for status or touched by it.
- Learn writes exactly two destinations: this project's vault `_lessons/` and the attached repo's `CLAUDE.md`.

## Single-location rule

Every accepted learning lands in **exactly one** destination. If a candidate would otherwise span both, decompose it into two distinct rows in the review table — one row per destination. The destinations and the lesson target forms live below; do not restate them elsewhere.

{% include "_partials/_learn_targets.j2" %}

## Retrospectives awaiting learning

{% set _learn_retros = 'core.learn_playbook.queries.candidates' | query -%}
{% if _learn_retros -%}
| Status | Title | Created | Primary plan | Path |
| --- | --- | --- | --- | --- |
{% for retro in _learn_retros -%}
| {{ retro.status }} | {{ retro.title }} | {{ retro.created if retro.created is not none else "—" }} | {{ retro.plan if retro.plan is not none else "—" }} | {{ retro.path }} |
{% endfor -%}
{%- else -%}
_No retrospectives awaiting learning._
{%- endif %}

{% set playbook_agents = config.core.learn_playbook -%}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
