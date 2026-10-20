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
- At the same time another project ran autonomous booping runs, and their playbooks and rules still called these commands: project-manager's "Corrections" used `booping correction add`, and autonomous gates logged via `booping defaults add`. The runs failed with `invalid choice: 'budget'` (that project's feedback, point 6).
- The current tree holds no reference to the removed commands (checked 2026-10-18).
- `booping` on PATH is this repo's working tree, so runs in every other project execute whatever the release branch holds at that moment (2026-10-18). The operator rename in plan 202610180333_vault-file-operators hits live runs the same way.
- Cause: a removal landed in the working tree that live runs in other projects execute from. Nothing tells a live run that the CLI it calls changed under it.
- Remedy: [clarify] not decided. Candidates are to run other projects only on a released plugin version, or to have a removal leave a stub that prints what replaced the command. Owner to settle.

## How to check

- The other project's feedback, point 6 (private note, not published); commits d5670a0 and 50f8495.
