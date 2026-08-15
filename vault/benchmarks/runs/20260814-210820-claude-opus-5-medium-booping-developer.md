---
benchmark: frontmatter-update-e2e
model: claude-opus-5
branch: bench/claude-opus-5-medium-booping-developer
run_id: 20260814-210820
date: '2026-08-14'
outcome: pass
code: 91.24
agentic: 90.0
review: 4.63
status: done
---

# Benchmark run — claude-opus-5

Branch `bench/claude-opus-5-medium-booping-developer` scored against the `frontmatter-update-e2e` registry entry, baseline `a025189`. Every number below is computed by `bench-score`; the history row in [history.md](../history.md) is this file's summary.

## Harness deviation

This run did not use the registry's `openrouter-developer` worker. Every milestone went to the in-process `booping:booping-developer` sub-agent — Claude Code's own harness, model `claude-opus-5` at reasoning effort `medium`, on subscription auth — because the run was requested as a read on the shipped developer agent rather than on a model behind OpenRouter. Three consequences, all of them affecting comparability with the other rows:

- **Cost is not measured.** Subscription auth emits no per-generation billing record, and the OpenRouter generation endpoint has nothing to answer for these turns. The `cost` cell reads `n/a`; it is not `$0.00` in any real sense. No figure was estimated.
- **Tokens come from the transcripts, not from OpenRouter.** The sub-agent transcripts were converted to the stream-json shape `bench-score process` reads, so the process profile, the token counts and the wall clock are all measured off the real run. `prompt` here includes cache reads (4.6M of the 5.1M total), which OpenRouter's `native_tokens_prompt` also does — but the two are counted by different meters and should not be compared to the decimal.
- **The harness differs, not just the model.** Claude Code's own agent loop, tool set and system prompt are in play here; the OpenRouter rows measure a model driven through `openrouter-developer`. A gap against those rows is a gap between harness-and-model pairs.

Everything else — the plan, the baseline, the branch scheme, the workspace clone, the gates, the corpus scoring, the mutation set and both diff reviewers — is the registry's standard run.

## Summary

| field | value |
| --- | --- |
| date | 2026-08-14 |
| model | `claude-opus-5` |
| outcome | pass |
| att | 1/1/1 |
| code | 91.2 |
| agentic | 90.0 |
| review | 4.63 |
| diff | 1832 |
| tokens | 5.1M |
| cost | n/a |
| wall | 13m19s |

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
| etalon recall | 30/34 (88.24%) | behaviour matches against the frozen etalon list — 8 by exact name, 22 mapped (see **Case mapping**) |
| gap cases | 2/3 | cases with no unit-test counterpart, judged on behaviour |
| four-channel cases | 29/30 (96.67%) | exit + stdout + stderr + expected all asserted |
| wildcard line ratio | 0.0017 | 1 wildcarded of 574 asserted lines |

## Case mapping

The branch names its cases after the assertion rather than the behaviour, so exact-name recall was 8/34 — the case-mapping judge settled the remaining 26 by reading the branch case bodies. Mapped recall is 30/34 (88.24%), gap coverage 2/3; the counts in Corpus quality and in the composites are the mapped counts.

| Etalon case | Branch case | Behaviour |
| --- | --- | --- |
| a-real-macro-runs-and-its-output-lands.txtar | real-macro-command-output-is-written.txtar | genuine argv-command macro runs through the subprocess boundary and its output lands coerced in the frontmatter |
| append-onto-a-scalar-is-rejected.txtar | append-onto-a-scalar-exits-1.txtar | `--append` onto a scalar key errors on stderr, exit 1, file untouched |
| appending-the-same-value-twice-adds-it-once.txtar | repeated-append-is-idempotent.txtar | second identical `--append` changes nothing, list keeps one entry |
| boolean-value-lands-unquoted.txtar | coerces-a-boolean-value.txtar | boolean-looking value lands as unquoted YAML boolean |
| diff-names-the-plan-on-both-sides.txtar | prints-a-unified-diff-on-stdout.txtar | unified diff on stdout with `--- plan.md`/`+++ plan.md` headers naming the same file on both sides |
| empty-key-in-a-pair-is-rejected.txtar | none | no branch case exercises an empty-key pair (e.g. `=value`); only the no-`=` malformed-pair branch exists |
| empty-value-lands-as-an-empty-string.txtar | none | no branch case sets a key to an empty value |
| float-value-lands-unquoted.txtar | coerces-a-float-value.txtar | float-looking value lands as unquoted YAML float |
| integer-value-lands-unquoted.txtar | coerces-an-integer-value.txtar | integer-looking value lands as unquoted YAML integer |
| macro-rendered-date-like-value-stays-a-string.txtar | macro-rendered-date-stays-a-string.txtar | macro-rendered date form is single-quoted so it reloads as a string, not a YAML date |
| malformed-append-pair-is-rejected.txtar | none | no branch case covers a `--append` value with no `=`; malformed-pair-exits-1 covers the positional-pair branch only |
| malformed-jinja-in-a-value-is-rejected.txtar | malformed-jinja-value-exits-2.txtar | unparsable Jinja value errors with the offending value on stderr, exit 2, file untouched |
| malformed-pair-is-rejected.txtar | malformed-pair-exits-1.txtar | positional argument with no `=` errors on stderr, exit 1, file untouched |
| missing-plan-file-is-rejected.txtar | missing-plan-file-exits-1.txtar | non-existent plan path errors on stderr, exit 1 |
| newline-and-tab-bearing-values-round-trip.txtar | keeps-tab-and-newline-escapes-in-a-value.txtar | tab and backslash-n-bearing value round-trips through the file; the branch notes a real newline cannot cross argv, so it exercises the escape form |
| nothing-to-do-is-rejected.txtar | nothing-to-do-exits-1.txtar | no pairs, `--append` or `--remove` errors on stderr, exit 1, file untouched |
| null-value-lands-unquoted.txtar | coerces-a-null-value.txtar | null-spelled value lands as unquoted YAML null |
| other-keys-comments-and-body-survive-the-set.txtar | preserves-other-keys-and-body.txtar | setting one key leaves every other frontmatter key and the body untouched; the fixture carries no comments, so that sub-claim is untested |
| pairs-removals-and-appends-combine-in-one-call.txtar | combines-pairs-removals-and-appends.txtar | one call sets a pair, drops a key and appends to a list, all reported in the stderr summary |
| partly-numeric-value-stays-a-plain-string.txtar | keeps-a-partly-numeric-value-a-plain-string.txtar | a value only starting with digits stays a plain unquoted string |
| re-setting-the-same-value-prints-no-diff.txtar | second-identical-call-prints-no-diff.txtar | repeated identical call is a no-op; only the first run prints a diff |
| sets-a-key-to-a-literal-value.txtar | sets-a-key-with-a-literal-value.txtar | sets a frontmatter key to a literal value, prints diff, reports the change |
| syntax-sensitive-string-keeps-its-quotes.txtar | quotes-syntax-sensitive-string-values.txtar | values opening with a YAML indicator, carrying a colon, or padded with spaces are quoted to reload unchanged |
| unknown-macro-path-is-rejected.txtar | unknown-macro-path-exits-2.txtar | macro call naming an undeclared config path errors on stderr, exit 2, file untouched |
| value-may-contain-equals-signs.txtar | none | no branch case sets a value string that itself contains an `=` character |
| yaml-1-1-boolean-word-stays-a-string.txtar | quotes-a-yaml-1-1-boolean-word.txtar | YAML-1.1 boolean word (e.g. `yes`) is quoted so it reloads as the string it was written as |

Gap verdicts:

- `a-real-macro-runs-and-its-output-lands.txtar` — covered by `real-macro-command-output-is-written.txtar`: an argv-command macro executes and its output is written into the frontmatter.
- `malformed-append-pair-is-rejected.txtar` — not covered: the only malformed-pair case exercises a positional pair with no `=`, not a `--append` argument lacking one.
- `newline-and-tab-bearing-values-round-trip.txtar` — covered by `keeps-tab-and-newline-escapes-in-a-value.txtar`: tab and `\n`-escape-bearing values round-trip, the branch noting real newlines cannot cross the argv boundary.

## Mutation kills

The frozen set at `vault/benchmarks/mutations/frontmatter-update-e2e` applied one patch at a time over the branch's corpus via `uv run pytest e2e/cases/frontmatter-update -q --tb=no`: **12/15 killed** (80.0%).

| patch | verdict | evidence |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | killed | coerces-a-boolean-value.txtar |
| `02_int-coercion-dropped.patch` | killed | coerces-an-integer-value.txtar, real-macro-command-output-is-written.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-value-lands-typed.txtar, summary-goes-to-stderr-not-stdout.txtar |
| `03_float-coercion-dropped.patch` | killed | coerces-a-float-value.txtar |
| `04_null-coercion-dropped.patch` | killed | coerces-a-null-value.txtar |
| `05_yaml-1-1-quoting-dropped.patch` | killed | quotes-a-yaml-1-1-boolean-word.txtar |
| `06_empty-value-becomes-null.patch` | **survived** | corpus exit 0 with no case named |
| `07_first-equals-split-lost.patch` | **survived** | corpus exit 0 with no case named |
| `08_empty-key-accepted.patch` | **survived** | corpus exit 0 with no case named |
| `09_macro-left-unrendered.patch` | killed | macro-rendered-date-stays-a-string.txtar, malformed-jinja-value-exits-2.txtar, real-macro-command-output-is-written.txtar, stubbed-macro-value-lands-typed.txtar, unknown-macro-path-exits-2.txtar |
| `10_macro-error-exits-1.patch` | killed | malformed-jinja-value-exits-2.txtar, unknown-macro-path-exits-2.txtar |
| `11_malformed-pair-exits-2.patch` | killed | malformed-pair-exits-1.txtar |
| `12_remove-is-a-noop.patch` | killed | combines-pairs-removals-and-appends.txtar, remove-drops-a-key.txtar |
| `13_diff-suppressed-on-change.patch` | killed | append-creates-a-list-on-a-null-key.txtar, append-creates-a-list-on-an-absent-key.txtar, append-extends-an-existing-list.txtar, coerces-a-boolean-value.txtar, coerces-a-float-value.txtar, coerces-a-null-value.txtar, coerces-an-integer-value.txtar, combines-pairs-removals-and-appends.txtar, keeps-a-partly-numeric-value-a-plain-string.txtar, keeps-tab-and-newline-escapes-in-a-value.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-rendered-date-stays-a-string.txtar, preserves-other-keys-and-body.txtar, prints-a-unified-diff-on-stdout.txtar, quotes-a-yaml-1-1-boolean-word.txtar, quotes-syntax-sensitive-string-values.txtar, real-macro-command-output-is-written.txtar, remove-drops-a-key.txtar, repeated-append-is-idempotent.txtar, second-identical-call-prints-no-diff.txtar, sets-a-key-with-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-value-lands-typed.txtar, summary-goes-to-stderr-not-stdout.txtar |
| `14_summary-to-stdout.patch` | killed | append-creates-a-list-on-a-null-key.txtar, append-creates-a-list-on-an-absent-key.txtar, append-extends-an-existing-list.txtar, coerces-a-boolean-value.txtar, coerces-a-float-value.txtar, coerces-a-null-value.txtar, coerces-an-integer-value.txtar, combines-pairs-removals-and-appends.txtar, keeps-a-partly-numeric-value-a-plain-string.txtar, keeps-tab-and-newline-escapes-in-a-value.txtar, logs-one-line-when-a-vault-is-attached.txtar, macro-rendered-date-stays-a-string.txtar, preserves-other-keys-and-body.txtar, prints-a-unified-diff-on-stdout.txtar, quotes-a-yaml-1-1-boolean-word.txtar, quotes-syntax-sensitive-string-values.txtar, real-macro-command-output-is-written.txtar, remove-drops-a-key.txtar, repeated-append-is-idempotent.txtar, second-identical-call-prints-no-diff.txtar, sets-a-key-with-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stubbed-macro-value-lands-typed.txtar, summary-goes-to-stderr-not-stdout.txtar |
| `15_log-line-dropped.patch` | killed | logs-one-line-when-a-vault-is-attached.txtar |

## Process profile

| milestone | attempts | feedback files | wall | tool calls | malformed | loops | deaths | blind rebaselines | pushed lines |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 1 | 0 | 4m39s | 25 | 0 | 0 | 0 | 1 | 2 |
| M02-list-ops-and-macro-cases | 1 | 0 | 4m41s | 37 | 0 | 0 | 0 | 0 | 459 |
| M03-delete-superseded-units | 1 | 0 | 3m58s | 18 | 0 | 0 | 0 | 0 | 62 |

Tool mix: Bash 42, Edit 4, Read 21, Write 13. Worker wall clock 13m19s across 3 attempt log(s); first log start to last log end spans 14m58s.

## Cost

| milestone | generations | cost USD | native prompt | native completion | of which cached |
| --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 0 | 0.0000 | 1.6M | 16.4k | 1.5M |
| M02-list-ops-and-macro-cases | 0 | 0.0000 | 2.3M | 20.3k | 2.1M |
| M03-delete-superseded-units | 0 | 0.0000 | 1.2M | 13.9k | 1.1M |

Cost is **not measured** for this run — see **Harness deviation** above. The run went through a Claude Code sub-agent on subscription auth, which emits neither an OpenRouter generation id nor a per-turn billing figure, so there was nothing for `bench-score cost` to query and nothing in the transcripts to fall back on. The `cost USD` column above is a structural zero, not a measurement, and no figure was estimated in its place. The token columns are real: they are summed from the sub-agent transcripts, `native prompt` including cache reads.

## Composites

`code` scores 91.24 of 100 available weight → **91.24/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| gates.ci | 10 | 10.0 | pass → 10 |
| gates.determinism | 10 | 10.0 | pass → 10 |
| gates.scope | 10 | 10.0 | pass → 10 |
| gates.e2e | 5 | 5.0 | pass → 5 |
| gates.unit_deleted | 5 | 5.0 | pass → 5 |
| corpus.recall | 15 | 13.24 | 30/34 etalon names × 15 |
| corpus.four_channel | 10 | 9.67 | 29/30 cases × 10 |
| corpus.gaps | 5 | 3.33 | 2/3 gap names × 5 |
| corpus.wildcard | 5 | 5.0 | wildcard line ratio 0.0017 against band 0.05–0.3 |
| corpus.mutation | 25 | 20.0 | 12/15 mutants killed × 25 |

`agentic` scores 90.0 of 100 available weight → **90.0/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| attempts | 30 | 30.0 | 30 − 10×0 retries |
| rebaseline | 20 | 10.0 | 20 − 10×1 blind rebaselines |
| tool_discipline | 30 | 30.0 | 30 − 2×0 malformed − 5×0 loops − 10×0 deaths |
| churn | 20 | 20.0 | 523 pushed ÷ 1832 diff = 0.2855× against band 1.5–4.0 |

## Review

Both reviewers worked from the same rubric, the branch diff against `a025189`, the case-mapping table and the scope allowlist. Per-reviewer grade is the mean of its four criterion grades; the history `review` cell is the mean of the two, **4.63/5**.

| reviewer       | grade /5 | findings                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| -------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fable:medium` | 4.25     | 4 — criteria 3/4/5/5: the unit file was deleted while three CLI-observable behaviours kept no corpus successor (empty key in a pair, a value containing `=`, an empty value), against the plan's own precondition for deletion; the malformed-pair branch is exercised only through a positional argument, never through `--append`; the newline gap case round-trips a literal backslash-n rather than a real newline, which a Jinja string literal would carry; the `# keep` trailing-comment survival assertion is dropped with no successor |
| `codex`        | 5.00     | 0 — criteria 5/5/5/5: plan requirements satisfied in scope, cases assert observable outcomes across all four channels, naming and format consistent with the scaffold corpus, no out-of-scope file touched                                                                                                                                                                                                                                                                                                                                      |

The two disagree on the same evidence: both saw the four unported etalon behaviours, `fable` graded them as a correctness defect against the plan's "delete wholesale once the corpus covers every CLI-observable behavior" decision, `codex` counted them as acknowledged in-scope gaps and returned no finding. The mutation set agrees with `fable`: patches `06_empty-value-becomes-null`, `07_first-equals-split-lost` and `08_empty-key-accepted` are exactly the three survivors.

## History row

| date | model | outcome | att | code | agentic | review | diff | tokens | cost | wall | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-14 | `claude-opus-5` | pass | 1/1/1 | 91.2 | 90.0 | 4.63 | 1832 | 5.1M | n/a | 13m19s | [20260814-210820](runs/20260814-210820-claude-opus-5-medium-booping-developer.md) |
