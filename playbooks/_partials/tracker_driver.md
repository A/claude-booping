{%- if config.core.tracker.driver == 'linear' -%}
{%- set _pb = tracker_playbook -%}
## Tracker driver: `linear`

This run is invoked one-shot from a tracker issue. Nothing reads the conversation, so every question is persisted or lost.

- Never call `AskUserQuestion`, and never end a message waiting on a chat reply.
- Never ask the user to confirm a review gate — a gate whose confirmation would come from chat is instead parked as a question, below.

**On entry**, before any step work:

1. Resolve the request issue ref: the ask's argument, else `$BOOPING_TRACKER_ISSUE`. With neither, stop and report `error: no tracker issue ref` — never guess one.
2. Find the run this ref already owns:

   ```
   booping query {% for g in config.core.plans.glob %}--glob {{ g }} {% endfor %}--columns path,status,return_to --where tracker_request={ref}
   ```

   No row → a fresh run, nothing to resume.
3. One row → `booping playbook-state {{ _pb }} --workdir {plan-dir}`, and on `awaiting-clarification` read `{plan-dir}/clarifications.md`: every question answered → take the return edge to the status `return_to` names and continue from there; any question still open → end the run without changing anything.

**A question this run cannot answer itself** parks the run:

1. Append it to `{plan-dir}/clarifications.md` in the format at `${CLAUDE_PLUGIN_ROOT}/docs/clarifications.md` — the next free `C{n}` id, state `open`, `**Asked:**` carrying the date and this step's name.
2. `booping playbook-transition {{ _pb }} awaiting-clarification --workdir {plan-dir}`.
3. **End the run there**, reporting the parked questions. The answers arrive as a later invocation, which resumes by the entry rules above.
{%- endif -%}
