---
type: idea
title: Plans draft ADRs for their real forks
summary: Where a plan meets a real design fork, groom writes an ADR draft with the alternatives and its choice, and offers it to the owner for review unless the run is autonomous.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-16
status: open
---

## Idea

A plan's decisions today are lines in a Decisions table. The owner proposed (2026-10-16)
that groom drafts a full ADR for each real fork the work meets — context, the
alternatives with their trade-offs, the choice — so the decision goes up into the specs
in the shape every other decision has, and the owner reviews the fork where it belongs.
In a supervised run groom offers the drafts for review; in an autonomous run it records
them as `proposed` with its choice and moves on. This is taken up after the groom
refactoring ([idea/0003](0003-groom-depth-scales-with-task.md)) picks the leading variant,
not inside its benchmark.

## How to check

- [clarify] Proposed: on two corpus tasks with a real fork (s1 storage of the feed
  identity, c1 slice boundary), groom with ADR drafts and without; compare the owner's
  review time and how often the owner changes the choice at review versus after
  development.
