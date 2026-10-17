---
type: story
title: Specs review with the owner
summary: The system reviews the owner's specs, fixes what is plainly stale, and brings the owner only the decisions that are theirs, one at a time and kept across restarts.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: done
sources: [playbooks/specs/guide/prompt.md]
---

As **the owner**, I want the system to review my specs and bring me only what needs my decision, so that the specs stay true without me rereading them.

## Criteria

- Reads every record type in every tier the project reaches and puts each record to its type test ([booping:rule/0034](../../specs/rule/0034-specs-review-tests-each-record.md)).
- Applies a fix that only makes a record say what is already decided or true, and reports it.
- Files every decision that is mine as a `clarify` item, so a restart picks the queue up from the open items; in the dialogue it asks one at a time in prose, with compact context, its own proposal and a counter ([booping:rule/0032](../../specs/rule/0032-approval-asked-in-prose.md)).
- Lists what it is about to take as decided before I accept anything ([booping:rule/0033](../../specs/rule/0033-decisions-listed-for-acceptance.md)).
- An incident it uncovers is written up as a `reference` tagged `postmortem`: timeline, causes, remedies.
