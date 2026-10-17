---
type: story
title: Groom
summary: Groom shapes a feature, bug or refactor into a specified, estimated plan the user approved, ending at ready-for-dev.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want a feature, bug or refactor shaped into a specified, estimated plan
I approved, so that develop can carry it out without coming back to me.

## Criteria

- Clarifies the request at intake before any drafting.
- Drafts the whole plan in one pass: `draft-plan` researches the code in-session, delegating bulk reads to the researcher, then drafts against the vault's plan template ([adr/0030](../adr/0030-groom-drafts-the-whole-plan-in-one-pass.md)).
- Creates `plans/{slug}/index.md` and one file per milestone under `milestones/` with `booping plan split` from the one-file draft ([adr/0031](../adr/0031-a-script-cuts-the-plan-into-milestone-files.md)).
- Drafts milestones, tasks and SP estimates and checks the milestone contract with mdcheck ([adr/0038](../adr/0038-milestone-shape-is-an-mdcheck-schema.md)); no separate review step ([adr/0035](../adr/0035-groom-has-no-separate-review-step.md)).
- Stops at a single approval gate near the end, landing the plan at `ready-for-dev`.
