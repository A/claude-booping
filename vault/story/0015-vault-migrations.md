---
type: story
title: Project Vault migrations
summary: The migrate playbook brings an existing Project Vault current with the plugin, one approval and one commit per migration.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want to bring my existing Project Vault current with a new plugin
version, so that an upgrade does not leave my vault in a shape the playbooks no longer
read.

## Criteria

- Every render surface warns when the marker's `latest_migration` watermark is behind.
- Surveys the pending plugin-shipped migrations against the watermark.
- Applies each pending migration in id order on one up-front approval, one Project
  Vault commit per migration.
- Converts an older vault's `_booping/` skill and agent extension files into targeted
  lessons, removing the originals.
- Halts on a failing migration, naming the id, the failure and a hand-applicable
  remedy.
