---
title: Lint housekeeping and lesson hygiene
type: feature
status: cancelled
summary: "Extends /booping:lint with housekeeping checks: orphaned retros, age nudges, lesson decoupling, stale-lesson detection"
source: "split-from:plans/20260422-plans-as-data-refactor.md"
created: 2026-04-22 16:42
---

# Lint housekeeping and lesson hygiene

## Context

Building on S2 (`plans/20260422-chat-overview-lint-core.md`), this sprint extends `/booping:lint` with housekeeping and lesson-hygiene checks that surface longer-lived drift rather than immediate state drift:

- Orphaned retros: files under `retrospectives/` with no plan frontmatter pointing at them via `retro:`.
- Broken `retro:` links: plan frontmatter references a retrospective file that does not exist.
- Age nudges for plans stuck in `awaiting-retro` or `awaiting-learning` beyond a configurable threshold.
- Lesson-file decoupling: enforce one lesson per file. Lint flags files containing multiple lesson blocks but does NOT auto-split (Anton's call: auto-splitting is too invasive for a lint rule).
- Domain-tag suggestions for untagged lessons. Fixed enum from `docs/agent-wiring.md` (`tech`, `product`, `qa`, `code`, `all`); new domain values are allowed but emit a lint warning so they get reviewed.
- Stale-lesson detection: a lesson is "stale" if it has not been referenced in the last N grooming sessions (default 10, configurable via `~/Claude/{project}/_booping/config.yml`). Session count is the unit, not calendar days — matches how grooming cadence actually works.

Deliverables include the config schema (`_booping/config.yml`), the session-count tracking (likely piggy-backing on `metrics/lesson-hits.md` or a new `metrics/grooming-sessions.log`), and documentation of the fixed-enum + warn-on-new-value domain policy.

Depends on S2 shipping: the `/booping:lint` skill scaffolding, frontmatter schema validator, and `--fix` plumbing must already exist.
