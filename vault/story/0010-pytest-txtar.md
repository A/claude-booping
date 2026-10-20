---
type: story
title: pytest-txtar
summary: The e2e corpus's case format and sandboxed runner ship as a standalone pytest plugin on PyPI.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P2
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a contributor**, I want the contract-case format and its sandboxed runner as a
standalone pytest plugin, so that the e2e corpus depends on it like any other package.

## Scenarios

1. A contributor adds a contract case for a `booping` subcommand as a txtar file: the
   fixtures, the command, and its expected exit code, stdout and stderr.
2. `just e2e` runs the case through the plugin's sandboxed runner and compares the
   actual output with the expected one.
3. When a behaviour changes on purpose, the contributor rebaselines the selected cases
   with `--txtar-update`.

## Edge cases

- `--txtar-update` runs the cases serially; a normal run runs them in parallel.

## Out of scope

- The case format's specification: it is owned by the plugin, not by booping.

## Criteria

- Contract cases are written in the txtar case format the plugin defines and run by its
  sandboxed runner.
- It is a PyPI dependency; booping's own e2e suite is its first consumer.
