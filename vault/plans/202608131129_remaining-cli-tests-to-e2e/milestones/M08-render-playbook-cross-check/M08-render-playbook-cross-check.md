---
id: "08"
title: "render-playbook cross-check and unit deletion"
sp: 3
status: in-progress
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M08: render-playbook cross-check and unit deletion

Every test in `tests/test_render_playbook.py` maps to a named corpus case or to a recorded, justified drop; then the file and its fixture tree are deleted.

**Scope**: closing the `render-playbook` half. Files: deleted `booping-python/tests/test_render_playbook.py` and `booping-python/tests/__fixtures__/render-playbook-home/`; new gap cases under `booping-python/e2e/cases/render-playbook/`; edited `booping-python/e2e/README.md`. The cross-check is the milestone's real work — deletion is what it authorises. `tests/__fixtures__/playbook-transition-home/` is untouched here.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Build the cross-check table: every one of the 131 tests against the case that replaces it, the milestone that wrote it, or a one-line reason it is dropped (covered by `tests/context/playbook_test.py`, or inexpressible in the sandbox). Write any case the table exposes as missing | `booping-python/e2e/cases/render-playbook/*.txtar` | 2 | pending |
| 8.2 | Delete `tests/test_render_playbook.py` and the `render-playbook-home` fixture tree, confirm no other consumer, and record the cross-check table in the milestone body and the commit message | `booping-python/tests/test_render_playbook.py`, `booping-python/tests/__fixtures__/render-playbook-home/`, `booping-python/e2e/README.md` | 1 | pending |

## Definition of Done

### Task 8.1

- [ ] The table has one row per test function in the file — 131 rows, and the count is verified mechanically, not by eye: the row count of the table equals `git show HEAD:booping-python/tests/test_render_playbook.py | grep -c '^def test_'`, and every test name from that same listing appears verbatim in a row. Both comparisons are run again after deletion, against `git show`, and their output is pasted into the commit message.
- [ ] Every row names either a `.txtar` case file that exists on disk, or a drop reason; no row is blank and none says "covered elsewhere" without naming the file and test.
- [ ] Any behaviour with no case gets one written in this milestone, in the case directory of the section it belongs to.
- [ ] A behaviour found to be untested before the migration is written as a gap case; any bug the porting exposes is recorded in this milestone body and left unfixed.

### Task 8.2

- [ ] `rg -n "render-playbook-home|test_render_playbook" booping-python` returns nothing outside the corpus and this plan.
- [ ] Both paths are deleted and `uv run pytest tests` passes.
- [ ] `just e2e` passes with the render-playbook case directory collected.
- [ ] `booping-python/e2e/README.md` gains the executable-hook `chmod` note only if M10 has already landed it; otherwise this milestone leaves the README alone.
- [ ] The cross-check table is committed — in this milestone file and referenced from the commit message.

## Cross-check

`git show HEAD:booping-python/tests/test_render_playbook.py | grep -c '^def test_'` → **120**, one row each below. (The plan's `index.md` says 131; that figure counted collected cases in an earlier revision of the file. 120 functions collect as 122 cases — `test_io_keys_are_never_rendered` is parametrized three ways. The mechanical count in the DoD is the authority.)

Case paths are relative to `booping-python/e2e/cases/render-playbook/`.

| # | test | replaced by / drop reason |
| --- | --- | --- |
| 1 | `test_section_order` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 2 | `test_verbatim_preamble_passes_through` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 3 | `test_no_notices_on_happy_path` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 4 | `test_graph_table_rows_in_dependency_order` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 5 | `test_graph_table_states_dependency_driven_ordering` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 6 | `test_detached_section_is_summary_then_delegation_order` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 7 | `test_detached_section_drops_deps_and_siblings` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 8 | `test_single_member_wave_has_after_no_parallel` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 9 | `test_summary_directive` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 10 | `test_summary_leads_the_delegation_order` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 11 | `test_model_detached_directive` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 12 | `test_named_detached_directive` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 13 | `test_gate_directive_verbatim` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 14 | `test_no_orphan_note_when_all_wired` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 15 | `test_missing_step_notice` | `a-graph-step-without-a-directory-blocks-the-render.txtar` |
| 16 | `test_unknown_dep_notice` | `an-unknown-dependency-blocks-the-render.txtar` |
| 17 | `test_cycle_notice` | `a-dependency-cycle-blocks-the-render.txtar` |
| 18 | `test_no_graph_notice` | `a-playbook-without-a-graph-blocks-the-render.txtar` |
| 19 | `test_inline_in_parallel_notice` | `a-non-detached-step-sharing-a-wave-blocks-the-render.txtar` |
| 20 | `test_legacy_agent_key_notice` | `the-renamed-agent-key-blocks-the-render.txtar` — gap case written in this milestone; M01–M07 left the `agent:` → `detached:` rename notice uncased |
| 21 | `test_orphan_note_non_blocking` | `an-unwired-step-directory-is-a-non-blocking-note.txtar` |
| 22 | `test_subgraph_happy_path_has_no_notices` | `a-subgraph-renders-as-a-tagged-row-group-an-intro-and-inner-sections.txtar` |
| 23 | `test_subgraph_key_is_not_missing` | `a-subgraph-renders-as-a-tagged-row-group-an-intro-and-inner-sections.txtar` |
| 24 | `test_missing_inner_step_dir_notice` | `a-subgraph-step-without-a-directory-blocks-the-render.txtar` |
| 25 | `test_inner_step_dir_is_not_an_orphan` | `an-inner-step-directory-is-not-an-orphan.txtar` |
| 26 | `test_unwired_step_dir_is_still_an_orphan` | `a-step-directory-wired-nowhere-is-an-orphan.txtar` |
| 27 | `test_inline_steps_sharing_an_inner_wave_notice` | `inline-steps-sharing-an-inner-wave-block-the-render.txtar` |
| 28 | `test_inline_inner_step_in_a_parallel_outer_wave_notice` | `an-inline-inner-step-in-a-parallel-outer-wave-blocks-the-render.txtar` |
| 29 | `test_inline_inner_step_alone_in_its_outer_wave_is_fine` | `an-inline-inner-step-alone-in-its-outer-wave-renders.txtar` |
| 30 | `test_parallel_wave_notice_is_not_repeated_per_scope` | `the-parallel-wave-notice-is-emitted-once-per-step.txtar` |
| 31 | `test_bad_node_notice` | `a-malformed-subgraph-node-blocks-the-render.txtar` |
| 32 | `test_bad_inner_node_notice_names_the_subgraph` | `a-malformed-inner-node-notice-names-its-subgraph.txtar` |
| 33 | `test_nested_subgraph_notice` | `a-nested-subgraph-blocks-the-render.txtar` |
| 34 | `test_duplicate_step_notice` | `a-step-name-in-two-scopes-blocks-the-render.txtar` |
| 35 | `test_inner_unknown_dep_notice_names_the_subgraph` | `an-inner-unknown-dependency-notice-names-its-subgraph.txtar` |
| 36 | `test_inner_cycle_notice_names_the_subgraph` | `an-inner-cycle-notice-names-its-subgraph.txtar` |
| 37 | `test_graph_table_carries_summary_and_gate` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 38 | `test_graph_table_lists_subgraph_then_its_inner_steps` | `a-subgraph-renders-as-a-tagged-row-group-an-intro-and-inner-sections.txtar` |
| 39 | `test_subgraph_section_order` | `a-subgraph-renders-as-a-tagged-row-group-an-intro-and-inner-sections.txtar` |
| 40 | `test_subgraph_intro_bullets` | `a-subgraph-renders-as-a-tagged-row-group-an-intro-and-inner-sections.txtar` |
| 41 | `test_subgraph_intro_without_repeat_has_no_repeat_bullet` | `a-subgraph-without-repeat-drops-the-repeat-bullet-and-the-part-of-suffix.txtar` |
| 42 | `test_inner_step_part_of_and_delegation_order` | `a-subgraph-renders-as-a-tagged-row-group-an-intro-and-inner-sections.txtar` |
| 43 | `test_inner_step_part_of_without_repeat_has_no_suffix` | `a-subgraph-without-repeat-drops-the-repeat-bullet-and-the-part-of-suffix.txtar` |
| 44 | `test_outer_steps_have_no_part_of_bullet` | `a-subgraph-renders-as-a-tagged-row-group-an-intro-and-inner-sections.txtar` |
| 45 | `test_step_flag_on_inner_step_returns_bare_body` | `the-step-flag-on-an-inner-step-prints-the-bare-body.txtar` |
| 46 | `test_io_keys_are_never_rendered` | `io-shaped-step-frontmatter-keys-never-reach-the-render.txtar` — the unit's three parametrized inputs (no extra keys, `inputs:`, `outputs:`) collapse into one fixture carrying both keys |
| 47 | `test_no_state_section_without_states` | `a-playbook-without-states-renders-no-state-section.txtar` |
| 48 | `test_state_section_follows_the_execution_graph` | `a-stateful-playbook-renders-one-state-entry-per-machine.txtar` |
| 49 | `test_state_section_outer_entry` | `a-stateful-playbook-renders-one-state-entry-per-machine.txtar` |
| 50 | `test_state_section_status_rows` | `a-stateful-playbook-renders-one-state-entry-per-machine.txtar` |
| 51 | `test_state_section_instance_entry` | `a-stateful-playbook-renders-one-state-entry-per-machine.txtar` |
| 52 | `test_graph_in_both_notice` | `a-graph-on-both-manifest-surfaces-blocks-the-render.txtar` |
| 53 | `test_bad_manifest_notice` | `a-malformed-manifest-blocks-the-render.txtar` |
| 54 | `test_bad_state_notice` | `a-malformed-states-entry-blocks-the-render.txtar` |
| 55 | `test_unknown_state_notice` | `an-unknown-state-reference-blocks-the-render.txtar` |
| 56 | `test_unknown_inner_state_notice_names_the_subgraph` | `an-unknown-inner-state-notice-names-its-subgraph.txtar` |
| 57 | `test_orphan_state_note_non_blocking` | `an-unreferenced-state-machine-is-a-non-blocking-note.txtar` |
| 58 | `test_non_jinja_playbook_output_unchanged` | `a-non-jinja-playbook-renders-its-bodies-verbatim.txtar` — the golden-file comparison becomes the case's own pinned stdout |
| 59 | `test_jinja_preamble_renders_expression_and_include` | `a-jinja-preamble-renders-expressions-and-includes.txtar` |
| 60 | `test_jinja_wave_one_step_shows_step_command` | `fetch-lines-are-identical-with-jinja.txtar` |
| 61 | `test_jinja_later_wave_step_shows_step_command` | `fetch-lines-are-identical-with-jinja.txtar` |
| 62 | `test_fetch_line_shape_is_uniform_across_jinja_modes` | `fetch-lines-are-identical-with-jinja.txtar` + `fetch-lines-are-identical-without-jinja.txtar` |
| 63 | `test_no_read_link_form_anywhere` | `fetch-lines-are-identical-with-jinja.txtar` + `fetch-lines-are-identical-without-jinja.txtar` — every case pins stdout whole, so a link-form fetch line would fail the corpus everywhere, not just here |
| 64 | `test_inline_embeds_non_detached_body_and_drops_fetch` | `inline-steps-from-the-flag-embeds-non-detached-bodies.txtar` |
| 65 | `test_inline_keeps_fetch_form_for_detached_steps` | `inline-steps-from-the-manifest-key-embeds-non-detached-bodies.txtar` |
| 66 | `test_inline_jinja_body_renders_through_context` | `an-inlined-jinja-body-renders-through-the-context.txtar` |
| 67 | `test_jinja_preamble_renders_macro_stamp` | `a-stubbed-macro-reaches-the-preamble-and-an-inlined-body.txtar` |
| 68 | `test_jinja_step_summary_renders_through_context` | `jinja-step-frontmatter-renders-through-the-context.txtar` |
| 69 | `test_jinja_step_detached_renders_through_context` | `jinja-step-frontmatter-renders-through-the-context.txtar` |
| 70 | `test_jinja_step_detached_rendering_empty_falls_back_to_inline` | `jinja-step-frontmatter-renders-through-the-context.txtar` |
| 71 | `test_non_jinja_playbook_leaves_frontmatter_verbatim` | `a-non-jinja-playbook-renders-its-bodies-verbatim.txtar` |
| 72 | `test_jinja_step_frontmatter_error_is_in_band_stop` | `broken-step-frontmatter-is-an-in-band-stop.txtar` |
| 73 | `test_manifest_inline_steps_key_implies_inline` | `inline-steps-from-the-manifest-key-embeds-non-detached-bodies.txtar` |
| 74 | `test_inline_appends_step_targeted_lessons` | `step-lessons-are-appended-to-an-inlined-step-section.txtar` |
| 75 | `test_inline_body_jinja_error_is_blocking` | `a-broken-inlined-body-blocks-the-render.txtar` |
| 76 | `test_inline_body_error_in_an_orphan_step_does_not_block` | `a-broken-body-in-an-unwired-step-does-not-block-an-inline-render.txtar` |
| 77 | `test_jinja_without_context_stops` | **dropped — not portable.** `_NO_CONTEXT` fires only when `compose()`/`compose_step()` are called with `context=None`, and `render_playbook._run` always passes an assembled context, so no argv reaches the branch. Recorded as drift by M04; behaviour left unfixed |
| 78 | `test_broken_step_body_does_not_break_compose` | `a-broken-step-body-surfaces-only-at-fetch-time.txtar` |
| 79 | `test_jinja_error_is_in_band_stop_notice_at_fetch_time` | `a-broken-step-body-surfaces-only-at-fetch-time.txtar` |
| 80 | `test_step_body_only_non_jinja` | `the-step-flag-prints-the-bare-body-and-logs.txtar` |
| 81 | `test_step_body_only_jinja_rendered` | `a-set-override-reaches-the-step-surface.txtar` |
| 82 | `test_include_from_playbook_dir_by_bare_name` | `a-bare-include-falls-back-to-the-playbook-directory.txtar` |
| 83 | `test_include_from_step_dir_by_bare_name` | `an-include-in-a-step-body-prefers-the-step-directory.txtar` |
| 84 | `test_include_from_playbook_root_by_root_relative_name` | `a-root-relative-include-resolves-from-the-playbook-root.txtar` |
| 85 | `test_plugin_partials_still_reachable` | `a-root-relative-include-falls-back-to-the-shipped-core-root.txtar` |
| 86 | `test_relative_includes_resolve_against_including_file` | `a-relative-include-resolves-against-its-including-file.txtar` |
| 87 | `test_later_wave_step_fetch_resolves_playbook_dir_include` | `a-later-wave-step-fetch-resolves-a-playbook-directory-include.txtar` |
| 88 | `test_root_relative_include_prefers_local` | `a-root-relative-include-prefers-the-vault-root-over-the-home-root.txtar` |
| 89 | `test_root_relative_include_falls_back_to_global` | `a-root-relative-include-falls-back-to-the-home-root.txtar` |
| 90 | `test_root_relative_include_falls_back_to_core` | `a-root-relative-include-falls-back-to-the-shipped-core-root.txtar` |
| 91 | `test_missing_include_is_blocking_notice` | `a-missing-include-blocks-the-step-body.txtar` |
| 92 | `test_requires_project_without_project_exits_1` | `a-requires-project-playbook-needs-a-vault.txtar` |
| 93 | `test_missing_playbook_exits_1` | `an-unknown-playbook-name-is-rejected.txtar` |
| 94 | `test_output_to_file` | `the-output-flag-writes-the-render-and-leaves-stdout-empty.txtar` |
| 95 | `test_project_flag_satisfies_requires_project` | `a-requires-project-playbook-needs-a-vault.txtar` |
| 96 | `test_step_prints_body_only_and_logs` | `the-step-flag-prints-the-bare-body-and-logs.txtar` |
| 97 | `test_step_renders_jinja_body` | `a-set-override-reaches-the-step-surface.txtar` |
| 98 | `test_unknown_step_exits_1` | `an-unknown-step-name-is-rejected.txtar` |
| 99 | `test_cli_renders_to_stdout` | `a-composed-render-is-preamble-then-table-then-step-sections.txtar` |
| 100 | `test_lessons_section_locked_format` | `the-lessons-section-is-a-count-sentence-then-one-heading-per-lesson.txtar` |
| 101 | `test_playbook_target_absent_from_step_surface` | `a-step-targeted-lesson-reaches-only-the-step-surface.txtar` |
| 102 | `test_step_target_absent_from_composed_section` | `a-step-targeted-lesson-reaches-only-the-step-surface.txtar` |
| 103 | `test_other_playbook_target_renders_nowhere` | `a-lesson-targeting-another-playbook-renders-nowhere.txtar` |
| 104 | `test_no_lessons_no_section` | `a-playbook-with-no-lessons-renders-no-lessons-section.txtar` |
| 105 | `test_lessons_section_between_preamble_and_graph` | `the-lessons-section-is-a-count-sentence-then-one-heading-per-lesson.txtar` |
| 106 | `test_lesson_body_is_not_jinja_rendered` | `a-lesson-body-is-never-jinja-rendered.txtar` |
| 107 | `test_step_lessons_locked_format` | `a-step-targeted-lesson-reaches-only-the-step-surface.txtar` |
| 108 | `test_step_lessons_on_jinja_playbook` | `step-lessons-render-on-a-jinja-playbook.txtar` |
| 109 | `test_step_lessons_inline_surface` | `step-lessons-are-appended-to-an-inlined-step-section.txtar` |
| 110 | `test_no_lessons_flag_suppresses_both_surfaces` | `the-no-lessons-flag-removes-the-composed-lessons-section.txtar` + `the-no-lessons-flag-removes-the-step-lesson-block.txtar` |
| 111 | `test_unknown_step_target_note_non_blocking` | `a-lesson-targeting-an-unknown-step-is-a-non-blocking-note.txtar` |
| 112 | `test_untargeted_lesson_note` | `an-untargeted-lesson-is-a-non-blocking-note.txtar` |
| 113 | `test_legacy_lesson_dirs_note` | `legacy-lesson-directories-are-a-non-blocking-note.txtar` |
| 114 | `test_no_notices_without_legacy_or_untargeted` | `the-lessons-section-is-a-count-sentence-then-one-heading-per-lesson.txtar` |
| 115 | `test_name_clash_notice_blocks` | `a-playbook-name-in-two-roots-blocks-the-render.txtar` |
| 116 | `test_cli_no_lessons_flag` | `the-no-lessons-flag-removes-the-composed-lessons-section.txtar` + `the-no-lessons-flag-removes-the-step-lesson-block.txtar` |
| 117 | `test_cli_help_lists_no_lessons` | `help-lists-every-flag-including-no-lessons.txtar` |
| 118 | `test_cli_unknown_step_still_exits_1_with_lessons` | `an-unknown-step-still-exits-1-with-lessons-present.txtar` |
| 119 | `test_stubbed_macro_reaches_playbook_bodies` | `a-stubbed-macro-reaches-the-preamble-and-an-inlined-body.txtar` + `a-stubbed-macro-reaches-a-step-fetch.txtar` |
| 120 | `test_unstubbed_macro_in_playbook_bodies_is_time_shaped` | `an-unstubbed-macro-runs-and-its-stdout-lands-in-the-render.txtar` |

One drop (row 77) and one gap case (row 20). No bug was exposed by the port.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook -q && uv run pytest tests/utils_test.py tests/context/playbook_test.py -q && rg -n "render-playbook-home|test_render_playbook" . ; echo "rg exit: $?"
```

The corpus and the two remaining consumers of what this milestone touched are green, and `rg` exits 1 — no reference to the deleted file or its fixture tree survives.
