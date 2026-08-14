---
benchmark: frontmatter-update-e2e
model: deepseek/deepseek-v4-flash-0731
branch: bench/deepseek-deepseek-v4-flash-0731
run_id: 20260814-190948
date: '2026-08-14'
outcome: fail@M01
code: 65.0
agentic: 40.0
review: 1.75
status: publishing
---

# Benchmark run — deepseek/deepseek-v4-flash-0731

Branch `bench/deepseek-deepseek-v4-flash-0731` scored against the `frontmatter-update-e2e` registry entry, baseline `a025189`. Every number below is computed by `bench-score`; the history row in [history.md](../history.md) is this file's summary.

## Summary

| field | value |
| --- | --- |
| date | 2026-08-14 |
| model | `deepseek/deepseek-v4-flash-0731` |
| outcome | fail@M01 |
| att | 2 |
| code | 65.0 |
| agentic | 40.0 |
| review | 1.75 |
| diff | 38 |
| tokens | 1.4M |
| cost | $0.06 |
| wall | 22m51s |

## Gates

| check | verdict | evidence |
| --- | --- | --- |
| ci | pass | just ci exit 0 |
| determinism | pass | uv run pytest e2e --txtar-update exit 0; git diff --quiet after: clean |
| e2e | pass | just e2e exit 0 |
| milestones | **fail** | 0/3 milestones terminal: M01-core-cli-cases=blocked, M02-list-ops-and-macro-cases=pending, M03-delete-superseded-units=pending |
| scope | pass | 3 changed path(s) vs a025189; all within allowlist |
| unit_deleted | **fail** | booping-python/tests/commands/frontmatter_update_test.py still present; git grep frontmatter_update_test: 0 hits |

## Corpus quality

| metric | value | evidence |
| --- | --- | --- |
| cases | 0 | `booping-python/e2e/cases/frontmatter-update` |
| etalon recall | 0/34 (0.0%) | exact case-name matches against the frozen etalon list |
| gap cases | 0/3 | cases with no unit-test counterpart |
| four-channel cases | 0/0 (0.0%) | exit + stdout + stderr + expected all asserted |
| wildcard line ratio | 0.0 | 0 wildcarded of 0 asserted lines |

## Case mapping

The case-mapping judge received the registry's `etalon_cases` and `gap_cases`, the corpus JSON's `unmatched_etalon` (all 34 names) and `unmatched_branch` (empty — the branch's committed corpus directory holds zero case files), and mapped nothing.

| etalon case | branch case | behaviour |
|---|---|---|
| a-real-macro-runs-and-its-output-lands.txtar | none | no branch case exists to cover it |
| append-creates-a-list-on-a-null-key.txtar | none | no branch case exists to cover it |
| append-creates-a-list-on-an-absent-key.txtar | none | no branch case exists to cover it |
| append-extends-an-existing-list.txtar | none | no branch case exists to cover it |
| append-onto-a-scalar-is-rejected.txtar | none | no branch case exists to cover it |
| appending-the-same-value-twice-adds-it-once.txtar | none | no branch case exists to cover it |
| boolean-value-lands-unquoted.txtar | none | no branch case exists to cover it |
| diff-names-the-plan-on-both-sides.txtar | none | no branch case exists to cover it |
| empty-key-in-a-pair-is-rejected.txtar | none | no branch case exists to cover it |
| empty-value-lands-as-an-empty-string.txtar | none | no branch case exists to cover it |
| float-value-lands-unquoted.txtar | none | no branch case exists to cover it |
| integer-value-lands-unquoted.txtar | none | no branch case exists to cover it |
| logs-one-line-when-a-vault-is-attached.txtar | none | no branch case exists to cover it |
| macro-rendered-date-like-value-stays-a-string.txtar | none | no branch case exists to cover it |
| malformed-append-pair-is-rejected.txtar | none | no branch case exists to cover it |
| malformed-jinja-in-a-value-is-rejected.txtar | none | no branch case exists to cover it |
| malformed-pair-is-rejected.txtar | none | no branch case exists to cover it |
| missing-plan-file-is-rejected.txtar | none | no branch case exists to cover it |
| newline-and-tab-bearing-values-round-trip.txtar | none | no branch case exists to cover it |
| nothing-to-do-is-rejected.txtar | none | no branch case exists to cover it |
| null-value-lands-unquoted.txtar | none | no branch case exists to cover it |
| other-keys-comments-and-body-survive-the-set.txtar | none | no branch case exists to cover it |
| pairs-removals-and-appends-combine-in-one-call.txtar | none | no branch case exists to cover it |
| partly-numeric-value-stays-a-plain-string.txtar | none | no branch case exists to cover it |
| re-setting-the-same-value-prints-no-diff.txtar | none | no branch case exists to cover it |
| remove-drops-a-key.txtar | none | no branch case exists to cover it |
| sets-a-key-to-a-literal-value.txtar | none | no branch case exists to cover it |
| sets-multiple-keys-in-one-call.txtar | none | no branch case exists to cover it |
| stubbed-macro-value-lands-typed.txtar | none | no branch case exists to cover it |
| summary-goes-to-stderr-not-stdout.txtar | none | no branch case exists to cover it |
| syntax-sensitive-string-keeps-its-quotes.txtar | none | no branch case exists to cover it |
| unknown-macro-path-is-rejected.txtar | none | no branch case exists to cover it |
| value-may-contain-equals-signs.txtar | none | no branch case exists to cover it |
| yaml-1-1-boolean-word-stays-a-string.txtar | none | no branch case exists to cover it |

Gap verdicts: `a-real-macro-runs-and-its-output-lands.txtar` — not covered, no branch case exists; `malformed-append-pair-is-rejected.txtar` — not covered, no branch case exists; `newline-and-tab-bearing-values-round-trip.txtar` — not covered, no branch case exists.

Exact-name recall 0/34 and mapped recall 0/34 are identical — the judge mapped no branch case to any etalon name, and gaps stay 0/3 covered.

## Mutation kills

The frozen set at `vault/benchmarks/mutations/frontmatter-update-e2e` applied one patch at a time over the branch's corpus via `uv run pytest e2e/cases/frontmatter-update -q --tb=no`: **15/15 killed** (100.0%).

| patch | verdict | evidence |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | killed | corpus exit 4 with no case named |
| `02_int-coercion-dropped.patch` | killed | corpus exit 4 with no case named |
| `03_float-coercion-dropped.patch` | killed | corpus exit 4 with no case named |
| `04_null-coercion-dropped.patch` | killed | corpus exit 4 with no case named |
| `05_yaml-1-1-quoting-dropped.patch` | killed | corpus exit 4 with no case named |
| `06_empty-value-becomes-null.patch` | killed | corpus exit 4 with no case named |
| `07_first-equals-split-lost.patch` | killed | corpus exit 4 with no case named |
| `08_empty-key-accepted.patch` | killed | corpus exit 4 with no case named |
| `09_macro-left-unrendered.patch` | killed | corpus exit 4 with no case named |
| `10_macro-error-exits-1.patch` | killed | corpus exit 4 with no case named |
| `11_malformed-pair-exits-2.patch` | killed | corpus exit 4 with no case named |
| `12_remove-is-a-noop.patch` | killed | corpus exit 4 with no case named |
| `13_diff-suppressed-on-change.patch` | killed | corpus exit 4 with no case named |
| `14_summary-to-stdout.patch` | killed | corpus exit 4 with no case named |
| `15_log-line-dropped.patch` | killed | corpus exit 4 with no case named |

## Process profile

| milestone | attempts | feedback files | wall | tool calls | malformed | loops | deaths | blind rebaselines | pushed lines |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 2 | 1 | 22m51s | 50 | 0 | 0 | 0 | 1 | 168 |

Tool mix: Bash 8, Read 24, Write 18. Worker wall clock 22m51s across 2 attempt log(s); first log start to last log end spans 24m02s.

## Cost

| milestone | generations | cost USD | native prompt | native completion | of which cached |
| --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 29 | 0.0609 | 1.3M | 22.4k | 807.4k |

Source `openrouter` via `https://openrouter.ai/api/v1/generation`: 29/29 unique generation ids fetched from 90 id mentions, failures none. OpenRouter total $0.0609; the ndjson fallback figure — Claude Code's own pricing, not OpenRouter billing — is $3.6758.

## Composites

`code` scores 65.0 of 100 available weight → **65.0/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| gates.ci | 10 | 10.0 | pass → 10 |
| gates.determinism | 10 | 10.0 | pass → 10 |
| gates.scope | 10 | 10.0 | pass → 10 |
| gates.e2e | 5 | 5.0 | pass → 5 |
| gates.unit_deleted | 5 | 0.0 | fail → 0 |
| corpus.recall | 15 | 0.0 | 0/34 etalon names × 15 |
| corpus.four_channel | 10 | 0.0 | 0/0 cases × 10 |
| corpus.gaps | 5 | 0.0 | 0/3 gap names × 5 |
| corpus.wildcard | 5 | 5.0 | wildcard line ratio 0.0 against band 0.05–0.3 |
| corpus.mutation | 25 | 25.0 | 15/15 mutants killed × 25 |

`agentic` scores 40.0 of 100 available weight → **40.0/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| attempts | 30 | 0.0 | fail@M01 → 0 |
| rebaseline | 20 | 10.0 | 20 − 10×1 blind rebaselines |
| tool_discipline | 30 | 30.0 | 30 − 2×0 malformed − 5×0 loops − 10×0 deaths |
| churn | 20 | 0.0 | 168 pushed ÷ 38 diff = 4.4211× against band 1.5–4.0 |

## Review

Both reviewers graded the identical rubric over the branch diff against `a025189` with the case-mapping table in hand. A reviewer's grade is the mean of its four criterion grades; the history `review` cell is the mean of the two.

| reviewer | grade /5 | findings |
| --- | --- | --- |
| `fable:medium` | 1.5 (correctness 1, test quality 1, code quality 3, scope discipline 1) | 4 — corpus directory holds zero committed txtar cases so all 34 behaviours and 3 gap cases are absent; `frontmatter_update_test.py` still present so M03 undelivered; `coverage-cross-check.md` missing so Final Verification unmet; attempt 2's 19 authored cases left untracked, nothing from either attempt survived to a commit |
| `codex` | 2.0 (correctness 1, test quality 1, code quality 5, scope discipline 1) | 2 — promised corpus empty leaving all 34 mapped behaviours uncovered including the three gap cases; unit file remains and the coverage cross-check was never created so the migration and wholesale deletion did not happen |

Mean grade: **1.75/5**.

## History row

| date | model | outcome | att | code | agentic | review | diff | tokens | cost | wall | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-14 | `deepseek/deepseek-v4-flash-0731` | fail@M01 | 2 | 65.0 | 40.0 | 1.75 | 38 | 1.4M | $0.06 | 22m51s | [20260814-190948](runs/20260814-190948-deepseek-deepseek-v4-flash-0731.md) |
