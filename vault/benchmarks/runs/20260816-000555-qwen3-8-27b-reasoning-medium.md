---
benchmark: frontmatter-update-e2e
model: 'Qwen3.8-27B_reasoning_medium'
branch: bench/qwen3-8-27b-reasoning-medium
run_id: 20260816-000555
date: '2026-08-16'
outcome: pass
code: 89.05
agentic: null
review: 3.63
status: publishing
---

# Benchmark run — Qwen3.8-27B_reasoning_medium

Branch `bench/qwen3-8-27b-reasoning-medium` scored against the `frontmatter-update-e2e` registry entry, baseline `a025189`. Every number below is computed by `bench-score`; the history row in [history.md](../history.md) is this file's summary.

## Summary

| field | value |
| --- | --- |
| date | 2026-08-16 |
| model | `Qwen3.8-27B_reasoning_medium` |
| provider | local |
| outcome | pass |
| att | 2/3/2 |
| code | 89.0 |
| agentic | - |
| review | 3.63 |
| diff | 1651 |
| tokens | - |
| cost | - |
| time | 1h53m |

`agentic`, `tokens` and `cost` are `-` for this run, not zero — see **Harness deviation** below. `time` is the sprint's wall clock measured by the runner (first transition 00:04 to plan `done` 01:57); the worker logs span 1h39m02s from first log start to last log end.

## Harness deviation

Not an `openrouter-developer` run, and not a Claude Code worker either. Every milestone went to the `pi-developer` agent, which hands the milestone to a headless **pi** session as `/orchestrate` and lets pi do its own planning, delegation and validation; the model behind it was `llama-local/Qwen3.8-27B_reasoning_medium` on the local llama-swap box. The registry entry's `worker` and `logs_dir` name `openrouter-developer` and `~/.tmp/openrouter-developer`; this run's logs were written by pi to `~/.tmp/pi-developer` and copied into the registry's `logs_dir` under its `{ts}-{model_slug}-{milestone}` naming so `bench-score` could select them.

What that costs the measurement, precisely:

- **`agentic` is dropped.** pi's ndjson is its own event schema (`tool_execution_start/end`, `message_*`, `turn_*`), not Claude Code's `assistant`/`user`/`result` stream, so `bench-score`'s detectors read no tool calls at all. Worse, the log is the *orchestrator's* session: pi's own implementation sub-agents return their work as text through `run_agent` results, so even a schema translation would not surface the coder's tool calls. The script therefore scored `rebaseline`, `tool_discipline` and `churn` as perfect on zero evidence (20 + 30 + 20 of 100) and only `attempts` — 30 − 10×4 retries → 0 — was real. Publishing 70 would state as measured what was never observed, so the composite is withheld. The `att` cell (2/3/2) and the retry count stand: they come from log counts and the `feedback.md` sidecars, not from tool events.
- **`tokens` and `cost` are dropped.** The same orchestrator-only logs carry usage for pi's own coordination turns and nothing for the sub-agents that did the work; pi records `cost: 0` throughout because the box bills nothing. `bench-score` found 0 generation ids and emitted $0.0000 — an absence, not a measurement.
- **Every other layer is the registry's standard run**: `code` (gates, corpus, mutation set), `diff`, `outcome` and both diff reviews are measured exactly as for any other row.

Attempt logs excluded from the process figures, all of them launches that never reached the model: one harness no-op on M01 (pi resumed a stale `state.yaml` marked `completed` from the previous attempt, ran one sanity check and stopped without reading the feedback, 222 KB), one M02 launch the user killed (1.7 MB), and two stillborn launches (30 KB, 33 KB). Seven genuine attempt logs remain, 2/3/2 across the milestones.

A run's worth of process signal is what this deviation costs. Making `agentic` measurable for pi-driven runs needs pi to emit per-sub-agent tool events, or a registry entry of its own with a translator — neither is this run's business.

## Gates

| check | verdict | evidence |
| --- | --- | --- |
| ci | pass | just ci exit 0 |
| determinism | pass | uv run pytest e2e --txtar-update exit 0; git diff --quiet after: clean |
| e2e | pass | just e2e exit 0 |
| milestones | pass | 3/3 milestones terminal: M01-core-cli-cases=done, M02-list-ops-and-macro-cases=done, M03-delete-superseded-units=done |
| scope | pass | 38 changed path(s) vs a025189; all within allowlist |
| unit_deleted | pass | booping-python/tests/commands/frontmatter_update_test.py absent; git grep frontmatter_update_test: 0 hits |

## Corpus quality

| metric | value | evidence |
| --- | --- | --- |
| cases | 29 | `booping-python/e2e/cases/frontmatter-update` |
| etalon recall | 29/34 (85.29%) | behaviour matches against the frozen etalon list — 3 by exact name, 26 mapped; see **Case mapping** |
| gap cases | 2/3 | cases with no unit-test counterpart |
| four-channel cases | 23/29 (79.31%) | exit + stdout + stderr + expected all asserted |
| wildcard line ratio | 0.0022 | 1 wildcarded of 447 asserted lines |

## Mutation kills

The frozen set at `vault/benchmarks/mutations/frontmatter-update-e2e` applied one patch at a time over the branch's corpus via `uv run pytest e2e/cases/frontmatter-update -q --tb=no`: **12/15 killed** (80.0%).

| patch | verdict | evidence |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | killed | a-bool-value-lands-unquoted.txtar |
| `02_int-coercion-dropped.patch` | killed | a-declared-macro-runs-and-lands-its-output.txtar, a-stubbed-macro-value-lands-typed.txtar, an-int-value-lands-unquoted.txtar, sets-multiple-keys-in-one-call.txtar |
| `03_float-coercion-dropped.patch` | killed | a-float-value-lands-unquoted.txtar |
| `04_null-coercion-dropped.patch` | killed | a-null-spelling-lands-as-null.txtar |
| `05_yaml-1-1-quoting-dropped.patch` | killed | a-yaml-1-1-yes-stays-a-string.txtar |
| `06_empty-value-becomes-null.patch` | **survived** | corpus exit 0 with no case named |
| `07_first-equals-split-lost.patch` | **survived** | corpus exit 0 with no case named |
| `08_empty-key-accepted.patch` | **survived** | corpus exit 0 with no case named |
| `09_macro-left-unrendered.patch` | killed | a-date-like-macro-value-stays-a-string.txtar, a-declared-macro-runs-and-lands-its-output.txtar, a-malformed-jinja-value-exits-2.txtar, a-stubbed-macro-value-lands-typed.txtar, an-unknown-macro-name-exits-2.txtar |
| `10_macro-error-exits-1.patch` | killed | a-malformed-jinja-value-exits-2.txtar, an-unknown-macro-name-exits-2.txtar |
| `11_malformed-pair-exits-2.patch` | killed | a-malformed-pair-is-rejected.txtar |
| `12_remove-is-a-noop.patch` | killed | a-remove-only-call-drops-the-key.txtar, an-append-combined-with-pairs-and-removals.txtar |
| `13_diff-suppressed-on-change.patch` | killed | a-bool-value-lands-unquoted.txtar, a-date-like-macro-value-stays-a-string.txtar, a-declared-macro-runs-and-lands-its-output.txtar, a-float-value-lands-unquoted.txtar, a-null-spelling-lands-as-null.txtar, a-remove-only-call-drops-the-key.txtar, a-second-identical-call-prints-no-diff.txtar, a-stubbed-macro-value-lands-typed.txtar, a-tab-bearing-value-round-trips.txtar, a-yaml-1-1-yes-stays-a-string.txtar, an-ambiguous-string-gets-single-quoted.txtar, an-append-combined-with-pairs-and-removals.txtar, an-append-creates-a-list-on-a-null-key.txtar, an-append-creates-a-list-on-an-absent-key.txtar, an-append-extends-an-existing-list.txtar, an-identical-second-append-prints-no-diff.txtar, an-int-value-lands-unquoted.txtar, logs-one-line-when-a-vault-is-attached.txtar, preserves-other-keys-and-body-when-setting-one-key.txtar, sets-a-key-with-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stdout-carries-the-unified-diff.txtar |
| `14_summary-to-stdout.patch` | killed | a-bool-value-lands-unquoted.txtar, a-date-like-macro-value-stays-a-string.txtar, a-declared-macro-runs-and-lands-its-output.txtar, a-float-value-lands-unquoted.txtar, a-null-spelling-lands-as-null.txtar, a-remove-only-call-drops-the-key.txtar, a-second-identical-call-prints-no-diff.txtar, a-stubbed-macro-value-lands-typed.txtar, a-tab-bearing-value-round-trips.txtar, a-yaml-1-1-yes-stays-a-string.txtar, an-ambiguous-string-gets-single-quoted.txtar, an-append-combined-with-pairs-and-removals.txtar, an-append-creates-a-list-on-a-null-key.txtar, an-append-creates-a-list-on-an-absent-key.txtar, an-append-extends-an-existing-list.txtar, an-identical-second-append-prints-no-diff.txtar, an-int-value-lands-unquoted.txtar, logs-one-line-when-a-vault-is-attached.txtar, preserves-other-keys-and-body-when-setting-one-key.txtar, sets-a-key-with-a-literal-value.txtar, sets-multiple-keys-in-one-call.txtar, stdout-carries-the-unified-diff.txtar, the-success-summary-goes-to-stderr.txtar |
| `15_log-line-dropped.patch` | killed | logs-one-line-when-a-vault-is-attached.txtar |

## Case mapping

The branch renamed nearly every case (`a-`/`an-` prefixes, reworded behaviours), so exact-name recall reads 3/34. A case-mapping judge read the unmatched bodies on both sides and mapped them by behaviour; the corpus JSON handed to `bench-score report` carries the mapped counts.

Exact-name recall 3/34 (8.82%) → mapped recall 29/34 (85.29%); gaps 0/3 exact → 2/3 mapped. All 26 unmatched branch cases mapped to an etalon name; 5 etalon behaviours have no branch case at all.

| Etalon case | Branch case | Behaviour |
| --- | --- | --- |
| a-real-macro-runs-and-its-output-lands.txtar | a-declared-macro-runs-and-lands-its-output.txtar | declares `echo 1` as a config macro (mapping form with `command:`) and asserts the key lands `1` unquoted, so the subprocess really ran |
| append-creates-a-list-on-a-null-key.txtar | an-append-creates-a-list-on-a-null-key.txtar | `--append sessions=abc-123` onto `sessions: null` turns it into a one-element block sequence, summary `sessions+=abc-123` |
| append-creates-a-list-on-an-absent-key.txtar | an-append-creates-a-list-on-an-absent-key.txtar | `--append` on a key the block never carried creates a one-element sequence at the end |
| append-extends-an-existing-list.txtar | an-append-extends-an-existing-list.txtar | `--append sessions=def-456` keeps existing members and adds the new one last |
| append-onto-a-scalar-is-rejected.txtar | an-append-onto-a-scalar-key-is-rejected.txtar | append onto a scalar key exits 1 with `cannot append to scalar key '…' in plan.md` and no write |
| appending-the-same-value-twice-adds-it-once.txtar | an-identical-second-append-prints-no-diff.txtar | two identical `--append` runs; second contributes no diff, still prints its summary, member unduplicated |
| boolean-value-lands-unquoted.txtar | a-bool-value-lands-unquoted.txtar | `blocked=true` lands unquoted (branch asserts `true` only, not the `false` companion) |
| diff-names-the-plan-on-both-sides.txtar | stdout-carries-the-unified-diff.txtar | asserts the stdout receipt is a unified diff with the plan path on `---`/`+++` and an `@@` hunk header |
| empty-key-in-a-pair-is-rejected.txtar | none | no branch case passes a pair with an empty key side; the only rejection case is the missing-`=` one |
| empty-value-lands-as-an-empty-string.txtar | none | no branch case sets `key=` with nothing after the `=` |
| float-value-lands-unquoted.txtar | a-float-value-lands-unquoted.txtar | `ratio=1.5` lands unquoted with its fractional part |
| integer-value-lands-unquoted.txtar | an-int-value-lands-unquoted.txtar | `sp=23` lands unquoted as a number |
| macro-rendered-date-like-value-stays-a-string.txtar | a-date-like-macro-value-stays-a-string.txtar | a stubbed macro resolving to `1970-01-02` lands single-quoted (branch omits the timestamp form) |
| malformed-append-pair-is-rejected.txtar | none | no branch case passes an `--append` argument lacking `=`; the malformed-pair case uses a bare positional argument |
| malformed-jinja-in-a-value-is-rejected.txtar | a-malformed-jinja-value-exits-2.txtar | `{{ macro( }}` exits 2 with `error: value '…': TemplateSyntaxError: …`, file untouched |
| malformed-pair-is-rejected.txtar | a-malformed-pair-is-rejected.txtar | positional argument without `=` exits 1 with `malformed key=value pair: '…'`, plan untouched |
| missing-plan-file-is-rejected.txtar | a-missing-plan-file-is-rejected.txtar | a non-existent plan path exits 1 with `plan not found: plan.md` before anything is parsed |
| newline-and-tab-bearing-values-round-trip.txtar | a-tab-bearing-value-round-trips.txtar | asserts the tab half only — `note: "a\tb"` double-quoted escape; the case explicitly declares a newline untypeable, so the folded single-quoted block is never asserted |
| null-value-lands-unquoted.txtar | a-null-spelling-lands-as-null.txtar | `retro=null` lands as a bare unquoted `null` (branch omits the `~` spelling) |
| other-keys-comments-and-body-survive-the-set.txtar | preserves-other-keys-and-body-when-setting-one-key.txtar | setting one key leaves sibling keys' order and the markdown body intact (no inline-comment fixture) |
| pairs-removals-and-appends-combine-in-one-call.txtar | an-append-combined-with-pairs-and-removals.txtar | one call sets, removes and appends; summary orders removals, pairs, appends |
| partly-numeric-value-stays-a-plain-string.txtar | none | no branch case sets a digit-leading value such as `23 things` to prove it stays bare and unquoted |
| re-setting-the-same-value-prints-no-diff.txtar | a-second-identical-call-prints-no-diff.txtar | two identical `status=ready` calls; stdout carries only the first diff, both summaries on stderr |
| remove-drops-a-key.txtar | a-remove-only-call-drops-the-key.txtar | `--remove business_goal` deletes the key's line, neighbours untouched, summary `-business_goal` |
| sets-a-key-to-a-literal-value.txtar | sets-a-key-with-a-literal-value.txtar | `status=ready` rewrites the key in place with diff on stdout and summary on stderr |
| stubbed-macro-value-lands-typed.txtar | a-stubbed-macro-value-lands-typed.txtar | a `macro_stubs:` pinned value is rendered without executing and coerced — integer stub lands unquoted |
| summary-goes-to-stderr-not-stdout.txtar | the-success-summary-goes-to-stderr.txtar | asserts stream separation — the `updated …` line is stderr's only output while stdout stays empty on the no-op |
| syntax-sensitive-string-keeps-its-quotes.txtar | an-ambiguous-string-gets-single-quoted.txtar | a value that would reload as another type gets single-quoted, but only for a date literal — none of the etalon's alias/anchor/tag/mapping/padded sigils are exercised |
| unknown-macro-path-is-rejected.txtar | an-unknown-macro-name-exits-2.txtar | an undeclared macro path exits 2 echoing the value and `no macro declared at config path: …`, no write |
| value-may-contain-equals-signs.txtar | none | no branch case proves the pair splits on the first `=` only with further `=` inside the value |
| yaml-1-1-boolean-word-stays-a-string.txtar | a-yaml-1-1-yes-stays-a-string.txtar | `summary=yes` is written `'yes'` so it reloads as a string under the YAML 1.1 resolver |

| Gap case | Verdict | Covered by |
| --- | --- | --- |
| a-real-macro-runs-and-its-output-lands.txtar | covered | a-declared-macro-runs-and-lands-its-output.txtar |
| malformed-append-pair-is-rejected.txtar | not covered | — |
| newline-and-tab-bearing-values-round-trip.txtar | covered | a-tab-bearing-value-round-trips.txtar |

## Process profile

| milestone | attempts | feedback files | wall | tool calls | malformed | loops | deaths | blind rebaselines | pushed lines |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 2 | 1 | 0m00s | 0 | 0 | 0 | 0 | 0 | 0 |
| M02-list-ops-and-macro-cases | 3 | 1 | 0m00s | 0 | 0 | 0 | 0 | 0 | 0 |
| M03-delete-superseded-units | 2 | 1 | 0m00s | 0 | 0 | 0 | 0 | 0 | 0 |

Tool mix: . Worker wall clock 0m00s across 7 attempt log(s); first log start to last log end spans 1h39m02s.

## Cost

| milestone | generations | cost USD | native prompt | native completion | of which cached |
| --- | --- | --- | --- | --- | --- |
| M01-core-cli-cases | 0 | 0.0000 | 0 | 0 | 0 |
| M02-list-ops-and-macro-cases | 0 | 0.0000 | 0 | 0 | 0 |
| M03-delete-superseded-units | 0 | 0.0000 | 0 | 0 | 0 |

Source `openrouter` via `https://openrouter.ai/api/v1/generation`: 0/0 unique generation ids fetched from 0 id mentions, failures none. OpenRouter total $0.0000; the ndjson fallback figure — Claude Code's own pricing, not OpenRouter billing — is $0.0000.

## Composites

`code` scores 89.05 of 100 available weight → **89.05/100**.

| component | weight | earned | arithmetic |
| --- | --- | --- | --- |
| gates.ci | 10 | 10.0 | pass → 10 |
| gates.determinism | 10 | 10.0 | pass → 10 |
| gates.scope | 10 | 10.0 | pass → 10 |
| gates.e2e | 5 | 5.0 | pass → 5 |
| gates.unit_deleted | 5 | 5.0 | pass → 5 |
| corpus.recall | 15 | 12.79 | 29/34 etalon behaviours (mapped) × 15 |
| corpus.four_channel | 10 | 7.93 | 23/29 cases × 10 |
| corpus.gaps | 5 | 3.33 | 2/3 gap names × 5 |
| corpus.wildcard | 5 | 5.0 | wildcard line ratio 0.0022 against band 0.05–0.3 |
| corpus.mutation | 25 | 20.0 | 12/15 mutants killed × 25 |

`agentic` is **withheld** — three of its four components had no evidence behind them. The table below is what `bench-score` emitted (70.0/100) and why each row does or does not stand; see **Harness deviation**.

| component | weight | earned | arithmetic | stands? |
| --- | --- | --- | --- | --- |
| attempts | 30 | 0.0 | 30 − 10×4 retries | yes — log counts and `feedback.md` sidecars |
| rebaseline | 20 | 20.0 | 20 − 10×0 blind rebaselines | no — zero tool calls parsed from pi's schema |
| tool_discipline | 30 | 30.0 | 30 − 2×0 malformed − 5×0 loops − 10×0 deaths | no — zero tool calls parsed from pi's schema |
| churn | 20 | 20.0 | 0 pushed ÷ 1651 diff = 0.0× against band 1.5–4.0 | no — pushed lines unobservable, so the ratio is vacuous |

## Review

Two independent reviewers graded the branch diff against the same rubric, both handed the case-mapping table and the entry's `scope_allowlist`. Mean grade **3.63/5**.

| reviewer | grade /5 | findings |
| --- | --- | --- |
| `fable:medium` | 4.0 | correctness 3, test quality 4, code quality 4, scope discipline 5. Seven findings, all downstream of the five unported behaviours and the cross-check's rationales for them: `test_empty_key_exits_1` dropped as "internal-only" though `=value` hits its own CLI branch with its own message (`frontmatter_update.py:132-134`), uncovered anywhere now; the empty-value half of `test_remove_key_and_add_empty` mapped to a case that never sets `key=`, so `coerce_scalar`'s empty-value early return lost all coverage; `test_value_with_equals_sign` dropped as internal-only though `goal=a = b` passes straight through the CLI, leaving the first-`=` `partition` contract unasserted; M01's DoD 1.2 box flipped `[x]` although the partly-numeric family has no case, which the cross-check itself records; a cross-check note claiming inline-comment preservation the mapped case's fixture never exercises; no `--append` argument lacking `=` anywhere, so the append-side exit-1 path is unproven; and two macro rows claiming live execution for a case that stubs the macro. Scope discipline full — four commits, nothing outside the allowlist. |
| `codex` | 3.25 | correctness 3, test quality 3, code quality 4, scope discipline 3. Five findings, converging on the same hole from the deletion side: the unit suite is gone while five CLI-observable behaviours remain unported, so `06_empty-value-becomes-null`, `07_first-equals-split-lost` and `08_empty-key-accepted` regressions would pass; the cross-check's "internal-only" and equivalence rationales for the empty-key, empty-value and first-`=` rows are inaccurate rather than merely terse; the partly-numeric family is dropped against a plan that asked for every scalar-typing family; and the sole malformed-pair case covers the positional side only. Scope marked down for an incomplete migration whose superseded unit file was already deleted, not for out-of-scope edits. |

Both reviewers independently flagged the same three mutation survivors the corpus left alive (`06`, `07`, `08`), reached from the cross-check rather than from the mutation run — the corpus and process layers agree on where this branch is thin.

## History row

| date | model | provider | outcome | att | code | agentic | review | diff | tokens | cost | time | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-16 | `Qwen3.8-27B_reasoning_medium` | local | pass | 2/3/2 | 89.0 | - | 3.63 | 1651 | - | - | 1h53m | [20260816-000555](runs/20260816-000555-qwen3-8-27b-reasoning-medium.md) |
