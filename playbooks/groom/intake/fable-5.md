# Frame the request

You need to read user request and confirm you have all information to work it out into a plan and file a request.

## Latest Plans

Check for context, in case a request is related to already existing plan.

{% set query_plans = 'core.groom_playbook.queries.latest_plans' -%}
{% include "_partials/plans_table.md" %}

## Task Types

Exactly one per plan. Pick the row the request meets, load its guidance before framing, and rule
the siblings out by name.

{% include "_partials/task_types.md" %}
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