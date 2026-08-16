---
benchmark: frontmatter-update-e2e
model: Qwen3.8-27B_reasoning_medium
branch: bench/qwen3-8-27b-reasoning-medium
run_id: 20260816-163342
date: 2026-08-16 16:33
outcome: pass
code: 89.05
agentic: 80.0
review: 3.13
status: done
---

# Benchmark run — Qwen3.8-27B_reasoning_medium

Branch `bench/qwen3-8-27b-reasoning-medium` scored against the `frontmatter-update-e2e` registry entry, baseline `a025189`. Every number below is computed by `bench-score`; the history row in [history.md](../history.md) is this file's summary.

## Summary

| field | value |
| --- | --- |
| date | 2026-08-16 16:33 |
| model | `Qwen3.8-27B_reasoning_medium` |
| provider | local |
| outcome | pass |
| att | 1/1/1 |
| code | 89.0 |
| agentic | 80.0 |
| review | 3.13 |
| diff | 1559 |
| tokens | in 4.1M out 122.3k |
| cache | in 3.6M out 0 |
| cost | $0.00 |
| time | 1h02m42s |

## Gates

| check | verdict | evidence |
| --- | --- | --- |
| ci | pass | just ci exit 0 |
| determinism | pass | uv run pytest e2e --txtar-update exit 0; git diff --quiet after: clean |
| e2e | pass | just e2e exit 0 |
| milestones | pass | 3/3 milestones terminal: M01-core-cli-cases=done, M02-list-ops-and-macro-cases=done, M03-delete-superseded-units=done |
| scope | pass | 35 changed path(s) vs a025189; all within allowlist |
| unit_deleted | pass | booping-python/tests/commands/frontmatter_update_test.py absent; git grep frontmatter_update_test: 0 hits |

## Corpus quality

| metric | value | evidence |
| --- | --- | --- |
| cases | 29 | `booping-python/e2e/cases/frontmatter-update` |
| etalon recall | 29/34 (85.29%) | exact case-name matches against the frozen etalon list |
| gap cases | 2/3 | cases with no unit-test counterpart |
| four-channel cases | 23/29 (79.31%) | exit + stdout + stderr + expected all asserted |
| wildcard line ratio | 0.0025 | 1 wildcarded of 395 asserted lines |

## Case mapping

Exact-name recall is 2/34; the judge below mapped 27 further etalon behaviours onto differently-named branch cases, so scored recall is 29/34. Gap cases are judged on behaviour, not spelling.

| etalon case | branch case | behaviour |
| --- | --- | --- |
| a-real-macro-runs-and-its-output-lands.txtar | real-macro-executes.txtar | unstubbed `["echo","1"]` macro runs through the subprocess boundary and its output lands typed |
| append-creates-a-list-on-a-null-key.txtar | append-creates-list-on-null-key.txtar | `--append` turns a null-valued key into a one-element block sequence |
| append-creates-a-list-on-an-absent-key.txtar | append-creates-list-on-absent-key.txtar | `--append` creates an absent key as a one-element sequence at the end of the block |
| append-extends-an-existing-list.txtar | append-extends-existing-list.txtar | `--append` adds a member to an existing sequence, keeping the old one |
| append-onto-a-scalar-is-rejected.txtar | append-onto-scalar-exits-1.txtar | appending to a scalar key exits 1 naming key and file, writing nothing |
| appending-the-same-value-twice-adds-it-once.txtar | idempotent-double-append.txtar | second identical append prints summary but no diff and does not duplicate the member |
| boolean-value-lands-unquoted.txtar | coerces-true-to-bool.txtar | a boolean word lands unquoted and reloads as a bool (branch covers `true` only, not `false`) |
| diff-names-the-plan-on-both-sides.txtar | diff-headers-on-stdout.txtar | stdout is a unified diff with the plan path on `---`/`+++` plus an `@@` hunk header |
| empty-key-in-a-pair-is-rejected.txtar | none | no branch case passes `=value` |
| empty-value-lands-as-an-empty-string.txtar | none | no branch case sets a key to an empty string |
| float-value-lands-unquoted.txtar | coerces-1-5-to-float.txtar | a decimal lands unquoted and reloads as a float |
| integer-value-lands-unquoted.txtar | coerces-23-to-int.txtar | an all-digit value lands unquoted and reloads as an int |
| macro-rendered-date-like-value-stays-a-string.txtar | macro-date-like-stays-string.txtar | macro-rendered date-like value stays a string — but the branch picks `2026-08-12 14:17`, not a YAML timestamp, so the single-quoting the etalon asserts is never exercised |
| malformed-append-pair-is-rejected.txtar | none | no branch case feeds `--append` an argument without `=` |
| malformed-jinja-in-a-value-is-rejected.txtar | malformed-jinja-exits-2.txtar | unparseable Jinja exits 2 with the TemplateSyntaxError on stderr, file untouched |
| malformed-pair-is-rejected.txtar | malformed-pair-exits-1.txtar | a positional argument without `=` exits 1 naming the pair, no stdout |
| missing-plan-file-is-rejected.txtar | missing-plan-exits-1.txtar | a non-existent plan path exits 1 with `plan not found` on stderr |
| newline-and-tab-bearing-values-round-trip.txtar | newline-and-tab-value-round-trips.txtar | a value carrying a newline and a tab round-trips unmangled through the writer |
| nothing-to-do-is-rejected.txtar | nothing-to-do-exits-1.txtar | no pairs/appends/removals exits 1 naming all three accepted forms |
| null-value-lands-unquoted.txtar | coerces-null-to-null.txtar | `null` lands unquoted and reloads as YAML null (branch omits the `~` spelling) |
| other-keys-comments-and-body-survive-the-set.txtar | preserves-other-keys-and-body.txtar | only the named key changes; other keys and body survive (branch fixture carries no comment, so comment survival is untested) |
| pairs-removals-and-appends-combine-in-one-call.txtar | combined-removals-pairs-appends.txtar | one call sets, removes and appends; summary orders removals, pairs, appends |
| partly-numeric-value-stays-a-plain-string.txtar | partly-numeric-string-stays-unquoted.txtar | `23 things` is written bare and stays a string |
| re-setting-the-same-value-prints-no-diff.txtar | second-identical-call-prints-no-diff.txtar | second identical set rewrites nothing, prints summary but no diff, exits 0 |
| remove-drops-a-key.txtar | remove-drops-key.txtar | `--remove` deletes the key's line, surrounding keys and body intact (branch fixture has no comment, so comment survival is untested) |
| sets-a-key-to-a-literal-value.txtar | sets-a-key-with-a-literal-value.txtar | a literal `key=value` lands in frontmatter with diff on stdout and summary on stderr (branch adds a new key rather than rewriting one in place) |
| stubbed-macro-value-lands-typed.txtar | stub-typed-landing.txtar | a `macro_stubs:`-pinned value is rendered then coerced, landing as a bare int |
| summary-goes-to-stderr-not-stdout.txtar | success-summary-goes-to-stderr.txtar | stdout carries the diff alone, the `updated …` summary is stderr's only line |
| syntax-sensitive-string-keeps-its-quotes.txtar | none | no branch case covers `@`/`*`/`&`/`!`/`%`/backtick leads, padding, or `a: b` |
| unknown-macro-path-is-rejected.txtar | unknown-macro-exits-2.txtar | a macro path declaring no macro exits 2 echoing value and path, writing nothing |
| value-may-contain-equals-signs.txtar | none | no branch case splits a pair on the first `=` only |
| yaml-1-1-boolean-word-stays-a-string.txtar | yaml-1-1-bool-word-gets-quoted.txtar | `yes` is written single-quoted so it reloads as the string |

Gap verdicts:

- `a-real-macro-runs-and-its-output-lands.txtar` — covered by `real-macro-executes.txtar`
- `malformed-append-pair-is-rejected.txtar` — not covered
- `newline-and-tab-bearing-values-round-trip.txtar` — covered by `newline-and-tab-value-round-trips.txtar`

## Mutation kills

The frozen set at `vault/benchmarks/mutations/frontmatter-update-e2e` applied one patch at a time over the branch's corpus via `uv run pytest e2e/cases/frontmatter-update -q --tb=no`: **12/15 killed** (80.0%).

| patch | verdict | evidence |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | killed | coerces-true-to-bool.txtar |
| `02_int-coercion-dropped.patch` | killed | coerces-23-to-int.txtar, real-macro-executes.txtar, sets-multiple-keys-in-one-call.txtar, stub-typed-landing.txtar, success-summary-goes-to-stderr.txtar |
| `03_float-coercion-dropped.patch` | killed | coerces-1-5-to-float.txtar |
| `04_null-coercion-dropped.patch` | killed | coerces-null-to-null.txtar |
| `05_yaml-1-1-quoting-dropped.patch` | killed | yaml-1-1-bool-word-gets-quoted.txtar |
| `06_empty-value-becomes-null.patch` | **survived** | corpus exit 0 with no case named |
| `07_first-equals-split-lost.patch` | **survived** | corpus exit 0 with no case named |
| `08_empty-key-accepted.patch` | **survived** | corpus exit 0 with no case named |
| `09_macro-left-unrendered.patch` | killed | macro-date-like-stays-string.txtar, malformed-jinja-exits-2.txtar, newline-and-tab-value-round-trips.txtar, real-macro-executes.txtar, stub-typed-landing.txtar, unknown-macro-exits-2.txtar |
| `10_macro-error-exits-1.patch` | killed | malformed-jinja-exits-2.txtar, unknown-macro-exits-2.txtar |
| `11_malformed-pair-exits-2.patch` | killed | malformed-pair-exits-1.txtar |
| `12_remove-is-a-noop.patch` | killed | combined-removals-pairs-appends.txtar, remove-drops-key.txtar |
| `13_diff-suppressed-on-change.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, coerces-1-5-to-float.txtar, coerces-23-to-int.txtar, coerces-null-to-null.txtar, coerces-true-to-bool.txtar, combined-removals-pairs-appends.txtar, diff-headers-on-stdout.txtar, idempotent-double-append.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-date-like-stays-string.txtar, newline-and-tab-value-round-trips.txtar, partly-numeric-string-stays-unquoted.txtar, preserves-other-keys-and-body.txtar, real-macro-executes.txtar, remove-drops-key.txtar, second-identical-call-prints-no-diff.txtar, sets-a-key-with-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stub-typed-landing.txtar, success-summary-goes-to-stderr.txtar, yaml-1-1-bool-word-gets-quoted.txtar |
| `14_summary-to-stdout.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, coerces-1-5-to-float.txtar, coerces-23-to-int.txtar, coerces-null-to-null.txtar, coerces-true-to-bool.txtar, combined-removals-pairs-appends.txtar, diff-headers-on-stdout.txtar, idempotent-double-append.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-date-like-stays-string.txtar, newline-and-tab-value-round-trips.txtar, partly-numeric-string-stays-unquoted.txtar, preserves-other-keys-and-body.txtar, real-macro-executes.txtar, remove-drops-key.txtar, second-identical-call-prints-no-diff.txtar, sets-a-key-with-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stub-typed-landing.txtar, success-summary-goes-to-stderr.txtar, yaml-1-1-bool-word-gets-quoted.txtar |
| `15_log-line-dropped.patch` | killed | logs-one-line-when-a-vault-is-attached.txtar |

## Process profile

| milestone | attempts | feedback files | wall | tool calls | malformed | loops | deaths | blind rebaselines | pushed lines |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 1 | 0 | 19m22s | 90 | 0 | 0 | 0 | 3 | 435 |
| M02-list-ops-and-macro-cases | 1 | 0 | 23m03s | 109 | 0 | 0 | 0 | 0 | 464 |
| M03-delete-superseded-units | 1 | 0 | 20m16s | 60 | 0 | 0 | 0 | 0 | 256 |

Tool mix: bash 95, edit 10, grep 13, ls 8, read 87, run_agent 9, write 37. Calls by agent: orchestrator 37, researcher 79, validator 49, worker 94. Log schema: pi. Worker wall clock 1h02m42s across 3 attempt log(s); first log start to last log end spans 1h05m38s.

## Cost

| milestone | generations | cost USD | in | out | cache in | cache out |
| --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 0 | 0.0000 | 1.5M | 37.1k | 1.4M | 0 |
| M02-list-ops-and-macro-cases | 0 | 0.0000 | 1.5M | 42.1k | 1.3M | 0 |
| M03-delete-superseded-units | 0 | 0.0000 | 1.0M | 43.1k | 930.6k | 0 |

Source `worker-usage`: no OpenRouter generation id appears in the logs, so the figures above are the worker's own usage accounting, not billing, totalling $0.0000.

## Composites

`code` scores 89.05 of 100 available weight → **89.05/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| gates.ci | 10 | 10.0 | pass → 10 |
| gates.determinism | 10 | 10.0 | pass → 10 |
| gates.scope | 10 | 10.0 | pass → 10 |
| gates.e2e | 5 | 5.0 | pass → 5 |
| gates.unit_deleted | 5 | 5.0 | pass → 5 |
| corpus.recall | 15 | 12.79 | 29/34 etalon names × 15 |
| corpus.four_channel | 10 | 7.93 | 23/29 cases × 10 |
| corpus.gaps | 5 | 3.33 | 2/3 gap names × 5 |
| corpus.wildcard | 5 | 5.0 | wildcard line ratio 0.0025 against band 0.05–0.3 |
| corpus.mutation | 25 | 20.0 | 12/15 mutants killed × 25 |

`agentic` scores 80.0 of 100 available weight → **80.0/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| attempts | 30 | 30.0 | 30 − 10×0 retries |
| rebaseline | 20 | 0.0 | 20 − 10×3 blind rebaselines |
| tool_discipline | 30 | 30.0 | 30 − 2×0 malformed − 5×0 loops − 10×0 deaths |
| churn | 20 | 20.0 | 1155 pushed ÷ 1559 diff = 0.7409× against band 1.5–4.0 |

## Review

Two independent reviewers graded the branch diff against `review-rubric.md` — four criteria each, out of 5; the grade below is each reviewer's mean over its four criteria, and the `review` cell is the mean of the two.

| reviewer | grade /5 | findings |
| --- | --- | --- |
| `fable:medium` | 3.5 | 7 — correctness 3, test quality 3, code quality 4, scope discipline 4. Worst: the cross-check passes the deletion gate on a false premise (`=value` mapped to the `noequals` branch, a distinct error path with a distinct message that no case reaches); all eight syntax-sensitive-quoting params mapped to a newline/tab case exercising none of their triggers; empty-value and first-`=`-split dropped as "internal" though both are CLI-observable; comment survival silently lost in `remove-drops-key.txtar` and `preserves-other-keys-and-body.txtar`; M02 task 2.1 and M01 task 1.2 DoD checked with behaviours they name uncovered. |
| `codex` | 2.75 | 8 — correctness 3, test quality 2, code quality 3, scope discipline 3. Worst: deleting the unit file removes assertions for first-`=` splitting, empty keys and values, syntax-sensitive strings and comment preservation with no replacement; the cross-check's non-equivalent mappings make the deletion proof materially inaccurate; no malformed `--append` case despite the task row claiming append coverage; `macro-date-like-stays-string.txtar` never exercises the date-like quoting path. |

Both reviewers converge: the corpus that exists is a strong contract pin (full expected bytes, four channels, wildcarded log line), and the loss is concentrated in the five etalon behaviours the case mapping already recorded as unported — with the cross-check document asserting coverage that the cases do not carry.

## History row

| date | model | provider | outcome | att | code | agentic | review | diff | tokens | cache | cost | time | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-16 16:33 | `Qwen3.8-27B_reasoning_medium` | local | pass | 1/1/1 | 89.0 | 80.0 | 3.13 | 1559 | in 4.1M out 122.3k | in 3.6M out 0 | $0.00 | 1h02m42s | [20260816-163342](runs/20260816-163342-qwen3-8-27b-reasoning-medium.md) |
