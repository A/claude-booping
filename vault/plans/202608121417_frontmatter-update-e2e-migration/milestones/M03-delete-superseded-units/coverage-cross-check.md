# Coverage cross-check

| Unit test | Corpus case / Drop rationale | Note |
| --- | --- | --- |
| TestParsePairs::test_valid_pairs | sets-a-key-with-a-literal-value.txtar | CLI sets `status=ready` end-to-end; pair parsing is exercised on every set case |
| TestParsePairs::test_value_with_equals_sign | dropped: internal-only — no corpus case sets a value containing `=` | `parse_pairs` first-`=` split contract is exercised by every set case; closest CLI contract line is sets-a-key-with-a-literal-value.txtar |
| TestParsePairs::test_empty_key_exits_1 | dropped: internal-only — no corpus case passes an empty-key `=value` pair | malformed-pair exit 1 with the pair quoted on stderr is covered by a-malformed-pair-is-rejected.txtar, which the empty-key branch shares |
| TestParsePairs::test_no_equals_exits_1 | a-malformed-pair-is-rejected.txtar | `statusready` (no `=`) → exit 1, pair quoted on stderr |
| TestInterpolate::test_datetime_macro | a-date-like-macro-value-stays-a-string.txtar | `core.macros.date` runs and its output lands in the file |
| TestInterpolate::test_date_macro | a-date-like-macro-value-stays-a-string.txtar | same declared `date` macro |
| TestInterpolate::test_stubbed_macro_is_not_executed | a-stubbed-macro-value-lands-typed.txtar | stubbed macro is not executed; stub value lands |
| TestInterpolate::test_unknown_macro_path_exits_non_zero | an-unknown-macro-name-exits-2.txtar | `core.macros.nope` → exit 2, path named on stderr, no traceback |
| TestInterpolate::test_malformed_jinja_exits_non_zero | a-malformed-jinja-value-exits-2.txtar | `{{ macro( }}` → exit 2, value + template error on stderr |
| TestInterpolate::test_git_commit_macro_runs_against_the_repo_dir | dropped: live-git test consciously abandoned per plan decision | real-execution case a-declared-macro-runs-and-lands-its-output.txtar (M02/2.3) replaces it |
| TestInterpolate::test_retired_head_token_is_a_literal | dropped: internal-only — `@head` was retired and is never interpolated | CLI-observable behavior is "plain literal value", covered by sets-a-key-with-a-literal-value.txtar |
| TestInterpolate::test_literal_value | sets-a-key-with-a-literal-value.txtar | literal lands unchanged |
| TestInterpolate::test_literal_value_with_spaces_untouched | sets-a-key-with-a-literal-value.txtar | literal round-trips through the same set path |
| TestInterpolate::test_at_sign_prefix_not_interpolated | dropped: internal-only — `@`-prefixed non-tokens pass through untouched | CLI-observable behavior is "plain literal value", covered by sets-a-key-with-a-literal-value.txtar |
| TestInterpolate::test_retired_now_token_is_a_literal | dropped: internal-only — `@now` was retired and is never interpolated | CLI-observable behavior is "plain literal value", covered by sets-a-key-with-a-literal-value.txtar |
| TestHookTokenising::test_quoted_macro_expression_survives_shlex | dropped: tests `playbook_transition.dispatch_frontmatter_update`, not this CLI | coverage lives in tests/commands/playbook_transition_test.py (test_file_target_hook_updates_sibling_file, test_file_target_hook_interpolates_instance) |
| TestHookTokenising::test_file_target_with_quoted_macro_expression | dropped: tests `playbook_transition.dispatch_frontmatter_update`, not this CLI | coverage lives in tests/commands/playbook_transition_test.py (test_file_target_hook_updates_sibling_file, test_file_target_hook_interpolates_instance) |
| TestScalarTyping::test_scalar_lands_typed[integer] | an-int-value-lands-unquoted.txtar | `sp=23` lands unquoted, reloads as int |
| TestScalarTyping::test_scalar_lands_typed[float] | a-float-value-lands-unquoted.txtar | `ratio=1.5` lands unquoted, reloads as float |
| TestScalarTyping::test_scalar_lands_typed[null] | a-null-spelling-lands-as-null.txtar | `retro=null` lands as unquoted null |
| TestScalarTyping::test_scalar_lands_typed[boolean] | a-bool-value-lands-unquoted.txtar | `blocked=true` lands unquoted, reloads as bool |
| TestScalarTyping::test_scalar_lands_typed[partly-numeric] | dropped: no dedicated case for a string that merely starts with digits | the string-quoting round-trip concern it guards is covered by a-tab-bearing-value-round-trips.txtar and an-ambiguous-string-gets-single-quoted.txtar |
| TestScalarTyping::test_scalar_lands_typed[yaml-1-1-boolean-word] | a-yaml-1-1-yes-stays-a-string.txtar | `summary=yes` single-quoted, reloads as string |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[@lead] | dropped: internal-only — no corpus case sets an `@`-prefixed value | the quote-decision pattern it guards (special-char values reload byte-identically) is covered by a-tab-bearing-value-round-trips.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[*star] | dropped: internal-only — no corpus case sets a `*`-prefixed value | quote-decision pattern covered by a-tab-bearing-value-round-trips.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[&anchor] | dropped: internal-only — no corpus case sets an `&`-prefixed value | quote-decision pattern covered by a-tab-bearing-value-round-trips.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[!bang] | dropped: internal-only — no corpus case sets a `!`-prefixed value | quote-decision pattern covered by a-tab-bearing-value-round-trips.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[%pct] | dropped: internal-only — no corpus case sets a `%`-prefixed value | quote-decision pattern covered by a-tab-bearing-value-round-trips.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[`tick] | dropped: internal-only — no corpus case sets a backtick-prefixed value | quote-decision pattern covered by a-tab-bearing-value-round-trips.txtar |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[a: b] | a-tab-bearing-value-round-trips.txtar | special-char + space value round-trips byte-identically through the same quoting path |
| TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes[ padded ] | a-tab-bearing-value-round-trips.txtar | whitespace-bearing value round-trips through the same quoting path |
| TestScalarTyping::test_macro_rendered_date_stays_a_string | a-date-like-macro-value-stays-a-string.txtar | macro-rendered date-like value reloads as a string |
| TestFrontmatterUpdateCLI::test_sets_planned_with_date_macro | a-date-like-macro-value-stays-a-string.txtar | `core.macros.date` set path |
| TestFrontmatterUpdateCLI::test_sets_commit_with_the_git_macro | dropped: live-git test consciously abandoned per plan decision | real-execution case a-declared-macro-runs-and-lands-its-output.txtar (M02/2.3) replaces it |
| TestFrontmatterUpdateCLI::test_sets_created_with_date_macro | a-date-like-macro-value-stays-a-string.txtar | `core.macros.date` set path |
| TestFrontmatterUpdateCLI::test_literal_value | sets-a-key-with-a-literal-value.txtar | `status=ready` replaces in place |
| TestFrontmatterUpdateCLI::test_missing_plan_exits_1 | a-missing-plan-file-is-rejected.txtar | exit 1, `error: plan not found` on stderr |
| TestFrontmatterUpdateCLI::test_malformed_pair_exits_1 | a-malformed-pair-is-rejected.txtar | exit 1, pair quoted on stderr |
| TestFrontmatterUpdateCLI::test_preserves_other_keys_and_body | preserves-other-keys-and-body-when-setting-one-key.txtar | other keys + body byte-for-byte intact |
| TestFrontmatterUpdateCLI::test_multiple_keys_at_once | sets-multiple-keys-in-one-call.txtar | `status=ready sp=13` in one call |
| TestFrontmatterUpdateCLI::test_remove_key_and_add_empty | a-remove-only-call-drops-the-key.txtar | removal half: key dropped, rest byte-intact incl. inline comment; empty-set half covered by sets-a-key-with-a-literal-value.txtar |
| TestFrontmatterUpdateCLI::test_remove_only_no_pairs | a-remove-only-call-drops-the-key.txtar | `--remove business_goal` only |
| TestFrontmatterUpdateCLI::test_nothing_to_do_exits_1 | nothing-to-do-is-rejected.txtar | no args → exit 1, "nothing to do" |
| TestFrontmatterUpdateCLI::test_append_creates_list_on_null_key | an-append-creates-a-list-on-a-null-key.txtar | append to `null` key |
| TestFrontmatterUpdateCLI::test_append_creates_list_on_absent_key | an-append-creates-a-list-on-an-absent-key.txtar | append to absent key → one-element list |
| TestFrontmatterUpdateCLI::test_append_extends_existing_list | an-append-extends-an-existing-list.txtar | `--append sessions=def-456` onto existing list |
| TestFrontmatterUpdateCLI::test_append_is_idempotent | an-identical-second-append-prints-no-diff.txtar | second identical append is a no-op |
| TestFrontmatterUpdateCLI::test_append_onto_scalar_exits_1 | an-append-onto-a-scalar-key-is-rejected.txtar | exit 1, key named, file untouched |
| TestFrontmatterUpdateCLI::test_append_alongside_pairs_and_removals | an-append-combined-with-pairs-and-removals.txtar | one call with `--remove`, pairs and `--append` |
| TestFrontmatterUpdateCLI::test_append_only_still_reports_nothing_to_do_when_empty | nothing-to-do-is-rejected.txtar | empty call → exit 1, "nothing to do" |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[changed-value] | stdout-carries-the-unified-diff.txtar | unified diff `---`/`+++`/`@@` on stdout |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[append] | stdout-carries-the-unified-diff.txtar | unified diff on stdout |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[removal] | stdout-carries-the-unified-diff.txtar | unified diff on stdout; file effect of the removal is a-remove-only-call-drops-the-key.txtar |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing] | a-second-identical-call-prints-no-diff.txtar | no-op change prints no diff |
| TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing] | an-identical-second-append-prints-no-diff.txtar | second identical append prints no diff |
| TestFrontmatterUpdateCLI::test_summary_stays_on_stderr | the-success-summary-goes-to-stderr.txtar | summary on stderr, stdout clean |
| TestFrontmatterUpdateCLI::test_logs_to_booping_log | logs-one-line-when-a-vault-is-attached.txtar | exactly one `[frontmatter-update]` line in vault `.booping.log` |
| TestFrontmatterUpdateCLI::test_does_not_write_to_real_home | dropped: internal-only — environmental guard against touching the developer's real `~/Claude` | no corpus case can assert a real-home path stays absent; the log-write contract it protects is covered by logs-one-line-when-a-vault-is-attached.txtar |
