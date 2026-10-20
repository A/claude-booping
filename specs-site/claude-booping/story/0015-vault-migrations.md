---
type: story
title: Project Vault migrations
summary: The migrate playbook brings an existing Project Vault current with the plugin on one up-front approval, with one commit per migration.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P1
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want to bring my existing Project Vault current with a new plugin
version, so that an upgrade does not leave my vault in a shape the playbooks no longer
read.

## Scenarios

1. The user updates the plugin; the next render sees the marker's `latest_migration`
   watermark behind the shipped migrations and prints a notice in place of its output.
2. The user runs `/playbook migrate`; it surveys the pending migrations against the
   watermark and lists them.
3. The user approves once, up front; the playbook applies each pending migration in id
   order, one Project Vault commit per migration, advancing the watermark after each.
4. The renders stop gating and the user's original request goes on.

Unattended: with `core.auto_migrate` on, the default, the notice orders the agent to run
`/playbook migrate` itself and then resume the original request.

## Edge cases

- A migration fails: the run halts, naming the id, the failure and a remedy the user can apply by hand.
- An older vault still holds `_booping/` skill and agent extension files: they become targeted rules and the originals are removed.
- `core.auto_migrate` is off: the notice stops the run and tells the user to run `/playbook migrate`; nothing else renders until the vault catches up.

## Criteria

- Every render surface warns when the marker's `latest_migration` watermark is behind.
- Surveys the pending plugin-shipped migrations against the watermark.
- Applies each pending migration in id order on one up-front approval, one Project
  Vault commit per migration.
- Converts an older vault's `_booping/` skill and agent extension files into targeted rules, removing the originals.
- Halts on a failing migration, naming the id, the failure and a hand-applicable
  remedy.
