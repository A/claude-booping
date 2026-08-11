---
id: "02"
title: "Throttle middleware"
sp: 5
status: in-progress
plan: "plans/19700106-api-throttling/index.md"
---

# M02: Throttle middleware

**Goal**: A client over its limit gets a 429 instead of starving the rest.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Reject over-limit requests with `Retry-After` | `src/api/middleware.py` | 5 | in-progress |

## Definition of Done

### Task 2.1

- [ ] An under-limit client is never rejected.

## Verify

`pytest tests/api/middleware_test.py`
