---
id: "01"
title: "Orphan sweep on expiry"
sp: 2
status: done
plan: "plans/19700103-session-cleanup/index.md"
---

# M01: Orphan sweep on expiry

**Goal**: Expiring a session deletes the rows that hang off it.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Cascade the delete from the session row | `src/auth/cleanup.py` | 2 | done |

## Definition of Done

### Task 1.1

- [x] No orphaned rows remain after an expiry.

## Verify

`pytest tests/auth/cleanup_test.py`
