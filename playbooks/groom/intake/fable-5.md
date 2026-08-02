# Frame the request

You need to read user request and confirm you have all information to work it out into a plan and file a request.

## Latest Plans

Check for context, in case a request is related to already existing plan.

{% set _plans = context.plans | rejectattr('status', 'in', ["backlog", "in-spec", "awaiting-plan-review"]) | list -%}
{% set _dated = _plans | selectattr('created') | sort(attribute='created', reverse=True) | list -%}
{% set _undated = _plans | rejectattr('created') | list -%}
{% set _latest = (_dated + _undated)[:10] -%}
{% if _latest %}
| state | name | summary | path |
| --- | --- | --- | --- |
{% for plan in _latest -%}
{% set _path = "plans/" ~ plan.slug ~ "/index.md" if plan.path.name in ("plan.md", "index.md") else "plans/" ~ plan.path.name -%}
| {{ plan.status | replace("|", "\|") | replace("\n", " ") }} | {{ plan.title | replace("|", "\|") | replace("\n", " ") }} | {{ plan.summary | replace("|", "\|") | replace("\n", " ") }} | [plan]({{ _path }}) |
{% endfor -%}
{% else %}
No plans filed.
{% endif %}

## Task Types

Exactly one per plan. Pick the row the request meets, load its guidance before framing, and rule
the siblings out by name.

| type | fits when | guidance |
| --- | --- | --- |
{% for t in config.tasks -%}
| `{{ t.type }}` | {{ t.description | replace("|", "\|") | replace("\n", " ") }} | [guidance]({{ t.doc_uri }}) |
{% endfor %}
## The brief — written to `request.md`, posted in chat

The framing brief is this step's outcome: it is written to `request.md`, which every later step
reads, and posted in chat, where the user answers it. Both carry the same block, with exactly
these parts, in this order:

- **Request** — the request as a blockquote, character-for-character. Nothing added, nothing
  tidied, nothing summarised.
- **Task type** — one backticked type from the catalogue, with the rationale that rules each
  sibling type out by name and on a stated test.
- **Problem** — what the system does today and what must change, in the request's own
  domain terms.
- **Clarifications and Decisions**: list of one-line clarifications and decisions made with user when refining on this plan