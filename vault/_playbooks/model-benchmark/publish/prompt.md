---
summary: Append the scorecard row to the history table, commit the vault artifacts, then open or update the benchmark branch's pull request against the reference branch — the branch itself left untouched.
review_gate: null
---

# Publish the scorecard

## 1. The row

Append `measure`'s history row as the last row of the table in `{vault}/benchmarks/history.md`, cells in the registry's `history_columns` order. Nothing else in that file is edited — earlier rows are history and are never rewritten, re-sorted or re-scored, not even when a column's meaning has moved on.

## 2. The commit

Commit the vault artifacts — the run detail and `history.md` — in the source repo, where the vault lives. That commit is the durable record of the run and is made before anything leaves this machine, so a push or a pull request that fails afterwards costs nothing but a retry. The workspace's own vault copy is scratch and is never committed from.

## 3. The pull request

The benchmark branch lives only in the workspace until this step, so this is where it leaves the machine. Push it from the workspace to the entry's `push_remote` — `origin` there points back at the source repo and is never pushed to — then look before creating:

```
git -C {workspace} push {push_remote.name} {branch}
gh pr list --head {branch}
```

- A pull request already exists → update its body from the detail report (`gh pr edit {number} --body-file {detail path}`). A re-run of a benchmark updates its pull request; it never opens a second one and never fails on the duplicate.
- None exists → `gh pr create --base bench/reference --head {branch} --body-file {detail path}`, titled with the model and the outcome.

The base is always `bench/reference`. The branch is left in place exactly as the sprint left it: never merged, never deleted, never rebased, and no commit added to it here.

A failed push or a failed `gh` call is reported as what it is, with the pull request's state named. The vault commit stays; nothing is reverted, and the run is not re-measured to try again. The workspace stays too — it is the only copy of an unpushed branch, so it is never pruned here, whether the push succeeded or not.

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
- branch: pushed to `{push_remote.name}` at {sha}, not merged, not deleted
- workspace: `{workspace path}` — left in place; prune with `rm -rf` when the branch is no longer needed locally
- transition: {the transition report verbatim}
```
