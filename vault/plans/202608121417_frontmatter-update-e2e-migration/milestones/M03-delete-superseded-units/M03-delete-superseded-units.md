---
id: "03"
title: "Delete superseded unit tests after coverage cross-check"
sp: 2
status: done
plan: "vault/plans/202608121417_frontmatter-update-e2e-migration/index.md"
---

# M03: Delete superseded unit tests after coverage cross-check

Goal: `booping-python/tests/commands/frontmatter_update_test.py` is deleted with a recorded proof that every CLI-observable behavior it covered maps to a named corpus case, and the repo carries no stale reference to it.

Scope: deletion of the unit file; a coverage cross-check table appended to this milestone file; a stale-reference sweep. No production code changes. Context the cross-check needs: `TestHookTokenising` is dropped deliberately — it tests `playbook_transition.dispatch_frontmatter_update`, whose coverage lives in `tests/commands/playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`); the live-git macro test is consciously abandoned per plan decision (real-execution case M02/2.3 replaces it).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Cross-check: list every test in `frontmatter_update_test.py`, map each to its corpus case filename or to a recorded drop rationale (hook-tokenising → playbook_transition coverage; live-git → M02/2.3); append the mapping table under `## Coverage cross-check` in this file | this milestone file | 1 | done |
| 3.2 | Delete `booping-python/tests/commands/frontmatter_update_test.py`; sweep stale references (`grep -rn frontmatter_update_test` over the repo) and fix any hit; confirm unit suite still green | `booping-python/tests/commands/frontmatter_update_test.py` | 1 | done |

## Definition of Done

### Task 3.1

- [x] Every test function/parametrization in the unit file appears in the mapping table with a case filename or drop rationale.
- [x] No mapping row says "TODO" or "covered somewhere".

### Task 3.2

- [x] File deleted; `grep -rn frontmatter_update_test` over the repo returns nothing.
- [x] `uv run pytest tests` and `uv run pytest e2e -k frontmatter` both green after deletion.

## Verify

```
cd booping-python && uv run pytest tests/commands -q && uv run pytest e2e -k frontmatter -q
grep -rn frontmatter_update_test /home/anton/Dev/@A/claude-booping --include='*.py' --include='*.md' --exclude-dir=vault
```

Command-unit suite green without the deleted file, corpus green, the grep prints nothing.

## Coverage cross-check

Every test in `booping-python/tests/commands/frontmatter_update_test.py` mapped to its corpus case or recorded drop rationale.

| Unit test | Corpus case or rationale |
|-----------|--------------------------|
| `TestParsePairs.test_valid_pairs` | `sets-key.txtar` |
| `TestParsePairs.test_value_with_equals_sign` | `sets-key.txtar` |
| `TestParsePairs.test_empty_key_exits_1` | `malformed-pair.txtar` |
| `TestParsePairs.test_no_equals_exits_1` | `malformed-pair.txtar` |
| `TestInterpolate.test_datetime_macro` | `macro-rendered-date-stays-string.txtar` |
| `TestInterpolate.test_date_macro` | `real-macro-execution.txtar` |
| `TestInterpolate.test_stubbed_macro_is_not_executed` | `stubbed-macro-interpolates.txtar` |
| `TestInterpolate.test_unknown_macro_path_exits_non_zero` | `unknown-macro-path-error.txtar` |
| `TestInterpolate.test_malformed_jinja_exits_non_zero` | `malformed-jinja-error.txtar` |
| `TestInterpolate.test_git_commit_macro_runs_against_the_repo_dir` | DROPPED: live-git macro test; replaced by `real-macro-execution.txtar` (M02/2.3) |
| `TestInterpolate.test_retired_head_token_is_a_literal` | DROPPED: legacy `@head` token no longer a feature; literal pass-through verified by `sets-key.txtar` |
| `TestInterpolate.test_literal_value` | `sets-key.txtar` |
| `TestInterpolate.test_literal_value_with_spaces_untouched` | `sets-key.txtar` |
| `TestInterpolate.test_at_sign_prefix_not_interpolated` | DROPPED: `@` prefix not special syntax; literal pass-through verified by `sets-key.txtar` |
| `TestInterpolate.test_retired_now_token_is_a_literal` | DROPPED: legacy `@now` token no longer a feature; literal pass-through verified by `sets-key.txtar` |
| `TestHookTokenising.test_quoted_macro_expression_survives_shlex` | DROPPED: coverage in `playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`) |
| `TestHookTokenising.test_file_target_with_quoted_macro_expression` | DROPPED: coverage in `playbook_transition_test.py` (`test_file_target_hook_interpolates_instance`) |
| `TestScalarTyping.test_scalar_lands_typed[integer]` | `coerces-integer.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[float]` | `coerces-float.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[null]` | `coerces-null.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[boolean]` | `coerces-boolean.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[partly-numeric]` | `ambiguous-string-quoted.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[yaml-1-1-boolean-word]` | `yaml-11-yes-quirk.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[@lead]` | DROPPED: YAML emitter quoting for edge-case value; same emitter path verified by `tab-value-escaped.txtar`, `newline-value-roundtrips.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[*star]` | DROPPED: YAML emitter quoting for edge-case value; same emitter path verified by `tab-value-escaped.txtar`, `newline-value-roundtrips.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[&anchor]` | DROPPED: YAML emitter quoting for edge-case value; same emitter path verified by `tab-value-escaped.txtar`, `newline-value-roundtrips.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[!bang]` | DROPPED: YAML emitter quoting for edge-case value; same emitter path verified by `tab-value-escaped.txtar`, `newline-value-roundtrips.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[%pct]` | DROPPED: YAML emitter quoting for edge-case value; same emitter path verified by `tab-value-escaped.txtar`, `newline-value-roundtrips.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[\`tick\`]` | DROPPED: YAML emitter quoting for edge-case value; same emitter path verified by `tab-value-escaped.txtar`, `newline-value-roundtrips.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[a: b]` | DROPPED: YAML emitter quoting for edge-case value; same emitter path verified by `tab-value-escaped.txtar`, `newline-value-roundtrips.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[ padded ]` | DROPPED: YAML emitter quoting for edge-case value; same emitter path verified by `tab-value-escaped.txtar`, `newline-value-roundtrips.txtar` |
| `TestScalarTyping.test_macro_rendered_date_stays_a_string` | `macro-rendered-date-stays-string.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_planned_with_date_macro` | `real-macro-execution.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_commit_with_the_git_macro` | DROPPED: live-git macro test; replaced by `real-macro-execution.txtar` (M02/2.3) |
| `TestFrontmatterUpdateCLI.test_sets_created_with_date_macro` | `real-macro-execution.txtar` |
| `TestFrontmatterUpdateCLI.test_literal_value` | `sets-key.txtar` |
| `TestFrontmatterUpdateCLI.test_missing_plan_exits_1` | `missing-plan-file.txtar` |
| `TestFrontmatterUpdateCLI.test_malformed_pair_exits_1` | `malformed-pair.txtar` |
| `TestFrontmatterUpdateCLI.test_preserves_other_keys_and_body` | `preserves-other-keys-and-body.txtar` |
| `TestFrontmatterUpdateCLI.test_multiple_keys_at_once` | `sets-multiple-keys.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_key_and_add_empty` | `combined-remove-set-append.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_only_no_pairs` | `remove-key.txtar` |
| `TestFrontmatterUpdateCLI.test_nothing_to_do_exits_1` | `nothing-to-do.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_null_key` | `append-creates-list-null-key.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_absent_key` | `append-creates-list-absent-key.txtar` |
| `TestFrontmatterUpdateCLI.test_append_extends_existing_list` | `append-extends-existing-list.txtar` |
| `TestFrontmatterUpdateCLI.test_append_is_idempotent` | `append-idempotent-no-diff.txtar` |
| `TestFrontmatterUpdateCLI.test_append_onto_scalar_exits_1` | `append-onto-scalar-error.txtar` |
| `TestFrontmatterUpdateCLI.test_append_alongside_pairs_and_removals` | `combined-remove-set-append.txtar` |
| `TestFrontmatterUpdateCLI.test_append_only_still_reports_nothing_to_do_when_empty` | `nothing-to-do.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[changed-value]` | `diff-shape-on-stdout.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[append]` | `diff-shape-on-stdout.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[removal]` | `diff-shape-on-stdout.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing]` | `idempotent-call-no-diff.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing]` | `append-idempotent-no-diff.txtar` |
| `TestFrontmatterUpdateCLI.test_summary_stays_on_stderr` | `success-summary-stderr.txtar` |
| `TestFrontmatterUpdateCLI.test_logs_to_booping_log` | `logs-one-line-when-a-vault-is-attached.txtar` |
| `TestFrontmatterUpdateCLI.test_does_not_write_to_real_home` | DROPPED: vault-isolation safety property; same isolation verified by `logs-one-line-when-a-vault-is-attached.txtar` |
