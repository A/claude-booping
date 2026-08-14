# Coverage cross-check

| Unit test | Corpus case filename | Rationale |
|-----------|-------------------|-----------|
| `TestParsePairs.test_valid_pairs` | `malformed-pair.txtar` | Tests valid parsing (complement to malformed case) |
| `TestParsePairs.test_value_with_equals_sign` | `value-with-equals.txtar` | Tests value parsing with `=` signs |
| `TestParsePairs.test_empty_key_exits_1` | `malformed-pair.txtar` | Tests empty key error handling |
| `TestParsePairs.test_no_equals_exits_1` | `malformed-pair.txtar` | Tests missing `=` error handling |
| `TestInterpolate.test_datetime_macro` | `stubbed-macro-date-like-value-stays-string.txtar` | Tests datetime macro interpolation with stubbed config |
| `TestInterpolate.test_date_macro` | `stubbed-macro-date-like-value-stays-string.txtar` | Tests date macro interpolation with stubbed config |
| `TestInterpolate.test_stubbed_macro_is_not_executed` | `stubbed-macro-string-value.txtar` | Tests stubbed macro behavior (literal string) |
| `TestInterpolate.test_unknown_macro_path_exits_non_zero` | `unknown-macro-exits-2.txtar` | Tests unknown macro error handling |
| `TestInterpolate.test_malformed_jinja_exits_non_zero` | `malformed-jinja-exits-2.txtar` | Tests malformed Jinja error handling |
| `TestInterpolate.test_git_commit_macro_runs_against_the_repo_dir` | M02/2.3 real-execution case | Live-git test consciously abandoned, replaced by real-execution corpus case |
| `TestInterpolate.test_retired_head_token_is_a_literal` | `set-key-literal-value.txtar` | Tests literal `@head` token handling |
| `TestInterpolate.test_literal_value` | `set-key-literal-value.txtar` | Tests literal value interpolation |
| `TestInterpolate.test_literal_value_with_spaces_untouched` | `set-key-literal-value.txtar` | Tests literal value with spaces handling |
| `TestInterpolate.test_at_sign_prefix_not_interpolated` | `set-key-literal-value.txtar` | Tests `@` prefix literal handling |
| `TestInterpolate.test_retired_now_token_is_a_literal` | `set-key-literal-value.txtar` | Tests literal `@now` token handling |
| `TestHookTokenising.test_quoted_macro_expression_survives_shlex` | `playbook_transition_test.py` coverage | Tests hook tokenising (covered by `test_file_target_hook_interpolates_instance`) |
| `TestHookTokenising.test_file_target_with_quoted_macro_expression` | `playbook_transition_test.py` coverage | Tests file target with macro (covered by `test_file_target_hook_updates_sibling_file`) |
| `TestScalarTyping.test_scalar_lands_typed.*` | coercion-*.txtar | All scalar type coercion tests covered by coercion corpus cases |
| `TestScalarTyping.test_syntax_sensitive_string_keeps_its_quotes` | `coercion-newline-tab-bearing-value.txtar` | Tests syntax-sensitive string quoting |
| `TestScalarTyping.test_macro_rendered_date_stays_a_string` | `stubbed-macro-date-like-value-stays-string.txtar` | Tests macro-rendered date remains string |
| `TestFrontmatterUpdateCLI.test_sets_planned_with_date_macro` | `stubbed-macro-date-like-value-stays-string.txtar` | Tests setting planned with date macro |
| `TestFrontmatterUpdateCLI.test_sets_commit_with_the_git_macro` | M02/2.3 real-execution case | Git macro test covered by real-execution corpus case |
| `TestFrontmatterUpdateCLI.test_sets_created_with_date_macro` | `stubbed-macro-date-like-value-stays-string.txtar` | Tests setting created with date macro |
| `TestFrontmatterUpdateCLI.test_literal_value` | `set-key-literal-value.txtar` | Tests setting literal value |
| `TestFrontmatterUpdateCLI.test_missing_plan_exits_1` | `missing-plan-file.txtar` | Tests missing plan error handling |
| `TestFrontmatterUpdateCLI.test_malformed_pair_exits_1` | `malformed-pair.txtar` | Tests malformed pair error handling |
| `TestFrontmatterUpdateCLI.test_preserves_other_keys_and_body` | `set-key-literal-value.txtar` | Tests preservation of existing keys and body |
| `TestFrontmatterUpdateCLI.test_multiple_keys_at_once` | `set-multiple-keys-one-call.txtar` | Tests setting multiple keys in one call |
| `TestFrontmatterUpdateCLI.test_remove_key_and_add_empty` | `combined-operations.txtar` | Tests key removal and addition |
| `TestFrontmatterUpdateCLI.test_remove_only_no_pairs` | `remove-key.txtar` | Tests key-only removal |
| `TestFrontmatterUpdateCLI.test_nothing_to_do_exits_1` | `nothing-to-do.txtar` | Tests nothing-to-do error handling |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_null_key` | `append-to-null-key.txtar` | Tests append to null key |
| `TestFrontmatterUpdateCLI.test_append_creates_list_on_absent_key` | `append-to-absent-key.txtar` | Tests append to absent key |
| `TestFrontmatterUpdateCLI.test_append_extends_existing_list` | `append-to-existing-list.txtar` | Tests append to existing list |
| `TestFrontmatterUpdateCLI.test_append_is_idempotent` | `append-identical-twice-idempotent.txtar` | Tests idempotent append |
| `TestFrontmatterUpdateCLI.test_append_onto_scalar_exits_1` | `append-to-scalar-exits-1.txtar` | Tests append to scalar error handling |
| `TestFrontmatterUpdateCLI.test_append_alongside_pairs_and_removals` | `combined-operations.txtar` | Tests combined operations with append |
| `TestFrontmatterUpdateCLI.test_append_only_still_reports_nothing_to_do_when_empty` | `append-only-nothing-to-change-exits-1.txtar` | Tests append nothing-to-do error |
| `TestFrontmatterUpdateCLI.test_prints_a_unified_diff_of_the_change.*` | `unified-diff-shape.txtar` | Tests unified diff output |
| `TestFrontmatterUpdateCLI.test_summary_stays_on_stderr` | `success-summary-on-stderr.txtar` | Tests stderr summary output |
| `TestFrontmatterUpdateCLI.test_logs_to_booping_log` | `log-when-vault-attached.txtar` | Tests logging to .booping.log when vault is attached |
| `TestFrontmatterUpdateCLI.test_does_not_write_to_real_home` | (no direct case) | Home isolation enforced by pytest-txtar harness sandbox |