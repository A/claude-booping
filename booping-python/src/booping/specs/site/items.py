from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from booping.specs.records import load_record
from booping.specs.site.model import SiteWarning

_ITEM_FILE = re.compile(r"OI-(\d+)\.md")


@dataclass(frozen=True)
class OpenItem:
    id: str
    title: str
    # The item's `record:` ref as written, resolved by the page that links it.
    record: str | None


def load_open_items(directory: Path) -> tuple[list[OpenItem], list[SiteWarning]]:
    """The `status: open` items of `directory`, in id order; one warning per file whose
    frontmatter does not parse. A missing directory holds no items."""
    if not directory.is_dir():
        return [], []
    files = sorted(
        (int(m.group(1)), path)
        for path in directory.iterdir()
        if (m := _ITEM_FILE.fullmatch(path.name)) and path.is_file()
    )
    items: list[OpenItem] = []
    warnings: list[SiteWarning] = []
    for _, path in files:
        loaded = load_record(path, "open-item")
        if loaded.frontmatter_error is not None:
            warnings.append(
                SiteWarning(path.resolve(), loaded.frontmatter_error_line, loaded.frontmatter_error)
            )
            continue
        fm = loaded.frontmatter
        if fm.get("status") != "open":
            continue
        record = fm.get("record")
        items.append(
            OpenItem(
                id=str(fm.get("id") or path.stem),
                title=str(fm.get("title") or ""),
                record=None if record is None else str(record),
            )
        )
    return items, warnings
