---
id: "02"
title: "Fix the idle window"
sp: 1
status: done
plan: "plans/19700102-login-timeout/index.md"
---

# M02: Fix the idle window

**Goal**: Sessions survive the full documented idle window.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Compare against the window's end, not its last tick | `src/auth/session.py` | 1 | done |

## Definition of Done

### Task 2.1

- [x] The regression test from M01 passes.

## Verify

`pytest tests/auth/session_test.py`
