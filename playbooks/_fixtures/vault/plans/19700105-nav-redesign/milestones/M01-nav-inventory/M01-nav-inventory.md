---
id: "01"
title: "Navigation inventory"
sp: 5
status: pending
plan: "plans/19700105-nav-redesign/index.md"
---

# M01: Navigation inventory

**Goal**: Every navigation entry is listed with the breakpoint it breaks at.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Inventory the entries and measure the overflow | `src/nav/entries.ts` | 5 | pending |

## Definition of Done

### Task 1.1

- [ ] The inventory names an owner for each entry.

## Verify

`npm test -- nav/entries`
