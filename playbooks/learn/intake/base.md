The current set of plans in `awaiting-learning` is listed in the [Plans awaiting learning](#plans-awaiting-learning) table of the preamble.

Resolve `$ARGUMENTS` to a retrospective file path.

**No `$ARGUMENTS`**: branch on the plans-list size.

- **Zero plans**: STOP with `No plans in awaiting-learning. Run the retro playbook first to write a retrospective.`
- **Exactly one plan**: auto-select it (do not call `AskUserQuestion` — it requires ≥2 options).
- **Multiple plans**: present the list via `AskUserQuestion` (single-select; one option per plan). Plans sharing one `retro:` value are one working set — offer the set as a single option, not one option per sibling.

Read the selected plan's `retro:` frontmatter to resolve the retrospective file.

**`$ARGUMENTS` provided**: treat it as the retrospective file path. Read it and follow its `plans:` frontmatter to the associated plans.

## Working set and workdir

The retrospective's `plans:` frontmatter is the **working set** — every plan this run absorbs lessons for. The plan whose directory holds the retrospective is the **primary**, and its directory `plans/{primary-slug}/` is the run workdir. A retrospective without a `plans:` list covers only the plan it was resolved from.

Validate every working-set plan's `status:` is `awaiting-learning`. On mismatch, STOP with this verbatim error:

> `learn playbook requires a plan in status 'awaiting-learning'; got '{current-status}' for {plan-path}. Use the list above to pick a candidate.`

Read the retrospective in full — it is the sole source the run extracts from. Read each working-set plan for context only: scope, decisions on record, what the retro's findings refer to.

## The report — posted in chat

```markdown
## Learn intake

Retrospective: {path}
Working set: {a table with columns: plan path, status, goal verdict from the retro's `goal_verdicts:` when present}
```
