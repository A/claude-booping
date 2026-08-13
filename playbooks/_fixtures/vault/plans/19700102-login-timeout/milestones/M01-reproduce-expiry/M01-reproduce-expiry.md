---
id: "01"
title: "Reproduce the early expiry"
sp: 1
status: done
plan: "plans/19700102-login-timeout/index.md"
---

# M01: Reproduce the early expiry

**Goal**: A failing test pins the session expiring one minute early.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Regression test at the documented idle window | `tests/auth/session_test.py` | 1 | done |

## Definition of Done

### Task 1.1

- [x] The test fails on the unfixed code and names the observed drift.

## Verify

`pytest tests/auth/session_test.py`
