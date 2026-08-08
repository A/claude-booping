---
title: Cleanup of references invalidated by a plan belongs inside the same sprint, not a follow-up sweep
targets:
  - groom/draft-plan
retro: retrospectives/20260425-migrate-retro-skill-to-template-pipeline.md
---

**Rule**: When a plan's work invalidates references — deleted partials, renamed agents, status-block lines in CLAUDE.md, broken doc links — the cleanups must be milestone tasks inside the same sprint, with their own DoD. A half-stale working tree at sprint close is itself the documentation gap; "we'll sweep this up after" leaves the repo inconsistent for hours or days and reliably gets dropped.

**Example**: M3 of the /retro template-pipeline migration made deleting `docs/partial_plan_transitions_retro.md` and updating the CLAUDE.md "Status (April 2026)" block its own milestone with explicit DoD checks; both landed inside the migration sprint instead of leaving stale references behind.
