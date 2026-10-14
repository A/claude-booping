---
type: story
title: Quality gates
summary: just ci runs lint, typecheck, pytest, snapshots, mdcheck and e2e in order, holding the plugin's behaviour.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **a contributor**, I want one command to run every check a change must pass, so that
a broken behaviour fails before it is committed.

## Criteria

- `just ci` runs lint, type-check and pytest (ruff, basedpyright, pytest) over the
  Python code.
- `just snapshots` diffs the committed playbook reports against a fresh hermetic render;
  `just snapshots-accept` accepts a new baseline.
- `mdcheck` structural rules run over every rendered report.
- Every `booping` subcommand's behaviour is a txtar end-to-end contract corpus run by
  `just e2e`.
