from __future__ import annotations

import json
import posixpath
import re
from pathlib import Path

import pytest

from booping.specs.site.items import OpenItem
from booping.specs.site.model import SiteRoot, load_site
from booping.specs.site.pages import build_site

TYPES = ["value", "adr", "rule"]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _site(tmp_path: Path, open_items: list[OpenItem]) -> dict[str, str]:
    """Core root `booping` (a reviewed value, an unreviewed rule) and the home root
    `proj` (a reviewed rule citing booping's rule, an ADR with a question)."""
    _write(
        tmp_path / "core" / "value" / "0001-clarity.md",
        "---\ntitle: Clarity\nkind: value\nreviewed: 2026-10-01\nupdated_at: 2026-10-05\n---\n",
    )
    _write(
        tmp_path / "core" / "rule" / "0001-small.md",
        "---\ntitle: Small\nstatus: accepted\nupdated_at: 2026-10-04\n---\n",
    )
    _write(
        tmp_path / "proj" / "rule" / "0001-linear.md",
        "---\ntitle: Linear\nstatus: accepted\nreviewed: 2026-10-02\nupdated_at: 2026-10-02\n"
        "related: [booping:rule/0001]\n---\n",
    )
    _write(
        tmp_path / "proj" / "adr" / "0001-pick.md",
        "---\ntitle: Pick\nstatus: accepted\nreviewed: 2026-10-03\nupdated_at: 2026-10-03\n---\n"
        "We [clarify] this.\n",
    )
    site = load_site(
        [SiteRoot("booping", tmp_path / "core"), SiteRoot("proj", tmp_path / "proj")], TYPES
    )
    files, _ = build_site(site, TYPES, home="proj", open_items=open_items, items_root="proj")
    return {path: text for path, text in files.items() if isinstance(text, str)}


@pytest.fixture
def pages(tmp_path: Path) -> dict[str, str]:
    return _site(tmp_path, [])


def _main(page: str) -> str:
    return page.split('<main id="main">', 1)[1]


def _cards(html: str) -> list[tuple[str, str, str]]:
    return re.findall(r'<li><a href="([^"]+)"><b>([^<]+) <span class="n">(\d+)</span></b>', html)


def _refs(html: str) -> list[str]:
    return re.findall(r'<code class="ref">([^<]+)</code>', html)


def _crumbs(page: str) -> list[str]:
    crumbs = page.split('<nav class="crumbs"', 1)[1].split("</nav>", 1)[0]
    return re.findall(r"<li[^>]*>(?:<a [^>]+>|<span[^>]*>)([^<]+)<", crumbs)


def test_overview_counts_the_home_registry_and_gives_another_root_its_own_block(
    pages: dict[str, str],
) -> None:
    own, other = _main(pages["index.html"]).split('<section class="registry"', 1)
    assert _cards(own) == [
        ("proj/adr/index.html", "ADRs", "1"),
        ("proj/rule/index.html", "Rules", "1"),
    ]
    assert re.findall(r'<p class="callout">.*?<a href="([^"]+)">([^<]+)</a>(.*?)</span>', own) == [
        ("review.html#source=proj", "1 needs you →", " · 1 open question")
    ]
    assert _refs(own) == ["adr/0001", "rule/0001"]
    assert re.search(
        r'<h2 id="registry-booping"><a href="booping/index.html">booping</a> '
        r'<span class="n">2</span></h2>',
        other,
    )
    assert _cards(other) == [
        ("booping/value/index.html", "Values", "1"),
        ("booping/rule/index.html", "Rules", "1"),
    ]
    assert re.findall(
        r'<p class="callout">.*?<a href="([^"]+)">([^<]+)</a>(.*?)</span>', other
    ) == [("review.html#source=booping", "1 needs you →", " · 1 unreviewed")]
    assert "recent" not in other


def test_records_of_another_root_show_their_namespaced_id_in_every_list(
    pages: dict[str, str],
) -> None:
    assert _refs(pages["records.html"]) == [
        "booping:value/0001",
        "booping:rule/0001",
        "adr/0001",
        "rule/0001",
    ]
    assert _refs(pages["review.html"]) == ["booping:rule/0001", "adr/0001"]
    assert _refs(pages["booping/rule/index.html"]) == ["booping:rule/0001"]
    assert _refs(pages["booping/index.html"]) == ["booping:value/0001", "booping:rule/0001"]
    index = json.loads(pages["search-index.js"].split("=", 1)[1].rstrip(";\n"))
    assert [entry["ref"] for entry in index] == [
        "booping:value/0001",
        "booping:rule/0001",
        "adr/0001",
        "rule/0001",
    ]


def test_record_pages_show_namespaced_ids_in_crumbs_relations_and_backlinks(
    pages: dict[str, str],
) -> None:
    core = pages["booping/rule/0001-small.html"]
    assert _crumbs(core) == ["Overview", "booping", "Rules", "booping:rule/0001"]
    assert 'data-ref="booping:rule/0001"' in core
    assert _refs(_main(core)) == ["rule/0001"]
    own = pages["proj/rule/0001-linear.html"]
    assert _crumbs(own) == ["Overview", "Rules", "rule/0001"]
    assert 'data-ref="rule/0001"' in own
    assert _refs(_main(own)) == ["booping:rule/0001"]


def test_home_root_page_redirects_to_the_overview_and_nothing_links_it(
    pages: dict[str, str],
) -> None:
    redirect = pages["proj/index.html"]
    assert '<meta http-equiv="refresh" content="0; url=../index.html">' in redirect
    assert '<a href="../index.html">Overview</a>' in redirect
    linked = {
        posixpath.normpath(posixpath.join(posixpath.dirname(path), href.partition("#")[0]))
        for path, text in pages.items()
        if path.endswith(".html")
        for href in re.findall(r'href="([^"#]+)', text)
    }
    assert "proj/index.html" not in linked
    assert "booping/index.html" in linked


def test_sidebar_counts_home_types_and_groups_another_root(pages: dict[str, str]) -> None:
    side = pages["records.html"].split('<nav class="side"', 1)[1].split("</nav>", 1)[0]
    groups = re.findall(r"<h4>([^<]+)</h4>\s*<ul>(.*?)</ul>", side, re.S)
    entries = {
        heading: re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)(?:<span class="n">(\d+))?', body)
        for heading, body in groups
    }
    assert list(entries) == ["Types", "booping"]
    assert entries["Types"] == [
        ("proj/adr/index.html", "ADRs", "1"),
        ("proj/rule/index.html", "Rules", "1"),
    ]
    assert entries["booping"] == [
        ("booping/index.html", "Overview", ""),
        ("booping/value/index.html", "Values", "1"),
        ("booping/rule/index.html", "Rules", "1"),
    ]


def test_open_items_count_toward_the_home_registry(tmp_path: Path) -> None:
    pages = _site(tmp_path, [OpenItem("OI-1", "Decide", "adr/0001")])
    own = _main(pages["index.html"]).split('<section class="registry"', 1)[0]
    assert re.findall(r'<a href="(review.html[^"]*)">([^<]+)</a>', own) == [
        ("review.html#source=proj", "2 need you →")
    ]
    assert re.findall(r'data-source="([^"]*)"', pages["review.html"]) == [
        "booping",
        "proj",
        "proj",
    ]
