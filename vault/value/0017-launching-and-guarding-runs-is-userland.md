---
type: value
title: Launching and guarding runs is userland
summary: When and how development runs start — triggers, schedules, tracker and messenger integrations — and guarding usage limits are the user's, not booping's; booping offers an integration surface at most.
kind: non-value
created_by: claude
created_at: 2026-10-17
updated_at: 2026-10-17
---

Booping does not solve how development is launched: triggers from a task moving on a board, a Jira or Multica integration, an event in a messenger such as ntfy, a schedule or a nightly run are userland. The same holds for the subscription's usage limits: booping never stops a user from spending them, and a user who wants a guard builds it. At most booping offers a surface to integrate through, such as rules and hooks (owner, 2026-10-17).

## In practice

The core ships no scheduler, no trigger, no tracker-specific integration and no usage gate; a user builds them on top of `booping run`, `booping items add` and playbook hooks, at the global or the project tier.
