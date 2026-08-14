# Coverage cross-check

| Test | Coverage |
|------|----------|
| TestParsePairs.test_valid_pairs | sets-multiple-keys-in-one-call.txtar |
| TestParsePairs.test_value_with_equals_sign | sets-multiple-keys-in-one-call.txtar |
| TestParsePairs.test_empty_key_exits_1 | malformed-pair-is-rejected.txtar |
| TestParsePairs.test_no_equals_exits_1 | malformed-pair-is-rejected.txtar |
| TestInterpolate.test_datetime_macro | macro-rendered-date-like-stays-a-string.txtar |
| TestInterpolate.test_date_macro | macro-rendered-date-like-stays-a-string.txtar |
| TestInterpolate.test_stubbed_macro_is_not_executed | stubbed-macro-lands-typed.txtar |
| TestInterpolate.test_unknown_macro_path_exits_non_zero | unknown-macro-exits-2.txtar |
| TestInterpolate.test_malformed_jinja_exits_non_zero | malformed-jinja-exits-2.txtar |
| TestInterpolate.test_git_commit_macro_runs_against_the_repo_dir | drop: live-git macro → M02/2.3 real-macro-execution-gap-case.txtar |
| TestInterpolate.test_retired_head_token_is_a_literal | sets-a-literal-value.txtar |
| TestInterpolate.test_literal_value | sets-a-literal-value.txtar |
| TestInterpolate.test_literal_value_with_spaces_untouched | sets-a-literal-value.txtar |
| TestInterpolate.test_at_sign_prefix_not_interpolated | sets-a-literal-value.txtar |
| TestInterpolate.test_retired_now_token_is_a_literal | sets-a-literal-value.txtar |
| TestHookTokenising.test_quoted_macro_expression_survives_shlex | drop: hook-tokenising → playbook_transition_test.py (test_file_target_hook_updates_sibling_file) |
| TestHookTokenising.test_file_target_with_quoted_macro_expression | drop: hook-tokenising → playbook_transition_test.py (test_file_target_hook_interpolates_instance) |
| TestScalarTyping.test_scalar_lands_typed [integer] | set-coerces-integer.txtar |
| TestScalarTyping.test_scalar_lands_typed [float] | set-coerces-float.txtar |
| TestScalarTyping.test_scalar_lands_typed [null] | set-coerces-null.txtar |
| TestScalarTyping.test_scalar_lands_typed [boolean] | set-coerces-boolean.txtar |
| TestScalarTyping.test_scalar_lands_typed [partly-numeric] | sets-a-literal-value.txtar |
| TestScalarTyping.test_scalar_lands_typed [yaml-1-1-boolean-word] | set-keeps-yes-as-string.txtar |
| TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes [@lead, *star, &anchor, !bang, %pct, \`tick, a: b, " padded "] | set-quotes-ambiguous-string.txtar |
| TestScalarTyping.test_macro_rendered_date_stays_a_string | macro-rendered-date-like-stays-a-string.txtar |
| TestFrontmatterUpdateCLI.test_sets_planned_with_date_macro | macro-rendered-date-like-stays-a-string.txtar |
| TestFrontmatterUpdateCLI.test_sets_commit_with_the_git_macro | drop: live-git macro → M02/2.3 real-macro-execution-gap-case.txtar |
| TestFrontmatterUpdateCLI.test_sets_created_with_date_macro | macro-rendered-date-like-stays-a-string.txtar |
| TestFrontmatterUpdateCLI.test_literal_value | sets-a-literal-value.txtar |
| TestFrontmatterUpdateCLI.test_missing_plan_exits_1 | missing-plan-file-is-rejected.txtar |
| TestFrontmatterUpdateCLI.test_malformed_pair_exits_1 | malformed-pair-is-rejected.txtar |
| TestFrontmatterUpdateCLI.test_preserves_other_keys_and_body | sets-a-literal-value.txtar |
| TestFrontmatterUpdateCLI.test_multiple_keys_at_once | sets-multiple-keys-in-one-call.txtar |
| TestFrontmatterUpdateCLI.test_remove_key_and_add_empty | remove-drops-a-key.txtar |
| TestFrontmatterUpdateCLI.test_remove_only_no_pairs | remove-drops-a-key.txtar |
| TestFrontmatterUpdateCLI.test_nothing_to_do_exits_1 | nothing-to-do-is-rejected.txtar |
| TestFrontmatterUpdateCLI.test_append_creates_list_on_null_key | append-creates-list-on-null-key.txtar |
| TestFrontmatterUpdateCLI.test_append_creates_list_on_absent_key | append-creates-list-on-absent-key.txtar |
| TestFrontmatterUpdateCLI.test_append_extends_existing_list | append-extends-existing-list.txtar |
| TestFrontmatterUpdateCLI.test_append_is_idempotent | append-is-idempotent-second-run-no-diff.txtar |
| TestFrontmatterUpdateCLI.test_append_onto_scalar_exits_1 | append-onto-scalar-exits-1.txtar |
| TestFrontmatterUpdateCLI.test_append_alongside_pairs_and_removals | combined-pairs-removals-and-appends.txtar |
| TestFrontmatterUpdateCLI.test_append_only_still_reports_nothing_to_do_when_empty | nothing-to-do-is-rejected.txtar |
| TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change [changed-value] | diff-shape-on-stdout.txtar |
| TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change [append] | diff-shape-on-stdout.txtar |
| TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change [removal] | diff-shape-on-stdout.txtar |
| TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change [unchanged-value-prints-nothing] | second-identical-call-prints-no-diff.txtar |
| TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change [idempotent-append-prints-nothing] | append-is-idempotent-second-run-no-diff.txtar |
| TestFrontmatterUpdateCLI.test_summary_stays_on_stderr | summary-line-on-stderr.txtar |
| TestFrontmatterUpdateCLI.test_logs_to_booping_log | logs-one-line-when-a-vault-is-attached.txtar |
| TestFrontmatterUpdateCLI.test_does_not_write_to_real_home | logs-one-line-when-a-vault-is-attached.txtar |
