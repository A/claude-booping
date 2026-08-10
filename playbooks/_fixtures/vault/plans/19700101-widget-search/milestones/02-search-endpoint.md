---
id: "02"
title: "Search endpoint"
sp: 2
status: done
plan: "plans/19700101-widget-search/index.md"
---

# M02: Search endpoint

**Goal**: A keyword query returns matching widgets over HTTP.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Serve `GET /widgets?q=` off the index | `src/widgets/api.py` | 2 | done |

## Definition of Done

### Task 2.1

- [x] A query with no matches returns an empty list, not a 404.

## Verify

`pytest tests/widgets/api_test.py`
