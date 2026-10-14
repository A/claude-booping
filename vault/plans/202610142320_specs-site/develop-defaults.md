# Develop defaults — autonomous run

Run on 2026-10-14, owner unavailable. Every point the runner settled itself, with the reason.

## D1 — branch

The provision gate asks the user to confirm a branch name. The owner's invocation pins the worktree branch `feat/specs` and forbids switching or creating branches, so the sprint reuses `feat/specs` as is; the gate is taken as confirmed by that instruction.

## D2 — intake drift

Plan `commit:` is `d30e0da`, HEAD `fb28dce`. The three commits between are groom's own vault commits on this plan (`index.md`, milestones, `clarifications.md`, `request.md`); no file in any task's `Files` column changed. Treated as no drift.

## D3 — repo commit message format

The develop step body asks for `{agent}: {plan title} {message}`; rule/0022 requires Conventional Commits with a scope, and every earlier sprint on this branch follows rule/0022 (`refactor(docs): …`). A rule outranks the step's default, so milestone commits read `feat(specs): …` / `docs(specs): …`.

## D4 — snapshot policy

Lesson 0013 / rule/0013 forbid `just snapshots-accept` from a run. The owner's standing permission for this feature (2026-10-14, C8) overrides it for this run only: accepted only when every drifted hunk is a change this plan describes, each accepted report listed under Accepted snapshots below. Any other drift stops the run.

## D5 — review gates

Autonomous run: gates auto-confirmed; no questions asked.

## Accepted snapshots

None yet.

## D6 — `.gitignore` anchored to `/site/`

The repo `.gitignore` rule `site/` (MkDocs output at the repo root) also matched the new package `booping-python/src/booping/specs/site/`, hiding it from git and from ruff. Anchored to `/site/` in M01's commit — outside the plan's file lists, but without it the package is neither committable by path nor linted.
