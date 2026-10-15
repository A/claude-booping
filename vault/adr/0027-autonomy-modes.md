---
type: adr
title: A project chooses supervised or autonomous work
summary: In a supervised project the user runs groom then develop and reviews; in an autonomous one a manager grooms and builds in batches; the project's config sets the mode.
created_by: claude
created_at: 2026-10-15
updated_at: 2026-10-15
status: accepted
values: [value/0009, value/0007]
---

## Context

The owner works two ways (2026-10-15): in work projects where risk and responsibility
are high, groom then develop with a review of what happens; in pet projects or
product-fit experiments, a manager that grooms and builds on its own, usually in
batches. Taking open items and other work autonomously needs to know which applies.

## Decision

A project config key sets the mode: `supervised` (default) — runs stop at their
review gates and the user drives groom then develop; `autonomous` — a manager takes
open items or a request, grooms and builds through the playbooks in batches, auto-
confirming gates and recording defaults. A state that should not exist — uncommitted
changes on a branch when a migration runs — is shown to the user and asked about in
either mode.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Mode per project](#mode-per-project) | accepted | low | high | Matches how the owner works |
| [One fixed mode](#one-fixed-mode) | rejected | low | high | Wrong for one of the two kinds |

### Mode per project

The project's config chooses supervised or autonomous.

- **Pros:** risky projects keep a human in the loop; experiments move fast.
- **Cons:** two behaviours to keep working.
- **Complexity:** low.
- **Reversibility:** high.

### One fixed mode

Every project works the same way.

- **Pros:** one behaviour.
- **Cons:** too slow for experiments or too loose for risky work.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- Confirmation: with `autonomous`, a specs playbook run takes open items through groom
  and develop without stopping; with `supervised`, it stops at the plan review.
