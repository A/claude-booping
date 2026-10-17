---
type: story
title: Project manager
summary: One manager the user talks to files every request as an item and carries it through groom, develop, review and merge, with a status computed from the vault.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: done
sources: [vault/plans/202610152006_project-manager-playbook/index.md]
---

As **a user**, I want one manager to talk to that turns what I say into tracked work and carries it to the end, so that no request, question or finished run gets lost between tracks.

## Criteria

- Every user message is split into items as it arrives, asides included, each keeping the user's words verbatim ([adr/0025](../adr/0025-open-items-are-an-index.md)).
- "What is going on" is computed by code from items, plans, runs and unreviewed records — no stored handoff that can go stale.
- A question lives on its item's sidecar; chat only points to the item.
- Every launched run is recorded with its item, and a finished run surfaces on the next turn.
- In an autonomous project, small items are batched by size and skip grooming.
