# Coverage cross-check

| Unit test (`booping-python/tests/commands/frontmatter_update_test.py`) | Corpus case (`booping-python/e2e/cases/frontmatter-update/`) or drop rationale |
|---|---|
| `TestParsePairs::test_valid_pairs` | `sets-multiple-keys-in-one-call.txtar` |
| `TestParsePairs::test_value_with_equals_sign` | Dropped without a corpus successor — no case passes a value containing `=`, so `parse_pairs`' partition-on-first-`=` is unasserted after deletion. Flagged to the runner as a coverage gap. |
| `TestParsePairs::test_empty_key_exits_1` | Dropped without a corpus successor — no case passes `=value`, so the distinct `error: empty key in pair` branch (exit 1) is unasserted after deletion. Flagged to the runner as a coverage gap. |
| `TestParsePairs::test_no_equals_exits_1` | `malformed-pair-exits-1.txtar` |
| `TestInterpolate::test_datetime_macro` | `macro-rendered-date-stays-a-string.txtar` |
| `TestInterpolate::test_date_macro` | `macro-rendered-date-stays-a-string.txtar` |
| `TestInterpolate::test_stubbed_macro_is_not_executed` | `stubbed-macro-value-lands-typed.txtar` |
| `TestInterpolate::test_unknown_macro_path_exits_non_zero` | `unknown-macro-path-exits-2.txtar` |
| `TestInterpolate::test_malformed_jinja_exits_non_zero` | `malformed-jinja-value-exits-2.txtar` |
| `TestInterpolate::test_git_commit_macro_runs_against_the_repo_dir` | Dropped by plan decision — the live-git macro against the real checkout is consciously abandoned; real macro execution is covered by `real-macro-command-output-is-written.txtar` (M02/2.3). |
| `TestInterpolate::test_retired_head_token_is_a_literal` | `quotes-syntax-sensitive-string-values.txtar` (`lead=@lead` — an `@`-prefixed value stays a literal string) |
| `TestInterpolate::test_literal_value` | `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate::test_literal_value_with_spaces_untouched` | `keeps-a-partly-numeric-value-a-plain-string.txtar` (`summary=23 things`) |
| `TestInterpolate::test_at_sign_prefix_not_interpolated` | `quotes-syntax-sensitive-string-values.txtar` (`lead=@lead`) |
| `TestInterpolate::test_retired_now_token_is_a_literal` | `quotes-syntax-sensitive-string-values.txtar` (`lead=@lead`) |
| `TestHookTokenising::test_quoted_macro_expression_survives_shlex` | Dropped deliberately — exercises `playbook_transition.dispatch_frontmatter_update`, whose coverage lives in `tests/commands/playbook_transition_test.py::test_file_target_hook_interpolates_instance`. |
| `TestHookTokenising::test_file_target_with_quoted_macro_expression` | Dropped deliberately — exercises `playbook_transition.dispatch_frontmatter_update`, whose coverage lives in `tests/commands/playbook_transition_test.py::test_file_target_hook_updates_sibling_file`. |
| `TestScalarTyping::test_scalar_lands_typed[integer]` | `coerces-an-integer-value.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[float]` | `coerces-a-float-value.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[null]` | `coerces-a-null-value.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[boolean]` | `coerces-a-boolean-value.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[partly-numeric]` | `keeps-a-partly-numeric-value-a-plain-string.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[yaml-1-1-boolean-word]` | `quotes-a-yaml-1-1-boolean-word.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[@lead]` | `quotes-syntax-sensitive-string-values.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[*star]` | `quotes-syntax-sensitive-string-values.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[&anchor]` | `quotes-syntax-sensitive-string-values.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[!bang]` | `quotes-syntax-sensitive-string-values.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[%pct]` | `quotes-syntax-sensitive-string-values.txtar` |
| ``TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[`tick]`` | `quotes-syntax-sensitive-string-values.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[a: b]` | `quotes-syntax-sensitive-string-values.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[ padded ]` | `quotes-syntax-sensitive-string-values.txtar` |
| `TestScalarTyping::test_macro_rendered_date_stays_a_string` | `macro-rendered-date-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI::test_sets_planned_with_date_macro` | `macro-rendered-date-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI::test_sets_commit_with_the_git_macro` | Dropped by plan decision — the live-git macro is consciously abandoned; real macro execution is covered by `real-macro-command-output-is-written.txtar` (M02/2.3). |
| `TestFrontmatterUpdateCLI::test_sets_created_with_date_macro` | `macro-rendered-date-stays-a-string.txtar` |
| `TestFrontmatterUpdateCLI::test_literal_value` | `sets-a-key-with-a-literal-value.txtar` |
| `TestFrontmatterUpdateCLI::test_missing_plan_exits_1` | `missing-plan-file-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_malformed_pair_exits_1` | `malformed-pair-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_preserves_other_keys_and_body` | `preserves-other-keys-and-body.txtar` |
| `TestFrontmatterUpdateCLI::test_multiple_keys_at_once` | `sets-multiple-keys-in-one-call.txtar` |
| `TestFrontmatterUpdateCLI::test_remove_key_and_add_empty` | `remove-drops-a-key.txtar` for the removal plus untouched keys and body; its two extra assertions — setting an empty value (`summary=`) and a trailing `# keep` comment surviving the rewrite — are dropped without a corpus successor. Flagged to the runner as a coverage gap. |
| `TestFrontmatterUpdateCLI::test_remove_only_no_pairs` | `remove-drops-a-key.txtar` |
| `TestFrontmatterUpdateCLI::test_nothing_to_do_exits_1` | `nothing-to-do-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_append_creates_list_on_null_key` | `append-creates-a-list-on-a-null-key.txtar` |
| `TestFrontmatterUpdateCLI::test_append_creates_list_on_absent_key` | `append-creates-a-list-on-an-absent-key.txtar` |
| `TestFrontmatterUpdateCLI::test_append_extends_existing_list` | `append-extends-an-existing-list.txtar` |
| `TestFrontmatterUpdateCLI::test_append_is_idempotent` | `repeated-append-is-idempotent.txtar` |
| `TestFrontmatterUpdateCLI::test_append_onto_scalar_exits_1` | `append-onto-a-scalar-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_append_alongside_pairs_and_removals` | `combines-pairs-removals-and-appends.txtar` |
| `TestFrontmatterUpdateCLI::test_append_only_still_reports_nothing_to_do_when_empty` | `nothing-to-do-exits-1.txtar` — no distinct CLI surface; empty `--append` invokes the CLI identically to the nothing-to-do path. |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[changed-value]` | `prints-a-unified-diff-on-stdout.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[append]` | `append-extends-an-existing-list.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[removal]` | `remove-drops-a-key.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing]` | `second-identical-call-prints-no-diff.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing]` | `repeated-append-is-idempotent.txtar` |
| `TestFrontmatterUpdateCLI::test_summary_stays_on_stderr` | `summary-goes-to-stderr-not-stdout.txtar` |
| `TestFrontmatterUpdateCLI::test_logs_to_booping_log` | `logs-one-line-when-a-vault-is-attached.txtar` |
| `TestFrontmatterUpdateCLI::test_does_not_write_to_real_home` | Dropped deliberately — home isolation is structural in the corpus: `e2e/conftest.py` maps `HOME`/`XDG_CONFIG_HOME` onto the per-case `home`/`xdg` roots, and `logs-one-line-when-a-vault-is-attached.txtar` asserts the log write lands under that mapped home. |
