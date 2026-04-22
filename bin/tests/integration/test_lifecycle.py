"""Integration test: full backlog → done lifecycle."""
import datetime
import textwrap

from booping_plans import EXIT_OK


INITIAL_PLAN = textwrap.dedent("""\
    ---
    title: Lifecycle Plan
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
    business_goal: Make things better
    ---

    # Lifecycle Plan

    Body text.
    """)


def _read_sprints(tmp_project) -> str:
    return (tmp_project.claude_root / "sprints.md").read_text()


def test_full_lifecycle(tmp_project):
    """Walk backlog → in-spec → ready-for-dev → in-progress → awaiting-retro → awaiting-learning → done."""
    p = tmp_project.write_plan("20260401-lifecycle.md", INITIAL_PLAN)

    # Step 1: backlog → in-spec
    rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=in-spec")
    assert rc == EXIT_OK
    assert "status: in-spec" in p.read_text()

    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    assert rc == EXIT_OK
    sprints = _read_sprints(tmp_project)
    assert "## Active" in sprints
    assert "Lifecycle Plan" in sprints
    active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
    assert "in-spec" in active_section

    # Step 2: in-spec → ready-for-dev (auto-fills planned)
    rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=ready-for-dev", "sp=3")
    assert rc == EXIT_OK
    text = p.read_text()
    assert "status: ready-for-dev" in text
    today = datetime.date.today().isoformat()
    assert today in text  # planned auto-filled

    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    assert rc == EXIT_OK
    sprints = _read_sprints(tmp_project)
    active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
    assert "ready-for-dev" in active_section

    # Step 3: ready-for-dev → in-progress (auto-fills started)
    rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=in-progress")
    assert rc == EXIT_OK
    text = p.read_text()
    assert "status: in-progress" in text
    assert today in text  # started auto-filled

    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    assert rc == EXIT_OK
    sprints = _read_sprints(tmp_project)
    active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
    assert "in-progress" in active_section

    # Step 4: in-progress → awaiting-retro (auto-fills completed)
    rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=awaiting-retro")
    assert rc == EXIT_OK
    text = p.read_text()
    assert "status: awaiting-retro" in text
    assert today in text  # completed auto-filled

    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    assert rc == EXIT_OK
    sprints = _read_sprints(tmp_project)
    active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
    assert "awaiting-retro" in active_section

    # Step 5: awaiting-retro → awaiting-learning (retro + goal set)
    rc, _, _ = tmp_project.run(
        "set", "--project=test-proj", str(p),
        "status=awaiting-learning",
        "retro=retrospectives/2026-04-lifecycle.md",
        "goal=success",
    )
    assert rc == EXIT_OK
    text = p.read_text()
    assert "status: awaiting-learning" in text
    assert "goal: success" in text

    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    assert rc == EXIT_OK
    sprints = _read_sprints(tmp_project)
    active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
    assert "awaiting-learning" in active_section

    # Step 6: awaiting-learning → done
    rc, _, _ = tmp_project.run("set", "--project=test-proj", str(p), "status=done")
    assert rc == EXIT_OK
    assert "status: done" in p.read_text()

    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    assert rc == EXIT_OK
    sprints = _read_sprints(tmp_project)
    history_section = sprints[sprints.index("## History"):]
    assert "done" in history_section
    assert "Lifecycle Plan" in history_section

    # Verify the plan does NOT appear in Active any more
    active_section = sprints[sprints.index("## Active"):sprints.index("## History")]
    assert "Lifecycle Plan" not in active_section

    # Verify sync-sprints is deterministic
    content1 = (tmp_project.claude_root / "sprints.md").read_bytes()
    rc, _, _ = tmp_project.run("sync-sprints", "--project=test-proj")
    content2 = (tmp_project.claude_root / "sprints.md").read_bytes()
    assert content1 == content2
