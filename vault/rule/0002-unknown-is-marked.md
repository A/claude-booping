---
type: rule
title: What is not in the source is marked, not invented
summary: A record or artefact states only what its source says; an open point is marked [clarify] or "not named in the source", never filled in by the agent.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
---

## Rule

A record or a run artefact states only what its source says: the conversation,
the user's answers, the code, a measurement, a document read. An option, an
argument or a detail the source lacks is written as "not named in the source";
a choice the agent made by default is marked `[clarify]` with one sentence on
what to settle; a reason that is only the user's preference is called that.

## Follows from

- [Adjustable control](../value/0009-adjustable-control.md) — the human finds what the
  agent decided alone only if it is marked.
- [Effective human review](../value/0008-effective-human-review.md) — a review checks the
  marks instead of rereading everything for what was guessed.
