---
type: idea
title: Learn prefers guidance to validators
summary: Learn should propose guidance that steers a step away from an issue, and propose a validator or sub-agent check only for critical cases.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: open
sources: [vault/notes/Improvment ideas.md]
---

## Idea

When learn turns a retro finding into a change, it should prefer guidance that helps a
step avoid the issue over adding a validator. Sub-agents are expensive and belong only in
critical situations. The learn steps (`extract-candidates`, `write`) and the target list
in `playbooks/learn/_partials/_learn_targets.j2` carry no such preference today.

## How to check

- [clarify] The source names no check. Proposed: count, over the lessons in
  `vault/_lessons/` and the learn runs recorded in `vault/retrospectives/`, how many
  proposals were a validator or a sub-agent check rather than guidance; if there are
  none, the idea has nothing to fix.
