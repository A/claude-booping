from __future__ import annotations

import json
import shutil
import subprocess
from importlib.resources import files
from pathlib import Path
from typing import Any

import pytest

from booping.specs.site.model import SiteRoot, load_site
from booping.specs.site.pages import build_site

ROOT = "https://s.example/specs/"
ALPHA = "https://s.example/specs/proj/adr/0001-alpha.html"

_RUNNER = """
const fs = require("fs");
const vm = require("vm");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const ctx = {};
vm.runInNewContext(input.source, ctx);
process.stdout.write(ctx.SpecsComments.format(input.comments, input.siteRoot));
"""


def _source() -> str:
    return files("booping.specs.site").joinpath("comments-format.js").read_text()


def _format(comments: list[dict[str, Any]], site_root: str = ROOT) -> str:
    node = shutil.which("node")
    if node is None:
        pytest.fail(
            "node is not on PATH: the comment export tests run comments-format.js under node"
        )
    stdin = json.dumps({"source": _source(), "comments": comments, "siteRoot": site_root})
    done = subprocess.run(
        [node, "-e", _RUNNER], input=stdin, capture_output=True, text=True, check=True
    )
    return done.stdout


def _comment(**fields: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "c1",
        "ref": "adr/0001",
        "title": "Alpha",
        "page": "proj/adr/0001-alpha.html",
        "anchor": "decision",
        "anchorText": "Decision",
        "kind": "span",
        "quote": "quoted",
        "note": "noted",
        "created": "2026-10-16T10:00:00.000Z",
        "sent": False,
    }
    return {**base, **fields}


def test_records_by_ref_and_comments_by_created_then_id() -> None:
    comments = [
        _comment(
            id="r1",
            ref="rule/0002",
            title="Beta",
            page="proj/rule/0002-beta.html",
            anchor="why",
            anchorText="Why",
            quote="third",
            note="three",
        ),
        _comment(id="a2", quote="second", note="two", created="2026-10-16T10:05:00.000Z"),
        _comment(id="a9", quote="first", note="one", created="2026-10-16T10:01:00.000Z"),
        _comment(id="a1", quote="first tie", note="one tie", created="2026-10-16T10:01:00.000Z"),
    ]
    assert _format(comments) == (
        "## adr/0001 — Alpha\n"
        "\n"
        f"[§ Decision]({ALPHA}#decision)\n"
        "\n"
        "> first tie\n"
        "\n"
        "one tie\n"
        "\n"
        f"[§ Decision]({ALPHA}#decision)\n"
        "\n"
        "> first\n"
        "\n"
        "one\n"
        "\n"
        f"[§ Decision]({ALPHA}#decision)\n"
        "\n"
        "> second\n"
        "\n"
        "two\n"
        "\n"
        "## rule/0002 — Beta\n"
        "\n"
        "[§ Why](https://s.example/specs/proj/rule/0002-beta.html#why)\n"
        "\n"
        "> third\n"
        "\n"
        "three\n"
    )


def test_section_comment_quotes_the_heading() -> None:
    comment = _comment(
        kind="section", anchor="context", anchorText="Context", quote="Context", note="Expand."
    )
    assert _format([comment]) == (
        f"## adr/0001 — Alpha\n\n[§ Context]({ALPHA}#context)\n\n> Context\n\nExpand.\n"
    )


def test_comment_above_the_first_heading_links_the_record_title() -> None:
    comment = _comment(anchor="", anchorText="", quote="Intro.", note="Why?")
    assert _format([comment]) == (f"## adr/0001 — Alpha\n\n[Alpha]({ALPHA})\n\n> Intro.\n\nWhy?\n")


def test_quote_lines_are_trimmed_and_blank_ones_dropped() -> None:
    comment = _comment(quote="  first line\n\n    indented\r\n   \nlast  ")
    assert _format([comment]) == (
        f"## adr/0001 — Alpha\n\n[§ Decision]({ALPHA}#decision)\n\n"
        "> first line\n> indented\n> last\n\nnoted\n"
    )


def test_note_keeps_inner_breaks_and_drops_trailing_whitespace() -> None:
    comment = _comment(note="Line one  \nline two   \n  ")
    assert _format([comment]) == (
        f"## adr/0001 — Alpha\n\n[§ Decision]({ALPHA}#decision)\n\n"
        "> quoted\n\nLine one  \nline two\n"
    )


def test_cyrillic_anchor_stays_raw_and_parens_and_percent_are_encoded() -> None:
    page = "proj/adr/0003-elka.html"
    comments = [
        _comment(
            id="e1",
            ref="adr/0003",
            title="Решение про ёлку",
            page=page,
            anchor="почему-так",
            anchorText="Почему так",
            quote="Ёлка нужна.",
            note="Точно?",
        ),
        _comment(
            id="e2",
            ref="adr/0003",
            title="Решение про ёлку",
            page=page,
            anchor="fix-(a)-50% off",
            anchorText="Fix (a) 50% off",
            quote="Option.",
            note="Pick it.",
            created="2026-10-16T11:00:00.000Z",
        ),
    ]
    url = f"https://s.example/specs/{page}"
    assert _format(comments) == (
        "## adr/0003 — Решение про ёлку\n"
        "\n"
        f"[§ Почему так]({url}#почему-так)\n"
        "\n"
        "> Ёлка нужна.\n"
        "\n"
        "Точно?\n"
        "\n"
        f"[§ Fix (a) 50% off]({url}#fix-%28a%29-50%25%20off)\n"
        "\n"
        "> Option.\n"
        "\n"
        "Pick it.\n"
    )


def test_no_comments_is_an_empty_string() -> None:
    assert _format([]) == ""


def test_built_site_ships_the_file_verbatim(tmp_path: Path) -> None:
    record = tmp_path / "s" / "adr" / "0001-a.md"
    record.parent.mkdir(parents=True)
    record.write_text("---\ntitle: A\n---\nx\n")
    built, _ = build_site(load_site([SiteRoot("s", tmp_path / "s")], ["adr"]), ["adr"])
    assert built["comments-format.js"] == _source()
