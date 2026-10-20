---
type: runbook
title: Accept new snapshot and contract baselines
summary: After an intentional change, the user reads the snapshot or txtar drift and accepts it; a run or a worker never accepts a baseline itself.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: live
sources: [justfile, scripts/snapshots.py, CLAUDE.md]
---

## When

`just snapshots` reports drift after an edit to playbook sources (manifests, step
`prompt.md`, shared partials, `src/templates/`), or a txtar case in `just e2e` fails
after an intended change in CLI output.

## Before you start

- The baselines are the user's review gate: an agent run or a worker briefing never runs
  `just snapshots-accept`, `--txtar-update`, or writes `playbooks/*/_reports/output.md`.
  At the end of a sprint it shows the drift and asks the user to accept.

## Steps

1. Run `just snapshots` and read the whole diff; it writes nothing.
2. If any hunk is not what the source edit meant, fix the source and repeat step 1.
3. Accept the drift for the playbooks you read: `just snapshots-accept <playbook>`, or
   `just snapshots-accept` for all.
4. For a txtar contract case, run `just e2e -k <case> --txtar-update`, then read the
   rewritten case file in `git diff` the same way.
5. Commit the source and its new baseline together, in one commit.

## Check

- `just snapshots` and `just e2e` pass.
- `just mdcheck` passes over the accepted reports.
- `git diff --stat HEAD~1` shows the source edit and its `_reports/output.md` or txtar
  case in the same commit.

## Rollback

- Restore the previous baseline with `git checkout HEAD~1 -- <path>` if it was committed
  by mistake, and return to step 1.
