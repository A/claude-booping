---
summary: Append the scorecard row to the README history table and commit and push the benchmarks repo — the benchmark branch left in the workspace exactly as the sprint left it.
review_gate: null
---

# Publish the scorecard

## 1. The row

Take `measure`'s history row and repoint its link cell before appending: `bench-score` emits it linking the run detail under `runs/`, and the published row links the human-readable report at `{reports_dir}/{run_id}-{model_slug}.md` instead — the chain is history row → report → detail, so the detail stays one click away through the report's own link. Nothing else in the row changes — the `comment` cell in particular stays empty: it is the human's cell, written by hand after the run, never by this step.

Append it as the last row of the history table in `{bench}/README.md`, cells in the registry's `history_columns` order. Nothing else in that table is edited — earlier rows are history and are never rewritten, re-sorted or re-scored, not even when a column's meaning has moved on. Column meanings and the method behind them live in `{bench}/method.md`; a run that deviated from that method says so in a footnote on its own row, and never by editing the method page.

## 2. The commit

Commit the run's artifacts — the run detail, the run report and the README row — in the benchmarks repo, then push it to its remote. That commit is the durable record of the run, and it is the last thing the run does. The workspace's own copies are scratch and are never committed from.

The benchmark branch stays in the workspace exactly as the sprint left it: never merged, never deleted, never rebased, and no commit added to it here. Pushing it anywhere is a later decision for the user, not this step's business — which is why the workspace is never pruned here either, being the only copy of that branch.

## Closing the step

Advance the run per the `## State` section once the row is committed.

## Return format

```markdown
## Changed:

- [UPDATED] {bench}/README.md — one history row appended for `{model}`, linking `{reports_dir}/{run_id}-{model_slug}.md`
- [COMMITTED] {sha} — {message}, pushed to the benchmarks repo remote

## Notes:

- row: {the appended row, verbatim}
- branch: `{branch}` left in the workspace at {sha}, not pushed, not merged, not deleted
- workspace: `{workspace path}` — left in place; it holds the only copy of the branch, so prune it only once the branch is no longer wanted
- transition: {the transition report verbatim}
```
