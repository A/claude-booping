# Coverage cross-check

| Unit test | Corpus case | Rationale |
|---|---|---|
| `TestParsePairs.test_valid_pairs` | `sets-key-with-literal-value.txtar` | |
| `TestParsePairs.test_value_with_equals_sign` | `tab-bearing-value-round-trips.txtar` | same quoting machinery for values containing special characters |
| `TestParsePairs.test_empty_key_exits_1` | `malformed-pair-errors.txtar` | |
| `TestParsePairs.test_no_equals_exits_1` | `malformed-pair-errors.txtar` | |
| `TestInterpolate.test_datetime_macro` | `real-macro-execution-through-cli.txtar` | M02/2.3 replaces unit-level macro execution test |
| `TestInterpolate.test_date_macro` | `real-macro-execution-through-cli.txtar` | M02/2.3 replaces unit-level macro execution test |
| `TestInterpolate.test_stubbed_macro_is_not_executed` | `stubbed-macro-lands-typed.txtar` | |
| `TestInterpolate.test_unknown_macro_path_exits_non_zero` | `unknown-macro-exits-2.txtar` | |
| `TestInterpolate.test_malformed_jinja_exits_non_zero` | `malformed-jinja-exits-2.txtar` | |
| `TestInterpolate.test_git_commit_macro_runs_against_the_repo_dir` | `real-macro-execution-through-cli.txtar` | DROPPED: live-git macro; replaced by M02/2.3 |
| `TestInterpolate.test_retired_head_token_is_a_literal` | `sets-key-with-literal-value.txtar` | literal passthrough |
| `TestInterpolate.test_literal_value` | `sets-key-with-literal-value.txtar` | |
| `TestInterpolate.test_literal_value_with_spaces_untouched` | `sets-key-with-literal-value.txtar` | |
| `TestInterpolate.test_at_sign_prefix_not_interpolated` | `sets-key-with-literal-value.txtar` | literal passthrough |
| `TestInterpolate.test_retired_now_token_is_a_literal` | `sets-key-with-literal-value.txtar` | literal passthrough |
| `TestHookTokenising.test_quoted_macro_expression_survives_shlex` | — | DROPPED: hook-tokenising; covered by `playbook_transition_test.py` |
| `TestHookTokenising.test_file_target_with_quoted_macro_expression` | — | DROPPED: hook-tokenising; covered by `playbook_transition_test.py` |
| `TestScalarTyping.test_scalar_lands_typed[integer]` | `coerces-int-value.txtar` | |
| `TestScalarTyping.test_scalar_lands_typed[float]` | `coerces-float-value.txtar` | |
| `TestScalarTyping.test_scalar_lands_typed[null]` | `coerces-null-value.txtar` | |
| `TestScalarTyping.test_scalar_lands_typed[boolean]` | `coerces-bool-value.txtar` | |
| `TestScalarTyping.test_scalar_lands_typed[partly-numeric]` | `coerces-int-value.txtar` | same coercion machinery; string-with-digits is not a YAML 1.1 scalar alias |
| `TestScalarTyping.test_scalar_lands_typed[yaml-1-1-boolean-word]` | `yaml11-yes-stays-string.txtar` | |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[@lead]` | `tab-bearing-value-round-trips.txtar` | same quoting machinery for YAML-special characters |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[*star]` | `tab-bearing-value-round-trips.txtar` | |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[&anchor]` | `tab-bearing-value-round-trips.txtar` | |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[!bang]` | `tab-bearing-value-round-trips.txtar` | |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[%pct]` | `tab-bearing-value-round-trips.txtar` | |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[\`tick]` | `tab-bearing-value-round-trips.txtar` | |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[a: b]` | `tab-bearing-value-round-trips.txtar` | |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes[ padded ]` | `tab-bearing-value-round-trips.txtar` | |
| `TestScalarTyping.test_macro_rendered_date_stays_a_string` | `macro-rendered-date-stays-string.txtar` | |
| `TestFrontmatterUpdateCLI.test_sets_planned_with_date_macro` | `real-macro-execution-through-cli.txtar` | M02/2.3 replaces unit-level macro execution test |
| `TestFrontmatterUpdateCLI.test_sets_commit_with_the_git_macro` | `real-macro-execution-through-cli.txtar` | DROPPED: live-git macro; replaced by M02/2.3 |
| `TestFrontmatterUpdateCLI.test_sets_created_with_date_macro` | `real-macro-execution-through-cli.txtar` | M02/2.3 replaces unit-level macro execution test |
| `TestFrontmatterUpdateCLI.test_literal_value` | `sets-key-with-literal-value.txtar` | |
| `TestFrontmatterUpdateCLI.test_missing_plan_exits_1` | `missing-plan-file-errors.txtar` | |
| `TestFrontmatterUpdateCLI.test_malformed_pair_exits_1` | `malformed-pair-errors.txtar` | |
| `TestFrontmatterUpdateCLI.test_preserves_other_keys_and_body` | `preserves-other-keys-and-body.txtar` | |
| `TestFrontmatterUpdateCLI.test_multiple_keys_at_once` | `sets-multiple-keys-in-one-call.txtar` | |
| `TestFrontmatterUpdateCLI.test_remove_key_and_add_empty` | `remove-drops-key.txtar` | |
| `TestFrontmatterUpdateCLI.test_remove_only_no_pairs` | `remove-drops-key.txtar` | |
| `TestFrontmatterUpdateCLI.test_nothing_to_do_exits_1` | `nothing-to-do-errors.txtar` | |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_null_key` | `append-creates-list-on-null-key.txtar` | |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_absent_key` | `append-creates-list-on-absent-key.txtar` | |
| `TestFrontmatterUpdateCLI.test_append_extends_existing_list` | `append-extends-existing-list.txtar` | |
| `TestFrontmatterUpdateCLI.test_append_is_idempotent` | `append-idempotent-second-run-no-diff.txtar` | |
| `TestFrontmatterUpdateCLI.test_append_onto_scalar_exits_1` | `append-onto-scalar-errors.txtar` | |
| `TestFrontmatterUpdateCLI.test_append_alongside_pairs_and_removals` | `combined-pairs-removals-and-appends.txtar` | |
| `TestFrontmatterUpdateCLI.test_append_only_still_reports_nothing_to_do_when_empty` | `nothing-to-do-errors.txtar` | |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[changed-value]` | `stdout-carries-unified-diff-shape.txtar` | |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[append]` | `stdout-carries-unified-diff-shape.txtar` | |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[removal]` | `stdout-carries-unified-diff-shape.txtar` | |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing]` | `identical-second-call-prints-no-diff.txtar` | |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing]` | `identical-second-call-prints-no-diff.txtar` | |
| `TestFrontmatterUpdateCLI.test_summary_stays_on_stderr` | `success-summary-on-stderr-not-stdout.txtar` | |
| `TestFrontmatterUpdateCLI.test_logs_to_booping_log` | `logs-one-line-when-a-vault-is-attached.txtar` | |
| `TestFrontmatterUpdateCLI.test_does_not_write_to_real_home` | `logs-one-line-when-a-vault-is-attached.txtar` | e2e runner sandbox isolates HOME; same log-isolation concern |
