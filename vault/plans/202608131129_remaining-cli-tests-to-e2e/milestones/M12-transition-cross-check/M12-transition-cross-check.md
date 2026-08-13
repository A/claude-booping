---
id: "12"
title: "playbook-transition cross-check and unit deletion"
sp: 2
status: done
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M12: playbook-transition cross-check and unit deletion

Every test in `tests/commands/playbook_transition_test.py` maps to a named corpus case or a recorded drop; then the file is deleted, with its fixture tree left in place for its other consumers.

**Scope**: closing the `playbook-transition` half and the sprint. Files: deleted `booping-python/tests/commands/playbook_transition_test.py`; new gap cases under `booping-python/e2e/cases/playbook-transition/`. `tests/__fixtures__/playbook-transition-home/` is **kept** — `tests/commands/playbook_state_test.py` and `tests/commands/playbook_run_integration_test.py` both plant from it and are out of this plan's scope.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 12.1 | Build the cross-check table over all 46 tests — case that replaces it, milestone that wrote it, or a one-line drop reason — and write any case it exposes as missing | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | done |
| 12.2 | Delete the unit file, confirm the fixture tree's remaining consumers still pass, and record the table in the milestone body and the commit message | `booping-python/tests/commands/playbook_transition_test.py` | 1 | done |

## Definition of Done

### Task 12.1

- [x] The table has one row per test function — 46 rows, verified mechanically: the row count equals `git show HEAD:booping-python/tests/commands/playbook_transition_test.py | grep -c '^def test_'`, and every test name from that listing appears verbatim in a row. Both comparisons are re-run after deletion, against `git show`, and pasted into the commit message.
- [x] Every row names an existing `.txtar` file or a drop reason naming the file and test that covers it instead; `test_cli_end_to_end` is mapped to the corpus case that subsumes it.
- [x] Any behaviour with no case gets one written here; any bug the porting exposes is recorded in this milestone body and left unfixed.

### Task 12.2

- [x] `tests/commands/playbook_transition_test.py` is deleted and `rg -n "playbook_transition_test" booping-python` returns nothing.
- [x] `tests/__fixtures__/playbook-transition-home/` still exists, and `uv run pytest tests/commands/playbook_state_test.py tests/commands/playbook_run_integration_test.py` passes.
- [x] The cross-check table is committed — in this milestone file and referenced from the commit message.

## Cross-check

`git show HEAD:booping-python/tests/commands/playbook_transition_test.py | grep -c '^def test_'` → **46**, one row each below.

Case paths are relative to `booping-python/e2e/cases/playbook-transition/`.

| # | test | replaced by / drop reason | written by |
| --- | --- | --- | --- |
| 1 | `test_bootstrap_creates_artifact_and_reports` | `bootstrap-creates-the-artifact-and-reports-it.txtar` | M09 |
| 2 | `test_bootstrap_creates_parent_dirs` | `a-nested-artifact-path-creates-its-parent-directories.txtar` | M09 |
| 3 | `test_missing_artifact_with_non_initial_target_exits_1` | `a-missing-artifact-with-a-non-initial-target-is-rejected.txtar` | M09 |
| 4 | `test_instance_required_for_instance_artifact` | `an-instance-machine-without-instance-is-rejected.txtar` | M09 |
| 5 | `test_instance_rejected_for_plain_artifact` | `an-instance-on-a-plain-machine-is-rejected.txtar` | M09 |
| 6 | `test_illegal_edge_exits_1_listing_allowed_targets` | `an-illegal-edge-lists-the-allowed-targets.txtar` | M09 |
| 7 | `test_idempotent_rerun_skips_edge_hooks` | `re-running-the-same-edge-is-idempotent.txtar` | M09 |
| 8 | `test_degenerate_artifact_without_frontmatter_exits_1` | `an-artifact-without-a-frontmatter-block-is-rejected.txtar` | M09 |
| 9 | `test_degenerate_artifact_without_status_key_exits_1` | `an-artifact-without-a-status-key-is-rejected.txtar` | M09 |
| 10 | `test_workdir_defaults_to_cwd` | `the-workdir-defaults-to-the-invocation-directory.txtar` | M09 |
| 11 | `test_unknown_playbook_exits_1` | `an-unknown-playbook-is-rejected.txtar` | M09 |
| 12 | `test_unknown_state_exits_1` | `an-unknown-state-is-rejected.txtar` | M09 |
| 13 | `test_playbook_without_states_exits_1` | `a-playbook-without-states-is-rejected.txtar` | M09 |
| 14 | `test_report_lines_for_a_normal_move` | `a-move-reports-the-edge-and-one-frontmatter-line-per-key.txtar` | M09 |
| 15 | `test_script_hook_env_and_cwd` | `a-script-hook-sees-the-artifact-workdir-and-cwd.txtar` | M10 |
| 16 | `test_script_hook_receives_instance_slug` | `a-script-hook-on-an-instance-machine-receives-the-slug.txtar` | M10 |
| 17 | `test_failing_script_hook_exits_2_and_relays_stderr` | `a-failing-script-hook-relays-its-stderr.txtar` | M10 |
| 18 | `test_unknown_hook_exits_2` | `an-unknown-hook-verb-is-rejected.txtar` | M10 |
| 19 | `test_instance_artifact_path_interpolated_and_moved` | `an-instance-artifact-is-interpolated-and-moved.txtar` | M09 |
| 20 | `test_script_hook_falls_back_to_a_discovery_root` | `a-script-falls-back-past-a-root-that-lacks-it.txtar` | M10 |
| 21 | `test_script_hook_passes_trailing_tokens_as_argv` | `a-script-hook-receives-trailing-tokens-as-argv.txtar` | M10 |
| 22 | `test_playbook_dir_script_shadows_the_root_copy` | `a-playbook-local-script-shadows-the-root-copy.txtar` | M10 |
| 23 | `test_root_script_used_when_the_playbook_carries_none` | `a-root-script-runs-when-the-playbook-carries-none.txtar` | M10 |
| 24 | `test_missing_script_names_every_probed_path` | `a-missing-script-names-every-probed-path.txtar` | M10 |
| 25 | `test_file_target_hook_updates_sibling_file` | `a-frontmatter-update-file-target-writes-a-sibling-file.txtar` | M10 |
| 26 | `test_file_target_hook_interpolates_instance` | `an-instance-file-target-is-interpolated.txtar` | M10 |
| 27 | `test_file_target_instance_without_instance_exits_2` | `an-instance-file-target-without-an-instance-is-rejected.txtar` | M10 |
| 28 | `test_file_target_missing_file_exits_2` | `a-missing-frontmatter-update-target-is-rejected.txtar` | M10 |
| 29 | `test_file_target_without_frontmatter_block_bootstraps_one` | `a-target-without-frontmatter-gains-a-block.txtar` | M10 |
| 30 | `test_no_target_hook_still_targets_the_artifact` | `a-frontmatter-update-hook-without-a-target-writes-the-artifact.txtar` | M10 |
| 31 | `test_cli_end_to_end` | subsumed by `bootstrap-creates-the-artifact-and-reports-it.txtar` — it asserts the same bootstrap through `bin/booping`, which is how the corpus runner invokes *every* case, so the whole directory is the binary-boundary test | M09 |
| 32 | `test_relative_target_overrides_the_declared_artifact` | `a-relative-target-overrides-the-declared-artifact.txtar` | M11 |
| 33 | `test_absolute_target_is_honoured` | `an-absolute-target-is-honoured-as-given.txtar` | M11 |
| 34 | `test_target_bootstraps_a_missing_file_at_the_initial_status` | `a-missing-target-is-bootstrapped-at-the-initial-status.txtar` | M11 |
| 35 | `test_target_bootstrap_rejects_a_non_initial_status` | `a-missing-target-with-a-non-initial-status-is-rejected.txtar` | M11 |
| 36 | `test_target_and_instance_together_exit_1` | `a-target-with-an-instance-is-rejected.txtar` | M11 |
| 37 | `test_hooks_receive_the_resolved_target_as_booping_artifact` | `hooks-under-a-target-address-the-resolved-target.txtar` | M11 |
| 38 | `test_absolute_target_implies_the_workdir` | `an-absolute-target-implies-its-workdir.txtar` | M11 |
| 39 | `test_explicit_workdir_wins_over_the_implied_one` | `an-explicit-workdir-beats-the-one-a-target-implies.txtar` | M11 |
| 40 | `test_absolute_target_off_the_declared_artifact_keeps_cwd` | `an-absolute-target-off-the-declared-artifact-keeps-the-invocation-directory.txtar` | M11 |
| 41 | `test_relative_target_is_not_re_anchored_under_an_implied_workdir` | `a-relative-target-is-never-re-anchored-under-an-implied-workdir.txtar` | M11 |
| 42 | `test_machine_without_artifact_requires_target` | `a-machine-without-an-artifact-requires-a-target.txtar` | M11 |
| 43 | `test_machine_without_artifact_moves_with_target` | `a-machine-without-an-artifact-moves-with-a-target.txtar` | M11 |
| 44 | `test_bootstrap_stamps_status_onto_an_existing_file` | `an-existing-target-is-stamped-without-losing-its-keys-or-body.txtar` | M11 |
| 45 | `test_existing_file_without_status_refuses_a_non_initial_target` | `an-existing-target-without-a-status-refuses-a-non-initial-status.txtar` — gap case written in this milestone; M11 recorded the drift, its `a-missing-artifact-with-a-non-initial-target-is-rejected.txtar` covers only the missing-file variant | M12 |
| 46 | `test_bootstrap_creates_a_frontmatter_block_when_the_file_has_none` | `a-target-with-no-frontmatter-block-gains-one.txtar` | M11 |

No drops and one gap case (row 45). Three corpus cases have no unit ancestor — `a-missing-workdir-is-rejected.txtar` (M09), `a-non-executable-script-is-rejected.txtar` and `a-script-hook-runs-and-reports-ok.txtar` (M10) — behaviours the units never pinned. No bug was exposed by the port.

## Verify

```
cd booping-python && uv run pytest e2e -k playbook-transition -q && uv run pytest tests/commands/playbook_state_test.py tests/commands/playbook_run_integration_test.py -q && rg -n "playbook_transition_test" . ; echo "rg exit: $?"
```

The corpus passes, the fixture tree's remaining consumers pass, and `rg` exits 1 — no reference to the deleted file survives.
