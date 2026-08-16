---
benchmark: frontmatter-update-e2e
model: deepseek/deepseek-v4-flash-0731
branch: bench/deepseek-deepseek-v4-flash-0731
run_id: 20260816-182530
date: 2026-08-16 18:25
outcome: pass
code: 89.57
agentic: 90.0
review: 3.95
status: publishing
---

# Benchmark run — deepseek/deepseek-v4-flash-0731

Branch `bench/deepseek-deepseek-v4-flash-0731` scored against the `frontmatter-update-e2e` registry entry, baseline `a025189`. Every number below is computed by `bench-score`; the history row in [history.md](../history.md) is this file's summary.

## Summary

| field | value |
| --- | --- |
| date | 2026-08-16 18:25 |
| model | `deepseek/deepseek-v4-flash-0731` |
| provider | openrouter |
| outcome | pass |
| att | 1/1/1 |
| code | 89.6 |
| agentic | 90.0 |
| review | 3.95 |
| diff | 1606 |
| tokens | in 13.1M out 216.7k |
| cache | in 5.9M out 0 |
| cost | $0.20 |
| time | 41m59s |

## Gates

| check | verdict | evidence |
| --- | --- | --- |
| ci | pass | just ci exit 0 |
| determinism | pass | uv run pytest e2e --txtar-update exit 0; git diff --quiet after: clean |
| e2e | pass | just e2e exit 0 |
| milestones | pass | 3/3 milestones terminal: M01-core-cli-cases=done, M02-list-ops-and-macro-cases=done, M03-delete-superseded-units=done |
| scope | pass | 36 changed path(s) vs a025189; all within allowlist |
| unit_deleted | pass | booping-python/tests/commands/frontmatter_update_test.py absent; git grep frontmatter_update_test: 0 hits |

## Corpus quality

| metric | value | evidence |
| --- | --- | --- |
| cases | 30 | `booping-python/e2e/cases/frontmatter-update` |
| etalon recall | 30/34 (88.24%) | exact case-name matches against the frozen etalon list |
| gap cases | 2/3 | cases with no unit-test counterpart |
| four-channel cases | 24/30 (80.0%) | exit + stdout + stderr + expected all asserted |
| wildcard line ratio | 0.0046 | 2 wildcarded of 437 asserted lines |

## Case mapping

The branch named nearly every case differently from the etalon corpus, so exact-name recall reads far below behavioural recall. The table a case-mapping judge returned, one row per etalon name the exact-name comparison left unmatched:

| Etalon case | Branch case | Behaviour |
| --- | --- | --- |
| `a-real-macro-runs-and-its-output-lands.txtar` | `real-macro-executes-command.txtar` | a genuine argv macro runs; the echoed `1` lands as a typed int |
| `append-creates-a-list-on-a-null-key.txtar` | `append-creates-list-on-null-key.txtar` | `--append` on a null-valued key replaces it with a one-element list |
| `append-creates-a-list-on-an-absent-key.txtar` | `append-creates-list-on-absent-key.txtar` | `--append` on an absent key creates a one-element list |
| `append-extends-an-existing-list.txtar` | `append-extends-existing-list.txtar` | `--append` onto an existing list appends an item |
| `append-onto-a-scalar-is-rejected.txtar` | `append-onto-scalar-exits-1.txtar` | exit 1 with an error naming the key and plan path, file unwritten |
| `appending-the-same-value-twice-adds-it-once.txtar` | `append-is-idempotent.txtar` | the second append produces no diff |
| `boolean-value-lands-unquoted.txtar` | `coerces-boolean.txtar` | a true/false value lands as an unquoted YAML boolean |
| `diff-names-the-plan-on-both-sides.txtar` | `stdout-is-a-unified-diff.txtar` | the plan path on both `---`/`+++` header lines with a `@@` hunk header |
| `empty-key-in-a-pair-is-rejected.txtar` | none | nothing asserts rejection of a pair with an empty key (`=value`) |
| `empty-value-lands-as-an-empty-string.txtar` | none | nothing asserts that `key=` sets an empty string |
| `float-value-lands-unquoted.txtar` | `coerces-float.txtar` | a decimal value lands as an unquoted YAML float |
| `integer-value-lands-unquoted.txtar` | `coerces-integer.txtar` | a numeric value lands as an unquoted YAML integer |
| `macro-rendered-date-like-value-stays-a-string.txtar` | `stub-macro-date-stays-a-string.txtar` | a date-like macro-stub value is single-quoted so it stays a string |
| `malformed-append-pair-is-rejected.txtar` | none | nothing asserts a malformed `--append key` (missing `=`) |
| `malformed-jinja-in-a-value-is-rejected.txtar` | `malformed-jinja-exits-2.txtar` | malformed Jinja exits 2 with a `TemplateSyntaxError` message |
| `malformed-pair-is-rejected.txtar` | `malformed-pair-exits-1.txtar` | a pair without `=` exits 1 naming the offending argument |
| `missing-plan-file-is-rejected.txtar` | `missing-plan-exits-1.txtar` | a nonexistent plan path exits 1 echoing the path on stderr |
| `newline-and-tab-bearing-values-round-trip.txtar` | `newline-and-tab-value-round-trips.txtar` | a newline/tab-bearing value round-trips as a double-quoted scalar |
| `nothing-to-do-is-rejected.txtar` | `nothing-to-do-exits-1.txtar` | an invocation with no pairs, removals or appends exits 1 |
| `null-value-lands-unquoted.txtar` | `coerces-null.txtar` | the `null` spelling lands unquoted |
| `other-keys-comments-and-body-survive-the-set.txtar` | `preserves-other-keys-and-body.txtar` | other keys and the body stay byte-identical; comment preservation is not asserted |
| `pairs-removals-and-appends-combine-in-one-call.txtar` | `combined-removals-sets-appends.txtar` | one call removing, setting and appending, removals first |
| `partly-numeric-value-stays-a-plain-string.txtar` | `partly-numeric-value-stays-a-string.txtar` | a digit-leading value stays a plain unquoted string |
| `re-setting-the-same-value-prints-no-diff.txtar` | `second-identical-call-is-a-no-op.txtar` | a second identical call prints no diff and exits 0 |
| `sets-a-key-to-a-literal-value.txtar` | `sets-a-literal-value.txtar` | sets a frontmatter key to a literal string |
| `stubbed-macro-value-lands-typed.txtar` | `stub-lands-typed-value.txtar` | a `macro_stubs` entry resolves without execution and lands typed |
| `summary-goes-to-stderr-not-stdout.txtar` | `summary-goes-to-stderr.txtar` | the summary line goes to stderr, stdout carries only the diff |
| `syntax-sensitive-string-keeps-its-quotes.txtar` | `syntax-sensitive-strings-keep-quotes.txtar` | YAML-syntax-sensitive values are written single-quoted |
| `unknown-macro-path-is-rejected.txtar` | `unknown-macro-exits-2.txtar` | an undeclared macro path exits 2 naming the missing config path |
| `value-may-contain-equals-signs.txtar` | none | nothing asserts the split-on-first-`=` rule for a value containing `=` |
| `yaml-1-1-boolean-word-stays-a-string.txtar` | `yaml-11-boolean-word-gets-quoted.txtar` | a YAML-1.1 boolean word (`yes`) is single-quoted |

Gap verdicts: `a-real-macro-runs-and-its-output-lands.txtar` covered by `real-macro-executes-command.txtar`; `newline-and-tab-bearing-values-round-trip.txtar` covered by `newline-and-tab-value-round-trips.txtar`; `malformed-append-pair-is-rejected.txtar` not covered.

Exact case-name recall was 3/34; the scored figure is the mapped 30/34, and gaps score 2/3 on behaviour. All 27 unmatched branch cases mapped onto an etalon behaviour — nothing the branch wrote is unaccounted for.

## Mutation kills

The frozen set at `vault/benchmarks/mutations/frontmatter-update-e2e` applied one patch at a time over the branch's corpus via `uv run pytest e2e/cases/frontmatter-update -q --tb=no`: **12/15 killed** (80.0%).

| patch | verdict | evidence |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | killed | coerces-boolean.txtar |
| `02_int-coercion-dropped.patch` | killed | coerces-integer.txtar, real-macro-executes-command.txtar, sets-multiple-keys-in-one-call.txtar, stub-lands-typed-value.txtar |
| `03_float-coercion-dropped.patch` | killed | coerces-float.txtar |
| `04_null-coercion-dropped.patch` | killed | coerces-null.txtar |
| `05_yaml-1-1-quoting-dropped.patch` | killed | yaml-11-boolean-word-gets-quoted.txtar |
| `06_empty-value-becomes-null.patch` | **survived** | corpus exit 0 with no case named |
| `07_first-equals-split-lost.patch` | **survived** | corpus exit 0 with no case named |
| `08_empty-key-accepted.patch` | **survived** | corpus exit 0 with no case named |
| `09_macro-left-unrendered.patch` | killed | malformed-jinja-exits-2.txtar, newline-and-tab-value-round-trips.txtar, real-macro-executes-command.txtar, stub-lands-typed-value.txtar, stub-macro-date-stays-a-string.txtar, unknown-macro-exits-2.txtar |
| `10_macro-error-exits-1.patch` | killed | malformed-jinja-exits-2.txtar, unknown-macro-exits-2.txtar |
| `11_malformed-pair-exits-2.patch` | killed | malformed-pair-exits-1.txtar |
| `12_remove-is-a-noop.patch` | killed | combined-removals-sets-appends.txtar, remove-drops-a-key.txtar |
| `13_diff-suppressed-on-change.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, append-is-idempotent.txtar, coerces-boolean.txtar, coerces-float.txtar, coerces-integer.txtar, coerces-null.txtar, combined-removals-sets-appends.txtar, logs-one-line-when-a-vault-is-attached.txtar, newline-and-tab-value-round-trips.txtar, partly-numeric-value-stays-a-string.txtar, preserves-other-keys-and-body.txtar, real-macro-executes-command.txtar, remove-drops-a-key.txtar, second-identical-call-is-a-no-op.txtar, sets-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stdout-is-a-unified-diff.txtar, stub-lands-typed-value.txtar, stub-macro-date-stays-a-string.txtar, summary-goes-to-stderr.txtar, syntax-sensitive-strings-keep-quotes.txtar, yaml-11-boolean-word-gets-quoted.txtar |
| `14_summary-to-stdout.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, append-is-idempotent.txtar, coerces-boolean.txtar, coerces-float.txtar, coerces-integer.txtar, coerces-null.txtar, combined-removals-sets-appends.txtar, logs-one-line-when-a-vault-is-attached.txtar, newline-and-tab-value-round-trips.txtar, partly-numeric-value-stays-a-string.txtar, preserves-other-keys-and-body.txtar, real-macro-executes-command.txtar, remove-drops-a-key.txtar, second-identical-call-is-a-no-op.txtar, sets-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stdout-is-a-unified-diff.txtar, stub-lands-typed-value.txtar, stub-macro-date-stays-a-string.txtar, summary-goes-to-stderr.txtar, syntax-sensitive-strings-keep-quotes.txtar, yaml-11-boolean-word-gets-quoted.txtar |
| `15_log-line-dropped.patch` | killed | logs-one-line-when-a-vault-is-attached.txtar |

## Process profile

| milestone | attempts | feedback files | wall | tool calls | malformed | loops | deaths | blind rebaselines | pushed lines |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 1 | 0 | 13m52s | 146 | 0 | 0 | 0 | 1 | 445 |
| M02-list-ops-and-macro-cases | 1 | 0 | 12m59s | 131 | 0 | 0 | 0 | 0 | 313 |
| M03-delete-superseded-units | 1 | 0 | 15m08s | 99 | 0 | 0 | 0 | 0 | 162 |

Tool mix: bash 147, edit 6, find 3, grep 3, ls 9, read 162, run_agent 9, write 37. Calls by agent: orchestrator 81, researcher 112, validator 58, worker 125. Log schema: pi. Worker wall clock 41m59s across 3 attempt log(s); first log start to last log end spans 44m51s.

## Cost

| milestone | generations | cost USD | in | out | cache in | cache out |
| --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 75 | 0.0726 | 4.8M | 74.1k | 2.2M | 0 |
| M02-list-ops-and-macro-cases | 73 | 0.0731 | 4.8M | 67.8k | 2.2M | 0 |
| M03-delete-superseded-units | 60 | 0.0546 | 3.5M | 74.8k | 1.6M | 0 |

Source `openrouter` via `https://openrouter.ai/api/v1/generation`: 208/208 unique generation ids fetched from 208 id mentions, failures none. OpenRouter total $0.2004; the ndjson fallback figure — the worker's own pricing, not OpenRouter billing — is $0.4007.

## Composites

`code` scores 89.57 of 100 available weight → **89.57/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| gates.ci | 10 | 10.0 | pass → 10 |
| gates.determinism | 10 | 10.0 | pass → 10 |
| gates.scope | 10 | 10.0 | pass → 10 |
| gates.e2e | 5 | 5.0 | pass → 5 |
| gates.unit_deleted | 5 | 5.0 | pass → 5 |
| corpus.recall | 15 | 13.24 | 30/34 etalon names × 15 |
| corpus.four_channel | 10 | 8.0 | 24/30 cases × 10 |
| corpus.gaps | 5 | 3.33 | 2/3 gap names × 5 |
| corpus.wildcard | 5 | 5.0 | wildcard line ratio 0.0046 against band 0.05–0.3 |
| corpus.mutation | 25 | 20.0 | 12/15 mutants killed × 25 |

`agentic` scores 90.0 of 100 available weight → **90.0/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| attempts | 30 | 30.0 | 30 − 10×0 retries |
| rebaseline | 20 | 10.0 | 20 − 10×1 blind rebaselines |
| tool_discipline | 30 | 30.0 | 30 − 2×0 malformed − 5×0 loops − 10×0 deaths |
| churn | 20 | 20.0 | 920 pushed ÷ 1606 diff = 0.5729× against band 1.5–4.0 |

## Review

Two reviewers graded the branch diff against `review-rubric.md`, both given the case-mapping table above and the entry's scope allowlist. Mean grade **3.95/5**.

| reviewer | grade /5 | findings |
| --- | --- | --- |
| `fable:medium` | 3.9 | 6 — the four etalon behaviours mapped to nothing (empty key `=value`, `key=` empty string, `=` inside a value, malformed `--append` pair), plus inline-comment preservation dropped from `preserves-other-keys-and-body.txtar`'s fixture, plus the M03 DoD reading as a complete migration over a cross-check that records three coverage-losing gaps. Sub-grades: correctness 4, test quality 3.5, code quality 5, scope discipline 5 |
| `codex` | 4.0 | 4 — the same four unported etalon behaviours, each traced to its mapping row and its cross-check acknowledgement. Sub-grades: correctness 4, test quality 3, code quality 4, scope discipline 5 |

The two reviewers agree on the whole of the smaller list: every finding `codex` raised is one of the four unported behaviours, and those four are also the three mutants that survived (`06_empty-value-becomes-null`, `07_first-equals-split-lost`, `08_empty-key-accepted`) plus the one uncovered gap case. Three independent measurement layers — mutation, case mapping and both reviewers — converge on the same hole.

## History row

| date | model | provider | outcome | att | code | agentic | review | diff | tokens | cache | cost | time | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-16 18:25 | `deepseek/deepseek-v4-flash-0731` | openrouter | pass | 1/1/1 | 89.6 | 90.0 | 3.95 | 1606 | in 13.1M out 216.7k | in 5.9M out 0 | $0.20 | 41m59s | [20260816-182530](runs/20260816-182530-deepseek-deepseek-v4-flash-0731.md) |
