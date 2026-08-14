# Coverage cross-check

| Test | Maps to |
|------|---------|
| TestParsePairs::test_valid_pairs | sets-multiple-keys-in-one-call.txtar |
| TestParsePairs::test_value_with_equals_sign | dropped: no named case pins splitting a pair at the first equals sign; the parse path is exercised by every set/append case |
| TestParsePairs::test_empty_key_exits_1 | dropped: no named case pins the empty-key error branch (exit 1, "empty key in pair"); the sibling no-equals branch is malformed-pair-exits-1.txtar |
| TestParsePairs::test_no_equals_exits_1 | malformed-pair-exits-1.txtar |
| TestInterpolate::test_datetime_macro | real-macro-output-lands-in-the-frontmatter.txtar |
| TestInterpolate::test_date_macro | real-macro-output-lands-in-the-frontmatter.txtar |
| TestInterpolate::test_stubbed_macro_is_not_executed | stubbed-macro-value-lands-typed.txtar |
| TestInterpolate::test_unknown_macro_path_exits_non_zero | unknown-macro-name-exits-2.txtar |
| TestInterpolate::test_malformed_jinja_exits_non_zero | malformed-jinja-exits-2.txtar |
| TestInterpolate::test_git_commit_macro_runs_against_the_repo_dir | dropped: live-git macro coverage abandoned per plan decision — real-execution case real-macro-output-lands-in-the-frontmatter.txtar (M02/2.3) carries the shell-execution guarantee; cwd: repo scoping stays in tests/macros_test.py |
| TestInterpolate::test_retired_head_token_is_a_literal | dropped: no named case pins an @-prefixed value passing through unexpanded; the general literal passthrough is sets-a-key-with-a-literal-value.txtar |
| TestInterpolate::test_literal_value | sets-a-key-with-a-literal-value.txtar |
| TestInterpolate::test_literal_value_with_spaces_untouched | sets-a-key-with-a-literal-value.txtar |
| TestInterpolate::test_at_sign_prefix_not_interpolated | dropped: no named case pins an @-prefixed value passing through unexpanded; the general literal passthrough is sets-a-key-with-a-literal-value.txtar |
| TestInterpolate::test_retired_now_token_is_a_literal | dropped: no named case pins an @-prefixed value passing through unexpanded; the general literal passthrough is sets-a-key-with-a-literal-value.txtar |
| TestHookTokenising::test_quoted_macro_expression_survives_shlex | dropped: hook tokenising lives in tests/commands/playbook_transition_test.py (test_file_target_hook_updates_sibling_file, test_file_target_hook_interpolates_instance) |
| TestHookTokenising::test_file_target_with_quoted_macro_expression | dropped: hook tokenising lives in tests/commands/playbook_transition_test.py (test_file_target_hook_updates_sibling_file, test_file_target_hook_interpolates_instance) |
| TestScalarTyping::test_scalar_lands_typed[integer] | integer-value-lands-unquoted.txtar |
| TestScalarTyping::test_scalar_lands_typed[float] | float-value-lands-unquoted.txtar |
| TestScalarTyping::test_scalar_lands_typed[null] | null-value-lands-as-null.txtar |
| TestScalarTyping::test_scalar_lands_typed[boolean] | boolean-value-lands-unquoted.txtar |
| TestScalarTyping::test_scalar_lands_typed[partly-numeric] | sets-a-key-with-a-literal-value.txtar |
| TestScalarTyping::test_scalar_lands_typed[yaml-1-1-boolean-word] | yaml-1-1-yes-stays-a-string.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[@lead] | ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[*star] | ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[&anchor] | ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[!bang] | ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[%pct] | ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[`tick] | ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[a: b] | ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[ padded ] | ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_macro_rendered_date_stays_a_string | macro-rendered-date-like-value-stays-a-string.txtar |
| TestFrontmatterUpdateCLI::test_sets_planned_with_date_macro | real-macro-output-lands-in-the-frontmatter.txtar |
| TestFrontmatterUpdateCLI::test_sets_commit_with_the_git_macro | dropped: live-git macro coverage abandoned per plan decision — real-execution case real-macro-output-lands-in-the-frontmatter.txtar (M02/2.3) carries the shell-execution guarantee; cwd: repo scoping stays in tests/macros_test.py |
| TestFrontmatterUpdateCLI::test_sets_created_with_date_macro | real-macro-output-lands-in-the-frontmatter.txtar |
| TestFrontmatterUpdateCLI::test_literal_value | sets-a-key-with-a-literal-value.txtar |
| TestFrontmatterUpdateCLI::test_missing_plan_exits_1 | missing-plan-file-exits-1.txtar |
| TestFrontmatterUpdateCLI::test_malformed_pair_exits_1 | malformed-pair-exits-1.txtar |
| TestFrontmatterUpdateCLI::test_preserves_other_keys_and_body | preserves-other-keys-and-the-body.txtar |
| TestFrontmatterUpdateCLI::test_multiple_keys_at_once | sets-multiple-keys-in-one-call.txtar |
| TestFrontmatterUpdateCLI::test_remove_key_and_add_empty | combines-sets-removals-and-appends-in-one-call.txtar |
| TestFrontmatterUpdateCLI::test_remove_only_no_pairs | remove-drops-a-key.txtar |
| TestFrontmatterUpdateCLI::test_nothing_to_do_exits_1 | nothing-to-do-exits-1.txtar |
| TestFrontmatterUpdateCLI::test_append_creates_list_on_null_key | append-creates-a-list-on-a-null-key.txtar |
| TestFrontmatterUpdateCLI::test_append_creates_list_on_absent_key | append-creates-a-list-on-an-absent-key.txtar |
| TestFrontmatterUpdateCLI::test_append_extends_existing_list | append-extends-an-existing-list.txtar |
| TestFrontmatterUpdateCLI::test_append_is_idempotent | second-identical-append-prints-no-diff.txtar |
| TestFrontmatterUpdateCLI::test_append_onto_scalar_exits_1 | append-onto-a-scalar-exits-1.txtar |
| TestFrontmatterUpdateCLI::test_append_alongside_pairs_and_removals | combines-sets-removals-and-appends-in-one-call.txtar |
| TestFrontmatterUpdateCLI::test_append_only_still_reports_nothing_to_do_when_empty | append-only-call-with-nothing-to-do-exits-1.txtar |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[changed-value] | stdout-carries-a-unified-diff.txtar |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[append] | append-extends-an-existing-list.txtar |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[removal] | remove-drops-a-key.txtar |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing] | second-identical-call-prints-no-diff.txtar |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing] | second-identical-append-prints-no-diff.txtar |
| TestFrontmatterUpdateCLI::test_summary_stays_on_stderr | success-summary-goes-to-stderr.txtar |
| TestFrontmatterUpdateCLI::test_logs_to_booping_log | logs-one-line-when-a-vault-is-attached.txtar |
| TestFrontmatterUpdateCLI::test_does_not_write_to_real_home | logs-one-line-when-a-vault-is-attached.txtar |
