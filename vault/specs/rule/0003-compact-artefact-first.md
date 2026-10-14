---
type: rule
title: The compact artefact is reviewed before the detail
summary: Where a human reviews, a run first produces a compact artefact the human can read and reorder, and builds the expensive detail only on the reviewed one.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
---

## Rule

A run with a human review step first produces a compact artefact — a feature
index before the stories, a plan outline before the milestones — and stops for
the human to read, reorder, fix and decompose it. The expensive detail is built
only on the reviewed artefact, so a later review never sends the run several
steps back.

## Follows from

- [Effective human review](../values/0001-booping.md#effective-human-review) — the cheap artefact
  is where a wrong direction is cheapest to catch.
