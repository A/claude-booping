---
type: story
title: Project manager
summary: One manager the user talks to files every request as an item and carries it through groom, develop, review and merge, with a status computed from the vault.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-20
status: done
priority: P1
---

As **a user**, I want one manager to talk to that turns what I say into tracked work and carries it to the end, so that no request, question or finished run gets lost between tracks.

## Scenarios

1. The user opens `/playbook project-manager`; it posts `booping status` and names what
   to act on first: finished or lost runs, items waiting on the user, plans ready for
   develop, plans without a review, open items.
2. The user writes a message with several requests; the manager files each as an item
   in the user's words and lists the items it created.
3. A planned item runs groom, then `booping run develop` and `booping run code-review`
   as recorded runs; the next turn surfaces each finished run, and the branch is merged
   locally on the user's yes.
4. A question the manager cannot settle goes into the item's body and the item moves to
   `clarify`; the user answers and the item returns to `open`.

Tiny fixes: in an autonomous project, small items are sized and packed into one worker
briefing, committed once per item and closed without grooming.

## Edge cases

- An instruction for this session, an answer or a gate confirmation: no item is filed.
- A develop run that fails: reported with its log, never retried silently.
- A second develop or code-review run on the same checkout: queued until the running one ends.
- An autonomous session: the manager settles the plan approval and the merge itself and logs each as an agent decision.

## Out of scope

- Pushing, opening a pull request or deploying: only when a project rule says how.

## Criteria

- Every user message is split into items as it arrives, asides included, each keeping the user's words verbatim ([adr/0025](../adr/0025-open-items-are-an-index.md)).
- "What is going on" is computed by code from items, plans, runs and unreviewed records — no stored handoff that can go stale.
- A question lives in its item's body, the item parked in `clarify`; chat only points to the item.
- Every launched run is recorded with its item, and a finished run surfaces on the next turn.
- In an autonomous project, small items are batched by size and skip grooming.
