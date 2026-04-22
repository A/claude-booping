"""Integration test: backlog → in-spec → cancelled path."""
import datetime
import textwrap

from booping_plans import EXIT_OK


INITIAL_PLAN = textwrap.dedent("""\
    ---
    title: Cancelled Feature
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

    # Cancelled Feature
    """)


def test_cancelled_path(tmp_project):
    """Walk backlog → in-spec → cancelled; plan appears in History."""
    p = tmp_project.write_plan("20260401-cancel.md", INITIAL_PLAN)
    today = datetime.date.today().isoformat()

    # backlog → in-spec
    rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=in-spec")
    assert rc == EXIT_OK
    assert "status: in-spec" in p.read_text()

    # in-spec → cancelled (auto-fills completed)
    rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=cancelled")
    assert rc == EXIT_OK
    text = p.read_text()
    assert "status: cancelled" in text
    assert today in text  # completed auto-filled

    # sync-sprints and verify History
    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    assert rc == EXIT_OK

    sprints = (tmp_project.claude_root / "sprints.md").read_text()
    history_section = sprints[sprints.index("## History"):]
    assert "cancelled" in history_section
    assert "Cancelled Feature" in history_section
    assert today in history_section  # completed date appears

    # Active should NOT contain the plan
    active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
    assert "Cancelled Feature" not in active_section
