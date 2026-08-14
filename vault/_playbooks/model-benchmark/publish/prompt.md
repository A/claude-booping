---
summary: Append the scorecard row to the history table, commit the vault artifacts, then open or update the benchmark branch's pull request against the reference branch — the branch itself left untouched.
review_gate: null
---

# Publish the scorecard

## 1. The row

Append `measure`'s history row as the last row of the table in `{vault}/benchmarks/history.md`, cells in the registry's `history_columns` order. Nothing else in that file is edited — earlier rows are history and are never rewritten, re-sorted or re-scored, not even when a column's meaning has moved on.

## 2. The commit

Commit the vault artifacts — the run detail and `history.md` — in the vault's own repo. That commit is the durable record of the run and is made before anything leaves this machine, so a push or a pull request that fails afterwards costs nothing but a retry.

## 3. The pull request

The benchmark branch lives in the entry's `repo`. Discover its remote before pushing (`git remote -v` — it is often not `origin`), push the branch, then look before creating:

```
gh pr list --head {branch}
```

- A pull request already exists → update its body from the detail report (`gh pr edit {number} --body-file {detail path}`). A re-run of a benchmark updates its pull request; it never opens a second one and never fails on the duplicate.
- None exists → `gh pr create --base bench/reference --head {branch} --body-file {detail path}`, titled with the model and the outcome.

The base is always `bench/reference`. The branch is left in place exactly as the sprint left it: never merged, never deleted, never rebased, and no commit added to it here.

A failed push or a failed `gh` call is reported as what it is, with the pull request's state named. The vault commit stays; nothing is reverted, and the run is not re-measured to try again.

## Closing the step

Advance the run per the `## State` section once the row is committed and the pull request is open or updated.

## Return format

```markdown
## Changed:

- [UPDATED] benchmarks/history.md — one row appended for `{model}`
- [COMMITTED] {sha} — {message}

## Notes:

- row: {the appended row, verbatim}
- pull request: {created|updated} {url} — base `bench/reference`, head `{branch}`
- branch: left in place at {sha}, not merged, not deleted
- transition: {the transition report verbatim}
```
