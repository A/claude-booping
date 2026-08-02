The current set of plans in `awaiting-retro` is listed in the [Plans awaiting retro](#plans-awaiting-retro) table of the preamble, SPs included.

Resolve `$ARGUMENTS` to plan paths.

**No plans provided**: present the list to the user via `AskUserQuestion` with `multiSelect: true` (one option per plan). The selected plans become the working set.

**One or more plans provided**:

1. Validate each provided plan's `status:` is `awaiting-retro`. On mismatch, STOP with this verbatim error:

   > `retro playbook requires a plan in status 'awaiting-retro'; got '<current-status>' for <plan-path>. Use the list above to pick a candidate.`

2. Identify *other* plans in `awaiting-retro` (those in the inlined list but not in `$ARGUMENTS`). If any exist, ask the user per other plan via `AskUserQuestion`:
   - **Include** — add to this retro run alongside the provided plans.
   - **Postpone** — leave in `awaiting-retro` (no-op).
   - **Skip retro and mark done** — apply the proper transition to the plan now (per the transitions table above) and exclude from this run.
3. Apply each "skip & mark done" transition before moving to the next step. One commit per plan.

## The report — posted in chat

```markdown
## Retro intake

{A table with columns: action (taken | postponed | skipped), plan path, current status, plan description, SPs }
```