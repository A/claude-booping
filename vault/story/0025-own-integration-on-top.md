---
type: story
title: Own integration on top of booping
summary: An advanced user wires their own triggers, schedules, tracker flows and usage guards on top of booping's surfaces; the core ships none of them.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: done
sources: [vault/value/0017-launching-and-guarding-runs-is-userland.md]
---

As **an advanced user**, I want to wire my own triggers, schedules, trackers and usage guards on top of booping, so that the core stays a framework and my setup stays mine ([value/0017](../value/0017-launching-and-guarding-runs-is-userland.md)).

## Criteria

- A run starts from anything that can launch a playbook run: a scheduler, a board event, a messenger hook.
- Incoming work enters as an open item, whatever channel it came from.
- Project or global playbooks, hooks and rules with `targets` shape the core playbooks for the setup.
- The core ships no scheduler, no trigger, no tracker-specific integration and no usage gate.
