---
type: rule
title: Every step ends by naming the next one
summary: A playbook step or a run that hands back to the user ends by naming the next step and how to call it; a premature call says what is missing.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
---

## Rule

A playbook run that hands control back to the user ends by naming the next step
and the exact way to call it — after grooming, how to call develop. A call on an
artefact that is not ready for it — an under-groomed plan given to develop —
says what is missing and which step makes it ready. The user may take another
path; the hint does not block it.

## Follows from

- [Guides to the goal](../values/0001-booping.md#guides-to-the-goal) — the system leads to the goal
  and lets a professional step aside.
