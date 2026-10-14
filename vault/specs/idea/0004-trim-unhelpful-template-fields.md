---
type: idea
title: Trim template fields that do not help
summary: Drop the business-goal logic from grooming and replace the retro action table's Owner column with "when to do it".
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: open
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/TODO.md, vault/notes/Notes.md
---

## Idea

Two small trims of content that does not earn its place:

- **Business-goal logic.** The source says it does not help and is AI-generated. It is
  still in the code: the `feature` task type's description in `src/config.yaml`
  ("Needs business goal"), `docs/task_feature.md` (no goal → no `ready-for-dev`) and the
  "Business-goal acceptance" item in `docs/plan_templates/backend.md`.
- **Retro action table.** Remove the `Owner` column and add "When to do it?" in
  `docs/retrospective_template.md`. Today the `Owner` column already takes "Next sprint /
  Person / standing", so part of the change is a rename.

## How to check

- [clarify] The source names no check. Proposed: read the last five done feature plans
  and the last five retros in this vault and note whether the goal section or the `Owner`
  cell changed anything a later step did; if neither did, trim both.
