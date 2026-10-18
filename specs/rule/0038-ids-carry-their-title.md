---
type: rule
title: Ids in chat carry their title
summary: Every id said in chat — an open item, an ADR, a rule, a plan — is followed by its short title; newly filed items are listed one per line with their title.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: accepted
---

## Rule

Every id the agent says in chat — an open item, an ADR, a rule, a plan, any other record — is
followed by its short title, so the user reads what it names without opening it. Newly filed items
are listed one per line, in the user's language: `Создан {id}: {title}` in Russian,
`Created {id}: {title}` in English.

The driving protocol (`src/templates/_partials/_playbook_driving.j2`) carries this rule for every playbook, so it needs no targets.

## Follows from

- [Effective human review](../../vault/value/0008-effective-human-review.md) — an id with its title
  is readable at a glance.
- [Guides to the goal](../../vault/value/0013-guides-to-the-goal.md) — the user follows the run
  without looking ids up.
