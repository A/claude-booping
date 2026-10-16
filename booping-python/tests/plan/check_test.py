from __future__ import annotations

from booping.plan.check import Finding, check_milestone

SECTIONS = ["Tasks", "Definition of Done", "References", "Verify"]
THRESHOLD = 5


def _milestone(
    *,
    sp: str = "3",
    tasks: str = "| Task | Description |\n| --- | --- |\n| 1.1 | edit `src/a.py` |\n",
    dod: str = "- [ ] a works\n",
    verify: str = "`pytest tests/a_test.py`\n",
) -> str:
    return (
        "---\n"
        'id: "01"\n'
        'title: "A"\n'
        f"sp: {sp}\n"
        "status: pending\n"
        "---\n"
        "\n"
        "# M01: A\n"
        "\n"
        f"## Tasks\n\n{tasks}\n"
        f"## Definition of Done\n\n{dod}\n"
        "## References\n\n- `src/b.py`\n\n"
        f"## Verify\n\n{verify}"
    )


def _checks(text: str) -> list[Finding]:
    return check_milestone(text, SECTIONS, THRESHOLD)


def test_clean_milestone_has_no_findings() -> None:
    assert _checks(_milestone()) == []


def test_verify_two_fenced_commands_fails() -> None:
    verify = "```\npytest a\n```\n\n```\npytest b\n```\n"

    assert _checks(_milestone(verify=verify)) == [
        Finding("verify", "Verify holds 2 commands, expected exactly one")
    ]


def test_verify_fenced_block_with_two_lines_fails() -> None:
    verify = "```bash\npytest a\npytest b\n```\n"

    assert _checks(_milestone(verify=verify)) == [
        Finding("verify", "Verify holds 2 commands, expected exactly one")
    ]


def test_verify_chained_on_one_line_passes() -> None:
    assert _checks(_milestone(verify="```\nmake lint && pytest a\n```\n")) == []
    assert _checks(_milestone(verify="`make lint && pytest a`\n")) == []


def test_verify_without_a_command_fails() -> None:
    assert _checks(_milestone(verify="Run the tests.\n")) == [
        Finding("verify", "Verify holds 0 commands, expected exactly one")
    ]


def test_files_tasks_naming_no_path_fails() -> None:
    tasks = "| Task | Description |\n| --- | --- |\n| 1.1 | make it `fast` |\n"

    assert _checks(_milestone(tasks=tasks)) == [Finding("files", "Tasks names no file path")]


def test_files_extension_alone_names_a_path() -> None:
    tasks = "| Task | Description |\n| --- | --- |\n| 1.1 | edit `README.md` |\n"

    assert _checks(_milestone(tasks=tasks)) == []


def test_dod_three_task_rows_two_checkboxes_fails() -> None:
    tasks = (
        "| Task | Description |\n"
        "| --- | --- |\n"
        "| 1.1 | edit `a.py` |\n"
        "| 1.2 | edit `b.py` |\n"
        "| 1.3 | edit `c.py` |\n"
    )
    dod = "- [ ] a\n- [x] b\n"

    assert _checks(_milestone(tasks=tasks, dod=dod)) == [
        Finding("dod", "2 DoD checkboxes for 3 tasks")
    ]


def test_dod_list_style_tasks() -> None:
    tasks = "- edit `a.py`\n- edit `b.py`\n  - a nested note\n"

    assert _checks(_milestone(tasks=tasks, dod="- [ ] a\n- [ ] b\n")) == []
    assert _checks(_milestone(tasks=tasks, dod="- [ ] a\n")) == [
        Finding("dod", "1 DoD checkboxes for 2 tasks")
    ]


def test_dod_no_tasks_fails() -> None:
    assert _checks(_milestone(tasks="See `src/a.py`.\n")) == [Finding("dod", "Tasks holds no task")]


def test_sp_at_threshold_fails() -> None:
    assert _checks(_milestone(sp="5")) == [
        Finding("sp", "sp 5 is at or above the re-decompose threshold 5")
    ]


def test_sp_below_threshold_passes() -> None:
    assert _checks(_milestone(sp="4")) == []


def test_sp_null_fails() -> None:
    assert _checks(_milestone(sp="null")) == [Finding("sp", "sp is not set")]
