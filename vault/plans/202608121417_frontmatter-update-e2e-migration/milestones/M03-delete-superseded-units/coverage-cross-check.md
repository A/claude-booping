# Coverage cross-check

| Unit test in `frontmatter_update_test.py` | Corpus case / Drop rationale |
|---|---|
| `TestParsePairs.test_valid_pairs` | `sets-multiple-keys-in-one-call.txtar` |
| `TestParsePairs.test_value_with_equals_sign` | `sets-a-key-with-a-literal-value.txtar` |
| `TestParsePairs.test_empty_key_exits_1` | `malformed-pair-is-rejected.txtar` |
| `TestParsePairs.test_no_equals_exits_1` | `malformed-pair-is-rejected.txtar` |
| `TestInterpolate.test_datetime_macro` | `interpolates-stubbed-macro-value.txtar` |
| `TestInterpolate.test_date_macro` | `interpolates-stubbed-macro-value.txtar` |
| `TestInterpolate.test_stubbed_macro_is_not_executed` | `interpolates-stubbed-macro-value.txtar` |
| `TestInterpolate.test_unknown_macro_path_exits_non_zero` | `unknown-macro-name-is-rejected.txtar` |
| `TestInterpolate.test_malformed_jinja_exits_non_zero` | `malformed-jinja-is-rejected.txtar` |
| `TestInterpolate.test_git_commit_macro_runs_against_the_repo_dir` | Dropped: live-git macro test consciously abandoned per plan decision; real-execution coverage lives in `executes-real-macro-command.txtar` (M02/2.3) |
| `TestInterpolate.test_retired_head_token_is_a_literal` | `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate.test_literal_value` | `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate.test_literal_value_with_spaces_untouched` | `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate.test_at_sign_prefix_not_interpolated` | `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate.test_retired_now_token_is_a_literal` | `sets-a-key-with-a-literal-value.txtar` |
| `TestHookTokenising.test_quoted_macro_expression_survives_shlex` | Dropped: tests `playbook_transition.dispatch_frontmatter_update`, covered in `tests/commands/playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`) |
| `TestHookTokenising.test_file_target_with_quoted_macro_expression` | Dropped: tests `playbook_transition.dispatch_frontmatter_update`, covered in `tests/commands/playbook_transition_test.py` (`test_file_target_hook_interpolates_instance`) |
| `TestScalarTyping.test_scalar_lands_typed[integer]` | `coerces-integer-value.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[float]` | `coerces-float-value.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[null]` | `coerces-null-value.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[boolean]` | `coerces-boolean-value.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[partly-numeric]` | `sets-a-key-with-a-literal-value.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[yaml-1-1-boolean-word]` | `coerces-yaml-1-1-boolean-word-as-quoted-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes` | `quotes-ambiguous-string-value.txtar` |
| `TestScalarTyping.test_macro_rendered_date_stays_a_string` | `macro-rendered-date-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_planned_with_date_macro` | `interpolates-stubbed-macro-value.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_commit_with_the_git_macro` | Dropped: live-git macro test consciously abandoned per plan decision; real-execution coverage lives in `executes-real-macro-command.txtar` (M02/2.3) |
| `TestFrontmatterUpdateCLI.test_sets_created_with_date_macro` | `interpolates-stubbed-macro-value.txtar` |
| `TestFrontmatterUpdateCLI.test_literal_value` | `sets-a-key-with-a-literal-value.txtar` |
| `TestFrontmatterUpdateCLI.test_missing_plan_exits_1` | `missing-plan-file-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_malformed_pair_exits_1` | `malformed-pair-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_preserves_other_keys_and_body` | `preserves-other-keys-and-body.txtar` |
| `TestFrontmatterUpdateCLI.test_multiple_keys_at_once` | `sets-multiple-keys-in-one-call.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_key_and_add_empty` | `removes-a-key.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_only_no_pairs` | `removes-a-key.txtar` |
| `TestFrontmatterUpdateCLI.test_nothing_to_do_exits_1` | `nothing-to-do-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_null_key` | `append-creates-list-on-null-key.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_absent_key` | `append-creates-list-on-absent-key.txtar` |
| `TestFrontmatterUpdateCLI.test_append_extends_existing_list` | `append-extends-existing-list.txtar` |
| `TestFrontmatterUpdateCLI.test_append_is_idempotent` | `append-is-idempotent.txtar` |
| `TestFrontmatterUpdateCLI.test_append_onto_scalar_exits_1` | `append-onto-scalar-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_append_alongside_pairs_and_removals` | `combined-pairs-removals-and-appends.txtar` |
| `TestFrontmatterUpdateCLI.test_append_only_still_reports_nothing_to_do_when_empty` | `append-only-nothing-to-do-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[changed-value]` | `diff-shape-is-unified-diff-on-stdout.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[append]` | `diff-shape-is-unified-diff-on-stdout.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[removal]` | `diff-shape-is-unified-diff-on-stdout.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing]` | `second-identical-call-prints-no-diff.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing]` | `append-is-idempotent.txtar` |
| `TestFrontmatterUpdateCLI.test_summary_stays_on_stderr` | `success-summary-line-on-stderr-not-stdout.txtar` |
| `TestFrontmatterUpdateCLI.test_logs_to_booping_log` | `logs-one-line-when-a-vault-is-attached.txtar` |
| `TestFrontmatterUpdateCLI.test_does_not_write_to_real_home` | `logs-one-line-when-a-vault-is-attached.txtar` |
