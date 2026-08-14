---
benchmark: frontmatter-update-e2e
model: google/gemini-3.7-flash
branch: bench/google-gemini-3-7-flash
run_id: 20260814-211700
date: '2026-08-14'
outcome: pass
code: 76.69
agentic: 80.0
review: 2.75
status: publishing
---

# Benchmark run — google/gemini-3.7-flash

Branch `bench/google-gemini-3-7-flash` scored against the `frontmatter-update-e2e` registry entry, baseline `a025189`. Every number below is computed by `bench-score`; the history row in [history.md](../history.md) is this file's summary.

## Summary

| field | value |
| --- | --- |
| date | 2026-08-14 |
| model | `google/gemini-3.7-flash` |
| outcome | pass |
| att | 1/1/1 |
| code | 76.7 |
| agentic | 80.0 |
| review | 2.75 |
| diff | 1564 |
| tokens | 9.4M |
| cost | $1.13 |
| wall | 21m45s |

## Gates

| check | verdict | evidence |
| --- | --- | --- |
| ci | pass | just ci exit 0 |
| determinism | pass | uv run pytest e2e --txtar-update exit 0; git diff --quiet after: clean |
| e2e | pass | just e2e exit 0 |
| milestones | pass | 3/3 milestones terminal: M01-core-cli-cases=done, M02-list-ops-and-macro-cases=done, M03-delete-superseded-units=done |
| scope | **fail** | 37 changed path(s) vs a025189; 1 outside: CLAUDE.md |
| unit_deleted | pass | booping-python/tests/commands/frontmatter_update_test.py absent; git grep frontmatter_update_test: 0 hits |

## Corpus quality

| metric | value | evidence |
| --- | --- | --- |
| cases | 30 | `booping-python/e2e/cases/frontmatter-update` |
| etalon recall | 28/34 (82.35%) | exact case-name matches against the frozen etalon list |
| gap cases | 1/3 | cases with no unit-test counterpart |
| four-channel cases | 23/30 (76.67%) | exit + stdout + stderr + expected all asserted |
| wildcard line ratio | 0.0025 | 1 wildcarded of 408 asserted lines |

## Case mapping

Exact-name recall was 5/34; the case-mapping judge mapped 23 further branch cases onto etalon names by behaviour, giving the 28/34 (82.35%) mapped recall the corpus table reports. Gap verdicts below are the judge's, scored on behaviour.

| etalon case | branch case | rationale |
|---|---|---|
| a-real-macro-runs-and-its-output-lands.txtar | executes-real-macro-command.txtar | defines a real `echo` macro in config, runs it unstubbed, and asserts its output lands in the frontmatter |
| append-creates-a-list-on-a-null-key.txtar | append-creates-list-on-null-key.txtar | `--append` onto `sessions: null` converts it to a one-element list |
| append-creates-a-list-on-an-absent-key.txtar | append-creates-list-on-absent-key.txtar | `--append` onto a missing key creates a one-element list |
| append-extends-an-existing-list.txtar | append-extends-existing-list.txtar | `--append` adds a second item to an existing list |
| append-onto-a-scalar-is-rejected.txtar | append-onto-scalar-is-rejected.txtar | `--append` onto scalar `status` exits 1 with a stderr error |
| appending-the-same-value-twice-adds-it-once.txtar | append-is-idempotent.txtar | appends the identical value in two calls and asserts the list holds it once, second call diffless |
| boolean-value-lands-unquoted.txtar | coerces-boolean-value.txtar | `blocked=true` is coerced and emitted as a bare boolean literal |
| diff-names-the-plan-on-both-sides.txtar | diff-shape-is-unified-diff-on-stdout.txtar | asserts unified-diff headers `--- plan.md` / `+++ plan.md` both carry the plan filename |
| empty-key-in-a-pair-is-rejected.txtar | none | no unmatched branch case passes a pair with an empty key |
| empty-value-lands-as-an-empty-string.txtar | none | no branch case sets `key=` with an empty value |
| float-value-lands-unquoted.txtar | coerces-float-value.txtar | `ratio=1.5` is coerced and emitted as a bare float literal |
| integer-value-lands-unquoted.txtar | coerces-integer-value.txtar | `sp=23` is coerced and emitted as a bare integer literal |
| macro-rendered-date-like-value-stays-a-string.txtar | macro-rendered-date-stays-a-string.txtar | stubbed macro yielding `2026-08-12 14:17` lands as a plain string |
| malformed-append-pair-is-rejected.txtar | none | no branch case passes a malformed `--append` argument |
| malformed-jinja-in-a-value-is-rejected.txtar | malformed-jinja-is-rejected.txtar | broken `{{ macro( }}` expression exits 2 with a TemplateSyntaxError on stderr |
| newline-and-tab-bearing-values-round-trip.txtar | none | preserves-newline-and-tab-in-value passes only literal backslash-t characters, never a real newline or tab |
| null-value-lands-unquoted.txtar | coerces-null-value.txtar | `retro=null` is coerced and emitted as a bare null literal |
| other-keys-comments-and-body-survive-the-set.txtar | preserves-other-keys-and-body.txtar | setting one key leaves untouched keys and the markdown body intact (branch fixture omits the comments facet) |
| pairs-removals-and-appends-combine-in-one-call.txtar | combined-pairs-removals-and-appends.txtar | one invocation with a pair, `--remove` and `--append` applies all three |
| partly-numeric-value-stays-a-plain-string.txtar | none | no branch case pins a partly-numeric value staying an unquoted plain string |
| re-setting-the-same-value-prints-no-diff.txtar | second-identical-call-prints-no-diff.txtar | identical second invocation exits 0 and emits no diff on stdout |
| remove-drops-a-key.txtar | removes-a-key.txtar | `--remove business_goal` deletes the key and diffs the drop |
| sets-a-key-to-a-literal-value.txtar | sets-a-key-with-a-literal-value.txtar | plain `status=in-progress` pair updates the key |
| stubbed-macro-value-lands-typed.txtar | interpolates-stubbed-macro-value.txtar | `macro_stubs` value `"19700101"` interpolates and lands typed in frontmatter |
| summary-goes-to-stderr-not-stdout.txtar | success-summary-line-on-stderr-not-stdout.txtar | asserts the `updated …` summary is on stderr while stdout carries only the diff |
| syntax-sensitive-string-keeps-its-quotes.txtar | quotes-ambiguous-string-value.txtar | value `@lead: 23 things` with syntax-sensitive characters is single-quoted to stay a string |
| unknown-macro-path-is-rejected.txtar | unknown-macro-name-is-rejected.txtar | `macro('core.macros.nope')` exits 2 with a no-macro-declared error on stderr |
| value-may-contain-equals-signs.txtar | none | no branch case passes a value containing `=` after the first split |
| yaml-1-1-boolean-word-stays-a-string.txtar | coerces-yaml-1-1-boolean-word-as-quoted-string.txtar | `summary=yes` is single-quoted so the YAML 1.1 boolean word stays a string |

Gap verdicts: `a-real-macro-runs-and-its-output-lands.txtar` covered by `executes-real-macro-command.txtar` (real `echo` macro executed across the subprocess boundary); `newline-and-tab-bearing-values-round-trip.txtar` not covered (only literal backslash-t, control characters never exercised); `malformed-append-pair-is-rejected.txtar` not covered (no case passes a malformed `--append` pair).

## Mutation kills

The frozen set at `vault/benchmarks/mutations/frontmatter-update-e2e` applied one patch at a time over the branch's corpus via `uv run pytest e2e/cases/frontmatter-update -q --tb=no`: **12/15 killed** (80.0%).

| patch | verdict | evidence |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | killed | coerces-boolean-value.txtar |
| `02_int-coercion-dropped.patch` | killed | coerces-integer-value.txtar, executes-real-macro-command.txtar, interpolates-stubbed-macro-value.txtar, sets-multiple-keys-in-one-call.txtar |
| `03_float-coercion-dropped.patch` | killed | coerces-float-value.txtar |
| `04_null-coercion-dropped.patch` | killed | coerces-null-value.txtar |
| `05_yaml-1-1-quoting-dropped.patch` | killed | coerces-yaml-1-1-boolean-word-as-quoted-string.txtar |
| `06_empty-value-becomes-null.patch` | **survived** | corpus exit 0 with no case named |
| `07_first-equals-split-lost.patch` | **survived** | corpus exit 0 with no case named |
| `08_empty-key-accepted.patch` | **survived** | corpus exit 0 with no case named |
| `09_macro-left-unrendered.patch` | killed | executes-real-macro-command.txtar, interpolates-stubbed-macro-value.txtar, macro-rendered-date-stays-a-string.txtar, malformed-jinja-is-rejected.txtar, unknown-macro-name-is-rejected.txtar |
| `10_macro-error-exits-1.patch` | killed | malformed-jinja-is-rejected.txtar, unknown-macro-name-is-rejected.txtar |
| `11_malformed-pair-exits-2.patch` | killed | malformed-pair-is-rejected.txtar |
| `12_remove-is-a-noop.patch` | killed | combined-pairs-removals-and-appends.txtar, removes-a-key.txtar |
| `13_diff-suppressed-on-change.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, append-is-idempotent.txtar, coerces-boolean-value.txtar, coerces-float-value.txtar, coerces-integer-value.txtar, coerces-null-value.txtar, coerces-yaml-1-1-boolean-word-as-quoted-string.txtar, combined-pairs-removals-and-appends.txtar, diff-shape-is-unified-diff-on-stdout.txtar, executes-real-macro-command.txtar, interpolates-stubbed-macro-value.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-rendered-date-stays-a-string.txtar, preserves-newline-and-tab-in-value.txtar, preserves-other-keys-and-body.txtar, quotes-ambiguous-string-value.txtar, removes-a-key.txtar, second-identical-call-prints-no-diff.txtar, sets-a-key-with-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, success-summary-line-on-stderr-not-stdout.txtar |
| `14_summary-to-stdout.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, append-is-idempotent.txtar, coerces-boolean-value.txtar, coerces-float-value.txtar, coerces-integer-value.txtar, coerces-null-value.txtar, coerces-yaml-1-1-boolean-word-as-quoted-string.txtar, combined-pairs-removals-and-appends.txtar, diff-shape-is-unified-diff-on-stdout.txtar, executes-real-macro-command.txtar, interpolates-stubbed-macro-value.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-rendered-date-stays-a-string.txtar, preserves-newline-and-tab-in-value.txtar, preserves-other-keys-and-body.txtar, quotes-ambiguous-string-value.txtar, removes-a-key.txtar, second-identical-call-prints-no-diff.txtar, sets-a-key-with-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, success-summary-line-on-stderr-not-stdout.txtar |
| `15_log-line-dropped.patch` | killed | logs-one-line-when-a-vault-is-attached.txtar |

## Process profile

| milestone | attempts | feedback files | wall | tool calls | malformed | loops | deaths | blind rebaselines | pushed lines |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 1 | 0 | 11m51s | 98 | 0 | 0 | 0 | 5 | 567 |
| M02-list-ops-and-macro-cases | 1 | 0 | 5m40s | 43 | 0 | 0 | 0 | 0 | 432 |
| M03-delete-superseded-units | 1 | 0 | 4m13s | 17 | 0 | 0 | 0 | 0 | 55 |

Tool mix: Bash 38, Read 65, Write 55. Worker wall clock 21m45s across 3 attempt log(s); first log start to last log end spans 24m16s.

## Cost

| milestone | generations | cost USD | native prompt | native completion | of which cached |
| --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 99 | 0.7399 | 6.2M | 12.9k | 4.8M |
| M02-list-ops-and-macro-cases | 44 | 0.2726 | 2.4M | 6.7k | 1.9M |
| M03-delete-superseded-units | 18 | 0.1134 | 774.1k | 3.9k | 548.3k |

Source `openrouter` via `https://openrouter.ai/api/v1/generation`: 161/161 unique generation ids fetched from 325 id mentions, failures none. OpenRouter total $1.1260; the ndjson fallback figure — Claude Code's own pricing, not OpenRouter billing — is $15.6020.

## Composites

`code` scores 76.69 of 100 available weight → **76.69/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| gates.ci | 10 | 10.0 | pass → 10 |
| gates.determinism | 10 | 10.0 | pass → 10 |
| gates.scope | 10 | 0.0 | fail → 0 |
| gates.e2e | 5 | 5.0 | pass → 5 |
| gates.unit_deleted | 5 | 5.0 | pass → 5 |
| corpus.recall | 15 | 12.35 | 28/34 etalon names × 15 |
| corpus.four_channel | 10 | 7.67 | 23/30 cases × 10 |
| corpus.gaps | 5 | 1.67 | 1/3 gap names × 5 |
| corpus.wildcard | 5 | 5.0 | wildcard line ratio 0.0025 against band 0.05–0.3 |
| corpus.mutation | 25 | 20.0 | 12/15 mutants killed × 25 |

`agentic` scores 80.0 of 100 available weight → **80.0/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| attempts | 30 | 30.0 | 30 − 10×0 retries |
| rebaseline | 20 | 0.0 | 20 − 10×5 blind rebaselines |
| tool_discipline | 30 | 30.0 | 30 − 2×0 malformed − 5×0 loops − 10×0 deaths |
| churn | 20 | 20.0 | 1054 pushed ÷ 1564 diff = 0.6739× against band 1.5–4.0 |

## Review

Both reviewers graded the same rubric over the branch diff against `a025189`, with the case-mapping table and the scope allowlist in the briefing. Reviewer grade is the mean of its four criterion grades; the `review` cell is the mean of the two reviewer grades: **2.75/5**.

| reviewer | grade /5 | findings |
| --- | --- | --- |
| `fable:medium` | 3.0 | correctness 3, test quality 2, code quality 4, scope discipline 3. Six findings: four coverage-cross-check rows claim coverage that does not exist (equals-bearing value, empty key, partly-numeric string, empty value), so those behaviours lost all coverage when the unit file was deleted; the newline/tab gap case passes only the literal two-character `\t`, never a real control character, though its DoD box is checked; `append-only-nothing-to-do-is-rejected.txtar` duplicates `nothing-to-do-is-rejected.txtar` and its description misstates its own `cmd`; `CLAUDE.md` edited outside the scope allowlist; no case exercises a malformed `--append` pair; `preserves-other-keys-and-body.txtar` drops the inline-comment facet the superseded unit asserted. |
| `codex` | 2.5 | correctness 2, test quality 2, code quality 4, scope discipline 2. Seven findings: the newline/tab case cannot detect corruption of real tab/newline values; cross-check rows map the empty-value, equals-bearing, empty-key and partly-numeric tests to cases that never exercise those inputs, leaving them untested after deletion; `append-only-nothing-to-do-is-rejected.txtar` duplicates the ordinary no-arguments case under a misleading name and no malformed `--append` pair is ever rejected; `CLAUDE.md` changed outside the allowlist. |

## History row

| date | model | outcome | att | code | agentic | review | diff | tokens | cost | wall | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-14 | `google/gemini-3.7-flash` | pass | 1/1/1 | 76.7 | 80.0 | 2.75 | 1564 | 9.4M | $1.13 | 21m45s | [20260814-211700](runs/20260814-211700-google-gemini-3-7-flash.md) |
