---
id: "07"
title: "Cross-check, delete the CLI query units, shrink the library file"
sp: 3
status: pending
plan: "vault/plans/202608130839_cli-tests-to-e2e-corpus/index.md"
---

# M07: Cross-check, delete the CLI query units, shrink the library file

`tests/commands/query_test.py` is deleted and `tests/query_test.py` holds only the template-integration coverage the CLI cannot reach.

**Scope**: the closing pass over query's two unit files, after M03–M06 have landed their cases. Files: deleted `booping-python/tests/commands/query_test.py`; edited `booping-python/tests/query_test.py`; possibly `booping-python/e2e/cases/query/*.txtar` for gaps the cross-check exposes.

The tier line this milestone enforces: e2e owns query semantics, because a case and the engine read the same YAML spec. Units keep only what proves query objects work inside templates — `TestRow` (6 tests: attribute access, nested mappings, absent-key behaviour, recursive unwrapping), `TestRowUnderJinja` (2: attribute lookup winning over dict methods, absent key rendering empty) and `TestQueryFilterWithoutAVault` (2: the `| query` filter with and without a vault). No `booping query` invocation reaches any of those. 10 tests retained of the file's 57; the other 47 are the semantics this plan moved.

A **gap**, for both cross-check tasks below, is either a unit assertion no case covers, or a behavior neither tier ever covered that the port makes visible. Both get a case here. A *bug* found while porting is neither: it is recorded in this milestone's body and left unfixed, per the plan's Decisions.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Cross-check all 35 tests in `tests/commands/query_test.py` — 27 CLI plus 8 `parse_where` — against the cases from M03–M06, add a case for any gap found, then delete the file | `booping-python/tests/commands/query_test.py`, `booping-python/e2e/cases/query/*.txtar` | 1 | pending |
| 7.2 | Cross-check the 47 semantics tests in `tests/query_test.py` (`TestSlugFor`, `TestDiscover`, `TestRun`, `TestWhere`, `TestOrderingOperators`, `TestSort`, `TestColumns`, `TestQuerySpec`, `TestRoot`) against the same cases, add cases for gaps, then delete those classes and the fixtures and imports they alone used | `booping-python/tests/query_test.py`, `booping-python/e2e/cases/query/*.txtar` | 2 | pending |

## Definition of Done

### Task 7.1

- [ ] A cross-check table maps each of the 35 tests to the case that replaces it, or records it as deliberately dropped with the reason.
- [ ] Any gap the cross-check exposes has a case before the deletion, not a TODO.
- [ ] `booping-python/tests/commands/query_test.py` is deleted and `grep -rn "commands/query_test\|parse_where" booping-python/tests` returns nothing.

### Task 7.2

- [ ] A cross-check table maps each of the 47 semantics tests to its replacing case, or records it as deliberately dropped with the reason.
- [ ] `tests/query_test.py` retains `TestRow`, `TestRowUnderJinja` and `TestQueryFilterWithoutAVault` and nothing else — 10 tests collected from the file, down from 57.
- [ ] Fixtures, imports and helpers left unused by the deletion are removed with it — `uv run ruff check` reports no unused import in the file.
- [ ] No retained test asserts a semantic reachable through a `booping query` invocation.

## Verify

```
cd booping-python && uv run pytest e2e tests/query_test.py
```

The corpus passes with no `--txtar-update` needed and the shrunken unit file passes, with the retained classes collecting as tests.
