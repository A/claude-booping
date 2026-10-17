---
type: story
title: Playbook driver
summary: The /playbook skill discovers a procedure across the core, global and project levels and drives it to completion.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want one `/playbook` skill to find a procedure and drive its steps in
graph order, so that any procedure runs to completion without me sequencing it.

## Criteria

- Lists the playbooks visible from the core, global and project levels and selects
  one by its trigger or by name; a name clash across levels is flagged and blocks the
  run.
- Drives steps in graph order, each parallel wave as detached sub-agents, with
  one-level subgraphs.
- Delegates each step inline, assisted or detached per its `detached:` field; an
  assisted step hands heavy reads to the config-named research agent, resumed by id
  across a loopback.
- Loads step bodies lazily with `booping render-playbook --step`.
- Pauses at review gates for an explicit verdict, never running past one on silence,
  and resumes an interrupted run from the state frontier.
