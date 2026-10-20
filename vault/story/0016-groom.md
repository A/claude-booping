---
type: story
title: Groom
summary: Groom shapes a feature, bug or refactor into a specified, estimated plan the user approved, ending at ready-for-dev.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P0
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want a feature, bug or refactor shaped into a specified, estimated plan
I approved, so that develop can carry it out without coming back to me.

## Scenarios

1. The user runs `/playbook groom` with a request; `intake` clarifies it, settles the
   scope and creates the plan directory with its briefing and a `commit:` at repo HEAD.
2. `draft-plan` researches the code the request touches, handing bulk reads to the
   research agent, and drafts the whole plan into `draft.md` against the matching plan
   template.
3. `booping plan split` cuts the draft into `index.md` and one milestone file per
   milestone; mdcheck checks the milestones against the contract and the run fixes what
   it flags.
4. `present` shows the approach, milestones, SP totals and the check; the user approves
   and the plan lands at `ready-for-dev`.

Change request: at `present` the user asks for a change touching the plan itself; the
run goes back to drafting, edits `draft.md` and splits again.

## Edge cases

- A call only the user can make, in an autonomous run: the question is written to the plan's `clarifications.md` and the run parks at `awaiting-clarification`.
- A draft the split cannot cut: it goes to the split fallback agent, which rewrites it into the format, and the run splits again.
- A task estimated at the redecompose threshold or above: the run cannot leave drafting until it is split.
- The user corrects the run: the correction is logged verbatim under `corrections/`.

## Criteria

- Clarifies the request at intake before any drafting.
- Drafts the whole plan in one pass: `draft-plan` researches the code in-session, delegating bulk reads to the researcher, then drafts against the vault's plan template ([adr/0030](../adr/0030-groom-drafts-the-whole-plan-in-one-pass.md)).
- Creates `plans/{slug}/index.md` and one file per milestone under `milestones/` with `booping plan split` from the one-file draft ([adr/0031](../adr/0031-a-script-cuts-the-plan-into-milestone-files.md)).
- Drafts milestones, tasks and SP estimates and checks the milestone contract with mdcheck ([adr/0038](../adr/0038-milestone-shape-is-an-mdcheck-schema.md)); no separate review step ([adr/0035](../adr/0035-groom-has-no-separate-review-step.md)).
- Stops at a single approval gate near the end, landing the plan at `ready-for-dev`.
