---
benchmark: frontmatter-update-e2e
model: google/gemini-3.7-flash
branch: bench/google-gemini-3-7-flash
run_id: 20260816-173144
date: 2026-08-16 17:31
outcome: pass
code: 89.05
agentic: 100.0
review: 3.5
status: publishing
---

# Benchmark run — google/gemini-3.7-flash

Branch `bench/google-gemini-3-7-flash` scored against the `frontmatter-update-e2e` registry entry, baseline `a025189`. Every number below is computed by `bench-score`; the history row in [history.md](../history.md) is this file's summary.

## Summary

| field | value |
| --- | --- |
| date | 2026-08-16 17:31 |
| model | `google/gemini-3.7-flash` |
| provider | openrouter |
| outcome | pass |
| att | 1/1/1 |
| code | 89.0 |
| agentic | 100.0 |
| review | 3.5 |
| diff | 1520 |
| tokens | in 18.6M out 111.7k |
| cache | in 8.3M out 0 |
| cost | $1.30 |
| time | 46m48s |

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
| wildcard line ratio | 0.0025 | 1 wildcarded of 393 asserted lines |

## Case mapping

Exact-name recall was 5/34; a case-mapping judge read the unmatched branch cases and mapped 24 of them onto etalon behaviours, giving the mapped recall 29/34 (85.29%) the composite scores on. The 5 unmapped etalon names below are behaviours this branch never ported.

| Etalon case | Branch case | Behaviour |
| --- | --- | --- |
| a-real-macro-runs-and-its-output-lands.txtar | executes-real-macro-and-coerces-output.txtar | Unstubbed macro declared as `["echo","1"]` in config actually runs through the subprocess boundary; captured stdout lands typed. |
| append-creates-a-list-on-a-null-key.txtar | append-creates-list-on-null-key.txtar | `--append` on a key present with `null` replaces it with a one-item list. |
| append-creates-a-list-on-an-absent-key.txtar | append-creates-list-on-absent-key.txtar | `--append` on a missing key creates a one-item list. |
| append-extends-an-existing-list.txtar | append-extends-existing-list.txtar | `--append` adds an item to an existing list, normalising indentation. |
| append-onto-a-scalar-is-rejected.txtar | append-onto-scalar-is-rejected.txtar | `--append` onto a scalar key exits 1 with an error on stderr, file untouched. |
| appending-the-same-value-twice-adds-it-once.txtar | append-is-idempotent.txtar | Two identical appends: both succeed and print summaries, second contributes no diff, member unduplicated. |
| boolean-value-lands-unquoted.txtar | coerces-boolean-value.txtar | `true` coerces to an unquoted YAML boolean. |
| diff-names-the-plan-on-both-sides.txtar | unified-diff-shape-on-stdout.txtar | stdout receipt is a unified diff with the plan path on `---`/`+++` and an `@@` hunk header. Branch version is thinner: 3-line file, so the "untouched body never reaches the diff" offset aspect is not exercised. |
| empty-key-in-a-pair-is-rejected.txtar | none | No branch case for `=value` rejecting with an empty-key-specific message distinct from malformed-pair. |
| empty-value-lands-as-an-empty-string.txtar | none | No branch case for `summary=` landing as `''` rather than null. |
| float-value-lands-unquoted.txtar | coerces-float-value.txtar | `1.5` coerces to an unquoted YAML float. |
| integer-value-lands-unquoted.txtar | coerces-integer-value.txtar | `23` coerces to an unquoted YAML integer. |
| macro-rendered-date-like-value-stays-a-string.txtar | macro-rendered-date-stays-string.txtar | Stubbed macro rendering `2026-08-12` lands single-quoted, not coerced to a date. |
| malformed-append-pair-is-rejected.txtar | none | Branch covers a malformed positional pair (exact-name match elsewhere) but nothing rejects `--append nope`. |
| malformed-jinja-in-a-value-is-rejected.txtar | malformed-jinja-is-rejected.txtar | Broken Jinja in a value exits 2 with a TemplateSyntaxError message on stderr. |
| newline-and-tab-bearing-values-round-trip.txtar | handles-newline-and-tab-bearing-value.txtar | Whitespace-bearing value round-trips: tab lands as a double-quoted `\t` escape. Branch passes a literal backslash-n (no Jinja string literal), so the real-newline folded-block half of the etalon behaviour is not asserted. |
| null-value-lands-unquoted.txtar | coerces-null-value.txtar | `null` coerces to an unquoted YAML null. |
| other-keys-comments-and-body-survive-the-set.txtar | preserves-other-keys-and-body.txtar | Untouched keys and the markdown body survive a set. Branch fixture carries no YAML comments, so comment survival is not asserted. |
| pairs-removals-and-appends-combine-in-one-call.txtar | combines-updates-removals-and-appends.txtar | A pair, a `--remove` and an `--append` in one invocation all land, with one combined summary line. |
| partly-numeric-value-stays-a-plain-string.txtar | none | No branch case for a digit-leading value like `23 things` staying bare and unquoted. |
| re-setting-the-same-value-prints-no-diff.txtar | second-identical-call-prints-no-diff-and-exits-0.txtar | Setting a key to the value it already holds exits 0, prints no stdout diff, still prints the stderr summary. |
| remove-drops-a-key.txtar | removes-key.txtar | `--remove` drops an existing key, summary shows `-key`. |
| sets-a-key-to-a-literal-value.txtar | sets-key-with-literal-value.txtar | A `key=value` pair rewrites the key in place, diff on stdout and summary on stderr. |
| stubbed-macro-value-lands-typed.txtar | stubbed-macro-resolves-typed-value.txtar | `macro_stubs` values resolve and land typed (int, bool, bare string). |
| summary-goes-to-stderr-not-stdout.txtar | summary-line-on-stderr-not-stdout.txtar | Stream split: stdout carries only the diff, stderr only the `updated …` summary. |
| syntax-sensitive-string-keeps-its-quotes.txtar | quotes-ambiguous-string-value.txtar | Syntax-sensitive strings are single-quoted. Branch asserts only `@lead`; the etalon's alias/anchor/tag/percent/backtick/padded/`a: b` sweep is not covered. |
| unknown-macro-path-is-rejected.txtar | unknown-macro-is-rejected.txtar | Unknown macro config path exits 2 with an error naming the path. |
| value-may-contain-equals-signs.txtar | none | No branch case for splitting on the first `=` only so `goal=a = b` keeps the trailing `=`. |
| yaml-1-1-boolean-word-stays-a-string.txtar | yaml-1-1-boolean-word-stays-string.txtar | `yes` is written single-quoted so it reloads as a string. |

Gap verdicts:

- `newline-and-tab-bearing-values-round-trip.txtar` — covered by `handles-newline-and-tab-bearing-value.txtar` (partial: tab only, no real newline)
- `malformed-append-pair-is-rejected.txtar` — not covered
- `a-real-macro-runs-and-its-output-lands.txtar` — covered by `executes-real-macro-and-coerces-output.txtar`

## Mutation kills

The frozen set at `vault/benchmarks/mutations/frontmatter-update-e2e` applied one patch at a time over the branch's corpus via `uv run pytest e2e/cases/frontmatter-update -q --tb=no`: **12/15 killed** (80.0%).

| patch | verdict | evidence |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | killed | coerces-boolean-value.txtar, stubbed-macro-resolves-typed-value.txtar |
| `02_int-coercion-dropped.patch` | killed | coerces-integer-value.txtar, executes-real-macro-and-coerces-output.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-resolves-typed-value.txtar, summary-line-on-stderr-not-stdout.txtar |
| `03_float-coercion-dropped.patch` | killed | coerces-float-value.txtar |
| `04_null-coercion-dropped.patch` | killed | coerces-null-value.txtar |
| `05_yaml-1-1-quoting-dropped.patch` | killed | yaml-1-1-boolean-word-stays-string.txtar |
| `06_empty-value-becomes-null.patch` | **survived** | corpus exit 0 with no case named |
| `07_first-equals-split-lost.patch` | **survived** | corpus exit 0 with no case named |
| `08_empty-key-accepted.patch` | **survived** | corpus exit 0 with no case named |
| `09_macro-left-unrendered.patch` | killed | executes-real-macro-and-coerces-output.txtar, macro-rendered-date-stays-string.txtar, malformed-jinja-is-rejected.txtar, stubbed-macro-resolves-typed-value.txtar, unknown-macro-is-rejected.txtar |
| `10_macro-error-exits-1.patch` | killed | malformed-jinja-is-rejected.txtar, unknown-macro-is-rejected.txtar |
| `11_malformed-pair-exits-2.patch` | killed | malformed-pair-is-rejected.txtar |
| `12_remove-is-a-noop.patch` | killed | combines-updates-removals-and-appends.txtar, removes-key.txtar |
| `13_diff-suppressed-on-change.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, append-is-idempotent.txtar, coerces-boolean-value.txtar, coerces-float-value.txtar, coerces-integer-value.txtar, coerces-null-value.txtar, combines-updates-removals-and-appends.txtar, executes-real-macro-and-coerces-output.txtar, handles-newline-and-tab-bearing-value.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-rendered-date-stays-string.txtar, preserves-other-keys-and-body.txtar, quotes-ambiguous-string-value.txtar, removes-key.txtar, sets-key-with-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-resolves-typed-value.txtar, summary-line-on-stderr-not-stdout.txtar, unified-diff-shape-on-stdout.txtar, yaml-1-1-boolean-word-stays-string.txtar |
| `14_summary-to-stdout.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, append-is-idempotent.txtar, coerces-boolean-value.txtar, coerces-float-value.txtar, coerces-integer-value.txtar, coerces-null-value.txtar, combines-updates-removals-and-appends.txtar, executes-real-macro-and-coerces-output.txtar, handles-newline-and-tab-bearing-value.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-rendered-date-stays-string.txtar, preserves-other-keys-and-body.txtar, quotes-ambiguous-string-value.txtar, removes-key.txtar, second-identical-call-prints-no-diff-and-exits-0.txtar, sets-key-with-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-resolves-typed-value.txtar, summary-line-on-stderr-not-stdout.txtar, unified-diff-shape-on-stdout.txtar, yaml-1-1-boolean-word-stays-string.txtar |
| `15_log-line-dropped.patch` | killed | logs-one-line-when-a-vault-is-attached.txtar |

## Process profile

| milestone | attempts | feedback files | wall | tool calls | malformed | loops | deaths | blind rebaselines | pushed lines |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 1 | 0 | 13m57s | 144 | 0 | 0 | 0 | 0 | 403 |
| M02-list-ops-and-macro-cases | 1 | 0 | 19m22s | 133 | 0 | 0 | 0 | 0 | 485 |
| M03-delete-superseded-units | 1 | 0 | 13m29s | 70 | 0 | 0 | 0 | 0 | 246 |

Tool mix: bash 100, edit 8, find 9, grep 9, ls 3, read 161, run_agent 10, write 47. Calls by agent: orchestrator 44, researcher 79, validator 61, worker 163. Log schema: pi. Worker wall clock 46m48s across 3 attempt log(s); first log start to last log end spans 49m58s.

## Cost

| milestone | generations | cost USD | in | out | cache in | cache out |
| --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 148 | 0.5042 | 7.9M | 41.3k | 3.5M | 0 |
| M02-list-ops-and-macro-cases | 137 | 0.5056 | 7.9M | 38.2k | 3.5M | 0 |
| M03-delete-superseded-units | 75 | 0.2857 | 2.9M | 32.2k | 1.2M | 0 |

Source `openrouter` via `https://openrouter.ai/api/v1/generation`: 360/360 unique generation ids fetched from 360 id mentions, failures none. OpenRouter total $1.2955; the ndjson fallback figure — the worker's own pricing, not OpenRouter billing — is $1.2955.

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

`agentic` scores 100.0 of 100 available weight → **100.0/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| attempts | 30 | 30.0 | 30 − 10×0 retries |
| rebaseline | 20 | 20.0 | 20 − 10×0 blind rebaselines |
| tool_discipline | 30 | 30.0 | 30 − 2×0 malformed − 5×0 loops − 10×0 deaths |
| churn | 20 | 20.0 | 1134 pushed ÷ 1520 diff = 0.7461× against band 1.5–4.0 |

## Review

Two reviewers graded the branch diff against `a025189` on the shared rubric — correctness, test quality, code quality, scope discipline, each /5 — with the case-mapping table above supplied as context. Mean grade **3.5/5**.

| reviewer | grade /5 | findings |
| --- | --- | --- |
| fable:medium | 3.75 (correctness 3, test quality 3, code quality 4, scope discipline 5) | 5 — the cross-check's empty-key and value-with-equals rows are false mappings; the partly-numeric family maps onto a case asserting the opposite behaviour while M01's coercion DoD is ticked; `handles-newline-and-tab-bearing-value.txtar` sends a literal backslash-n rather than a newline; the empty-value set and YAML-comment survival are dropped without a rationale; eight syntax-sensitive quoting values thin to one |
| codex | 3.25 (correctness 2, test quality 4, code quality 5, scope discipline 2) | 3 — `coverage-cross-check.md` maps `test_value_with_equals_sign` onto a case with no equals in its value; maps `test_empty_key_exits_1` onto a case testing a missing equals sign rather than an empty key; `quotes-ambiguous-string-value.txtar` asserts only `@lead` against a unit test parametrized over eight values |

Both reviewers converge on the same defect: the M03 coverage cross-check — the artifact that justifies deleting the unit file — claims coverage for behaviours no corpus case asserts (empty key, value containing `=`, empty value, partly-numeric string, full syntax-sensitive quoting sweep). That matches the mutation layer independently, where `06_empty-value-becomes-null`, `07_first-equals-split-lost` and `08_empty-key-accepted` all survived.

## History row

| date | model | provider | outcome | att | code | agentic | review | diff | tokens | cache | cost | time | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-16 17:31 | `google/gemini-3.7-flash` | openrouter | pass | 1/1/1 | 89.0 | 100.0 | 3.5 | 1520 | in 18.6M out 111.7k | in 8.3M out 0 | $1.30 | 46m48s | [20260816-173144](runs/20260816-173144-google-gemini-3-7-flash.md) |
