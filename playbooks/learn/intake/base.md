The current set of candidate retrospectives is listed in the **Retrospectives awaiting learning** table of the preamble.

Resolve `$ARGUMENTS` to a retrospective file path under `retrospectives/`.

**`$ARGUMENTS` provided**: treat it as that path — no lookup through any plan.

**No `$ARGUMENTS`**: branch on the table's size.

- **Zero rows**: STOP with `No retrospectives at this run's entry status. Run the retro playbook first to write one.`
- **Exactly one row**: auto-select it (do not call `AskUserQuestion` — it requires ≥2 options).
- **Multiple rows**: present them via `AskUserQuestion` (single-select; one option per retrospective).

Validate the selected retrospective's `status:` is the status the `## State` section names as this run's entry. On mismatch, STOP with this verbatim error:

> `learn playbook requires a retrospective in status '{entry-status}'; got '{current-status}' for {retro-path}. Use the list above to pick a candidate.`

## Workdir and covered plans

The run workdir is the **vault root**, and the retrospective is addressed by `--target retrospectives/{slug}.md` on every state call.

Read the retrospective in full — it is the sole source the run extracts from. Read each plan in its `plans:` list for context only: scope, decisions on record, what the retro's findings refer to. Plan `status:` is neither checked nor written here.

## The report — posted in chat

```markdown
## Learn intake

Retrospective: {path}
Plans covered: {a table with columns: plan path, goal verdict from the retro's `goal_verdicts:` when present}
```
