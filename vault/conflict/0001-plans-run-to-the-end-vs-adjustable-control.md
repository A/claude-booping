---
type: conflict
title: Plans run to the end ↔ Adjustable control
summary: An agent that carries a plan to the end on its own pulls against a human who can review deeply and take control back; the run's autonomy mode settles which applies.
created_by: claude
created_at: 2026-10-17
updated_at: 2026-10-18
status: resolved
values: [value/0007, value/0009]
---

## Conflict

[value/0007](../value/0007-plans-run-to-the-end.md) has the agent carry a plan through to the end on its own unless force majeure stops it. [value/0009](../value/0009-adjustable-control.md) has the human able to review the system deeply, or give the agent more freedom, and take control back easily. Every stop for the human's review is a point where the plan does not run on its own; every step run without review is a point where the human gave up control.

## Resolution

The run's mode settles it, in prose ([adr/0036](../adr/0036-autonomy-is-settled-in-prose.md)): the user says so, or `booping run … --autonomous` launches it ([value/0009](../value/0009-adjustable-control.md)). Supervised (the default) stops at the runs' review gates and the user drives groom then develop; autonomous lets a manager groom and build in batches, auto-confirming gates and recording the defaults it chose, so what the agent did without review stays visible. A state that should not exist, such as uncommitted changes on a branch when a migration runs, is asked about in either mode.
