---
summary: Append the scorecard row to the history table and commit the vault artifacts — the benchmark branch left in the workspace exactly as the sprint left it.
review_gate: null
---

# Publish the scorecard

## 1. The row

Append `measure`'s history row as the last row of the table in `{vault}/benchmarks/history.md`, cells in the registry's `history_columns` order. Nothing else in that file is edited — earlier rows are history and are never rewritten, re-sorted or re-scored, not even when a column's meaning has moved on. Column meanings and the method behind them live in `{vault}/benchmarks/method.md`; a run that deviated from that method says so in a footnote on its own row, and never by editing the method page.

## 2. The commit

Commit the vault artifacts — the run detail and `history.md` — in the source repo, where the vault lives. That commit is the durable record of the run, and it is the last thing the run does. The workspace's own vault copy is scratch and is never committed from.

Nothing is pushed and no pull request is opened. The benchmark branch stays in the workspace exactly as the sprint left it: never merged, never deleted, never rebased, and no commit added to it here. Pushing it anywhere is a later decision for the user, not this step's business — which is why the workspace is never pruned here either, being the only copy of that branch.

## Closing the step

Advance the run per the `## State` section once the row is committed.

## Return format

```markdown
## Changed:

- [UPDATED] benchmarks/history.md — one row appended for `{model}`
- [COMMITTED] {sha} — {message}

## Notes:

- row: {the appended row, verbatim}
- branch: `{branch}` left in the workspace at {sha}, not pushed, not merged, not deleted
- workspace: `{workspace path}` — left in place; it holds the only copy of the branch, so prune it only once the branch is no longer wanted
- transition: {the transition report verbatim}
```
