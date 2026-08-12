---
id: "03"
title: "Delete superseded unit tests after coverage cross-check"
sp: 2
status: in-progress
plan: "vault/plans/202608121417_frontmatter-update-e2e-migration/index.md"
---

# M03: Delete superseded unit tests after coverage cross-check

Goal: `booping-python/tests/commands/frontmatter_update_test.py` is deleted with a recorded proof that every CLI-observable behavior it covered maps to a named corpus case, and the repo carries no stale reference to it.

Scope: deletion of the unit file; a coverage cross-check table appended to this milestone file; a stale-reference sweep. No production code changes. Context the cross-check needs: `TestHookTokenising` is dropped deliberately — it tests `playbook_transition.dispatch_frontmatter_update`, whose coverage lives in `tests/commands/playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`); the live-git macro test is consciously abandoned per plan decision (real-execution case M02/2.3 replaces it).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Cross-check: list every test in `frontmatter_update_test.py`, map each to its corpus case filename or to a recorded drop rationale (hook-tokenising → playbook_transition coverage; live-git → M02/2.3); append the mapping table under `## Coverage cross-check` in this file | this milestone file | 1 | pending |
| 3.2 | Delete `booping-python/tests/commands/frontmatter_update_test.py`; sweep stale references (`grep -rn frontmatter_update_test` over the repo) and fix any hit; confirm unit suite still green | `booping-python/tests/commands/frontmatter_update_test.py` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] Every test function/parametrization in the unit file appears in the mapping table with a case filename or drop rationale.
- [ ] No mapping row says "TODO" or "covered somewhere".

### Task 3.2

- [ ] File deleted; `grep -rn frontmatter_update_test` over the repo returns nothing.
- [ ] `uv run pytest tests` and `uv run pytest e2e -k frontmatter` both green after deletion.

## Verify

```
cd booping-python && uv run pytest tests/commands -q && uv run pytest e2e -k frontmatter -q
grep -rn frontmatter_update_test /home/anton/Dev/@A/claude-booping --include='*.py' --include='*.md' --exclude-dir=vault
```

Command-unit suite green without the deleted file, corpus green, the grep prints nothing.

## Coverage cross-check

Every test function and parametrization of `booping-python/tests/commands/frontmatter_update_test.py`, mapped to its corpus case under `booping-python/e2e/cases/frontmatter-update/` or to a drop rationale.

| Unit test (class::test[param]) | Corpus case / drop rationale |
|---|---|
| `TestParsePairs::test_valid_pairs` | `sets-multiple-keys-in-one-call.txtar` |
| `TestParsePairs::test_value_with_equals_sign` | `value-may-contain-equals-signs.txtar` |
| `TestParsePairs::test_empty_key_exits_1` | `empty-key-in-a-pair-is-rejected.txtar` |
| `TestParsePairs::test_no_equals_exits_1` | `malformed-pair-is-rejected.txtar` |
| `TestInterpolate::test_datetime_macro` | `macro-rendered-date-like-value-stays-a-string.txtar` (timestamp form) |
| `TestInterpolate::test_date_macro` | `macro-rendered-date-like-value-stays-a-string.txtar` (date form) |
| `TestInterpolate::test_stubbed_macro_is_not_executed` | `stubbed-macro-value-lands-typed.txtar` — stubbed argv is `false`, so any execution would fail the case |
| `TestInterpolate::test_unknown_macro_path_exits_non_zero` | `unknown-macro-path-is-rejected.txtar` |
| `TestInterpolate::test_malformed_jinja_exits_non_zero` | `malformed-jinja-in-a-value-is-rejected.txtar` |
| `TestInterpolate::test_git_commit_macro_runs_against_the_repo_dir` | **Dropped** — live-git macro coverage consciously abandoned (plan decision); real macro execution across the subprocess boundary is proven by `a-real-macro-runs-and-its-output-lands.txtar` |
| `TestInterpolate::test_retired_head_token_is_a_literal` | `syntax-sensitive-string-keeps-its-quotes.txtar` (`a=@lead` lands as the literal text) |
| `TestInterpolate::test_retired_now_token_is_a_literal` | `syntax-sensitive-string-keeps-its-quotes.txtar` (same `@`-prefixed literal path) |
| `TestInterpolate::test_at_sign_prefix_not_interpolated` | `syntax-sensitive-string-keeps-its-quotes.txtar` (same `@`-prefixed literal path) |
| `TestInterpolate::test_literal_value` | `sets-a-key-to-a-literal-value.txtar` |
| `TestInterpolate::test_literal_value_with_spaces_untouched` | `partly-numeric-value-stays-a-plain-string.txtar` (`23 things`) |
| `TestHookTokenising::test_quoted_macro_expression_survives_shlex` | **Dropped** — exercises `playbook_transition.dispatch_frontmatter_update`, covered by `tests/commands/playbook_transition_test.py::test_file_target_hook_interpolates_instance` |
| `TestHookTokenising::test_file_target_with_quoted_macro_expression` | **Dropped** — same module; covered by `tests/commands/playbook_transition_test.py::test_file_target_hook_updates_sibling_file` |
| `TestScalarTyping::test_scalar_lands_typed[integer]` | `integer-value-lands-unquoted.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[float]` | `float-value-lands-unquoted.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[null]` | `null-value-lands-unquoted.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[boolean]` | `boolean-value-lands-unquoted.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[partly-numeric]` | `partly-numeric-value-stays-a-plain-string.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[yaml-1-1-boolean-word]` | `yaml-1-1-boolean-word-stays-a-string.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[@lead,*star,&anchor,!bang,%pct,`tick,a: b, padded ]` | `syntax-sensitive-string-keeps-its-quotes.txtar` — all eight values in one call |
| `TestScalarTyping::test_macro_rendered_date_stays_a_string` | `macro-rendered-date-like-value-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI::test_sets_planned_with_date_macro` | `macro-rendered-date-like-value-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI::test_sets_created_with_date_macro` | `macro-rendered-date-like-value-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI::test_sets_commit_with_the_git_macro` | **Dropped** — live-git macro, same rationale as above; `a-real-macro-runs-and-its-output-lands.txtar` covers real execution |
| `TestFrontmatterUpdateCLI::test_literal_value` | `sets-a-key-to-a-literal-value.txtar` |
| `TestFrontmatterUpdateCLI::test_missing_plan_exits_1` | `missing-plan-file-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI::test_malformed_pair_exits_1` | `malformed-pair-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI::test_preserves_other_keys_and_body` | `other-keys-comments-and-body-survive-the-set.txtar` |
| `TestFrontmatterUpdateCLI::test_multiple_keys_at_once` | `sets-multiple-keys-in-one-call.txtar` |
| `TestFrontmatterUpdateCLI::test_remove_key_and_add_empty` | `remove-drops-a-key.txtar` + `empty-value-lands-as-an-empty-string.txtar` |
| `TestFrontmatterUpdateCLI::test_remove_only_no_pairs` | `remove-drops-a-key.txtar` |
| `TestFrontmatterUpdateCLI::test_nothing_to_do_exits_1` | `nothing-to-do-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI::test_append_only_still_reports_nothing_to_do_when_empty` | `nothing-to-do-is-rejected.txtar` — the CLI surface is one and the same empty call |
| `TestFrontmatterUpdateCLI::test_append_creates_list_on_null_key` | `append-creates-a-list-on-a-null-key.txtar` |
| `TestFrontmatterUpdateCLI::test_append_creates_list_on_absent_key` | `append-creates-a-list-on-an-absent-key.txtar` |
| `TestFrontmatterUpdateCLI::test_append_extends_existing_list` | `append-extends-an-existing-list.txtar` |
| `TestFrontmatterUpdateCLI::test_append_is_idempotent` | `appending-the-same-value-twice-adds-it-once.txtar` |
| `TestFrontmatterUpdateCLI::test_append_onto_scalar_exits_1` | `append-onto-a-scalar-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI::test_append_alongside_pairs_and_removals` | `pairs-removals-and-appends-combine-in-one-call.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[changed-value]` | `diff-names-the-plan-on-both-sides.txtar` + `sets-a-key-to-a-literal-value.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[append]` | `append-extends-an-existing-list.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[removal]` | `remove-drops-a-key.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing]` | `re-setting-the-same-value-prints-no-diff.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing]` | `appending-the-same-value-twice-adds-it-once.txtar` |
| `TestFrontmatterUpdateCLI::test_summary_stays_on_stderr` | `summary-goes-to-stderr-not-stdout.txtar` |
| `TestFrontmatterUpdateCLI::test_logs_to_booping_log` | `logs-one-line-when-a-vault-is-attached.txtar` |
| `TestFrontmatterUpdateCLI::test_does_not_write_to_real_home` | **Dropped** — the guarantee is now structural: `e2e/conftest.py` maps `HOME`/`XDG_CONFIG_HOME` into per-case sandbox roots and every case asserts its whole `expected/` tree, so a write outside the sandbox has nowhere to land; `logs-one-line-when-a-vault-is-attached.txtar` pins the log's exact location |

New corpus cases with no unit counterpart (gap coverage added by this plan): `newline-and-tab-bearing-values-round-trip.txtar`, `malformed-append-pair-is-rejected.txtar`, `a-real-macro-runs-and-its-output-lands.txtar`.
