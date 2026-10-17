from __future__ import annotations

from pathlib import Path

from booping.specs.open_items import Mark, marks
from booping.specs.records import load_record


def test_marks_carry_their_kind_and_skip_a_quoted_mark(tmp_path: Path) -> None:
    ideas = tmp_path / "idea"
    ideas.mkdir()
    path = ideas / "0001-probe.md"
    path.write_text(
        "---\ntype: idea\n---\n\n## Idea\n\n"
        "Status is computed. [clarify] Which tier counts? [unknown] Who reads it.\n\n"
        "A quoted `[clarify]` is no mark.\n",
        encoding="utf-8",
    )

    found = marks([load_record(path, "idea")], tmp_path)

    assert found == [
        Mark("clarify", "idea/0001#idea", "Which tier counts"),
        Mark("unknown", "idea/0001#idea", "Who reads it"),
    ]
