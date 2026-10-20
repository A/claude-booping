---
type: conflict
title: Effective human review ↔ Plans run to the end ↔ Quality at a rational cost
summary: More review checkpoints make review effective but cost run time and stops; core playbooks stop for review once, and groom runs no separate review step.
created_by: claude
created_at: 2026-10-17
updated_at: 2026-10-17
status: resolved
values: [value/0008, value/0007, value/0012]
---

## Conflict

[value/0008](../value/0008-effective-human-review.md) checks the cheap, compact artefact before the expensive detail is built on it, at the trade-off of more review checkpoints in a run. [value/0007](../value/0007-plans-run-to-the-end.md) has the agent carry a plan to the end on its own, and [value/0012](../value/0012-quality-at-a-rational-cost.md) spends tokens rationally and keeps a balance between simplicity and the quality of the result. Each added checkpoint or review step is another stop, more calls and more minutes per run.

## Resolution

[adr/0015](../adr/0015-one-review-gate-per-run.md): each core playbook stops for review once and takes other user decisions in-step; the old groom's four confirm points went, since gate round-trips were the playbook's remaining cost. [adr/0035](../adr/0035-groom-has-no-separate-review-step.md): a fresh review of the plan lifts quality but adds about 10 minutes a plan (4–5 at best) for a gain inside the plans' own spread, so groom runs no separate review step; the step stays available behind `core.groom_playbook.cross_review_agent` for a user who wants it.
