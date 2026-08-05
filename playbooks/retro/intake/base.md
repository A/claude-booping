The current set of candidate plans is listed in the **Plans awaiting retro** table of the preamble, SPs included.

Resolve `$ARGUMENTS` to plan paths.

**No plans provided**: present the list to the user via `AskUserQuestion` with `multiSelect: true` (one option per plan). The selected plans become the working set.

**One or more plans provided**:

1. Validate each provided plan's `status:` is the status the `## State` section names as this run's entry. On mismatch, STOP with this verbatim error:

   > `retro playbook requires a plan in status '{entry-status}'; got '{current-status}' for {plan-path}. Use the list above to pick a candidate.`

2. Identify *other* plans at that same entry status (those in the inlined list but not in `$ARGUMENTS`). If any exist, ask the user per other plan via `AskUserQuestion`:
   - **Include** — add to this retro run alongside the provided plans.
   - **Postpone** — leave the plan where it is (no-op).
   - **Skip retro and mark done** — close the plan now and exclude it from this run.
3. Close each "skip & mark done" plan before moving to the next step, one `_scripts/drop-plan {slug}` invocation per plan — never a hand edit. The script stamps `status: done`, `goal: skipped` and `completed:` and commits the vault, one commit per plan.

## The report — posted in chat

```markdown
## Retro intake

{A table with columns: action (taken | postponed | skipped), plan path, current status, plan description, SPs }
```