---
id: "02"
title: "Backfill existing orphans"
sp: 1
status: done
plan: "plans/19700103-session-cleanup/index.md"
---

# M02: Backfill existing orphans

**Goal**: Rows orphaned before the sweep landed are cleared once.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | One-shot backfill command | `src/auth/backfill.py` | 1 | done |

## Definition of Done

### Task 2.1

- [x] Re-running the command is a no-op.

## Verify

`pytest tests/auth/backfill_test.py`
