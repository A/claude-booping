---
type: rule
title: Approval is asked in prose
summary: A review gate that asks the user to approve a plan or an artefact asks in prose at the end of the message, never through a multiple-choice question tool.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-16
status: accepted
targets: [groom, develop, code-review]
brief: Ask for approval at a review gate in prose at the end of your message, never through AskUserQuestion; a change request sends the run back to drafting.
---

## Rule

At a review gate, the agent presents the artefact and asks for approval in prose, at the
end of the message. It never asks through a multiple-choice question tool: approval means
the user may read and answer with feedback of any length, which a set of options does not
allow, and a prose question distracts less (owner, 2026-10-16). A reply that asks for
changes sends the run back to the step that drafts the artefact; the gate does not absorb
the change and ask again.

## Follows from

- [Effective human review](../../vault/value/0008-effective-human-review.md) — the review
  step takes the user's full feedback where it is convenient for them.
- [Adjustable control](../../vault/value/0009-adjustable-control.md) — the user steers by
  writing back, not by picking from options the agent prepared.
