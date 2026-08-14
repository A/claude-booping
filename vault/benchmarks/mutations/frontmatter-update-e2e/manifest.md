# Mutation set — `frontmatter-update-e2e`

Fifteen hand-authored behaviour breaks in `booping-python/src/booping/commands/frontmatter_update.py`, each produced by `git diff` of a single hand-edit on a worktree of baseline `e0d1796`. `bench-score mutations` applies one at a time to a scored branch, runs that branch's frontmatter-update corpus, and records the patch killed when the corpus goes red.

The set is **frozen**. Patches are written against the `frontmatter_update.py` blob `db3dacc` and never regenerated, so every model's corpus faces an identical set. What pins the set is that blob, not the baseline commit: the baseline moved from `e0d1796` to `6fd0f38` when the milestone contracts were regroomed, and `db3dacc` is byte-identical across both. A baseline whose `frontmatter_update.py` blob differs is a different benchmark, with its own registry entry and its own mutation directory.

Every patch touches only `frontmatter_update.py` — no test file, no other source. Two behaviours named in the milestone's task list, append idempotency and append-creates-a-list-on-null, are **not** in the set: both are implemented in `booping/context/_yaml.py`'s `update_frontmatter`, outside the single-file mutation target, and could not be broken from the command module without rewriting it. The append surface is still represented, through `11_malformed-pair-exits-2` (which mutates the `parse_pairs` both pairs and `--append` share) and `12_remove-is-a-noop` (which fails the combined pairs/removals/appends case).

## Patches

| patch | behaviour broken | expected killer(s) from the etalon list |
| --- | --- | --- |
| `01_bool-coercion-dropped.patch` | A `true`/`false` value is single-quoted instead of written as a bare boolean. | `boolean-value-lands-unquoted.txtar` |
| `02_int-coercion-dropped.patch` | An integer value is single-quoted instead of written as a bare int. | `integer-value-lands-unquoted.txtar` |
| `03_float-coercion-dropped.patch` | A float value is single-quoted instead of written as a bare float. | `float-value-lands-unquoted.txtar` |
| `04_null-coercion-dropped.patch` | The null spellings stop resolving to a real null and land quoted. | `null-value-lands-unquoted.txtar` |
| `05_yaml-1-1-quoting-dropped.patch` | A string whose plain form reloads as another type under the YAML 1.1 resolver is written unquoted, so it no longer reloads as a string. | `yaml-1-1-boolean-word-stays-a-string.txtar`, `syntax-sensitive-string-keeps-its-quotes.txtar` |
| `06_empty-value-becomes-null.patch` | A pair with nothing after the `=` sets null instead of an explicit empty string. | `empty-value-lands-as-an-empty-string.txtar` |
| `07_first-equals-split-lost.patch` | A pair splits on its **last** `=`, so a value containing `=` is truncated into the key. | `value-may-contain-equals-signs.txtar` |
| `08_empty-key-accepted.patch` | A pair with an empty key is accepted and written instead of rejected. | `empty-key-in-a-pair-is-rejected.txtar` |
| `09_macro-left-unrendered.patch` | The Jinja test is inverted, so a value carrying a macro call passes through as literal text. | `a-real-macro-runs-and-its-output-lands.txtar`, `stubbed-macro-value-lands-typed.txtar`, `unknown-macro-path-is-rejected.txtar` |
| `10_macro-error-exits-1.patch` | A macro or template failure exits 1 instead of 2, collapsing the user-error and macro-error codes. | `unknown-macro-path-is-rejected.txtar`, `malformed-jinja-in-a-value-is-rejected.txtar` |
| `11_malformed-pair-exits-2.patch` | A malformed `key=value` pair exits 2 instead of 1 — the same swap in the other direction. | `malformed-pair-is-rejected.txtar`, `malformed-append-pair-is-rejected.txtar` |
| `12_remove-is-a-noop.patch` | `--remove` is dropped before the write, so the key survives while the summary still claims it went. | `remove-drops-a-key.txtar`, `pairs-removals-and-appends-combine-in-one-call.txtar` |
| `13_diff-suppressed-on-change.patch` | The unified diff is computed and thrown away, so a real change prints nothing on stdout. | `diff-names-the-plan-on-both-sides.txtar`, `re-setting-the-same-value-prints-no-diff.txtar` |
| `14_summary-to-stdout.patch` | The `updated …` summary goes to stdout, mixing the receipt into the pipeable diff stream. | `summary-goes-to-stderr-not-stdout.txtar` |
| `15_log-line-dropped.patch` | No `[frontmatter-update]` line is appended to an attached vault's log. | `logs-one-line-when-a-vault-is-attached.txtar` |

A patch that changes a widely-asserted channel fails far more than its designed killer — `14_summary-to-stdout` reddens 26 of the 34 etalon cases, `13_diff-suppressed-on-change` 14. The column above names the case that exists *for* that behaviour; the full per-patch failure list is the `killed_by` field of the `bench-score mutations` JSON.

## Validation

Run `2026-08-14` against the etalon corpus — the opus run at bench-repo `master` (`f1df61c`), whose `frontmatter_update.py` is byte-identical to baseline `e0d1796`:

```
bench-score mutations --benchmark frontmatter-update-e2e --branch master
```

**15/15 killed**, 0 survived, 0 not-applicable, worktree clean. Every patch also passes `git apply --check` on a fresh `e0d1796` worktree.

The same sweep against `bench/deepseek-deepseek-v4-pro-0813` scores **12/15**. The three survivors — `06_empty-value-becomes-null`, `07_first-equals-split-lost`, `08_empty-key-accepted` — are precisely the three etalon behaviours that branch's corpus never asserts, which is what the set is for.
