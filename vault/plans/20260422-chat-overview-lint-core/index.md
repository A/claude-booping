---
title: Chat overview and lint core
type: feature
status: cancelled
summary: "New /chat overview phase (status counts) and /booping:lint core: frontmatter validation, sprints.md drift, --fix"
source: "split-from:plans/20260422-plans-as-data-refactor.md"
created: 2026-04-22 16:42
---

# Chat overview and lint core

## Context

Once plans become the canonical state record (S1: `plans/20260422-plans-as-data-refactor.md`), `/chat` and a new `/booping:lint` skill can read that state and surface drift without Anton reading files himself. This sprint adds:

- A `/chat` overview phase that queries `booping-plans list --format=json` and reports per-status counts (planned / in-progress / awaiting-retro / awaiting-learning) plus a nudge when the backlog or awaiting-retro pile grows (e.g. "N backlog plans — review them?", "M plans awaiting retro for ≥7 days").
- A new `/booping:lint` skill core that:
  - validates plan frontmatter against the S1 schema (required keys per status, enum values, date formats),
  - detects `sprints.md` drift by running `sync-sprints` in a temp location and diffing against the committed file,
  - reports pending retros (status=`awaiting-retro` with no retro file) and pending learnings (status=`awaiting-learning` with no matching lesson extraction),
  - finds stray plan-shaped markdown files outside `plans/` (top-level or in `backlog/` from an un-migrated install) and suggests `git mv` commands,
  - supports `--fix` that auto-applies the safe subset (regenerate `sprints.md`, normalise frontmatter key order).

GitHub Actions CI to run `just lint-backlog` + the lint skill's validation subset is folded into this sprint (deferred here from S1).

Depends on S1 shipping: `plans/` directory, frontmatter schema, and `booping-plans` CLI must exist before any of this work starts. Out of scope here: the housekeeping checks (orphan retros, age nudges, lesson decoupling, domain tags, staleness) — those live in S3 (`plans/20260422-lint-housekeeping.md`).
