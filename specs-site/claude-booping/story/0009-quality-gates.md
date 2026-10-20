---
type: story
title: Quality gates
summary: just ci runs lint, typecheck, pytest, snapshots, mdcheck and e2e in order, holding the plugin's behaviour.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P1
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a contributor**, I want one command to run every check a change must pass, so that
a broken behaviour fails before it is committed.

## Scenarios

1. A contributor finishes a change and runs `just ci` before committing.
2. It runs lint, type-check and pytest, then diffs the committed playbook reports
   against a fresh hermetic render, runs the mdcheck structural rules over the rendered
   reports, checks the specs tiers and runs the txtar e2e corpora, in that order.
3. Any failing check fails the run, and the contributor fixes the change before
   committing.
4. When a playbook edit changes a report on purpose, the contributor reads the
   `just snapshots` diff and accepts the new baseline with `just snapshots-accept`.

## Edge cases

- A report drifts: `just snapshots` only shows the diff and writes nothing; `just snapshots-accept` is the only writer of a committed report.
- `mdcheck` is not installed: the checks that need it cannot run until the binary is installed.
- A `-k` selection matches cases in one e2e corpus only: the other collects nothing, which is not a failure.

## Criteria

- `just ci` runs lint, type-check and pytest (ruff, basedpyright, pytest) over the
  Python code.
- `just snapshots` diffs the committed playbook reports against a fresh hermetic render;
  `just snapshots-accept` accepts a new baseline.
- `mdcheck` structural rules run over every rendered report.
- Every `booping` subcommand's behaviour is a txtar end-to-end contract corpus run by
  `just e2e`.
