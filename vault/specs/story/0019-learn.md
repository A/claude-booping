---
type: story
title: Learn
summary: Learn turns retrospective findings the user confirmed into targeted lessons or CLAUDE.md entries.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **a user**, I want retrospective findings turned into durable behaviour changes I
confirmed, so that the next runs do not repeat the same mistakes.

## Criteria

- Extracts atomic candidates from the retrospective and sweeps them against existing
  lessons.
- Shows the full playbook table of contents and fetches the targets of each touched
  playbook.
- Confirms a review table with the user before anything is written, each row carrying
  its exact `targets:`.
- Routes each accepted item to exactly one destination: a targeted lesson in the
  Project Vault or the repo's `CLAUDE.md`.
- Closes the covered retrospective at `done`.
