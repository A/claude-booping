# Coverage cross-check

| Unit test | Corpus case or drop rationale |
|---|---|
| `TestParsePairs.test_valid_pairs` | `sets-key.txtar` (pair parsing exercised through CLI) |
| `TestParsePairs.test_value_with_equals_sign` | `coercion-newline-tab-value.txtar` (special chars in values) |
| `TestParsePairs.test_empty_key_exits_1` | `error-malformed-pair.txtar` |
| `TestParsePairs.test_no_equals_exits_1` | `error-malformed-pair.txtar` |
| `TestInterpolate.test_datetime_macro` | `macro-real-execution.txtar` |
| `TestInterpolate.test_date_macro` | `macro-date-stays-string.txtar` |
| `TestInterpolate.test_stubbed_macro_is_not_executed` | `macro-stubbed-interpolation.txtar` |
| `TestInterpolate.test_unknown_macro_path_exits_non_zero` | `macro-unknown-exits-2.txtar` |
| `TestInterpolate.test_malformed_jinja_exits_non_zero` | `macro-malformed-jinja-exits-2.txtar` |
| `TestInterpolate.test_git_commit_macro_runs_against_the_repo_dir` | Dropped: live-git macro test; real-execution coverage in `macro-real-execution.txtar` (M02/2.3) |
| `TestInterpolate.test_retired_head_token_is_a_literal` | Dropped: `@*` token syntax retired; literal passthrough implicit in all e2e cases |
| `TestInterpolate.test_literal_value` | `sets-key.txtar` |
| `TestInterpolate.test_literal_value_with_spaces_untouched` | `sets-key.txtar` |
| `TestInterpolate.test_at_sign_prefix_not_interpolated` | Dropped: `@*` token syntax retired; literal passthrough implicit in all e2e cases |
| `TestInterpolate.test_retired_now_token_is_a_literal` | Dropped: `@*` token syntax retired; literal passthrough implicit in all e2e cases |
| `TestHookTokenising.test_quoted_macro_expression_survives_shlex` | Dropped: hook-tokenising coverage in `playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`) |
| `TestHookTokenising.test_file_target_with_quoted_macro_expression` | Dropped: hook-tokenising coverage in `playbook_transition_test.py` (`test_file_target_hook_interpolates_instance`) |
| `TestScalarTyping.test_scalar_lands_typed[integer]` | `coercion-integer.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[float]` | `coercion-float.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[null]` | `coercion-null.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[boolean]` | `coercion-boolean.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[partly-numeric]` | Dropped: numeric-prefixed strings covered by coercion corpus as unquoted literals |
| `TestScalarTyping.test_scalar_lands_typed[yaml-1-1-boolean-word]` | `coercion-yaml11-boolean-word.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes` | Dropped: 8 special-char variants covered implicitly by e2e coercion corpus |
| `TestScalarTyping.test_macro_rendered_date_stays_a_string` | `macro-date-stays-string.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_planned_with_date_macro` | `macro-real-execution.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_commit_with_the_git_macro` | `macro-real-execution.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_created_with_date_macro` | `macro-date-stays-string.txtar` |
| `TestFrontmatterUpdateCLI.test_literal_value` | `sets-key.txtar` |
| `TestFrontmatterUpdateCLI.test_missing_plan_exits_1` | `error-missing-plan-file.txtar` |
| `TestFrontmatterUpdateCLI.test_malformed_pair_exits_1` | `error-malformed-pair.txtar` |
| `TestFrontmatterUpdateCLI.test_preserves_other_keys_and_body` | `preserves-keys-and-body.txtar` |
| `TestFrontmatterUpdateCLI.test_multiple_keys_at_once` | `sets-multiple-keys.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_key_and_add_empty` | `list-remove-drops-key.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_only_no_pairs` | Dropped: removal-only path covered by `list-remove-drops-key.txtar` |
| `TestFrontmatterUpdateCLI.test_nothing_to_do_exits_1` | `error-nothing-to-do.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_null_key` | `list-append-creates-on-null-key.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_absent_key` | `list-append-creates-on-absent-key.txtar` |
| `TestFrontmatterUpdateCLI.test_append_extends_existing_list` | `list-append-extends-existing.txtar` |
| `TestFrontmatterUpdateCLI.test_append_is_idempotent` | `list-append-idempotent.txtar` |
| `TestFrontmatterUpdateCLI.test_append_onto_scalar_exits_1` | `list-append-scalar-errors.txtar` |
| `TestFrontmatterUpdateCLI.test_append_alongside_pairs_and_removals` | `list-combined-operations.txtar` |
| `TestFrontmatterUpdateCLI.test_append_only_still_reports_nothing_to_do_when_empty` | `error-nothing-to-do.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[changed-value]` | `output-diff-shape.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[append]` | `list-append-extends-existing.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[removal]` | `list-remove-drops-key.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing]` | `identical-call-no-diff.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing]` | `list-append-nothing-to-change.txtar` |
| `TestFrontmatterUpdateCLI.test_summary_stays_on_stderr` | `output-summary-stderr.txtar` |
| `TestFrontmatterUpdateCLI.test_logs_to_booping_log` | `logs-one-line-vault-attached.txtar` |
| `TestFrontmatterUpdateCLI.test_does_not_write_to_real_home` | Dropped: HOME isolation safety check; functional logging covered by `logs-one-line-vault-attached.txtar` |
