---
benchmark: frontmatter-update-e2e
model: poolside/laguna-s-2.1:free
branch: bench/poolside-laguna-s-2-1-free
run_id: 20260814-230156
date: '2026-08-14'
outcome: pass
code: 78.54
agentic: 68.0
review: 3.5
status: publishing
---

# Benchmark run — poolside/laguna-s-2.1:free

Branch `bench/poolside-laguna-s-2-1-free` scored against the `frontmatter-update-e2e` registry entry, baseline `a025189`. Every number below is computed by `bench-score`; the history row in [history.md](../history.md) is this file's summary.

## Summary

| field | value |
| --- | --- |
| date | 2026-08-14 |
| model | `poolside/laguna-s-2.1:free` |
| outcome | pass |
| att | 2/1/1 |
| code | 78.5 |
| agentic | 68.0 |
| review | 3.5 |
| diff | 1524 |
| tokens | 12.5M |
| cost | $0.00 |
| time | 2h41m09s |

## Gates

| check | verdict | evidence |
| --- | --- | --- |
| ci | pass | just ci exit 0 |
| determinism | pass | uv run pytest e2e --txtar-update exit 0; git diff --quiet after: clean |
| e2e | pass | just e2e exit 0 |
| milestones | pass | 3/3 milestones terminal: M01-core-cli-cases=done, M02-list-ops-and-macro-cases=done, M03-delete-superseded-units=done |
| scope | **fail** | 36 changed path(s) vs a025189; 1 outside: CLAUDE.md |
| unit_deleted | pass | booping-python/tests/commands/frontmatter_update_test.py absent; git grep frontmatter_update_test: 0 hits |

## Corpus quality

| metric | value | evidence |
| --- | --- | --- |
| cases | 28 | `booping-python/e2e/cases/frontmatter-update` |
| etalon recall | 28/34 (82.35%) | exact case-name matches against the frozen etalon list |
| gap cases | 2/3 | cases with no unit-test counterpart |
| four-channel cases | 22/28 (78.57%) | exit + stdout + stderr + expected all asserted |
| wildcard line ratio | 0.0053 | 2 wildcarded of 380 asserted lines |

## Case mapping

Judged by a case-mapping sub-agent over the corpus JSON's unmatched lists; recall and gap counts above are the mapped counts.

| Etalon case | Branch case | Behaviour asserted by the branch case |
|---|---|---|
| a-real-macro-runs-and-its-output-lands.txtar | real-macro-execution-gap-case.txtar | a real argv macro (`echo 1`) under `core.macros` executes and its output lands in frontmatter |
| append-creates-a-list-on-a-null-key.txtar | append-creates-list-on-null-key.txtar | `--append` turns a null key into a one-element block list |
| append-creates-a-list-on-an-absent-key.txtar | append-creates-list-on-absent-key.txtar | `--append` creates a one-element block list on an absent key |
| append-extends-an-existing-list.txtar | append-extends-existing-list.txtar | `--append` adds the value to an existing list |
| append-onto-a-scalar-is-rejected.txtar | append-onto-scalar-exits-1.txtar | appending onto a scalar key exits 1 with a stderr error, file unchanged |
| appending-the-same-value-twice-adds-it-once.txtar | append-is-idempotent-second-run-no-diff.txtar | a second identical `--append` is a no-op — list keeps one element, no second diff |
| boolean-value-lands-unquoted.txtar | set-coerces-boolean.txtar | literal `true` lands as a YAML boolean (unquoted) |
| diff-names-the-plan-on-both-sides.txtar | diff-shape-on-stdout.txtar | stdout carries a unified diff whose `---`/`+++` headers both name the plan file |
| empty-key-in-a-pair-is-rejected.txtar | none | — |
| empty-value-lands-as-an-empty-string.txtar | none | — |
| float-value-lands-unquoted.txtar | set-coerces-float.txtar | decimal literal lands as a YAML float (unquoted) |
| integer-value-lands-unquoted.txtar | set-coerces-integer.txtar | numeric literal lands as a YAML integer (unquoted) |
| macro-rendered-date-like-value-stays-a-string.txtar | macro-rendered-date-like-stays-a-string.txtar | a macro-rendered date-like value stays a string in the file |
| malformed-append-pair-is-rejected.txtar | none | — |
| malformed-jinja-in-a-value-is-rejected.txtar | malformed-jinja-exits-2.txtar | malformed Jinja in a value exits 2 with a stderr error, file unchanged |
| null-value-lands-unquoted.txtar | set-coerces-null.txtar | literal `null` lands as a YAML null (unquoted) |
| other-keys-comments-and-body-survive-the-set.txtar | none | — (no branch fixture carries comments; sibling-key/body preservation only rides along in sets-a-literal-value) |
| pairs-removals-and-appends-combine-in-one-call.txtar | combined-pairs-removals-and-appends.txtar | one call combines removals, sets and appends with an ordered stderr summary |
| partly-numeric-value-stays-a-plain-string.txtar | none | — |
| re-setting-the-same-value-prints-no-diff.txtar | second-identical-call-prints-no-diff.txtar | a second identical set prints no diff and exits 0 |
| sets-a-key-to-a-literal-value.txtar | sets-a-literal-value.txtar | sets a scalar key from a literal, preserving siblings and body |
| stubbed-macro-value-lands-typed.txtar | stubbed-macro-lands-typed.txtar | a `macro_stubs` value resolves without execution and lands typed (int) |
| summary-goes-to-stderr-not-stdout.txtar | summary-line-on-stderr.txtar | the success summary line goes to stderr, never stdout |
| syntax-sensitive-string-keeps-its-quotes.txtar | set-quotes-ambiguous-string.txtar | a mapping-like value (`a: b`) is single-quoted so it stays a string |
| unknown-macro-path-is-rejected.txtar | unknown-macro-exits-2.txtar | an undeclared, unstubbed macro path exits 2 naming the missing path |
| value-may-contain-equals-signs.txtar | none | — |
| yaml-1-1-boolean-word-stays-a-string.txtar | set-keeps-yes-as-string.txtar | YAML-1.1 word `yes` is single-quoted to stay a string |

Gap verdicts: `newline-and-tab-bearing-values-round-trip.txtar` covered by the branch case of the same name (tab as double-quoted escape, Jinja-carried newline as folded single-quoted block); `a-real-macro-runs-and-its-output-lands.txtar` covered by `real-macro-execution-gap-case.txtar`; `malformed-append-pair-is-rejected.txtar` not covered — no branch case passes a malformed pair to `--append`.

Exact-name recall was 7/34 (20.59%); mapped recall is 28/34 (82.35%) — the model named cases in its own scheme, and 21 behaviours mapped one-to-one.

## Mutation kills

The frozen set at `vault/benchmarks/mutations/frontmatter-update-e2e` applied one patch at a time over the branch's corpus via `uv run pytest e2e/cases/frontmatter-update -q --tb=no`: **12/15 killed** (80.0%).

| patch | verdict | evidence |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | killed | set-coerces-boolean.txtar |
| `02_int-coercion-dropped.patch` | killed | diff-shape-on-stdout.txtar, real-macro-execution-gap-case.txtar, set-coerces-integer.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-lands-typed.txtar |
| `03_float-coercion-dropped.patch` | killed | set-coerces-float.txtar |
| `04_null-coercion-dropped.patch` | killed | set-coerces-null.txtar |
| `05_yaml-1-1-quoting-dropped.patch` | killed | newline-and-tab-bearing-values-round-trip.txtar, set-keeps-yes-as-string.txtar |
| `06_empty-value-becomes-null.patch` | **survived** | corpus exit 0 with no case named |
| `07_first-equals-split-lost.patch` | **survived** | corpus exit 0 with no case named |
| `08_empty-key-accepted.patch` | **survived** | corpus exit 0 with no case named |
| `09_macro-left-unrendered.patch` | killed | macro-rendered-date-like-stays-a-string.txtar, malformed-jinja-exits-2.txtar, newline-and-tab-bearing-values-round-trip.txtar, real-macro-execution-gap-case.txtar, stubbed-macro-lands-typed.txtar, unknown-macro-exits-2.txtar |
| `10_macro-error-exits-1.patch` | killed | malformed-jinja-exits-2.txtar, unknown-macro-exits-2.txtar |
| `11_malformed-pair-exits-2.patch` | killed | malformed-pair-is-rejected.txtar |
| `12_remove-is-a-noop.patch` | killed | combined-pairs-removals-and-appends.txtar, remove-drops-a-key.txtar |
| `13_diff-suppressed-on-change.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, append-is-idempotent-second-run-no-diff.txtar, combined-pairs-removals-and-appends.txtar, diff-shape-on-stdout.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-rendered-date-like-stays-a-string.txtar, newline-and-tab-bearing-values-round-trip.txtar, real-macro-execution-gap-case.txtar, remove-drops-a-key.txtar, second-identical-call-prints-no-diff.txtar, set-coerces-boolean.txtar, set-coerces-float.txtar, set-coerces-integer.txtar, set-coerces-null.txtar, set-keeps-yes-as-string.txtar, set-quotes-ambiguous-string.txtar, sets-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-lands-typed.txtar, summary-line-on-stderr.txtar |
| `14_summary-to-stdout.patch` | killed | append-creates-list-on-absent-key.txtar, append-creates-list-on-null-key.txtar, append-extends-existing-list.txtar, append-is-idempotent-second-run-no-diff.txtar, combined-pairs-removals-and-appends.txtar, diff-shape-on-stdout.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-rendered-date-like-stays-a-string.txtar, newline-and-tab-bearing-values-round-trip.txtar, real-macro-execution-gap-case.txtar, remove-drops-a-key.txtar, second-identical-call-prints-no-diff.txtar, set-coerces-boolean.txtar, set-coerces-float.txtar, set-coerces-integer.txtar, set-coerces-null.txtar, set-keeps-yes-as-string.txtar, set-quotes-ambiguous-string.txtar, sets-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-lands-typed.txtar, summary-line-on-stderr.txtar |
| `15_log-line-dropped.patch` | killed | logs-one-line-when-a-vault-is-attached.txtar |

## Process profile

| milestone | attempts | feedback files | wall | tool calls | malformed | loops | deaths | blind rebaselines | pushed lines |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 2 | 1 | 1h13m03s | 121 | 1 | 0 | 0 | 6 | 179 |
| M02-list-ops-and-macro-cases | 1 | 0 | 34m29s | 72 | 0 | 0 | 0 | 0 | 351 |
| M03-delete-superseded-units | 1 | 0 | 53m36s | 59 | 0 | 0 | 0 | 0 | 55 |

Tool mix: Bash 73, Edit 3, Read 116, TaskCreate 11, TaskUpdate 17, Write 32. Worker wall clock 2h41m09s across 4 attempt log(s); first log start to last log end spans 2h45m14s.

## Cost

| milestone | generations | cost USD | native prompt | native completion | of which cached |
| --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 66 | 0.0000 | 6.1M | 145.2k | 4.7M |
| M02-list-ops-and-macro-cases | 38 | 0.0000 | 3.8M | 89.2k | 3.1M |
| M03-delete-superseded-units | 26 | 0.0000 | 2.2M | 126.4k | 1.3M |

Source `openrouter` via `https://openrouter.ai/api/v1/generation`: 130/130 unique generation ids fetched from 473 id mentions, failures none. OpenRouter total $0.0000; the ndjson fallback figure — Claude Code's own pricing, not OpenRouter billing — is $28.3405.

## Composites

`code` scores 78.54 of 100 available weight → **78.54/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| gates.ci | 10 | 10.0 | pass → 10 |
| gates.determinism | 10 | 10.0 | pass → 10 |
| gates.scope | 10 | 0.0 | fail → 0 |
| gates.e2e | 5 | 5.0 | pass → 5 |
| gates.unit_deleted | 5 | 5.0 | pass → 5 |
| corpus.recall | 15 | 12.35 | 28/34 etalon names × 15 |
| corpus.four_channel | 10 | 7.86 | 22/28 cases × 10 |
| corpus.gaps | 5 | 3.33 | 2/3 gap names × 5 |
| corpus.wildcard | 5 | 5.0 | wildcard line ratio 0.0053 against band 0.05–0.3 |
| corpus.mutation | 25 | 20.0 | 12/15 mutants killed × 25 |

`agentic` scores 68.0 of 100 available weight → **68.0/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| attempts | 30 | 20.0 | 30 − 10×1 retries |
| rebaseline | 20 | 0.0 | 20 − 10×6 blind rebaselines |
| tool_discipline | 30 | 28.0 | 30 − 2×1 malformed − 5×0 loops − 10×0 deaths |
| churn | 20 | 20.0 | 585 pushed ÷ 1524 diff = 0.3839× against band 1.5–4.0 |

## Review

Mean grade **3.5/5** — one reviewer graded; codex returned nothing usable (its `codex exec` run timed out at the relay's 2-minute limit before producing grades) and is recorded without a grade, per the measure step's no-re-run rule.

| reviewer | grade /5 | findings |
| --- | --- | --- |
| fable:medium | 3.5 (correctness 3, test quality 3, code quality 4, scope discipline 4) | 8 — worst first: (1) cross-check maps `test_value_with_equals_sign` to `sets-multiple-keys-in-one-call.txtar`, which carries no equals-bearing value — behaviour untested after the unit deletion; (2) `test_empty_key_exits_1` mapped to `malformed-pair-is-rejected.txtar`, which only exercises a no-equals pair — empty-key rejection uncovered; (3) 8-way `test_syntax_sensitive_string_keeps_its_quotes` mapped to `set-quotes-ambiguous-string.txtar` covering only `a: b` — seven quoting behaviours dropped without a drop rationale; (4) `test_remove_key_and_add_empty` mapped to `remove-drops-a-key.txtar` with no empty-value pair and no YAML comment in the fixture — empty-value and comment-survival uncovered; (5) partly-numeric `23 things` mapped to `sets-a-literal-value.txtar` whose value is `in-progress` — partly-numeric-stays-string contract lost; (6) M03 DoD ticked `[x]` on a cross-check findings 1–5 show does not hold; (7) `append-onto-scalar-exits-1.txtar` and `malformed-jinja-exits-2.txtar` describe "file left unchanged" but assert no `expected/` section; (8) `CLAUDE.md:21` edited outside the scope allowlist and against the plan's "No CLAUDE.md changes required". |
| codex | none — `codex exec` timed out after 2m with no output | — |

## History row

| date | model | outcome | att | code | agentic | review | diff | tokens | cost | time | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-14 | `poolside/laguna-s-2.1:free` | pass | 2/1/1 | 78.5 | 68.0 | 3.5 | 1524 | 12.5M | $0.00 | 2h41m09s | [20260814-230156](runs/20260814-230156-poolside-laguna-s-2-1-free.md) |
