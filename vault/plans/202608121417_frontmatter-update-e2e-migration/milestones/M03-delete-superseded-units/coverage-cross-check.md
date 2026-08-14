# Coverage cross-check

| Test | Mapping |
| :--- | :--- |
| `TestParsePairs.test_valid_pairs` | `set-single-key.txtar` |
| `TestParsePairs.test_value_with_equals_sign` | `coerce-ambiguous-string.txtar` |
| `TestParsePairs.test_empty_key_exits_1` | `error-malformed-pair.txtar` |
| `TestParsePairs.test_no_equals_exits_1` | `error-malformed-pair.txtar` |
| `TestInterpolate.test_datetime_macro` | `macro-stubbed-success.txtar` |
| `TestInterpolate.test_date_macro` | `macro-stubbed-success.txtar` |
| `TestInterpolate.test_stubbed_macro_is_not_executed` | `macro-stubbed-date-string.txtar` |
| `TestInterpolate.test_unknown_macro_path_exits_non_zero` | `macro-stubbed-unknown-error.txtar` |
| `TestInterpolate.test_malformed_jinja_exits_non_zero` | `macro-stubbed-malformed-error.txtar` |
| `TestInterpolate.test_git_commit_macro_runs_against_the_repo_dir` | `macro-real-execution.txtar` |
| `TestInterpolate.test_retired_head_token_is_a_literal` | `set-single-key.txtar` |
| `TestInterpolate.test_literal_value` | `set-single-key.txtar` |
| `TestInterpolate.test_literal_value_with_spaces_untouched` | `set-single-key.txtar` |
| `TestInterpolate.test_at_sign_prefix_not_interpolated` | `set-single-key.txtar` |
| `TestInterpolate.test_retired_now_token_is_a_literal` | `set-single-key.txtar` |
| `TestHookTokenising.test_quoted_macro_expression_survives_shlex` | rationale: `playbook_transition` coverage |
| `TestHookTokenising.test_file_target_with_quoted_macro_expression` | rationale: `playbook_transition` coverage |
| `TestScalarTyping.test_scalar_lands_typed` (integer) | `coerce-int.txtar` |
| `TestScalarTyping.test_scalar_lands_typed` (float) | `coerce-float.txtar` |
| `TestScalarTyping.test_scalar_lands_typed` (null) | `coerce-null.txtar` |
| `TestScalarTyping.test_scalar_lands_typed` (boolean) | `coerce-bool-true.txtar` |
| `TestScalarTyping.test_scalar_lands_typed` (partly-numeric) | `coerce-int.txtar` |
| `TestScalarTyping.test_scalar_lands_typed` (yaml-1-1-boolean-word) | `coerce-yaml-yes.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes` | `coerce-ambiguous-string.txtar` |
| `TestScalarTyping.test_macro_rendered_date_stays_a_string` | `macro-stubbed-success.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_planned_with_date_macro` | `macro-stubbed-success.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_commit_with_the_git_macro` | `macro-real-execution.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_created_with_date_macro` | `macro-stubbed-success.txtar` |
| `TestFrontmatterUpdateCLI.test_literal_value` | `set-single-key.txtar` |
| `TestFrontmatterUpdateCLI.test_missing_plan_exits_1` | `error-missing-plan.txtar` |
| `TestFrontmatterUpdateCLI.test_malformed_pair_exits_1` | `error-malformed-pair.txtar` |
| `TestFrontmatterUpdateCLI.test_preserves_other_keys_and_body` | `set-single-key.txtar` |
| `TestFrontmatterUpdateCLI.test_multiple_keys_at_once` | `set-multiple-keys.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_key_and_add_empty` | `list-op-remove.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_only_no_pairs` | `list-op-remove.txtar` |
| `TestFrontmatterUpdateCLI.test_nothing_to_do_exits_1` | `error-nothing-to-do.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_null_key` | `list-op-append-null.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_absent_key` | `list-op-append-absent.txtar` |
| `TestFrontmatterUpdateCLI.test_append_extends_existing_list` | `list-op-append-extend.txtar` |
| `TestFrontmatterUpdateCLI.test_append_is_idempotent` | `list-op-append-idempotent.txtar` |
| `TestFrontmatterUpdateCLI.test_append_onto_scalar_exits_1` | `list-op-append-scalar-error.txtar` |
| `TestFrontmatterUpdateCLI.test_append_alongside_pairs_and_removals` | `list-op-combined.txtar` |
| `TestFrontmatterUpdateCLI.test_append_only_still_reports_nothing_to_do_when_empty` | `list-op-nothing-to-do-error.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change` | `output-diff-shape.txtar` |
| `TestFrontmatterUpdateCLI.test_summary_stays_on_stderr` | `output-summary-stderr.txtar` |
| `TestFrontmatterUpdateCLI.test_logs_to_booping_log` | `output-log-side-effect.txtar` |
| `TestFrontmatterUpdateCLI.test_does_not_write_to_real_home` | `output-log-side-effect.txtar` |
