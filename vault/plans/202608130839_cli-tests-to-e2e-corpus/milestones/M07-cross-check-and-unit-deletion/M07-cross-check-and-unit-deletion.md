---
id: "07"
title: "Cross-check, delete the CLI query units, shrink the library file"
sp: 3
status: done
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
| 7.1 | Cross-check all 35 tests in `tests/commands/query_test.py` — 27 CLI plus 8 `parse_where` — against the cases from M03–M06, add a case for any gap found, then delete the file | `booping-python/tests/commands/query_test.py`, `booping-python/e2e/cases/query/*.txtar` | 1 | done |
| 7.2 | Cross-check the 47 semantics tests in `tests/query_test.py` (`TestSlugFor`, `TestDiscover`, `TestRun`, `TestWhere`, `TestOrderingOperators`, `TestSort`, `TestColumns`, `TestQuerySpec`, `TestRoot`) against the same cases, add cases for gaps, then delete those classes and the fixtures and imports they alone used | `booping-python/tests/query_test.py`, `booping-python/e2e/cases/query/*.txtar` | 2 | done |

## Definition of Done

### Task 7.1

- [x] A cross-check table maps each of the 35 tests to the case that replaces it, or records it as deliberately dropped with the reason.
- [x] Any gap the cross-check exposes has a case before the deletion, not a TODO.
- [x] `booping-python/tests/commands/query_test.py` is deleted and `grep -rn "commands/query_test\|parse_where" booping-python/tests` returns nothing.

### Task 7.2

- [x] A cross-check table maps each of the 47 semantics tests to its replacing case, or records it as deliberately dropped with the reason.
- [x] `tests/query_test.py` retains `TestRow`, `TestRowUnderJinja` and `TestQueryFilterWithoutAVault` and nothing else — 10 tests collected from the file, down from 57.
- [x] Fixtures, imports and helpers left unused by the deletion are removed with it — `uv run ruff check` reports no unused import in the file.
- [x] No retained test asserts a semantic reachable through a `booping query` invocation.

## Cross-check record

### 7.1 — `tests/commands/query_test.py`, 35 tests

| unit | case |
| --- | --- |
| `TestParseWhere::test_equality`, `test_inequality_keeps_the_operator_suffix` | `equality-and-inequality-split-the-same-fixture` |
| `test_membership_splits_on_commas` | `membership-splits-on-commas-and-trims-options` |
| `test_value_may_contain_equals_signs` | `a-where-value-may-contain-equals-signs` |
| `test_ordering_keeps_the_operator_suffix` | `ordering-clauses-filter-numerically` |
| `test_negative_ordering_operand` | `a-negative-ordering-operand-is-a-value-not-a-flag` |
| `test_malformed_pairs_raise` | gap → `malformed-where-pair-is-rejected`, new `a-where-clause-with-no-field-is-rejected`, new `an-operator-suffix-does-not-excuse-a-missing-field`; the `!=done` / `:in=a,b` / `:lt=3` params reach the same `if not field` branch and got no further files |
| `test_an_empty_ordering_operand_raises` | `empty-ordering-operand-is-rejected` + new `a-whitespace-only-ordering-operand-is-rejected` (the only test pinning the `.strip()`) |
| `TestAddressing` (9) | `config-path-resolves-a-project-spec`, `inline-glob-runs-without-a-config-entry`, `repeated-where-applies-both-clauses`, `inline-flags-narrow-a-resolved-spec`, `a-spec-matching-nothing-exits-zero`, `help-lists-every-flag-and-the-where-operators` (both help tests), `ordering-clauses-filter-numerically`, `a-negative-ordering-operand-is-a-value-not-a-flag` |
| `TestUserErrors` (9) | `malformed-where-pair-is-rejected`, `empty-ordering-operand-is-rejected`, `unknown-config-path-is-rejected`, `non-mapping-config-value-is-rejected`, `both-addressing-forms-are-rejected`, `neither-addressing-form-is-rejected`, `vault-relative-spec-without-a-project-is-rejected`, `unknown-output-format-is-rejected` |
| `TestUserErrors::test_distinct_messages_per_error` | dropped — each case pins its exact stderr line, so distinctness is visible in the goldens; no single case asserts a set-of-three property |
| `TestOutputFormats::test_table_escapes_pipes_and_collapses_newlines` | `a-pipe-in-a-value-is-escaped-in-the-table` + `a-multi-line-value-collapses-to-one-table-row` |
| `TestOutputFormats` (rest) | `table-is-the-default-output`, `json-output-is-an-array-of-objects`, `yaml-output-carries-the-json-rows`, `paths-output-is-one-relative-path-per-line` |
| `test_warnings_go_to_stderr_only` (4 params) | gap → `an-unparseable-file-is-skipped-with-a-warning` extended from `paths` only to all four formats with `--columns slug` |
| `TestCoreRoot` (3) | `root-core-globs-the-plugin-root-without-a-vault`, `an-unknown-query-root-is-rejected`, `an-unknown-spec-key-is-rejected` |

### 7.2 — `tests/query_test.py`, 47 semantics tests

| unit class | case |
| --- | --- |
| `TestSlugFor` (3) | `an-index-pattern-slugs-by-the-directory-name`, `a-wildcard-final-segment-slugs-by-the-file-stem`, `a-single-segment-pattern-slugs-by-the-stem` |
| `TestDiscover` (3) | `overlapping-globs-yield-one-row-per-slug`, `reversing-the-globs-flips-the-winner`, `a-directory-matching-the-pattern-is-not-a-row` |
| `TestRun` (6) | `json-output-is-an-array-of-objects`, `path-is-relative-to-the-pinned-project-root`, `rows-come-back-in-slug-order-not-discovery-order`, `overlapping-globs-yield-one-row-per-slug`, `an-unparseable-file-is-skipped-with-a-warning`, `a-file-without-frontmatter-yields-path-and-slug`, `a-spec-matching-nothing-exits-zero` |
| `TestWhere` (6) | `equality-and-inequality-split-the-same-fixture` (×2), `membership-splits-on-commas-and-trims-options`, `repeated-where-applies-both-clauses`, `a-row-missing-the-field-is-excluded-by-every-operator`, `omitting-where-keeps-every-discovered-row` |
| `TestOrderingOperators` (11) | `ordering-clauses-filter-numerically`, `a-negative-ordering-operand-is-a-value-not-a-flag`, `ordering-coerces-both-sides-to-float`, `fractional-values-compare-numerically`, `ordering-failures-drop-the-row-not-the-run`, `a-row-missing-the-field-is-excluded-by-every-operator`, `a-field-named-like-the-operator-cannot-shadow-it` |
| `test_a_jinja_undefined_operand_fails_the_clause` | dropped — a `LenientUndefined` operand only arrives from a template-supplied spec and lands on the same `float()` guard the non-numeric-operand case pins; the retained set is fixed to the three template classes, so it has no home in the unit file either |
| `TestSort` (4) | `sort-ascending-and-descending-reverse-the-same-rows`, `rows-without-a-sort-value-come-last-in-both-directions` (its fixture carries both an absent `created` and an explicit `created: null`) |
| `TestColumns` (3) | `columns-keep-declared-keys-plus-path-and-slug`, `a-declared-path-column-is-not-duplicated`, `empty-columns-leave-only-path-and-slug` |
| `TestQuerySpec` (6) | `the-same-spec-without-root-still-needs-a-vault`, `root-core-globs-the-plugin-root-without-a-vault`, `an-unknown-query-root-is-rejected`, `an-unknown-spec-key-is-rejected`, `config-path-resolves-a-project-spec` + `empty-columns-leave-only-path-and-slug` (`test_carries_where_sort_and_columns`) |
| `TestQuerySpec::test_defaults` | dropped as a change detector on constructor defaults; observable as behavior in `omitting-where-keeps-every-discovered-row`, `rows-come-back-in-slug-order-not-discovery-order`, `json-output-is-an-array-of-objects` |
| `TestRoot` (5) | `root-core-globs-the-plugin-root-without-a-vault`, `vault-relative-spec-without-a-project-is-rejected`, `the-same-spec-without-root-still-needs-a-vault`, `paths-output-is-one-relative-path-per-line` |

No bug surfaced during the cross-check, so nothing is recorded under the plan's "record, don't fix" decision. Corpus note: `a-whitespace-only-ordering-operand-is-rejected.txtar` ends with a golden line carrying two significant trailing spaces — a trailing-whitespace stripper over `e2e/cases/` would break it.

## Verify

```
cd booping-python && uv run pytest e2e tests/query_test.py
```

The corpus passes with no `--txtar-update` needed and the shrunken unit file passes, with the retained classes collecting as tests.
