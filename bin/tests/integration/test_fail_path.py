"""Integration test: in-progress → fail path."""
import datetime
import textwrap

from booping_plans import EXIT_OK


INITIAL_PLAN = textwrap.dedent("""\
    ---
    title: Failed Sprint
    type: feature
    status: in-progress
    sp: 2
    source: ad-hoc
    created: 2026-04-01
    planned: 2026-04-01
    started: 2026-04-02
    completed: null
    retro: null
    goal: null
    business_goal: null
    ---

    # Failed Sprint
    """)


def test_fail_path(tmp_project):
    """Walk in-progress → fail; plan appears in History with fail and completed filled."""
    p = tmp_project.write_plan("20260401-fail.md", INITIAL_PLAN)
    today = datetime.date.today().isoformat()

    # in-progress → fail (auto-fills completed)
    rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=fail")
    assert rc == EXIT_OK
    text = p.read_text()
    assert "status: fail" in text
    assert today in text  # completed auto-filled

    # sync-sprints and verify History
    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    assert rc == EXIT_OK

    sprints = (tmp_project.claude_root / "sprints.md").read_text()
    history_section = sprints[sprints.index("## History"):]
    assert "fail" in history_section
    assert "Failed Sprint" in history_section
    assert today in history_section  # completed date appears

    # Active should NOT contain the plan
    active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
    assert "Failed Sprint" not in active_section
