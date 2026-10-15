from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from booping.specs.site.model import Site, SiteRoot, load_site
from booping.specs.site.pages import build_site

TYPES = ["value", "rule", "adr", "idea"]

RECORDS = {
    "core/value/0001-clarity.md": "---\ntitle: Clarity\nsummary: Say what you mean.\n---\nc\n",
    "core/rule/0001-small.md": (
        "---\ntitle: Small [steps] rule\nsummary: One concern per commit.\nstatus: accepted\n"
        "tags: [git, review]\nvalues: [value/0001]\n---\nr\n"
    ),
    "proj/adr/0001-old.md": "---\ntitle: Old\nsummary: First try.\nstatus: superseded\n---\no\n",
    "proj/adr/0002-new.md": (
        "---\ntitle: New\nsummary: Second try.\nstatus: accepted\nupdated_at: 2026-10-15\n"
        "supersedes: [adr/0001]\nrules: [core:rule/0001]\n---\nn [clarify]\n"
    ),
    "proj/idea/0001-hunch.md": "---\ntitle: Hunch\n---\nh\n",
}


@pytest.fixture
def roots(tmp_path: Path) -> list[SiteRoot]:
    for rel, text in RECORDS.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return [SiteRoot("core", tmp_path / "core"), SiteRoot("proj", tmp_path / "proj")]


@pytest.fixture
def site(roots: list[SiteRoot]) -> Site:
    return load_site(roots, TYPES)


def _files(site: Site) -> dict[str, str | bytes]:
    return build_site(site, TYPES, site_title="Specs")[0]


def test_llms_txt_matches_the_locked_format(site: Site) -> None:
    assert _files(site)["llms.txt"] == (
        "# Specs\n"
        "\n"
        "> Say what you mean.\n"
        "\n"
        "## Values — core\n"
        "\n"
        "- [value/0001 Clarity](core/value/0001-clarity.md): Say what you mean.\n"
        "\n"
        "## Rules — core\n"
        "\n"
        "- [rule/0001 Small \\[steps\\] rule](core/rule/0001-small.md):"
        " One concern per commit. (accepted; git, review)\n"
        "\n"
        "## ADRs — proj\n"
        "\n"
        "- [adr/0001 Old](proj/adr/0001-old.md): First try. (superseded)\n"
        "- [adr/0002 New](proj/adr/0002-new.md): Second try. (accepted)\n"
        "\n"
        "## Ideas — proj\n"
        "\n"
        "- [idea/0001 Hunch](proj/idea/0001-hunch.md)\n"
    )


def test_llms_txt_without_a_value_summary_has_no_blockquote(tmp_path: Path) -> None:
    path = tmp_path / "s" / "idea" / "0001-hunch.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\ntitle: Hunch\n---\nh\n")
    site = load_site([SiteRoot("s", tmp_path / "s")], TYPES)
    assert _files(site)["llms.txt"] == (
        "# Specs\n\n## Ideas — s\n\n- [idea/0001 Hunch](s/idea/0001-hunch.md)\n"
    )


def _records(site: Site) -> list[dict[str, Any]]:
    text = _files(site)["index.json"]
    assert isinstance(text, str)
    document = json.loads(text)
    assert list(document) == ["title", "lang", "records"]
    assert (document["title"], document["lang"]) == ("Specs", "en")
    return document["records"]


def test_index_json_holds_every_record_once_in_page_order(site: Site) -> None:
    assert [r["id"] for r in _records(site)] == [
        "core:value/0001",
        "core:rule/0001",
        "proj:adr/0001",
        "proj:adr/0002",
        "proj:idea/0001",
    ]


def test_index_json_record_fields(site: Site) -> None:
    by_id = {r["id"]: r for r in _records(site)}
    assert by_id["proj:adr/0002"] == {
        "id": "proj:adr/0002",
        "root": "proj",
        "ref": "adr/0002",
        "type": "adr",
        "title": "New",
        "summary": "Second try.",
        "status": "accepted",
        "kind": None,
        "tags": [],
        "created_by": None,
        "created_at": None,
        "updated_at": "2026-10-15",
        "reviewed": None,
        "url": "proj/adr/0002-new.html",
        "md": "proj/adr/0002-new.md",
        "marks": {"clarify": 1, "unknown": 0},
        "relations": {"rules": ["core:rule/0001"], "supersedes": ["proj:adr/0001"]},
        "superseded_by": [],
        "backlinks": [],
    }
    assert list(by_id["proj:adr/0002"]) == list(by_id["proj:idea/0001"])
    assert by_id["proj:adr/0001"]["superseded_by"] == ["proj:adr/0002"]
    assert by_id["core:rule/0001"]["backlinks"] == ["proj:adr/0002"]
    assert by_id["core:rule/0001"]["tags"] == ["git", "review"]
    assert by_id["proj:idea/0001"]["summary"] is None
    assert by_id["proj:idea/0001"]["relations"] == {}


def test_index_json_is_indented_unescaped_and_newline_terminated(tmp_path: Path) -> None:
    path = tmp_path / "s" / "value" / "0001-clarity.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\ntitle: Ясность\n---\nя\n")
    text = _files(load_site([SiteRoot("s", tmp_path / "s")], TYPES))["index.json"]
    assert isinstance(text, str)
    assert '\n   "title": "Ясность",\n' in text
    assert text.endswith("}\n") and not text.endswith("\n\n")


def test_machine_files_are_repeatable(site: Site, roots: list[SiteRoot]) -> None:
    first, second = _files(site), _files(load_site(roots, TYPES))
    assert first["llms.txt"] == second["llms.txt"]
    assert first["index.json"] == second["index.json"]
