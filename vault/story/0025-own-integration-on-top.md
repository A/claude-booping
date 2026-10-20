---
type: story
title: Own integration on top of booping
summary: An advanced user wires their own triggers, schedules, tracker flows and usage guards on top of booping's surfaces; the core ships none of them.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-20
status: done
priority: P3
sources: [vault/value/0017-launching-and-guarding-runs-is-userland.md]
---

As **an advanced user**, I want to wire my own triggers, schedules, trackers and usage guards on top of booping, so that the core stays a framework and my setup stays mine ([value/0017](../value/0017-launching-and-guarding-runs-is-userland.md)).

## Scenarios

1. The user's scheduler, board event or messenger hook files the incoming work as an
   open item with `booping create`, whatever channel it came from.
2. The same trigger launches a playbook run on it, for example `booping run groom` or
   `booping run develop`.
3. The user shapes the core playbooks for their setup with project or global playbooks,
   hooks and rules carrying `targets`.
4. The user's own guard decides when a run may start; booping runs it as any other run.

## Edge cases

- A setup with no integration at all: booping works as shipped, driven by hand.

## Out of scope

- A scheduler, a trigger, a tracker-specific integration or a usage gate in the core.

## Criteria

- A run starts from anything that can launch a playbook run: a scheduler, a board event, a messenger hook.
- Incoming work enters as an open item, whatever channel it came from.
- Project or global playbooks, hooks and rules with `targets` shape the core playbooks for the setup.
- The core ships no scheduler, no trigger, no tracker-specific integration and no usage gate.
