The candidate plans are the **Plans awaiting retro** table of the preamble — the `core.retro_playbook.queries.candidates` query, SPs included.

Resolve `$ARGUMENTS` to plan paths.

**No plans provided**: present the list to the user via `AskUserQuestion` with `multiSelect: true` (one option per plan). The selected plans become the working set.

**One or more plans provided**:

1. Validate each provided plan is in the candidate table. A plan that is not there is either already retro'd or not finished; STOP with this verbatim error:

   > `retro playbook requires a finished plan with no retrospective yet; {plan-path} is not in the candidate list above. Use the list to pick a candidate.`

2. Identify *other* candidates (those in the table but not in `$ARGUMENTS`). If any exist, ask the user per other plan via `AskUserQuestion`:
   - **Include** — add to this retro run alongside the provided plans.
   - **Postpone** — leave the plan where it is (no-op).
   - **Skip retro** — exclude the plan from this run and from the queue for good.
3. Close each "skip retro" plan before moving to the next step, one `_scripts/drop-plan {slug}` invocation per plan — never a hand edit. The script stamps `retro: skipped` (the sentinel that drops the plan out of the candidates query) and `goal: skipped`, and commits the vault, one commit per plan.

## The report — posted in chat

```markdown
## Retro intake

{A table with columns: action (taken | postponed | skipped), plan path, plan description, SPs }
```
