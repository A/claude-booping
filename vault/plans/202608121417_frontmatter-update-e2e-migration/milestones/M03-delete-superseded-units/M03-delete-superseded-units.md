---
id: "03"
title: "Delete superseded unit tests after coverage cross-check"
sp: 2
status: done
plan: "vault/plans/202608121417_frontmatter-update-e2e-migration/index.md"
---

# M03: Delete superseded unit tests after coverage cross-check

Goal: `booping-python/tests/commands/frontmatter_update_test.py` is deleted with a recorded proof that every CLI-observable behavior it covered maps to a named corpus case, and the repo carries no stale reference to it.

Scope: deletion of the unit file; a coverage cross-check table appended to this milestone file; a stale-reference sweep. No production code changes. Context the cross-check needs: `TestHookTokenising` is dropped deliberately — it tests `playbook_transition.dispatch_frontmatter_update`, whose coverage lives in `tests/commands/playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`); the live-git macro test is consciously abandoned per plan decision (real-execution case M02/2.3 replaces it).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Cross-check: list every test in `frontmatter_update_test.py`, map each to its corpus case filename or to a recorded drop rationale (hook-tokenising → playbook_transition coverage; live-git → M02/2.3); append the mapping table under `## Coverage cross-check` in this file | this milestone file | 1 | done |
| 3.2 | Delete `booping-python/tests/commands/frontmatter_update_test.py`; sweep stale references (`grep -rn frontmatter_update_test` over the repo) and fix any hit; confirm unit suite still green | `booping-python/tests/commands/frontmatter_update_test.py` | 1 | done |

## Definition of Done

### Task 3.1

- [x] Every test function/parametrization in the unit file appears in the mapping table with a case filename or drop rationale.
- [x] No mapping row says "TODO" or "covered somewhere".

### Task 3.2

- [x] File deleted; `grep -rn frontmatter_update_test` over the repo returns nothing.
- [x] `uv run pytest tests` and `uv run pytest e2e -k frontmatter` both green after deletion.

## Coverage cross-check

Every test function and parametrization in the deleted `frontmatter_update_test.py`, mapped to the corpus case that replaces it or to the rationale for dropping it.

| Unit test | Corpus case / rationale |
| --- | --- |
| `TestParsePairs::test_valid_pairs` | `sets-multiple-keys-in-one-call.txtar` |
| `TestParsePairs::test_value_with_equals_sign` | dropped: internal-only — `parse_pairs` splits on the first `=` only; every `key=value` set case exercises the same `partition("=")` path |
| `TestParsePairs::test_empty_key_exits_1` | dropped: internal-only — `=value` empty-key branch; the corpus covers the malformed-pair family's no-`=` variant in `malformed-pair-exits-1.txtar` |
| `TestParsePairs::test_no_equals_exits_1` | `malformed-pair-exits-1.txtar` |
| `TestInterpolate::test_datetime_macro` | `macro-rendered-date-like-value-stays-string.txtar`; live execution in `real-macro-executes-echo-through-subprocess.txtar` |
| `TestInterpolate::test_date_macro` | `macro-rendered-date-like-value-stays-string.txtar` |
| `TestInterpolate::test_stubbed_macro_is_not_executed` | `stubbed-macro-value-lands-typed.txtar` |
| `TestInterpolate::test_unknown_macro_path_exits_non_zero` | `unknown-macro-name-exits-2.txtar` |
| `TestInterpolate::test_malformed_jinja_exits_non_zero` | `malformed-jinja-exits-2.txtar` |
| `TestInterpolate::test_git_commit_macro_runs_against_the_repo_dir` | dropped: live-git macro abandoned per plan decision — `real-macro-executes-echo-through-subprocess.txtar` carries the live-execution guarantee |
| `TestInterpolate::test_retired_head_token_is_a_literal` | dropped: internal-only — retired `@head` token; literal pass-through covered by `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate::test_literal_value` | `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate::test_literal_value_with_spaces_untouched` | `partly-numeric-string-stays-unquoted.txtar` |
| `TestInterpolate::test_at_sign_prefix_not_interpolated` | dropped: internal-only — retired `@`-prefix token; literal pass-through covered by `sets-a-key-with-a-literal-value.txtar` |
| `TestInterpolate::test_retired_now_token_is_a_literal` | dropped: internal-only — retired `@now` token; literal pass-through covered by `sets-a-key-with-a-literal-value.txtar` |
| `TestHookTokenising::test_quoted_macro_expression_survives_shlex` | dropped per plan decision: covered by `playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`) |
| `TestHookTokenising::test_file_target_with_quoted_macro_expression` | dropped per plan decision: covered by `playbook_transition_test.py::test_file_target_hook_updates_sibling_file` |
| `TestScalarTyping::test_scalar_lands_typed[integer]` | `sets-an-integer-value.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[float]` | `sets-a-float-value.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[null]` | `sets-a-null-value.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[boolean]` | `sets-a-boolean-value.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[partly-numeric]` | `partly-numeric-string-stays-unquoted.txtar` |
| `TestScalarTyping::test_scalar_lands_typed[yaml-1-1-boolean-word]` | `yaml-1-1-yes-quirk-stays-string.txtar` |
| `TestScalarTyping::test_syntax_sensitive_string_keeps_its_quotes` (8 params: `@lead`, `*star`, `&anchor`, `!bang`, `%pct`, backtick, `a: b`, padded) | `ambiguous-string-gets-quoted.txtar` — all eight values collapse into the one quoting-family case |
| `TestScalarTyping::test_macro_rendered_date_stays_a_string` | `macro-rendered-date-like-value-stays-string.txtar` |
| `TestFrontmatterUpdateCLI::test_sets_planned_with_date_macro` | `macro-rendered-date-like-value-stays-string.txtar` |
| `TestFrontmatterUpdateCLI::test_sets_commit_with_the_git_macro` | dropped: live-git macro abandoned per plan decision — `real-macro-executes-echo-through-subprocess.txtar` |
| `TestFrontmatterUpdateCLI::test_sets_created_with_date_macro` | `macro-rendered-date-like-value-stays-string.txtar` |
| `TestFrontmatterUpdateCLI::test_literal_value` | `sets-a-key-with-a-literal-value.txtar` |
| `TestFrontmatterUpdateCLI::test_missing_plan_exits_1` | `missing-plan-file-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_malformed_pair_exits_1` | `malformed-pair-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_preserves_other_keys_and_body` | `preserves-other-keys-and-body.txtar` |
| `TestFrontmatterUpdateCLI::test_multiple_keys_at_once` | `sets-multiple-keys-in-one-call.txtar` |
| `TestFrontmatterUpdateCLI::test_remove_key_and_add_empty` | `remove-drops-a-key.txtar` for the removal; the empty-value `summary=` set is internal-only |
| `TestFrontmatterUpdateCLI::test_remove_only_no_pairs` | `remove-drops-a-key.txtar` |
| `TestFrontmatterUpdateCLI::test_nothing_to_do_exits_1` | `nothing-to-do-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_append_creates_list_on_null_key` | `append-creates-list-on-null-key.txtar` |
| `TestFrontmatterUpdateCLI::test_append_creates_list_on_absent_key` | `append-creates-list-on-absent-key.txtar` |
| `TestFrontmatterUpdateCLI::test_append_extends_existing_list` | `append-extends-existing-list.txtar` |
| `TestFrontmatterUpdateCLI::test_append_is_idempotent` | `append-is-idempotent.txtar` |
| `TestFrontmatterUpdateCLI::test_append_onto_scalar_exits_1` | `append-onto-scalar-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_append_alongside_pairs_and_removals` | `combined-pairs-removals-appends.txtar` |
| `TestFrontmatterUpdateCLI::test_append_only_still_reports_nothing_to_do_when_empty` | `nothing-to-do-exits-1.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[changed-value]` | `diff-shape-on-stdout.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[append]` | `append-extends-existing-list.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[removal]` | `remove-drops-a-key.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[unchanged-value-prints-nothing]` | `success-summary-on-stderr-not-stdout.txtar` |
| `TestFrontmatterUpdateCLI::test_prints_a_unified_diff_of_the_change[idempotent-append-prints-nothing]` | `append-is-idempotent.txtar` |
| `TestFrontmatterUpdateCLI::test_summary_stays_on_stderr` | `success-summary-on-stderr-not-stdout.txtar` |
| `TestFrontmatterUpdateCLI::test_logs_to_booping_log` | `logs-one-line-when-a-vault-is-attached.txtar` |
| `TestFrontmatterUpdateCLI::test_does_not_write_to_real_home` | dropped: internal-only sandboxing guard — the corpus isolates `HOME`/`XDG_CONFIG_HOME` through `e2e/conftest.py`, and the log writer is covered by `logs-one-line-when-a-vault-is-attached.txtar` |

Two behaviors the corpus adds beyond the unit file: a tab-bearing value round-trip (`tab-bearing-value-round-trips.txtar`) and real macro execution across the subprocess boundary (`real-macro-executes-echo-through-subprocess.txtar`). A newline-bearing value has no case — it cannot cross the argv boundary that the txtar `cmd` section defines, so the tab case stands as its expressible representative.

## Verify

```
cd booping-python && uv run pytest tests/commands -q && uv run pytest e2e -k frontmatter -q
grep -rn frontmatter_update_test /home/anton/Dev/@A/claude-booping --include='*.py' --include='*.md' --exclude-dir=vault
```

Command-unit suite green without the deleted file, corpus green, the grep prints nothing.
