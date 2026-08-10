---
title: Session cleanup sweep
type: refactoring
status: done
sp: 3
created: 1970-01-03
planned: 19700103 08:00
started: 19700103 09:00
completed: 19700103 11:00
retro: retrospectives/197001031100_session-cleanup.md
code_reviews:
  - codereviews/19700103-session-cleanup/197001031300.md
goal: Expired sessions leave no rows behind.
summary: Sweep orphaned session rows on expiry.
commit: cccccccccccccccccccccccccccccccccccccccc
---

# Session cleanup sweep

Fixture plan — directory shape, already covered by a retrospective, so the retro queue skips it and the learn queue has a retrospective to pick up.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | Orphan sweep on expiry | 2 | done |
| 02 | Backfill existing orphans | 1 | done |

