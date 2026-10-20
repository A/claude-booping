from __future__ import annotations

from collections import Counter
from pathlib import Path

from booping.plan.split import SECTION_KEYS, Cut, cut_draft

FIXTURES = Path(__file__).parent / "__fixtures__"


def _draft(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _placed(cut: Cut) -> Counter[str]:
    lines = [*cut.plan_lines, *cut.overview_lines, *cut.marker_lines]
    for m in cut.milestones:
        for key in SECTION_KEYS:
            lines += m.sections[key]
    return Counter(lines)


def _numbered(text: str, numbers: list[int]) -> list[str]:
    lines = text.splitlines(keepends=True)
    return [lines[n - 1] for n in numbers]


def _milestones(sps: list[int | None]) -> str:
    parts = ["# Plan\n", "\n", "## Milestones\n", "\n"]
    for k, sp in enumerate(sps, 1):
        parts += [f"### M{k:02d} — Step {k}\n"]
        if sp is not None:
            parts += [f"sp: {sp}\n"]
        parts += ["\n", "#### Tasks\n", "\n", f"- do thing {k}\n", "\n"]
    return "".join(parts)


def test_fixed_format_fields_and_sections() -> None:
    cut = cut_draft(_draft("fixed.md"), 15)

    assert [(m.id, m.title, m.slug, m.sp, m.depends_on) for m in cut.milestones] == [
        ("01", "Parser core", "parser-core", 3, ()),
        ("02", "CLI wiring", "cli-wiring", 2, ("01",)),
    ]
    first, second = cut.milestones
    assert first.sections == {
        "tasks": (
            "| Task | Description |\n",
            "|------|-------------|\n",
            "| 1.1 | Write `src/a.py` |\n",
            "\n",
        ),
        "dod": ("- [ ] parser exists\n", "\n"),
        "references": ("- `src/b.py`\n", "\n"),
        "verify": ("```\n", "pytest tests/a_test.py\n", "```\n", "\n"),
    }
    assert second.sections == {
        "tasks": ("- wire `src/cli.py`\n", "\n"),
        "dod": ("- [ ] cli runs\n", "\n"),
        "references": (),
        "verify": ("`booping --help`\n",),
    }
    assert cut.plan_lines == (
        "# Demo plan\n",
        "\n",
        "## Context\n",
        "\n",
        "Some context.\n",
        "\n",
        "\n",
        "\n",
        "## Final Verification\n",
        "\n",
        "- [ ] all green\n",
    )
    assert cut.overview_lines == ("## Milestones\n",)
    assert cut.generated_at == 6
    assert cut.groups == (("01", "02"),)
    assert cut.flags == ()
    assert cut.demoted == 0


def test_fixed_format_places_every_line_once() -> None:
    text = _draft("fixed.md")
    cut = cut_draft(text, 15)

    markers = [9, 10, 11, 12, 13, 14, 19, 20, 23, 24, 27, 28]
    markers += [33, 34, 35, 36, 37, 38, 41, 42, 45, 46, 47, 48]
    assert list(cut.marker_lines) == _numbered(text, markers)
    assert _placed(cut) == Counter(text.splitlines(keepends=True))


def test_path_headings() -> None:
    text = _draft("path-headings.md")
    cut = cut_draft(text, 15)

    assert [(m.id, m.title, m.slug, m.sp, m.depends_on) for m in cut.milestones] == [
        ("01", "setup db", "setup-db", 2, ()),
        ("02", "api", "api", 3, ("01",)),
    ]
    assert cut.milestones[0].sections["tasks"] == ("- create `db.sql`\n", "\n")
    assert cut.milestones[0].sections["verify"] == ("`make db`\n", "\n")
    assert cut.milestones[1].sections["tasks"] == (
        "- add `api.py`\n",
        "\n",
        "## Notes\n",
        "\n",
        "- keep it small\n",
    )
    assert cut.flags == (
        "M01: title taken from the path heading",
        "M02: title taken from the path heading",
    )
    assert cut.demoted == 1
    assert cut.plan_lines == ("# Plan\n", "\n")
    assert cut.generated_at == 2
    markers = [3, 4, 5, 6, 7, 8, 11, 12, 15, 16, 17, 18, 19, 20, 21]
    assert list(cut.marker_lines) == _numbered(text, markers)
    assert _placed(cut) == Counter(text.splitlines(keepends=True))


def test_heading_inside_code_fence_is_not_a_cut() -> None:
    text = (
        "## Milestones\n"
        "\n"
        "### M01 — Only one\n"
        "sp: 1\n"
        "\n"
        "#### Tasks\n"
        "\n"
        "```markdown\n"
        "### M02 — x\n"
        "```\n"
    )
    cut = cut_draft(text, 15)

    assert [m.id for m in cut.milestones] == ["01"]
    assert cut.milestones[0].sections["tasks"] == ("```markdown\n", "### M02 — x\n", "```\n")
    assert cut.flags == ()


def test_no_milestone_heading_yields_no_milestones() -> None:
    text = "# Plan\n\n## Context\n\nNothing to cut.\n"
    cut = cut_draft(text, 15)

    assert cut.milestones == ()
    assert cut.groups == ()
    assert "".join(cut.plan_lines) == text


def test_missing_sp_is_none_and_flagged_per_milestone() -> None:
    cut = cut_draft(_milestones([None, None]), 15)

    assert [m.sp for m in cut.milestones] == [None, None]
    assert cut.flags == (
        "M01: sp not stated anywhere; left null",
        "M02: sp not stated anywhere; left null",
    )


def test_groups_close_past_the_cap() -> None:
    cut = cut_draft(_milestones([5, 5, 5, 1]), 10)

    assert cut.groups == (("01", "02"), ("03", "04"))


def test_groups_sum_equal_to_cap_stays_together() -> None:
    cut = cut_draft(_milestones([5, 5, 5, 1]), 15)

    assert cut.groups == (("01", "02", "03"), ("04",))


def test_lone_milestone_over_the_cap_is_its_own_group() -> None:
    cut = cut_draft(_milestones([20, 2]), 15)

    assert cut.groups == (("01",), ("02",))


def test_no_cap_puts_each_milestone_alone() -> None:
    cut = cut_draft(_milestones([1, 1, 1]), None)

    assert cut.groups == (("01",), ("02",), ("03",))


def test_depends_on_a_later_milestone_is_flagged() -> None:
    text = "### M01 — First\nsp: 1\ndepends_on: [M02]\n\n- a\n\n### M02 — Second\nsp: 1\n\n- b\n"
    cut = cut_draft(text, 15)

    assert cut.milestones[0].depends_on == ("02",)
    assert cut.flags == ("M01: depends on later M02",)


def test_line_endings_are_kept() -> None:
    text = "# Plan\r\n\r\n### M01 — One\r\nsp: 1\r\n\r\n#### Tasks\r\n\r\n- a  \r\n"
    cut = cut_draft(text, 15)

    assert cut.milestones[0].sections["tasks"] == ("- a  \r\n",)
    assert cut.plan_lines == ("# Plan\r\n", "\r\n")
