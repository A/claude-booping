---
type: rule
title: Decisions are listed for acceptance
summary: Before the user accepts anything, the agent lists every decision it takes as settled, one numbered line each, marking its own proposals; an unanswered item is never accepted.
created_by: claude
created_at: 2026-10-17
updated_at: 2026-10-17
status: accepted
---

## Rule

Before the user accepts anything — a gate, a plan, a record drafted from the dialogue, a package of answers — the agent shows every decision it will take as settled as a numbered list, one plain line each, readable at a glance, never only inside prose or folded into one sentence. Each line names its source: the user's words, or the agent's own proposal. The user accepts the list or clarifies lines of it. A decision that was never on such a list, or a question the user left unanswered, is not accepted: it stays open, and where it lands in a record or a plan it is marked `[clarify]` (owner, 2026-10-17).

The driving protocol (`src/templates/_partials/_playbook_driving.j2`) and the specs guidance carry this rule for every playbook and every record, so it needs no targets.

## Follows from

- [Effective human review](../../vault/value/0008-effective-human-review.md) — a list is read and answered line by line; a decision buried in prose is easy to miss.
- [Adjustable control](../../vault/value/0009-adjustable-control.md) — the user sees what the agent decides alone and can stop it.
- [Guides to the goal](../../vault/value/0013-guides-to-the-goal.md) — the system is clear to the user: what it is about to take as decided is in plain sight.
- [Postmortem: the budget gate slipped into the core unasked](../../vault/reference/0008-postmortem-budget-gate-slipped-into-core.md) — a one-line proposal and an unanswered question became core code.
