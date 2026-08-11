---
id: "02"
title: "Single-row layout"
sp: 3
status: pending
plan: "plans/19700105-nav-redesign/index.md"
---

# M02: Single-row layout

**Goal**: The primary navigation fits one row at every breakpoint.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Collapse overflow entries behind a menu | `src/nav/Bar.tsx` | 3 | pending |

## Definition of Done

### Task 2.1

- [ ] No entry wraps to a second row at the narrowest breakpoint.

## Verify

`npm test -- nav/bar`
