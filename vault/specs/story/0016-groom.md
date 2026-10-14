---
type: story
title: Groom
summary: Groom shapes a feature, bug or refactor into a specified, estimated plan the user approved, ending at ready-for-dev.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **a user**, I want a feature, bug or refactor shaped into a specified, estimated plan
I approved, so that develop can carry it out without coming back to me.

## Criteria

- Clarifies the request at intake before any drafting.
- Researches the codebase and the web as parallel detached passes; other steps run
  inline or assisted.
- Creates `plans/{slug}/index.md` with one file per milestone under `milestones/` in a
  single `booping scaffold` call, stamping `commit:` from repo HEAD, and offers the
  vault's plan templates as the drafting shape.
- Drafts milestones, tasks and SP estimates, and cross-reviews the draft in a detached
  pass when `core.groom_playbook.cross_review_agent` names an agent.
- Stops at a single approval gate near the end, landing the plan at `ready-for-dev`.
