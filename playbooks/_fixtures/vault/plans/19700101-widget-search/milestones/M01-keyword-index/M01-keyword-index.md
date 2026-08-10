---
id: "01"
title: "Keyword index"
sp: 3
status: done
plan: "plans/19700101-widget-search/index.md"
---

# M01: Keyword index

**Goal**: Every widget write lands in a full-text index.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Index the catalog on write | `src/widgets/index.py` | 3 | done |

## Definition of Done

### Task 1.1

- [x] A written widget is retrievable by any word in its name.

## Verify

`pytest tests/widgets/index_test.py`
