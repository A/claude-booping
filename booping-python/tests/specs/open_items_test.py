from __future__ import annotations

from pathlib import Path

from booping.context import Context
from booping.context import config as config_mod
from booping.rendering import get_plugin_root
from booping.specs.open_items import Mark, marks, write_item
from booping.specs.records import load_record

TAKEN = '---\nid: OI-0002\ntitle: "Filed by a racing writer"\n---\n'


def _stale_listing(directory: Path) -> list[str]:
    return ["OI-0001.md"]


def test_add_skips_an_id_a_stale_listing_missed(tmp_path: Path) -> None:
    items = tmp_path / "open-items"
    items.mkdir()
    (items / "OI-0001.md").write_text("---\nid: OI-0001\n---\n", encoding="utf-8")
    (items / "OI-0002.md").write_text(TAKEN, encoding="utf-8")
    ctx = Context(vault=tmp_path, config=config_mod.load(get_plugin_root(), []))

    path = write_item(
        ctx,
        title="Ship it",
        direction=None,
        record=None,
        source="request",
        body="Ship it.\n",
        listing=_stale_listing,
    )

    assert path == items / "OI-0003.md"
    assert "id: OI-0003\n" in path.read_text(encoding="utf-8")
    assert (items / "OI-0002.md").read_text(encoding="utf-8") == TAKEN


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
