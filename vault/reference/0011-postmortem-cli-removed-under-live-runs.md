---
type: reference
title: "Postmortem: CLI commands removed under live runs"
summary: On 2026-10-17/18 booping removed the budget, correction and defaults commands while autonomous runs in another project still called them, and those runs failed.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: live
tags: [postmortem]
---

## Facts

- 2026-10-17/18: `booping budget` was removed in d5670a0 and `booping correction` and `booping defaults` in 50f8495, on release/2.0.0.
- At the same time the lightspace-android project ran autonomous booping runs, and their playbooks and rules still called these commands: project-manager's "Corrections" used `booping correction add`, and autonomous gates logged via `booping defaults add`. The runs failed with `invalid choice: 'budget'` (lightspace feedback, point 6).
- The current tree holds no reference to the removed commands (checked 2026-10-18).
- How the lightspace runs loaded the plugin, whether from this working tree or from a released version, is not named in the source.
- Cause: a removal landed while runs that had loaded the old bodies, or that render from the same plugin, were still going. Nothing tells a live run that the CLI it calls changed under it.
- Remedy: [clarify] not decided. Candidates are to run other projects only on a released plugin version, or to have a removal leave a stub that prints what replaced the command. Owner to settle.

## How to check

- [lightspace-android feedback](../notes/20261018-lightspace-android-feedback.md), point 6; commits d5670a0 and 50f8495.
