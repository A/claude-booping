---
type: rule
title: Decisions are asked in prose
summary: An approval, or any decision the user must understand the context to make, is asked in prose, one at a time with compact context and a counter; a multiple-choice tool only for mechanical picks.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-17
status: accepted
---

## Rule

At a review gate, the agent presents the artefact and asks for approval in prose, at the end of the message. It never asks through a multiple-choice question tool: approval means the user may read and answer with feedback of any length, which a set of options does not allow, and a prose question distracts less (owner, 2026-10-16). A reply that asks for changes sends the run back to the step that drafts the artefact; the gate does not absorb the change and ask again.

The same holds for every decision the user has to understand the context to make — settling a conflict, a design fork, a review finding, a departure from a record: the agent asks in prose, one decision at a time, each with the compact context it needs (what the records say, what the code does, where it came from) and its own proposal, and with a counter (`[n/total]`) when several are queued. The user reads, asks back, then decides; options the agent prepared cut that short (owner, 2026-10-17). What the user accepts at a gate is the decision list of [booping:rule/0033](0033-decisions-listed-for-acceptance.md). A multiple-choice tool is only for a mechanical pick whose answer needs no context, such as a branch name or which of two files.

The driving protocol (`src/templates/_partials/_playbook_driving.j2`) carries this rule for every playbook, so it needs no targets.

## Follows from

- [Effective human review](../../vault/value/0008-effective-human-review.md) — the review step takes the user's full feedback where it is convenient for them.
- [Adjustable control](../../vault/value/0009-adjustable-control.md) — the user steers by writing back, not by picking from options the agent prepared.
