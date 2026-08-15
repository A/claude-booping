# Frame the request

You need to read user request and confirm you have all information to work it out into a plan and file a request.
{%- if config.core.tracker.driver == 'linear' %}

## The request comes from the tracker

The chat carries no request under this driver — the issue does.

1. Resolve the request issue ref, in this order: the argument the ask carries (`/playbook groom LIN-123`), else `$BOOPING_TRACKER_ISSUE`. With neither, stop and report `error: no tracker issue ref` — no branch guesses a ref, and nothing is scaffolded without one.
2. Read it: `booping-tracker show --issue {ref}`. Its description is the request, and it is what the brief's **Request** blockquote quotes character-for-character. Never take the request from chat.
3. After the plan directory exists, record where the run came from — never by hand-editing frontmatter:

   ```
   booping frontmatter-update {plan-dir}/index.md tracker_provider=linear tracker_request={ref}
   ```

The scope-challenge questions are not asked in chat: write them to `{plan-dir}/clarifications.md` and park the run, per the preamble's `Tracker driver` rules. This step's `Review gate:` line does not apply — the answers arrive as a later invocation, not as a reply.
{%- endif %}

## Latest Plans

Check for context, in case a request is related to already existing plan.

{% set query_plans = 'core.groom_playbook.queries.latest_plans' -%}
{% include "_partials/plans_table.md" %}

## Task Type

Exactly one per plan. Pick the row the request meets, load its guidance before framing and pick one.

{% include "_partials/task_types.md" %}
## The plan directory

Create it in one call, with `{plan-dir}` the preamble's `Plan dir:` line resolved against the
vault and `{title}` the plan's descriptive title:

```
booping scaffold core.groom_playbook.scaffold {plan-dir} --set title="{title}" --set type={type}
```

The printed diff is the confirmation — do not read the created files back. A target reported as
already existing was not written; decide what that means for this run.

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