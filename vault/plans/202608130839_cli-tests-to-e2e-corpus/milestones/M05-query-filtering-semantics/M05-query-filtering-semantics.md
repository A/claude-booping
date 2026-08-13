---
id: "05"
title: "query corpus — where clauses, ordering operators, sort"
sp: 5
status: done
plan: "vault/plans/202608130839_cli-tests-to-e2e-corpus/index.md"
---

# M05: query corpus — where clauses, ordering operators, sort

Filtering and ordering semantics — `where` operators, the numeric ordering operators and `sort` — are covered by txtar cases instead of direct `booping.query` calls.

**Scope**: the semantics `tests/query_test.py` asserts in `TestWhere` (6), `TestOrderingOperators` (11) and `TestSort` (4), re-expressed as CLI invocations over fixture vaults. Each case shapes the frontmatter it needs — mixed types for coercion, missing and null fields for exclusion — and asserts the row set that comes back. Files: new `booping-python/e2e/cases/query/*.txtar`.

The ordering operators are the subtle part: they coerce both sides to float, and every failure mode (non-numeric row value, non-numeric operand, undefined operand, missing field, a field literally named like the operator) must *exclude* the row rather than error the run.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `where` cases: equality keeps only matching rows; inequality drops them; `:in` keeps rows matching any option; multiple clauses are conjunctive; a row missing the field is excluded by every operator; no `where` keeps every row | `booping-python/e2e/cases/query/*.txtar` | 2 | done |
| 5.2 | Ordering-operator cases: `gt` and `lt` are strict; a negative operand matches every number above it; coercion is float on both sides across int, float and numeric-string frontmatter; fractional values compare numerically rather than lexically | `booping-python/e2e/cases/query/*.txtar` | 2 | done |
| 5.3 | Ordering-failure and `sort` cases: a non-numeric row value, a non-numeric operand and a missing field each fail the clause and drop the row without failing the run; a field named like the operator suffix cannot shadow it; ascending and descending sort by field; rows missing the field come last in both directions; a null value counts as missing | `booping-python/e2e/cases/query/*.txtar` | 1 | done |

## Definition of Done

### Task 5.1

- [x] `--where status=done` returns exactly the rows whose `status` is `done`.
- [x] `--where 'status!=done'` returns exactly the complement over the same fixture.
- [x] `--where 'status:in=done, fail'` returns the union of both option sets.
- [x] Two clauses in one invocation return only the intersection.
- [x] A vault where one file lacks the queried field returns that row for no operator — equality, inequality, `:in` and the ordering operators alike.
- [x] A spec with no `where` returns every discovered row.

### Task 5.2

- [x] `--where sp:gt=3` excludes a row whose `sp` is exactly 3, and `--where sp:lt=3` excludes it too.
- [x] `--where sp:gt=-1` returns every row carrying a number.
- [x] A fixture mixing `sp: 4`, `sp: 4.0` and `sp: "4"` returns all three for the same clause, proving both sides coerce to float.
- [x] `--where sp:gt=1.5` returns a row whose `sp` is `1.75` and excludes one whose `sp` is `1.25`, so the comparison is numeric and not lexical.

### Task 5.3

- [x] A row whose value is a non-numeric string, a row compared against a non-numeric operand, and a row missing the field are each excluded, and the run still exits 0 with the remaining rows.
- [x] A fixture carrying a frontmatter key literally named `sp:gt` does not satisfy an `sp:gt=` clause.
- [x] `--sort created` and `--sort -created` return the same rows in opposite orders.
- [x] Rows missing the sort field come last under both directions, not first under one of them.
- [x] A row whose sort field is `null` sorts with the missing rows, not as a smallest value.

## Verify

```
cd booping-python && uv run pytest e2e -k query
```

Every case in this milestone passes with no `--txtar-update` needed.
