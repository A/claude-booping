---
type: idea
title: Claude wires a worker agent into booping on request
summary: The user asks Claude Code to add a native agent or a CLI-backed agent to a playbook, and Claude writes the agent, the config entry and the targeted rule.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: open
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/User Stories.md
---

## Idea

The user wants Claude Code to add an agent to booping's harness when they need one —
either a native Claude Code agent or a CLI agent (a `pi` call or another external
harness) that saves tokens. Choosing such an agent by `good_for` / `bad_for` and
delegating to it already works (`core.{name}_playbook.agents.<id>`), and
`documentation/integrating-external-agents.md` and the external-agents recipe describe
the manual steps; no playbook or skill does the wiring for the user.

## How to check

- [clarify] The source names no check. Proposed: in a fresh session on a project vault,
  ask Claude "add a codex worker to develop" with no other help and check whether it
  produces a working proxy agent, the config entry and the targeted rule from the
  documentation alone; if it does, the idea is covered by the docs and is rejected.
