---
type: story
title: Learn
summary: Learn turns retrospective findings the user confirmed into rule records in the project specs tier or CLAUDE.md entries.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P1
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want retrospective findings turned into durable behaviour changes I
confirmed, so that the next runs do not repeat the same mistakes.

## Scenarios

1. The user runs `/playbook learn` on a retrospective at `awaiting-learning`.
2. The run decomposes the retrospective into atomic candidates, each routed to one
   destination, and sweeps them against the rules of the three specs tiers and the
   repo's `CLAUDE.md`: update, create, covered or conflict.
3. It reads the playbook table of contents and the targets of each touched playbook, and
   presents one review table, each rule row carrying its exact `targets:`.
4. The user accepts all, rejects rows by number or adds a row; the run writes the
   accepted items and closes the retrospective at `done`.

## Edge cases

- The project has no specs tier yet: the run creates it before writing the first rule.
- A finding a core or global rule already holds: shown as `covered`, never written.
- A finding that contradicts an existing rule: flagged a conflict for the user to resolve in the review table.
- A user row carrying two rules: split into two before writing.

## Criteria

- Extracts atomic candidates from the retrospective and sweeps them against existing
  rules.
- Shows the full playbook table of contents and fetches the targets of each touched
  playbook.
- Confirms a review table with the user before anything is written, each row carrying
  its exact `targets:`.
- Routes each accepted item to exactly one destination: a rule record in the
  project specs tier or the repo's `CLAUDE.md`.
- Closes the covered retrospective at `done`.
