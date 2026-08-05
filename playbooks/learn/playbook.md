---
name: learn
title: Learn
summary: Turn retrospective findings into durable behavior changes routed to
  exactly one target each — extract atomic candidates, sweep for duplicates,
  confirm a review table with the user, write the accepted items, close the
  plans out.
trigger: absorb lessons from a retrospective after /retro; fold retro findings
  into lessons and extensions (playbook variant, parallel to /learn)
jinja: true
inline_steps: true
requires_project: true
---
Turn retrospective findings into durable behavior changes routed to exactly one target each.

## Guidance

- Learn handles plans in `{{ config.skills.learn.status }}` status.
- The retrospective lives at `plans/{primary-slug}/retro.md`; its `plans:` frontmatter lists the working set the run covers, and the plan whose directory holds it is the **primary**.
- The run workdir is the primary plan's directory `plans/{primary-slug}/` — `index.md` there is the run artifact.
- Learn writes only to this project's vault (`_lessons/`, `_booping/`) and the attached repo's `CLAUDE.md` — **never** the global `~/.claude/CLAUDE.md` or any user-level scope.

## Single-location rule

Every accepted learning lands in **exactly one** target. If a candidate would otherwise span two targets, decompose it into two distinct rows in the review table — one row per target. The four targets, when-to-use tests, and example filenames live in the routing matrix below; do not restate it elsewhere.

{% include "_partials/_learn_targets.j2" %}

## Plans awaiting learning

{% set _learn_plans = 'skills.learn.queries.candidates' | query -%}
{% if _learn_plans -%}
| Status | SP | Title | Created | Completed | Retro | Path |
| --- | --- | --- | --- | --- | --- | --- |
{% for plan in _learn_plans -%}
| {{ plan.status }} | {{ plan.sp if plan.sp is not none else "—" }} | {{ plan.title }} | {{ plan.created if plan.created is not none else "—" }} | {{ plan.completed if plan.completed is not none else "—" }} | {{ plan.retro if plan.retro is not none else "—" }} | {{ plan.path }} |
{% endfor -%}
{%- else -%}
_No plans at `{{ config.skills.learn.status }}`._
{%- endif %}

## High-level workflow

1. Intake — resolve the retrospective and its working set; validate `{{ config.skills.learn.status }}` status.
2. Extract candidates — inline, decomposed into atomic rules, routed via the matrix.
3. Update-vs-create sweep — filtered read of existing lessons and extensions.
4. Present unified review table — user accepts / rejects / adds rows.
5. Write accepted items — one pass per target type, no per-edit prompts.
6. Transition and commit.

{% set agents_skill = "learn" %}
{% include "_partials/available_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
