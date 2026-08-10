---
id: "01"
title: "Rate limit store"
sp: 8
status: done
plan: "plans/19700106-api-throttling/index.md"
---

# M01: Rate limit store

**Goal**: Per-client request counts are tracked in a shared window store.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Sliding-window counter keyed by client | `src/api/limits.py` | 8 | done |

## Definition of Done

### Task 1.1

- [x] Counts expire with their window instead of growing unbounded.

## Verify

`pytest tests/api/limits_test.py`
