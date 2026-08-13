---
id: "10"
title: "corpus cross-check and tier audit"
sp: 2
status: done
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M10: corpus cross-check and tier audit

Every deleted test is accounted for, the corpus README records the rules this migration relied on, and the whole gate runs green.

**Scope**: the migration's closing audit. Files: edited `booping-python/e2e/README.md`; this milestone file, which carries the cross-check tables. No case or unit is written here — anything the audit finds missing is a case added under the milestone that owns it.

Depends on every other milestone.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 10.1 | Build the cross-check table with the columns `unit file`, `test name`, `replaced by`, `kind` — where `kind` is one of `case`, `surviving unit` or `dropped`, and `replaced by` names the `.txtar` path, the unit file, or the drop reason — sourcing its rows from `git show HEAD~N:<path>` for each deleted file so no test is missed from memory, then close any gap it exposes in the owning milestone | this milestone file | 1 | done |
| 10.2 | Record in `e2e/README.md` the two rules this migration ran on: shipped-content dependence limited to existence rather than extent, and the conditions under which a case legitimately omits its `stdout` section | `booping-python/e2e/README.md` | 1 | done |

## Definition of Done

### Task 10.1

- [x] Every one of the fourteen `render_test.py` tests appears in the table against a named case file.
- [x] Every one of the eighteen `playbook_state_test.py` tests and the one run-integration test appears against a named case file or the surviving `test_report_writes_nothing` unit.
- [x] Every `test_session_stats.py` test removed in M07 appears against a named case file, and the one recorded drop carries its reason. Amended during the sprint: M07 removed twelve, not fourteen — eleven CLI tests plus the recorded drop; this milestone's count and M07's own "thirteen CLI tests" prose were both off.
- [x] The `build_test.py` tests appear marked as dropped with the command's retirement as the reason.
- [x] No row is blank, and any gap the table exposed was closed by a case added under the milestone that owns that command.

### Task 10.2

- [x] `e2e/README.md` states that a case may depend on shipped plugin content only through its existence, never its extent, and gives the migration gate as the worked example.
- [x] It states that omitting a `stdout` section means unasserted rather than empty, names `debug-context` as the one command relying on that, and says a case doing so must comment why.
- [x] Neither addition restates the `pytest-txtar` case format, which the plugin's own README owns.

## Cross-check table

Case paths are relative to `booping-python/e2e/cases/`.

| unit file | test name | replaced by | kind |
| --- | --- | --- | --- |
| `tests/commands/render_test.py` | `test_render_resolves_relative_path_against_plugin_root_not_cwd` | `render/a-relative-path-resolves-against-the-plugin-root.txtar` | case |
| `tests/commands/render_test.py` | `test_render_set_override_wins_over_core_value` | `render/a-set-override-wins-over-the-core-config-value.txtar` | case |
| `tests/commands/render_test.py` | `test_render_set_override_repeated_pairs_later_wins` | `render/repeated-set-pairs-render-the-later-value.txtar` | case |
| `tests/commands/render_test.py` | `test_render_set_deep_merges_leaving_siblings` | `render/a-set-override-deep-merges-and-leaves-siblings-intact.txtar` | case |
| `tests/commands/render_test.py` | `test_render_macro_runs_a_core_declared_macro` | `render/an-unstubbed-macro-runs-and-its-stdout-lands-in-the-render.txtar` | case |
| `tests/commands/render_test.py` | `test_render_stub_macro_returns_the_literal` | `render/a-stubbed-macro-returns-the-literal-without-executing.txtar` | case |
| `tests/commands/render_test.py` | `test_render_stub_macro_key_may_carry_the_call_arguments` | `render/a-stub-key-may-carry-the-call-arguments.txtar` | case |
| `tests/commands/render_test.py` | `test_render_stub_macro_malformed_pair_exits_1` | `render/a-malformed-stub-macro-pair-is-rejected.txtar` | case |
| `tests/commands/render_test.py` | `test_render_set_malformed_pair_exits_1` | `render/a-malformed-set-pair-is-rejected.txtar` | case |
| `tests/commands/render_test.py` | `test_render_gates_a_behind_vault` | `render/a-behind-vault-gates-the-render-command.txtar` | case |
| `tests/commands/render_test.py` | `test_render_playbook_gates_a_behind_vault` | `render-playbook/a-behind-vault-gates-the-playbook-render.txtar` | case |
| `tests/commands/render_test.py` | `test_render_playbook_migrate_is_exempt_from_the_gate` | `render-playbook/the-migrate-playbook-is-exempt-from-the-gate.txtar` | case |
| `tests/commands/render_test.py` | `test_render_playbook_migrate_step_is_exempt_from_the_gate` | `render-playbook/a-migrate-step-fetch-is-exempt-from-the-gate.txtar` | case |
| `tests/commands/render_test.py` | `test_render_playbook_project_pins_the_marker_to_that_root` | `render-playbook/the-project-flag-pins-the-marker-to-that-root.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_missing_artifact_reports_not_started_with_bootstrap_edge` | `playbook-state/a-missing-artifact-reports-not-started-with-the-bootstrap-edge.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_outer_state_reports_status_and_next_edges` | `playbook-state/a-mid-run-status-reports-every-outgoing-edge-with-its-when-and-gates.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_terminal_status_has_no_next` | `playbook-state/a-terminal-status-omits-next.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_outer_state_is_reported_first` | `playbook-state/the-outer-state-is-reported-before-the-inner-one.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_instance_state_is_empty_before_any_instance_exists` | `playbook-state/a-per-instance-machine-with-no-instance-reports-an-empty-mapping.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_instances_keyed_by_slug_and_sorted` | `playbook-state/instances-are-keyed-by-slug-and-sorted.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_instance_key_is_what_the_placeholder_matched[flat]` | `playbook-state/a-flat-instance-path-keys-on-the-matched-filename-segment.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_instance_key_is_what_the_placeholder_matched[nested]` | `playbook-state/a-nested-instance-path-keys-on-the-matched-directory-segment.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_unknown_playbook_exits_1` | `playbook-state/an-unknown-playbook-lists-the-known-names.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_playbook_without_states_exits_1` | `playbook-state/a-playbook-with-no-states-block-is-refused.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_report_writes_nothing` | `booping-python/tests/commands/playbook_state_writes_nothing_test.py` | surviving unit |
| `tests/commands/playbook_state_test.py` | `test_workdir_defaults_to_cwd` | `playbook-state/an-omitted-workdir-reports-the-run-in-the-cwd.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_target_reports_that_files_frontier` | `playbook-state/a-relative-target-reports-that-files-frontier.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_absolute_target_is_honoured` | `playbook-state/an-absolute-target-is-honoured-as-given.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_missing_target_reports_not_started` | `playbook-state/a-target-naming-a-missing-file-reports-not-started.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_machine_without_artifact_needs_target` | `playbook-state/a-machine-without-an-artifact-refuses-without-a-target.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_machine_without_artifact_reports_with_target` | `playbook-state/a-machine-without-an-artifact-reports-with-a-target.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_existing_file_without_status_reports_not_started` | `playbook-state/frontmatter-without-a-status-key-reports-not-started.txtar` | case |
| `tests/commands/playbook_state_test.py` | `test_file_without_a_frontmatter_block_reports_not_started` | `playbook-state/an-artifact-with-no-frontmatter-block-reports-not-started.txtar` | case |
| `tests/commands/playbook_run_integration_test.py` | `test_full_run_walk` | `playbook-state/run-walk.txtar` | case |
| `tests/test_session_stats.py` | `test_directory_walks_by_mask_in_sorted_path_order` | `session-stats/a-directory-walks-artifacts-in-sorted-path-order.txtar` | case |
| `tests/test_session_stats.py` | `test_file_path_yields_one_entry_and_ignores_mask` | `session-stats/a-file-path-yields-one-entry-and-ignores-the-mask.txtar` | case |
| `tests/test_session_stats.py` | `test_artifact_without_sessions_key_is_skipped_with_a_stderr_note` | `session-stats/an-artifact-without-a-sessions-key-is-noted-and-left-out-of-the-report.txtar` | case |
| `tests/test_session_stats.py` | `test_stdout_is_json_only_while_warnings_go_to_stderr` | `session-stats/stdout-carries-one-json-document-while-notes-and-warnings-go-to-stderr.txtar` | case |
| `tests/test_session_stats.py` | `test_missing_path_exits_1` | `session-stats/a-path-that-does-not-exist-is-refused.txtar` | case |
| `tests/test_session_stats.py` | `test_mask_matching_nothing_exits_1` | `session-stats/a-mask-matching-nothing-under-a-real-directory-is-refused.txtar` | case |
| `tests/test_session_stats.py` | `test_fresh_artifact_gets_all_six_keys_and_reports_written` | `session-stats/a-fresh-artifact-gains-all-six-metrics-keys.txtar` | case |
| `tests/test_session_stats.py` | `test_rerun_without_force_is_a_byte_identical_skip` | `session-stats/an-already-stamped-artifact-is-reported-and-left-untouched.txtar` | case |
| `tests/test_session_stats.py` | `test_force_overwrites_existing_values` | `session-stats/force-overwrites-stale-metrics-with-fresh-ones.txtar` | case |
| `tests/test_session_stats.py` | `test_dry_run_matches_a_real_run_and_writes_nothing` | `session-stats/a-dry-run-alone-leaves-the-artifact-unstamped.txtar` + `session-stats/a-dry-run-then-a-wet-run-agree-on-the-totals.txtar` | case |
| `tests/test_session_stats.py` | `test_session_objects_use_the_frontmatter_key_names_verbatim` | `session-stats/a-fresh-artifact-gains-all-six-metrics-keys.txtar` | case |
| `tests/test_session_stats.py` | `test_cli_registers_session_stats_with_contract_defaults` | argparse-`Namespace` inspection producing no output; its four defaults are each exercised by a flag-omitting case (`mask` by the directory walk, `projects_root` by every default-root case, `force` by the already-stamped case, `dry_run` by the fresh-artifact case) | dropped |
| `tests/commands/build_test.py` | `test_build_writes_rendered_files` | `booping build` retired in M09 — no subcommand to pin | dropped |
| `tests/commands/build_test.py` | `test_build_is_idempotent` | `booping build` retired in M09 — no subcommand to pin | dropped |
| `tests/commands/build_test.py` | `test_build_missing_files_dir_exits_2` | `booping build` retired in M09 — no subcommand to pin | dropped |
### Gap cases with no unit ancestor

`render/an-absolute-path-renders-that-file-to-stdout`, `render/the-output-flag-writes-the-render-and-leaves-stdout-empty`, `render/without-a-set-override-the-render-shows-the-core-config-value`, `playbook-state/a-missing-workdir-is-refused`, `session-stats/an-explicit-mask-selects-what-the-default-mask-misses`, `session-stats/an-explicit-projects-root-overrides-the-home-default`, `session-stats/a-scalar-sessions-key-is-refused`, `session-stats/a-session-with-no-transcript-warns-and-the-run-continues`, `session-stats/an-artifact-whose-frontmatter-cannot-be-parsed-is-refused`, `session-stats/malformed-transcript-lines-are-counted-and-skipped`, and both `debug-context/` cases.

### Findings carried out of the sprint

- The plan's `## I/O contract` for `session-stats` is wrong: an artifact with no `sessions:` key is omitted from the `artifacts` array entirely; `skipped` is reserved for the already-stamped path. Pinned as shipped in M05, not fixed — behaviour fixes are out of scope.
- M09's sweep leaves one intentionally-stale match at `playbooks/groom/_specs/steps/research-codebase/index.md:70`, plus two live-docs follow-ups not edited: `vault/docs/_specs/features.md:21,51` still describes two-stage rendering and `vault/docs/_specs/roles.md:20` still names a build artefact.
- `resolve_target`'s `is_absolute()` guard is not independently observable, so the absolute-`--target` case pins the contract but cannot fail on that guard's removal alone (M03).

## Verify

```
cd booping-python && uv run pytest e2e --collect-only -q | tail -1 && rg -c "existence, never its extent|unasserted" e2e/README.md
```

The corpus collects every case the cross-check table names, and the README carries both recorded rules. The whole-repo gate for this sprint is `just ci`, which belongs to the plan's Final Verification and runs once there.
