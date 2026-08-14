# Coverage cross-check

| Test | Maps to |
|------|---------|
| `TestParsePairs.test_valid_pairs` | `sets-multiple-keys-in-one-call.txtar` |
| `TestParsePairs.test_value_with_equals_sign` | `sets-a-key-with-a-literal-value.txtar` |
| `TestParsePairs.test_empty_key_exits_1` | `malformed-pair-is-rejected.txtar` |
| `TestParsePairs.test_no_equals_exits_1` | `malformed-pair-is-rejected.txtar` |
| `TestInterpolate.test_datetime_macro` | `macro-rendered-date-stays-a-string.txtar` |
| `TestInterpolate.test_date_macro` | `macro-rendered-date-stays-a-string.txtar` |
| `TestInterpolate.test_stubbed_macro_is_not_executed` | `stubbed-macro-lands-typed.txtar` |
| `TestInterpolate.test_unknown_macro_path_exits_non_zero` | `unknown-macro-is-rejected.txtar` |
| `TestInterpolate.test_malformed_jinja_exits_non_zero` | `malformed-jinja-is-rejected.txtar` |
| `TestInterpolate.test_git_commit_macro_runs_against_the_repo_dir` | dropped — live-git abandoned; M02/2.3 `real-echo-macro-writes-its-output.txtar` |
| `TestInterpolate.test_retired_head_token_is_a_literal` | `quotes-an-ambiguous-string.txtar` |
| `TestInterpolate.test_literal_value` | `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate.test_literal_value_with_spaces_untouched` | `partly-numeric-string-stays-unquoted.txtar` |
| `TestInterpolate.test_at_sign_prefix_not_interpolated` | `quotes-an-ambiguous-string.txtar` |
| `TestInterpolate.test_retired_now_token_is_a_literal` | `quotes-an-ambiguous-string.txtar` |
| `TestHookTokenising.test_quoted_macro_expression_survives_shlex` | dropped — hook-tokenising; `playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`) |
| `TestHookTokenising.test_file_target_with_quoted_macro_expression` | dropped — hook-tokenising; `playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`) |
| `TestScalarTyping.test_scalar_lands_typed[integer]` | `coerces-integer.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[float]` | `coerces-float.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[null]` | `coerces-null.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[boolean]` | `coerces-boolean.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[partly-numeric]` | `partly-numeric-string-stays-unquoted.txtar` |
| `TestScalarTyping.test_scalar_lands_typed[yaml-1-1-boolean-word]` | `yaml-1-1-yes-quirk-stays-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[@lead]` | `quotes-an-ambiguous-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[*star]` | `quotes-an-ambiguous-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[&anchor]` | `quotes-an-ambiguous-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[!bang]` | `quotes-an-ambiguous-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[%pct]` | `quotes-an-ambiguous-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[\`tick]` | `quotes-an-ambiguous-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[a: b]` | `quotes-an-ambiguous-string.txtar` |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[ padded ]` | `quotes-an-ambiguous-string.txtar` |
| `TestScalarTyping.test_macro_rendered_date_stays_a_string` | `macro-rendered-date-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_planned_with_date_macro` | `macro-rendered-date-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_commit_with_the_git_macro` | dropped — live-git abandoned; M02/2.3 `real-echo-macro-writes-its-output.txtar` |
| `TestFrontmatterUpdateCLI.test_sets_created_with_date_macro` | `macro-rendered-date-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI.test_literal_value` | `sets-a-key-with-a-literal-value.txtar` |
| `TestFrontmatterUpdateCLI.test_missing_plan_exits_1` | `missing-plan-file-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_malformed_pair_exits_1` | `malformed-pair-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_preserves_other_keys_and_body` | `preserves-other-keys-and-body.txtar` |
| `TestFrontmatterUpdateCLI.test_multiple_keys_at_once` | `sets-multiple-keys-in-one-call.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_key_and_add_empty` | `removes-a-key-and-sets-an-empty-value.txtar` |
| `TestFrontmatterUpdateCLI.test_remove_only_no_pairs` | `removes-a-key.txtar` |
| `TestFrontmatterUpdateCLI.test_nothing_to_do_exits_1` | `nothing-to-do-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_null_key` | `appends-to-a-null-key.txtar` |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_absent_key` | `appends-to-an-absent-key.txtar` |
| `TestFrontmatterUpdateCLI.test_append_extends_existing_list` | `appends-to-an-existing-list.txtar` |
| `TestFrontmatterUpdateCLI.test_append_is_idempotent` | `second-identical-append-prints-no-diff.txtar` |
| `TestFrontmatterUpdateCLI.test_append_onto_scalar_exits_1` | `append-onto-a-scalar-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_append_alongside_pairs_and_removals` | `sets-removes-and-appends-in-one-call.txtar` |
| `TestFrontmatterUpdateCLI.test_append_only_still_reports_nothing_to_do_when_empty` | `nothing-to-do-is-rejected.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[changed-value]` | `prints-a-unified-diff-of-the-change.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[append]` | `appends-to-an-existing-list.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[removal]` | `removes-a-key.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing]` | `second-identical-call-prints-no-diff.txtar` |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing]` | `second-identical-append-prints-no-diff.txtar` |
| `TestFrontmatterUpdateCLI.test_summary_stays_on_stderr` | `success-summary-stays-on-stderr.txtar` |
| `TestFrontmatterUpdateCLI.test_logs_to_booping_log` | `logs-one-line-when-a-vault-is-attached.txtar` |
| `TestFrontmatterUpdateCLI.test_does_not_write_to_real_home` | dropped — not CLI-observable; e2e runner isolates `HOME`/`XDG_CONFIG_HOME` |
