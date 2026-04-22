"""Unit tests for booping_plans.py — ≥20 tests covering list, set, sync-sprints."""
import datetime
import re
import textwrap
from pathlib import Path

from booping_plans import EXIT_OK, EXIT_NOT_FOUND, EXIT_MALFORMED_NONFATAL
from booping_plans import EXIT_MISSING_PROJECT, EXIT_INVALID_ENUM, EXIT_MALFORMED_FATAL

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASIC_PLAN = textwrap.dedent("""\
    ---
    title: My Plan
    type: feature
    status: backlog
    sp: null
    source: ad-hoc
    created: 2026-04-01
    planned: null
    started: null
    completed: null
    retro: null
    goal: null
    business_goal: null
    ---

    # My Plan body
    """)

MALFORMED_PLAN = textwrap.dedent("""\
    ---
    title: [unclosed
    ---
    # Body
    """)


# ---------------------------------------------------------------------------
# list tests (≥4)
# ---------------------------------------------------------------------------

class TestList:
    def test_list_all_plans(self, tmp_project):
        """list returns all plans in the directory."""
        tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, out, _ = tmp_project.run("list", "--project=test-proj")
        assert rc == EXIT_OK
        assert "My Plan" in out
        assert "backlog" in out

    def test_list_status_filter(self, tmp_project):
        """list --status filters to matching plans only."""
        tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        in_spec_plan = BASIC_PLAN.replace("status: backlog", "status: in-spec").replace("title: My Plan", "title: Spec Plan")
        tmp_project.write_plan("20260401-beta.md", in_spec_plan)

        rc, out, _ = tmp_project.run("list", "--project=test-proj", "--status=in-spec")
        assert rc == EXIT_OK
        assert "Spec Plan" in out
        assert "My Plan" not in out

    def test_list_malformed_warn_skip(self, tmp_project):
        """Malformed YAML warns on stderr, skips that file, exits 3."""
        tmp_project.write_plan("20260401-good.md", BASIC_PLAN)
        tmp_project.write_plan("20260401-bad.md", MALFORMED_PLAN)

        rc, out, err = tmp_project.run("list", "--project=test-proj")
        assert rc == EXIT_MALFORMED_NONFATAL
        assert "warning:" in err
        assert "My Plan" in out  # good file still listed

    def test_list_missing_project_exits_4(self, tmp_project):
        """list without --project exits 4."""
        rc, _, err = tmp_project.run("list")
        assert rc == EXIT_MISSING_PROJECT
        assert "--project is required" in err

    def test_list_invalid_status_filter_exits_5(self, tmp_project):
        """list --status=invalid exits 5 with appropriate message."""
        rc, _, err = tmp_project.run("list", "--project=test-proj", "--status=notastatus")
        assert rc == EXIT_INVALID_ENUM
        assert "status must be one of" in err

    def test_list_empty_directory(self, tmp_project):
        """list on empty plans dir exits 0 with no rows."""
        rc, out, _ = tmp_project.run("list", "--project=test-proj")
        assert rc == EXIT_OK
        assert out == ""


# ---------------------------------------------------------------------------
# set tests (≥12)
# ---------------------------------------------------------------------------

class TestSet:
    def test_set_status_transition(self, tmp_project):
        """set status=in-spec updates the frontmatter status."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=in-spec")
        assert rc == EXIT_OK
        text = p.read_text()
        assert "status: in-spec" in text

    def test_set_autofill_planned_on_ready_for_dev(self, tmp_project):
        """status=ready-for-dev auto-fills planned when absent."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        today = datetime.date.today().isoformat()
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=ready-for-dev")
        assert rc == EXIT_OK
        text = p.read_text()
        assert "status: ready-for-dev" in text
        assert today in text  # planned was auto-filled

    def test_set_autofill_started_on_in_progress(self, tmp_project):
        """status=in-progress auto-fills started when absent."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        today = datetime.date.today().isoformat()
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=in-progress")
        assert rc == EXIT_OK
        text = p.read_text()
        assert "status: in-progress" in text
        assert today in text  # started was auto-filled

    def test_set_autofill_completed_on_awaiting_retro(self, tmp_project):
        """status=awaiting-retro auto-fills completed when absent."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        today = datetime.date.today().isoformat()
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=awaiting-retro")
        assert rc == EXIT_OK
        text = p.read_text()
        assert "status: awaiting-retro" in text
        assert today in text

    def test_set_autofill_completed_on_fail(self, tmp_project):
        """status=fail auto-fills completed when absent."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        today = datetime.date.today().isoformat()
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=fail")
        assert rc == EXIT_OK
        text = p.read_text()
        assert "status: fail" in text
        assert today in text

    def test_set_autofill_completed_on_cancelled(self, tmp_project):
        """status=cancelled auto-fills completed when absent."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        today = datetime.date.today().isoformat()
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=cancelled")
        assert rc == EXIT_OK
        text = p.read_text()
        assert "status: cancelled" in text
        assert today in text

    def test_set_invalid_status_enum_exits_5(self, tmp_project):
        """set with invalid status exits 5 with 'must be one of' message."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, err = tmp_project.run("set", "--project=test-proj", str(p), "status=groomed")
        assert rc == EXIT_INVALID_ENUM
        assert "status must be one of" in err

    def test_set_invalid_goal_enum_exits_5(self, tmp_project):
        """set with invalid goal exits 5."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, err = tmp_project.run("set", "--project=test-proj", str(p), "goal=bad-value")
        assert rc == EXIT_INVALID_ENUM
        assert "goal must be one of" in err

    def test_set_invalid_type_enum_exits_5(self, tmp_project):
        """set with invalid type exits 5."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, err = tmp_project.run("set", "--project=test-proj", str(p), "type=sprint")
        assert rc == EXIT_INVALID_ENUM
        assert "type must be one of" in err

    def test_set_invalid_date_exits_5(self, tmp_project):
        """set with invalid date format exits 5."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, err = tmp_project.run("set", "--project=test-proj", str(p), "planned=not-a-date")
        assert rc == EXIT_INVALID_ENUM
        assert "YYYY-MM-DD" in err

    def test_set_multi_key_with_equals_in_value(self, tmp_project):
        """key=value where value contains = is parsed correctly."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, _ = tmp_project.run(
            "set", "--project=test-proj", str(p),
            "business_goal=x=y means something"
        )
        assert rc == EXIT_OK
        text = p.read_text()
        assert "x=y means something" in text

    def test_set_idempotent_re_set(self, tmp_project):
        """Running the same set twice produces byte-identical output."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc1, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=ready-for-dev")
        assert rc1 == EXIT_OK
        content_after_first = p.read_bytes()

        rc2, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=ready-for-dev")
        assert rc2 == EXIT_OK
        content_after_second = p.read_bytes()

        assert content_after_first == content_after_second

    def test_set_comment_preservation(self, tmp_project):
        """Inline # comments survive round-trip, still attached to their key line."""
        content = (FIXTURES_DIR / "plan_with_comment.md").read_text(encoding="utf-8")
        p = tmp_project.write_plan("20260401-alpha.md", content)
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=in-spec")
        assert rc == EXIT_OK
        text = p.read_text()
        assert re.search(r"^source:\s+ad-hoc\s+#\s*inline comment\s*$", text, re.MULTILINE)

    def test_set_block_scalar_preservation(self, tmp_project):
        """Block scalar (|) indicator and indented body survive round-trip."""
        content = (FIXTURES_DIR / "plan_block_scalar.md").read_text(encoding="utf-8")
        p = tmp_project.write_plan("20260401-alpha.md", content)
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=in-spec")
        assert rc == EXIT_OK
        text = p.read_text()
        assert re.search(r"^business_goal:\s*\|", text, re.MULTILINE)
        # Confirm at least two indented lines still follow (still a block, not a folded string)
        indented_lines = [
            line for line in text.splitlines()
            if line.startswith("  ") and line.strip()
        ]
        assert len(indented_lines) >= 2

    def test_set_unknown_key_exits_5(self, tmp_project):
        """Unknown keys are rejected with exit 5."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, err = tmp_project.run("set", "--project=test-proj", str(p), "not_a_key=value")
        assert rc == EXIT_INVALID_ENUM
        assert "not_a_key" in err

    def test_set_malformed_frontmatter_exits_6(self, tmp_project):
        """Malformed frontmatter on set is fatal (exit 6)."""
        p = tmp_project.write_plan("20260401-bad.md", MALFORMED_PLAN)
        rc, _, err = tmp_project.run("set", "--project=test-proj", str(p), "status=in-spec")
        assert rc == EXIT_MALFORMED_FATAL
        assert "error:" in err

    def test_set_file_not_found_exits_2(self, tmp_project):
        """set on missing path exits 2 and does NOT create the file."""
        nonexistent = tmp_project.plans_dir / "ghost.md"
        assert not nonexistent.exists()
        rc, _, err = tmp_project.run("set", "--project=test-proj", str(nonexistent), "status=in-spec")
        assert rc == EXIT_NOT_FOUND
        assert not nonexistent.exists()
        assert "plan not found" in err

    def test_set_autofill_not_passed_not_present_rule(self, tmp_project):
        """Auto-fill only triggers when the field is not already set."""
        # Plan already has planned filled
        plan_with_planned = BASIC_PLAN.replace("planned: null", "planned: 2026-03-01")
        p = tmp_project.write_plan("20260401-alpha.md", plan_with_planned)
        rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=ready-for-dev")
        assert rc == EXIT_OK
        text = p.read_text()
        # The original planned date should remain, not overwritten with today
        assert "2026-03-01" in text

    def test_set_explicit_date_overrides_autofill(self, tmp_project):
        """When user passes planned= explicitly, it wins over auto-fill."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, _ = tmp_project.run(
            "set", "--project=test-proj", str(p),
            "status=ready-for-dev", "planned=2026-05-15"
        )
        assert rc == EXIT_OK
        text = p.read_text()
        assert "2026-05-15" in text

    def test_set_missing_project_exits_4(self, tmp_project):
        """set without --project exits 4."""
        p = tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, err = tmp_project.run("set", str(p), "status=in-spec")
        assert rc == EXIT_MISSING_PROJECT
        assert "--project is required" in err


# ---------------------------------------------------------------------------
# sync-sprints tests (≥4)
# ---------------------------------------------------------------------------

class TestSyncSprints:
    def test_sync_sprints_header(self, tmp_project):
        """sync-sprints output starts with the required header."""
        tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc == EXIT_OK
        sprints = (tmp_project.claude_root / "sprints.md").read_text()
        assert sprints.startswith("# Sprints\n")
        assert "Generated by booping-plans sync-sprints" in sprints
        assert "## Active" in sprints
        assert "## History" in sprints

    def test_sync_sprints_deterministic_byte_equal(self, tmp_project):
        """Running sync-sprints twice produces byte-identical output."""
        tmp_project.write_plan("20260401-alpha.md", BASIC_PLAN)
        tmp_project.write_plan("20260401-beta.md", BASIC_PLAN.replace("title: My Plan", "title: Other Plan"))
        rc1, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc1 == EXIT_OK
        content1 = (tmp_project.claude_root / "sprints.md").read_bytes()
        rc2, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc2 == EXIT_OK
        content2 = (tmp_project.claude_root / "sprints.md").read_bytes()
        assert content1 == content2

    def test_sync_sprints_history_fallback_sort_no_typeerror(self, tmp_project):
        """History sort with absent 'completed' doesn't raise TypeError."""
        # Plan with status=done but no completed date
        done_plan = BASIC_PLAN.replace(
            "status: backlog", "status: done"
        ).replace("title: My Plan", "title: Done Plan")
        tmp_project.write_plan("20260401-done.md", done_plan)
        # Should not raise; should produce valid output
        rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc == EXIT_OK
        sprints = (tmp_project.claude_root / "sprints.md").read_text()
        assert "Done Plan" in sprints
        assert "## History" in sprints

    def test_sync_sprints_malformed_warn_skip(self, tmp_project):
        """Malformed plan in sync-sprints: warn + skip + exit 3."""
        tmp_project.write_plan("20260401-good.md", BASIC_PLAN)
        tmp_project.write_plan("20260401-bad.md", MALFORMED_PLAN)
        rc, _, err = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc == EXIT_MALFORMED_NONFATAL
        assert "warning:" in err
        sprints = (tmp_project.claude_root / "sprints.md").read_text()
        assert "My Plan" in sprints  # good plan still rendered

    def test_sync_sprints_filename_tiebreak(self, tmp_project):
        """Plans with same planned date are sorted by filename."""
        plan_a = BASIC_PLAN.replace("planned: null", "planned: 2026-04-01").replace(
            "title: My Plan", "title: Alpha Plan"
        ).replace("status: backlog", "status: ready-for-dev")
        plan_b = BASIC_PLAN.replace("planned: null", "planned: 2026-04-01").replace(
            "title: My Plan", "title: Beta Plan"
        ).replace("status: backlog", "status: ready-for-dev")
        tmp_project.write_plan("20260401-beta.md", plan_b)
        tmp_project.write_plan("20260401-alpha.md", plan_a)
        rc1, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc1 == EXIT_OK
        content1 = (tmp_project.claude_root / "sprints.md").read_bytes()
        rc2, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc2 == EXIT_OK
        content2 = (tmp_project.claude_root / "sprints.md").read_bytes()
        assert content1 == content2
        sprints = content1.decode()
        alpha_pos = sprints.index("Alpha Plan")
        beta_pos = sprints.index("Beta Plan")
        assert alpha_pos < beta_pos  # alpha.md < beta.md alphabetically

    def test_sync_sprints_missing_project_exits_4(self, tmp_project):
        """sync-sprints without --project exits 4."""
        rc, _, err = tmp_project.run("sync-sprints")
        assert rc == EXIT_MISSING_PROJECT
        assert "--project is required" in err

    def test_sync_sprints_active_vs_history_split(self, tmp_project):
        """Terminal statuses go to History, non-terminal to Active."""
        active_plan = BASIC_PLAN  # status: backlog
        done_plan = BASIC_PLAN.replace("status: backlog", "status: done").replace(
            "title: My Plan", "title: Done Plan"
        )
        tmp_project.write_plan("20260401-active.md", active_plan)
        tmp_project.write_plan("20260401-done.md", done_plan)
        rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc == EXIT_OK
        sprints = (tmp_project.claude_root / "sprints.md").read_text()
        active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
        history_section = sprints[sprints.index("## History"):]
        assert "My Plan" in active_section
        assert "Done Plan" in history_section
        assert "Done Plan" not in active_section

    def test_sync_sprints_history_filename_desc_tiebreak(self, tmp_project):
        """History plans with identical completed dates sort by filename descending."""
        aardvark_plan = BASIC_PLAN.replace("status: backlog", "status: done").replace(
            "title: My Plan", "title: Aardvark Plan"
        ).replace("completed: null", "completed: 2026-03-01")
        zebra_plan = BASIC_PLAN.replace("status: backlog", "status: done").replace(
            "title: My Plan", "title: Zebra Plan"
        ).replace("completed: null", "completed: 2026-03-01")
        tmp_project.write_plan("20260301-aardvark.md", aardvark_plan)
        tmp_project.write_plan("20260301-zebra.md", zebra_plan)
        rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
        assert rc == EXIT_OK
        sprints = (tmp_project.claude_root / "sprints.md").read_text()
        history_section = sprints[sprints.index("## History"):]
        zebra_pos = history_section.index("Zebra Plan")
        aardvark_pos = history_section.index("Aardvark Plan")
        assert zebra_pos < aardvark_pos  # descending filename: zebra before aardvark
