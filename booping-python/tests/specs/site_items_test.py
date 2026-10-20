from __future__ import annotations

from pathlib import Path

from booping.specs.site.items import OpenItem, load_open_items


def _item(directory: Path, id_: str, status: str, record: str = "null") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{id_}.md").write_text(
        f"---\nid: {id_}\ntitle: Item {id_}\nstatus: {status}\nrecord: {record}\n---\nbody\n"
    )


def test_only_open_items_in_id_order(tmp_path: Path) -> None:
    directory = tmp_path / "open-items"
    _item(directory, "OI-0010", "open")
    _item(directory, "OI-0002", "open", "adr/0003")
    _item(directory, "OI-0003", "done")
    _item(directory, "OI-0004", "planned")
    (directory / "questions").mkdir()
    (directory / "notes.md").write_text("not an item\n")

    assert load_open_items(directory) == (
        [
            OpenItem(id="OI-0002", title="Item OI-0002", record="adr/0003"),
            OpenItem(id="OI-0010", title="Item OI-0010", record=None),
        ],
        [],
    )


def test_missing_directory_holds_nothing(tmp_path: Path) -> None:
    assert load_open_items(tmp_path / "open-items") == ([], [])


def test_unparsable_frontmatter_is_one_warning_and_no_item(tmp_path: Path) -> None:
    directory = tmp_path / "open-items"
    _item(directory, "OI-0001", "open")
    bad = directory / "OI-0002.md"
    bad.write_text("---\nid: OI-0002\ntitle: [unclosed\nstatus: open\n---\nbody\n")

    items, warnings = load_open_items(directory)

    assert [i.id for i in items] == ["OI-0001"]
    assert len(warnings) == 1
    assert warnings[0].path == bad.resolve()
