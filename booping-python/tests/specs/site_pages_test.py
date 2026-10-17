from __future__ import annotations

import posixpath
import re
from collections.abc import Callable
from html.parser import HTMLParser
from pathlib import Path

import pytest

from booping.specs.site import pages as site_pages
from booping.specs.site.index import Project, build_index
from booping.specs.site.items import OpenItem
from booping.specs.site.labels import load_labels
from booping.specs.site.model import Site, SiteRoot, load_site
from booping.specs.site.pages import SiteWarning, build_site, environment
from booping.specs.site.write import SiteError, write_site

TYPES = ["value", "adr"]

ADR = (
    "---\n"
    "title: Pick\n"
    "status: accepted\n"
    "values:\n"
    "- core:value/0001\n"
    "- core:value/0009\n"
    "---\n"
    "See [why](../../core/value/0001-clarity.md#why) and [top](#decision).\n"
    "\n"
    "We [clarify] this.\n"
    "\n"
    "Broken [gone](missing.md).\n"
    "\n"
    "## Decision\n"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _roots(tmp_path: Path) -> list[SiteRoot]:
    return [SiteRoot("core", tmp_path / "core"), SiteRoot("proj", tmp_path / "proj")]


@pytest.fixture
def roots(tmp_path: Path) -> list[SiteRoot]:
    _write(
        tmp_path / "core" / "value" / "0001-clarity.md",
        "---\ntitle: Clarity\nkind: value\nreviewed: 2026-10-01\n---\n"
        "# Clarity\n\n## Why\n\nBecause.\n",
    )
    _write(tmp_path / "proj" / "adr" / "0001-pick.md", ADR)
    return _roots(tmp_path)


@pytest.fixture
def site(roots: list[SiteRoot]) -> Site:
    return load_site(roots, TYPES)


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()
        self.scripts = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self.scripts += 1
        for name, value in attrs:
            if name in ("href", "src") and value is not None:
                self.hrefs.append(value)
            elif name == "id" and value is not None:
                self.ids.add(value)


def _texts(site: Site) -> dict[str, str]:
    files, _ = build_site(site, TYPES)
    return {path: text for path, text in files.items() if isinstance(text, str)}


def _parse(html: str) -> _Links:
    parser = _Links()
    parser.feed(html)
    return parser


def _check_links(files: dict[str, str | bytes]) -> int:
    """Every relative href and src lands on a written file, and its fragment on an id."""
    pages = {
        path: _parse(text)
        for path, text in files.items()
        if path.endswith(".html") and isinstance(text, str)
    }
    checked = 0
    for path, parsed in pages.items():
        text = files[path]
        assert isinstance(text, str)
        extra = 2 if 'class="filters"' in text else 2 if path == "search.html" else 0
        assert parsed.scripts == 5 + extra, path
        for href in parsed.hrefs:
            assert "://" not in href and not href.startswith("/"), (path, href)
            target, _, fragment = href.partition("#")
            if target:
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                assert target in files, (path, href)
            else:
                target = path
            # A `key=value` fragment is list filter state, not an element id.
            if fragment and "=" not in fragment:
                assert fragment in pages[target].ids, (path, href)
            checked += 1
    return checked


def test_every_relative_link_lands_on_a_page_and_id(site: Site) -> None:
    assert _check_links(build_site(site, TYPES)[0]) > 20


def test_page_map_paths(site: Site) -> None:
    files, _ = build_site(site, TYPES)
    assert sorted(files) == [
        "comments-format.js",
        "comments.html",
        "comments.js",
        "core/index.html",
        "core/value/0001-clarity.html",
        "core/value/0001-clarity.md",
        "core/value/index.html",
        "filter-format.js",
        "filter.js",
        "fonts.css",
        "fonts/OFL-golos-text.txt",
        "fonts/OFL-jetbrains-mono.txt",
        "index.html",
        "index.json",
        "llms.txt",
        "proj/adr/0001-pick.html",
        "proj/adr/0001-pick.md",
        "proj/adr/index.html",
        "proj/index.html",
        "records.html",
        "review.html",
        "search-body.js",
        "search-index.js",
        "search.html",
        "search.js",
        "site.js",
        "style.css",
    ]


def test_build_is_repeatable(site: Site, roots: list[SiteRoot]) -> None:
    assert build_site(site, TYPES) == build_site(load_site(roots, TYPES), TYPES)


def _two_root_site(tmp_path: Path) -> dict[str, str]:
    reviewed = "reviewed: 2026-10-01\n"
    _write(
        tmp_path / "a" / "value" / "0001-x.md",
        f"---\ntitle: X\nupdated_at: 2026-09-01\n{reviewed}---\nx\n",
    )
    # Two records of root `a` need review: one unreviewed with a [clarify], one with a [clarify].
    _write(
        tmp_path / "a" / "adr" / "0001-p.md",
        "---\ntitle: P\nupdated_at: 2026-09-03\n---\n[clarify] p\n",
    )
    _write(
        tmp_path / "a" / "adr" / "0002-q.md",
        f"---\ntitle: Q\nupdated_at: 2026-09-02\n{reviewed}---\n[clarify] q\n",
    )
    _write(
        tmp_path / "b" / "adr" / "0001-r.md",
        f"---\ntitle: R\nupdated_at: 2026-09-05\n{reviewed}---\nr\n",
    )
    roots = [SiteRoot("a", tmp_path / "a"), SiteRoot("b", tmp_path / "b")]
    return _texts(load_site(roots, TYPES))


def test_root_page_is_the_overview_landing_for_that_root(tmp_path: Path) -> None:
    files = _two_root_site(tmp_path)
    page = files["a/index.html"]
    main = page[page.index('<main id="main">') :]
    callout = re.search(
        r'<p class="callout">.*?<span><a href="([^"]+)">([^<]+)</a>([^<]*)</span>', main
    )
    assert callout is not None
    assert callout.groups() == (
        "../review.html#source=a",
        "2 need you →",
        " · 1 unreviewed · 2 open questions",
    )
    measures = re.findall(r'<div class="measure">\n(.*?)\n</div>', main, flags=re.S)
    assert len(measures) == 2
    assert measures[0].startswith("<h1>a</h1>\n")
    assert 'class="callout"' in measures[0]
    assert '<p class="lead">' not in main
    assert re.findall(
        r'<li><a href="([^"]+)"><b>([^<]+) <span class="n">(\d+)</span></b>', main
    ) == [("value/index.html", "Values", "1"), ("adr/index.html", "ADRs", "2")]
    assert "<h2>Recently updated</h2>" in measures[1]
    assert re.findall(
        r'<li><code class="ref">([^<]+)</code><a href="([^"]+)">[^<]+</a>'
        r'<time datetime="([^"]+)">',
        measures[1],
    ) == [
        ("adr/0001", "../a/adr/0001-p.html", "2026-09-03"),
        ("adr/0002", "../a/adr/0002-q.html", "2026-09-02"),
        ("value/0001", "../a/value/0001-x.html", "2026-09-01"),
    ]
    assert 'class="mark"' not in main
    assert "Records:" not in main


def test_root_page_with_nothing_to_review_has_no_callout(tmp_path: Path) -> None:
    page = _two_root_site(tmp_path)["b/index.html"]
    main = page[page.index('<main id="main">') :]
    assert 'class="callout"' not in main
    assert re.findall(r'<li><a href="([^"]+)"><b>', main) == ["adr/index.html"]
    assert '<a href="../b/adr/0001-r.html">R</a>' in main


def test_value_page_lists_cross_root_backlink(site: Site) -> None:
    files = _texts(site)
    assert (
        '<li><a href="../../proj/adr/0001-pick.html">Pick</a>'
        ' <code class="ref">proj:adr/0001</code> <span class="b ok">'
    ) in files["core/value/0001-clarity.html"]
    assert "Nothing references this record." in files["proj/adr/0001-pick.html"]


def test_record_page_links_refs_and_body(site: Site) -> None:
    page = _texts(site)["proj/adr/0001-pick.html"]
    assert (
        '<dt>Serves values</dt>\n<dd><ul class="rel">\n'
        '<li><a href="../../core/value/0001-clarity.html">Clarity</a>'
        ' <code class="ref">core:value/0001</code></li>\n'
        '<li><code class="unresolved">core:value/0009</code></li>\n'
    ) in page
    assert '<a href="../../core/value/0001-clarity.html#why">why</a>' in page
    assert '<span class="unresolved">gone</span>' in page
    badges = re.findall(r"<span class=\"b ([a-z]+)\">(?:<svg[^>]*>.*?</svg>)([^<]+)</span>", page)
    assert badges == [("ok", "accepted"), ("warn", "1 question for you"), ("plain", "unreviewed")]


def test_type_page_is_one_row_per_record_without_bodies(tmp_path: Path) -> None:
    page = _record_page(tmp_path)["s/adr/index.html"]
    assert page.count('<li class="row"') == 2
    assert re.findall(r'<a class="t" href="([^"]+)">([^<]+)</a>', page) == [
        ("../../s/adr/0001-robot.html", "Robot"),
        ("../../s/adr/0002-chassis.html", "Chassis"),
    ]
    assert '<p class="lead">why it was decided so</p>' in page
    assert "Intro." not in page
    assert "<article" not in page


def test_value_kind_is_a_raw_row_and_reviewed_hides_unreviewed(site: Site) -> None:
    page = _texts(site)["core/value/0001-clarity.html"]
    assert "<dt>kind</dt>\n<dd>value</dd>" in page
    assert '<dt>Reviewed</dt>\n<dd><time datetime="2026-10-01">1 October 2026</time></dd>' in page
    assert '<div class="badges">' not in page


def test_no_page_holds_a_table(site: Site) -> None:
    files = _texts(site)
    home = files["index.html"]
    assert re.findall(r"<h2>([^<]+)</h2>", home) == []
    assert '<ul class="types">' not in home
    assert all("<table" not in html for path, html in files.items() if path.endswith(".html"))


def test_warnings_once_per_record_sorted(site: Site, tmp_path: Path) -> None:
    adr = (tmp_path / "proj" / "adr" / "0001-pick.md").resolve()
    assert build_site(site, TYPES)[1] == [
        SiteWarning(adr, 6, "unresolved ref core:value/0009"),
        SiteWarning(adr, 12, "unresolved link missing.md"),
    ]


def _refusal_file(tmp_path: Path) -> Path:
    out = tmp_path / "out"
    out.write_text("keep\n")
    return out


def _refusal_inside_root(tmp_path: Path) -> Path:
    return tmp_path / "proj" / "site"


def _refusal_contains_root(tmp_path: Path) -> Path:
    _write(tmp_path / ".booping-site", "booping specs site\n")
    return tmp_path


def _refusal_unmarked(tmp_path: Path) -> Path:
    out = tmp_path / "out"
    _write(out / "mine.txt", "keep\n")
    return out


def _snapshot(base: Path) -> dict[str, str]:
    return {
        str(p.relative_to(base)): p.read_text() if p.is_file() else ""
        for p in sorted(base.rglob("*"))
    }


@pytest.mark.parametrize(
    ("make_out", "message"),
    [
        (_refusal_file, "is a file"),
        (_refusal_inside_root, "is inside root proj"),
        (_refusal_contains_root, "contains root core"),
        (_refusal_unmarked, "is not empty and has no .booping-site marker"),
    ],
)
def test_write_site_refuses(
    site: Site,
    roots: list[SiteRoot],
    tmp_path: Path,
    make_out: Callable[[Path], Path],
    message: str,
) -> None:
    out = make_out(tmp_path)
    before = _snapshot(tmp_path)
    files, _ = build_site(site, TYPES)
    with pytest.raises(SiteError) as exc:
        write_site(files, out, roots)
    assert message in str(exc.value)
    assert str(out) in str(exc.value)
    assert "\n" not in str(exc.value)
    assert _snapshot(tmp_path) == before


def test_rewrite_over_marker_drops_deleted_record(
    site: Site, roots: list[SiteRoot], tmp_path: Path
) -> None:
    out = tmp_path / "out"
    write_site(build_site(site, TYPES)[0], out, roots)
    assert (out / ".booping-site").read_text() == "booping specs site\n"
    assert (out / "proj" / "adr" / "0001-pick.html").is_file()

    (tmp_path / "proj" / "adr" / "0001-pick.md").unlink()
    write_site(build_site(load_site(roots, TYPES), TYPES)[0], out, roots)
    assert not (out / "proj" / "adr").exists()
    assert (out / "core" / "value" / "0001-clarity.html").is_file()
    assert (out / ".booping-site").read_text() == "booping specs site\n"


def test_marker_precedes_pages_so_a_failed_run_is_clearable(
    roots: list[SiteRoot], tmp_path: Path
) -> None:
    out = tmp_path / "out"
    with pytest.raises(OSError):
        write_site({"a": "page\n", "a/b": "unwritable\n"}, out, roots)
    assert (out / ".booping-site").is_file()
    write_site({"index.html": "ok\n"}, out, roots)
    assert sorted(p.name for p in out.iterdir()) == [".booping-site", "index.html"]


def test_icon_sprite_holds_fifteen_unique_symbols() -> None:
    labels, lang, _ = load_labels({})
    sprite = environment(labels, lang, "Specs").get_template("_icons.html.j2").render()
    ids = re.findall(r'<symbol id="([^"]+)"', sprite)
    assert len(ids) == 15
    assert len(set(ids)) == 15
    assert {"i-sun", "i-auto", "i-moon", "i-clarify", "i-comment", "i-outbox"} <= set(ids)


def test_state_badges_pair_every_icon_with_text() -> None:
    labels, lang, _ = load_labels({"lang": "ru"})
    html = (
        environment(labels, lang, "Specs")
        .from_string(
            '{% from "_macros.html.j2" import state_badges %}{{ state_badges(state, labels) }}'
        )
        .render(state={"status": "accepted", "clarify": 3, "unknown": 1, "unreviewed": True})
    )
    badges = re.findall(r'<span class="b ([a-z]+)">(<svg[^>]*>.*?</svg>)([^<]+)</span>', html)
    assert [(css, text) for css, _, text in badges] == [
        ("ok", "принято"),
        ("warn", "3 вопроса к тебе"),
        ("bad", "[unknown]"),
        ("plain", "без ревью"),
    ]
    assert all('aria-hidden="true"' in svg for _, svg, _ in badges)


def test_every_page_sits_in_the_shell(site: Site) -> None:
    files = _texts(site)
    depths: set[int] = set()
    for path, html in files.items():
        if not path.endswith(".html"):
            continue
        prefix = "../" * path.count("/")
        depths.add(path.count("/"))
        assert html.count('<main id="main">') == 1, path
        assert html.count('<a class="skip" href="#main">') == 1, path
        assert '<html lang="en">' in html, path
        assert f'<link rel="stylesheet" href="{prefix}fonts.css">' in html, path
        assert f'<link rel="stylesheet" href="{prefix}style.css">' in html, path
        assert f'<script src="{prefix}site.js" defer></script>' in html, path
        assert html.index("<script>") < html.index('<link rel="stylesheet"'), path
        assert "<footer>Generated by booping specs site</footer>" in html, path
    assert depths == {0, 1, 2}


def _side(page: str) -> str:
    start = page.index('<nav class="side"')
    return page[start : page.index("</nav>", start)]


def _side_links(side: str) -> list[tuple[str, str, str]]:
    return [
        (href, re.sub(r"<[^>]+>", "", label), count)
        for href, label, count in re.findall(
            r'<a href="([^"]+)"[^>]*>(.*?)(?:<span class="n">(\d+)</span>)?</a>', side
        )
    ]


def test_sidebar_holds_the_groups_in_order_with_counts(site: Site) -> None:
    files, _ = build_site(site, TYPES, open_items=[OpenItem("OI-0001", "Ask", None)])
    page = files["proj/adr/index.html"]
    assert isinstance(page, str)
    side = _side(page)
    assert re.findall(r"<h4>([^<]+)</h4>", side) == ["Types", "Sources"]
    # The ADR is unreviewed with a clarify mark, the value is reviewed: 1 record + 1 item.
    assert _side_links(side) == [
        ("../../index.html", "Overview", ""),
        ("../../review.html", "Awaiting review", "2"),
        ("../../records.html", "All records", "2"),
        ("../../records.html#type=value", "Values", "1"),
        ("../../records.html#type=adr", "ADRs", "1"),
        ("../../core/index.html", "core", "1"),
        ("../../proj/index.html", "proj", "1"),
        ("../../llms.txt", "llms.txt", ""),
    ]
    assert 'aria-current="page"' not in side
    assert '<a href="records.html" aria-current="page">' in _side(_texts(site)["records.html"])


def test_sidebar_tags_group_per_root_with_top_level_counts(tmp_path: Path) -> None:
    _write(tmp_path / "core" / "value" / "0001-a.md", "---\ntitle: A\ntags: [ux:nav]\n---\nx\n")
    _write(tmp_path / "core" / "value" / "0002-b.md", "---\ntitle: B\ntags: [ux]\n---\nx\n")
    _write(tmp_path / "proj" / "adr" / "0001-c.md", "---\ntitle: C\ntags: [ops]\n---\nx\n")
    _write(tmp_path / "core" / "tags.yaml", "ux: UX\nidle: Nobody carries it\n")
    pages = _texts(load_site(_roots(tmp_path), TYPES))
    side = _side(pages["index.html"])
    assert re.findall(r"<h4>([^<]+)</h4>", side) == ["Types", "Tags", "Sources"]
    assert re.findall(r"<h5>([^<]+)</h5>", side) == ["core", "proj"]
    tags = side[side.index("<h4>Tags</h4>") : side.index("<h4>Sources</h4>")]
    assert _side_links(tags) == [
        ("core/tags/ux.html", "ux", "2"),
        ("core/tags/index.html", "All tags", ""),
        ("proj/tags/ops.html", "ops", "1"),
        ("proj/tags/index.html", "All tags", ""),
    ]
    assert '<a href="core/tags/ux.html">ux<span class="n">2</span></a>' in tags
    assert "<code>" not in tags
    assert "idle" not in side
    assert 'href="idle.html"' in pages["core/tags/index.html"]


def test_sidebar_tags_have_no_root_heading_with_one_tagged_root(tmp_path: Path) -> None:
    _write(tmp_path / "core" / "value" / "0001-a.md", "---\ntitle: A\ntags: [ux]\n---\nx\n")
    _write(tmp_path / "proj" / "adr" / "0001-c.md", "---\ntitle: C\n---\nx\n")
    side = _side(_texts(load_site(_roots(tmp_path), TYPES))["index.html"])
    assert "<h5>" not in side
    assert '<a href="core/tags/ux.html">ux<span class="n">1</span></a>' in side


ROW_DATA = re.compile(
    r'<li class="row" data-type="([^"]*)" data-source="([^"]*)" data-status="([^"]*)"'
    r' data-flags="([^"]*)" data-updated="([^"]*)" data-title="([^"]*)"'
    r' data-created-by="([^"]*)" data-order="(\d+)">'
)


def test_rows_carry_the_filter_data(tmp_path: Path) -> None:
    pages = _record_page(tmp_path)
    robot = ("adr", "s", "superseded", "unreviewed clarify", "2026-10-15", "Robot", "claude")
    chassis = ("adr", "s", "", "unreviewed", "", "Chassis", "")
    craft = ("value", "s", "accepted", "unreviewed", "", "Craft", "")
    type_page = pages["s/adr/index.html"]
    assert ROW_DATA.findall(type_page) == [(*robot, "0"), (*chassis, "1")]
    assert type_page.count('<li class="row"') == 2
    records = pages["records.html"]
    assert ROW_DATA.findall(records) == [(*craft, "0"), (*robot, "1"), (*chassis, "2")]
    assert records.count('<li class="row"') == 3


def test_all_records_lists_every_root_in_page_order(site: Site) -> None:
    page = _texts(site)["records.html"]
    assert re.findall(r'<a class="t" href="([^"]+)">([^<]+)</a>', page) == [
        ("core/value/0001-clarity.html", "Clarity"),
        ("proj/adr/0001-pick.html", "Pick"),
    ]
    assert "<h1>All records</h1>" in page
    assert (
        '<li><a href="index.html">Overview</a></li>\n'
        '<li><span aria-current="page">All records</span></li>'
    ) in page


def test_new_navigation_labels_resolve_from_the_russian_table(tmp_path: Path) -> None:
    page = _record_page(tmp_path, "ru")["records.html"]
    for english in ("Navigation", "Awaiting review", "All records", "Tags", "All tags", "Sources"):
        assert f">{english}<" not in page
        assert f'"{english}"' not in page
    assert "<h1>Все записи</h1>" in page
    assert re.findall(r"<h4>([^<]+)</h4>", _side(page)) == ["Разделы", "Теги", "Источники"]


def test_crumbs_are_an_ordered_list_with_the_current_page_last(site: Site) -> None:
    page = _texts(site)["proj/adr/0001-pick.html"]
    assert (
        '<nav class="crumbs" aria-label="breadcrumb">\n<ol>\n'
        '<li><a href="../../index.html">Overview</a></li>\n'
        '<li class="mid"><a href="../index.html">proj</a></li>\n'
        '<li class="mid"><a href="index.html">ADRs</a></li>\n'
        '<li><span aria-current="page">adr/0001</span></li>\n'
        "</ol>\n</nav>"
    ) in page


def _record_page(tmp_path: Path, lang: str = "en") -> dict[str, str]:
    _write(
        tmp_path / "s" / "value" / "0001-craft.md", "---\ntitle: Craft\nstatus: accepted\n---\nc\n"
    )
    _write(
        tmp_path / "s" / "adr" / "0001-robot.md",
        "---\ntitle: Robot\nstatus: superseded\ncreated_by: claude\nupdated_at: 2026-10-15\n"
        "values: [value/0001]\ntags: [robot]\ntargets: [develop]\n---\n"
        "Intro.\n\nWho swaps [clarify] slots?\n",
    )
    _write(
        tmp_path / "s" / "adr" / "0002-chassis.md",
        "---\ntitle: Chassis\nsupersedes: [adr/0001]\n---\nx\n",
    )
    labels, lang, _ = load_labels({"lang": lang})
    files, _ = build_site(load_site([SiteRoot("s", tmp_path / "s")], TYPES), TYPES, labels, lang)
    return {path: text for path, text in files.items() if isinstance(text, str)}


def test_record_page_head_facts_and_relations_in_russian(tmp_path: Path) -> None:
    page = _record_page(tmp_path, "ru")["s/adr/0001-robot.html"]
    facts = page[page.index('<dl class="facts">') : page.index("</dl>")]
    assert re.findall(r"<dt>([^<]+)</dt>", facts) == [
        "Автор",
        "Изменено",
        "Ревью",
        "Служит ценностям",
        "Заменено на",
    ]
    assert "<dd>агент</dd>" in facts
    assert '<dd><time datetime="2026-10-15">15 октября 2026</time></dd>' in facts
    assert "<dd>ещё не было</dd>" in facts
    assert (
        '<dt>Служит ценностям</dt>\n<dd><ul class="rel">\n'
        '<li><a href="../../s/value/0001-craft.html">Craft</a> <code class="ref">value/0001</code>'
    ) in facts
    assert "<section" not in page[: page.index('<aside class="rail rv-rail"')]
    assert page.count("<dl") == 2
    measure = page[page.index('<div class="measure">') :]
    assert measure.index("<article ") < measure.index('<dl class="facts">')
    assert measure.index('<h2 id="referenced-by">') < measure.index("</div>\n</main>")
    assert '<a class="tag" href="../../s/tags/robot.html">#robot</a>' in page
    anchor = re.search(r'<a href="#(L\d+)"><span class="b warn">', page)
    assert anchor is not None
    assert anchor.group(1) in _parse(page).ids
    assert "<dt>targets</dt>\n<dd>develop</dd>" in page
    for raw in ("created_by", "updated_at"):
        assert f"<dt>{raw}</dt>" not in page


def test_superseded_record_names_its_superseder(tmp_path: Path) -> None:
    page = _record_page(tmp_path)["s/adr/0001-robot.html"]
    assert (
        '<dt>Superseded by</dt>\n<dd><ul class="rel">\n'
        '<li><a href="../../s/adr/0002-chassis.html">Chassis</a>'
        ' <code class="ref">adr/0002</code></li>'
    ) in page


STYLE = (Path(site_pages.__file__).parent / "style.css").read_text()
LIST_CLASSES = {
    "rows",
    "row",
    "t",
    "s",
    "why",
    "ref",
    "tags",
    "tag",
    "facts",
    "rel",
}


def _rules(css: str) -> list[tuple[str, str]]:
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [(sel.strip(), body) for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", stripped)]


def test_list_and_record_classes_the_pages_emit_are_styled(tmp_path: Path) -> None:
    pages = _record_page(tmp_path)
    emitted = {
        cls
        for html in pages.values()
        for attr in re.findall(r'class="([^"]+)"', html)
        for cls in attr.split()
    }
    assert emitted >= LIST_CLASSES
    selectors = " ".join(selector for selector, _ in _rules(STYLE))
    unstyled = {c for c in LIST_CLASSES if not re.search(rf"\.{c}(?![\w-])", selectors)}
    assert unstyled == set()
    for ul in ("ul.rows", "ul.rel"):
        assert any(
            ul in selector.split(", ") and "list-style: none" in body and "padding: 0" in body
            for selector, body in _rules(STYLE)
        ), ul


CHIP = re.compile(
    r'<button type="button" class="chip" data-key="([^"]+)" data-value="([^"]*)"'
    r' aria-pressed="false">(?:<svg[^>]*>.*?</svg>)?([^<]+)<span class="n">(\d+)</span></button>'
)


def _facets(page: str) -> list[tuple[str, list[tuple[str, str, str, str]]]]:
    bar = page[page.index('<div class="filters"') : page.index('<p class="count"')]
    groups = re.findall(
        r'<div class="chips" role="group" aria-label="([^"]+)">(.*?)</div>', bar, re.S
    )
    return [(label, CHIP.findall(body)) for label, body in groups]


def test_type_page_chips_and_counts(tmp_path: Path) -> None:
    reviewed = "reviewed: 2026-10-01\n"
    _write(
        tmp_path / "s" / "adr" / "0001-a.md", f"---\ntitle: A\nstatus: accepted\n{reviewed}---\nx\n"
    )
    _write(
        tmp_path / "s" / "adr" / "0002-b.md", f"---\ntitle: B\nstatus: accepted\n{reviewed}---\nx\n"
    )
    _write(
        tmp_path / "s" / "adr" / "0003-c.md", "---\ntitle: C\nstatus: proposed\n---\n[clarify] x\n"
    )
    page = _texts(load_site([SiteRoot("s", tmp_path / "s")], TYPES))["s/adr/index.html"]
    assert _facets(page) == [
        (
            "Status",
            [("status", "accepted", "accepted", "2"), ("status", "proposed", "proposed", "1")],
        ),
        (
            "Needs",
            [
                ("flag", "unreviewed", "Unreviewed", "1"),
                ("flag", "clarify", "Has [clarify]", "1"),
            ],
        ),
    ]
    assert '<div class="filters" data-default-sort="number">' in page
    assert re.findall(r'<option value="([a-z]+)"( selected)?>', page) == [
        ("number", " selected"),
        ("updated", ""),
        ("title", ""),
    ]
    assert '<p class="count" role="status"' in page
    assert ">3 records shown</p>" in page
    assert '<p class="empty" hidden>Nothing matches the filter.</p>' in page


def test_all_records_with_two_roots_has_a_source_facet(site: Site) -> None:
    page = _texts(site)["records.html"]
    facets = _facets(page)
    assert [label for label, _ in facets] == ["Type", "Source", "Needs"]
    assert facets[1][1] == [("source", "core", "core", "1"), ("source", "proj", "proj", "1")]
    rows = ROW_DATA.findall(page)
    columns = {"type": 0, "source": 1, "status": 2}
    for _, chips in facets:
        for key, value, _, count in chips:
            if key == "flag":
                carried = [row for row in rows if value in row[3].split()]
            else:
                carried = [row for row in rows if row[columns[key]] == value]
            assert len(carried) == int(count), (key, value)


def test_filter_script_is_written_and_loaded_only_by_filtered_pages(site: Site) -> None:
    files = _texts(site)
    assert "history.replaceState" in files["filter.js"]
    loading = sorted(
        path for path, html in files.items() if "filter.js" in html and path.endswith(".html")
    )
    filtered = sorted(path for path, html in files.items() if 'class="filters"' in html)
    assert (
        loading
        == filtered
        == [
            "core/value/index.html",
            "proj/adr/index.html",
            "records.html",
            "review.html",
        ]
    )
    assert '<script src="../../filter.js" defer></script>' in files["proj/adr/index.html"]
    assert "SpecsFilters" in files["filter-format.js"]
    loading_format = sorted(
        path
        for path, html in files.items()
        if "filter-format.js" in html and path.endswith(".html")
    )
    assert loading_format == filtered
    assert (
        '<script src="../../filter-format.js" defer></script>\n'
        '<script src="../../filter.js" defer></script>'
    ) in files["proj/adr/index.html"]


def _filter_parts(page: str) -> tuple[str, str, str]:
    """The `.filters` block split into before the sheet, the sheet, and after it."""
    start = page.index('<div class="filters"')
    bar = page[start : page.index('<p class="empty"', start)]
    head, rest = bar.split("<dialog ", 1)
    sheet, tail = rest.split("</dialog>", 1)
    return head, "<dialog " + sheet, tail


def _assert_filter_sheet(page: str, facets: list[str]) -> None:
    head, sheet, tail = _filter_parts(page)
    assert re.search(
        r'<button type="button" class="filter-open" aria-haspopup="dialog" data-label="Filters">'
        r"Filters</button>\n"
        r'<div class="filter-active" data-remove="Remove filter: \{label\}"></div>\n$',
        head,
    )
    assert sheet.startswith('<dialog class="filter-sheet" aria-label="Filters">\n')
    assert (
        '<div class="filter-head">\n<h2>Filters</h2>\n'
        '<button class="iconbtn filter-close" type="button" aria-label="Close">&times;</button>\n'
        "</div>"
    ) in sheet
    assert re.findall(r'<p class="facet">([^<]+)</p>\n<div class="chips"', sheet) == facets
    assert sheet.count('<div class="chips"') == len(facets)
    assert '<select class="sort">' in sheet
    assert sheet.endswith('<button type="button" class="filter-done">Show records</button>\n')
    assert "chips" not in head + tail and "sort" not in tail
    assert tail.startswith('\n<p class="count" role="status"')
    assert tail.rstrip().endswith("</p>\n</div>")


def test_records_page_wraps_chips_and_sort_in_the_filter_sheet(site: Site) -> None:
    _assert_filter_sheet(_texts(site)["records.html"], ["Type", "Source", "Needs"])


def test_type_and_review_pages_carry_the_filter_sheet(tmp_path: Path) -> None:
    files, _ = _review_site(tmp_path)
    _assert_filter_sheet(files["review.html"], ["Needs"])
    _write(tmp_path / "t" / "adr" / "0001-a.md", "---\ntitle: A\nstatus: accepted\n---\nx\n")
    _write(tmp_path / "t" / "adr" / "0002-b.md", "---\ntitle: B\nstatus: proposed\n---\nx\n")
    page = _texts(load_site([SiteRoot("t", tmp_path / "t")], TYPES))["t/adr/index.html"]
    _assert_filter_sheet(page, ["Status", "Needs"])


def test_russian_filter_labels(tmp_path: Path) -> None:
    page = _record_page(tmp_path, "ru")["records.html"]
    assert [label for label, _ in _facets(page)] == ["Раздел", "Статус", "Пометки"]
    head, sheet, _ = _filter_parts(page)
    assert 'data-label="Фильтры">Фильтры</button>' in head
    assert 'data-remove="Убрать фильтр: {label}"' in head
    assert '<dialog class="filter-sheet" aria-label="Фильтры">' in sheet
    assert "<h2>Фильтры</h2>" in sheet and 'aria-label="Закрыть"' in sheet
    assert '<button type="button" class="filter-done">Показать записи</button>' in sheet
    for english in ("Filters", "Show records", "Remove filter"):
        assert english not in page
    assert ">Показаны 3 записи</p>" in page
    assert "Ничего не подходит под фильтр." in page
    for english in ("Sort", "By number", "Recently updated", "By title", "Unreviewed", "Needs"):
        assert f">{english}<" not in page


def _review_site(tmp_path: Path) -> tuple[dict[str, str], OpenItem]:
    reviewed = "reviewed: 2026-10-01\n"
    _write(tmp_path / "s" / "value" / "0001-fresh.md", "---\ntitle: Fresh\n---\nx\n")
    # Frontmatter is lines 1-4, so the mark's paragraph opens on line 5.
    _write(
        tmp_path / "s" / "value" / "0002-murky.md",
        f"---\ntitle: Murky\n{reviewed}---\nWho [unknown] knows.\n",
    )
    _write(
        tmp_path / "s" / "adr" / "0001-done.md",
        f"---\ntitle: Done\nstatus: accepted\n{reviewed}---\nx\n",
    )
    item = OpenItem("OI-0007", "Clarify murk", "value/0002")
    files, _ = build_site(
        load_site([SiteRoot("s", tmp_path / "s")], TYPES), TYPES, open_items=[item], items_root="s"
    )
    return {p: t for p, t in files.items() if isinstance(t, str)}, item


def test_review_page_lists_the_pool_with_mark_links_and_items(tmp_path: Path) -> None:
    files, _ = _review_site(tmp_path)
    page = files["review.html"]
    assert page.count('<li class="row"') == 3
    assert re.findall(r'<code class="ref">([^<]+)</code>', page) == [
        "value/0001",
        "value/0002",
        "OI-0007",
    ]
    assert "Done" not in page
    assert '<a href="s/value/0002-murky.html#L5"><span class="b bad">' in page
    assert (
        '<code class="ref">OI-0007</code><a class="t" href="s/value/0002-murky.html">'
        "Clarify murk</a>"
    ) in page
    item = re.search(r'<li class="row"([^>]*)><code class="ref">OI-0007', page)
    assert item is not None
    assert 'data-flags="open"' in item.group(1)
    assert 'data-source=""' in item.group(1) and 'data-type=""' in item.group(1)
    assert 'data-status="open"' in item.group(1) and 'data-order="2"' in item.group(1)
    assert "<h1>Needs you</h1>" in page
    assert '<div class="filters" data-default-sort="review">' in page
    assert re.findall(r'<option value="([a-z]+)"( selected)?>', page) == [
        ("review", " selected"),
        ("number", ""),
        ("updated", ""),
        ("title", ""),
    ]
    assert (
        '<li><a href="index.html">Overview</a></li>\n'
        '<li><span aria-current="page">Awaiting review</span></li>'
    ) in page
    assert _side_links(_side(page))[1] == ("review.html", "Awaiting review", "3")
    murky = _parse(files["s/value/0002-murky.html"])
    assert "L5" in murky.ids


def test_review_flag_facet_shows_present_reasons_with_counts(tmp_path: Path) -> None:
    files, _ = _review_site(tmp_path)
    assert _facets(files["review.html"]) == [
        (
            "Needs",
            [
                ("flag", "unreviewed", "Unreviewed", "1"),
                ("flag", "unknown", "Has [unknown]", "1"),
                ("flag", "open", "Open", "1"),
            ],
        ),
    ]


def test_review_item_without_a_resolving_record_is_unlinked(site: Site) -> None:
    files, _ = build_site(site, TYPES, open_items=[OpenItem("OI-0001", "Ask", "adr/0099")])
    page = files["review.html"]
    assert isinstance(page, str)
    assert '<code class="ref">OI-0001</code><span class="t">Ask</span>' in page


def test_empty_review_pool_says_nothing_needs_you(tmp_path: Path) -> None:
    _write(
        tmp_path / "s" / "value" / "0001-a.md",
        "---\ntitle: A\nreviewed: 2026-10-01\n---\nx\n",
    )
    page = _texts(load_site([SiteRoot("s", tmp_path / "s")], TYPES))["review.html"]
    assert '<p class="empty">Nothing needs you.</p>' in page
    assert 'class="filters"' not in page
    assert "filter.js" not in page


def _home_site(tmp_path: Path, lang: str = "en") -> str:
    reviewed = "reviewed: 2026-10-01\n"
    _write(
        tmp_path / "s" / "value" / "0001-why.md",
        f"---\ntitle: Why\nsummary: We ship small.\n{reviewed}---\nx\n",
    )
    # Three records need review: one unreviewed, two carrying a [clarify] mark each.
    _write(tmp_path / "s" / "adr" / "0001-a.md", "---\ntitle: A\n---\nx\n")
    _write(tmp_path / "s" / "adr" / "0002-b.md", f"---\ntitle: B\n{reviewed}---\n[clarify] x\n")
    _write(tmp_path / "s" / "adr" / "0003-c.md", f"---\ntitle: C\n{reviewed}---\n[clarify] y\n")
    for n in range(4, 16):
        _write(
            tmp_path / "s" / "adr" / f"{n:04d}-d{n}.md",
            f"---\ntitle: D{n}\nupdated_at: 2026-09-{n:02d}\n{reviewed}---\nx\n",
        )
    labels, lang, _ = load_labels({"lang": lang})
    files, _ = build_site(load_site([SiteRoot("s", tmp_path / "s")], TYPES), TYPES, labels, lang)
    page = files["index.html"]
    assert isinstance(page, str)
    return page


def test_home_lead_callout_scenarios_and_recent(tmp_path: Path) -> None:
    home = _home_site(tmp_path)
    assert '<p class="lead">We ship small.</p>' in home
    callout = re.search(
        r'<p class="callout">.*?<span><a href="([^"]+)">([^<]+)</a>([^<]*)</span>', home
    )
    assert callout is not None
    # One record lacks `reviewed:`; the two [clarify] marks are the open questions.
    assert callout.groups() == (
        "review.html",
        "3 need you →",
        " · 1 unreviewed · 2 open questions",
    )
    measures = re.findall(r'<div class="measure">\n(.*?)\n</div>', home, flags=re.S)
    assert len(measures) == 2
    assert '<p class="lead">We ship small.</p>' in measures[0]
    assert 'class="callout"' in measures[0]
    assert "<h2>Recently updated</h2>" in measures[1]
    assert '<ul class="recent">' in measures[1]
    assert all('class="scen"' not in m for m in measures)
    assert '<ul class="scen">' in home
    assert 'class="mark"' not in home
    assert "[clarify]" not in home
    assert re.findall(
        r'<a href="(records\.html#type=[a-z]+)"><b>([^<]+) <span class="n">(\d+)', home
    ) == [
        ("records.html#type=value", "Values", "1"),
        ("records.html#type=adr", "ADRs", "15"),
    ]
    assert "<h2>Recently updated</h2>" in home
    recent = home[home.index('<ul class="recent">') :]
    rows = re.findall(
        r'<li><code class="ref">([^<]+)</code><a href="[^"]+">[^<]+</a><time datetime="([^"]+)">',
        recent,
    )
    assert rows == [(f"adr/{n:04d}", f"2026-09-{n:02d}") for n in range(15, 5, -1)]
    assert '<time datetime="2026-09-15">15 September 2026</time>' in recent


def test_home_callout_omits_unreviewed_when_every_record_is_reviewed(tmp_path: Path) -> None:
    _write(
        tmp_path / "s" / "adr" / "0001-a.md",
        "---\ntitle: A\nreviewed: 2026-10-01\n---\n[clarify] x\n",
    )
    home = _texts(load_site([SiteRoot("s", tmp_path / "s")], TYPES))["index.html"]
    assert '<a href="review.html">1 needs you →</a> · 1 open question</span>' in home
    assert " unreviewed" not in home


def test_home_without_value_or_review_has_no_lead_or_callout(tmp_path: Path) -> None:
    _write(tmp_path / "s" / "adr" / "0001-a.md", "---\ntitle: A\nreviewed: 2026-10-01\n---\nx\n")
    home = _texts(load_site([SiteRoot("s", tmp_path / "s")], TYPES))["index.html"]
    assert '<p class="lead">' not in home
    assert 'class="callout"' not in home
    assert "Recently updated" not in home


def test_home_callout_in_russian_uses_the_few_form(tmp_path: Path) -> None:
    home = _home_site(tmp_path, "ru")
    assert (
        '<a href="review.html">3 записи ждут тебя →</a> · 1 без ревью · 2 открытых вопроса</span>'
    ) in home
    assert "<h2>Недавно изменённое</h2>" in home


def _tag_site(tmp_path: Path) -> dict[str, str | bytes]:
    root = tmp_path / "s"
    _write(root / "tags.yaml", "a: A\na:b: AB\n")
    _write(root / "adr" / "0001-one.md", "---\ntitle: One\ntags: [a:b]\n---\nx\n")
    _write(root / "adr" / "0002-two.md", "---\ntitle: Two\ntags: [a:b:c]\n---\nx\n")
    _write(root / "value" / "0001-three.md", "---\ntitle: Three\ntags: [x]\n---\nx\n")
    _write(root / "value" / "0002-odd.md", "---\ntitle: Odd\ntags: q\n---\nx\n")
    _write(tmp_path / "p" / "adr" / "0001-bare.md", "---\ntitle: Bare\n---\nx\n")
    roots = [SiteRoot("s", root), SiteRoot("p", tmp_path / "p")]
    return build_site(load_site(roots, TYPES), TYPES)[0]


def _crumbs(page: str) -> list[tuple[str | None, str]]:
    nav = page[page.index('<nav class="crumbs"') :]
    nav = nav[: nav.index("</nav>")]
    return [
        (href or None, label)
        for href, label in re.findall(
            r'<li[^>]*>(?:<a href="([^"]+)">|<span[^>]*>)(?:<code>)?([^<]+)', nav
        )
    ]


def test_tag_tree_page_nests_nodes_with_counts(tmp_path: Path) -> None:
    files = _tag_site(tmp_path)
    page = files["s/tags/index.html"]
    assert isinstance(page, str)
    assert "<h1>Tags</h1>" in page
    assert _crumbs(page) == [
        ("../../index.html", "Overview"),
        ("../index.html", "s"),
        (None, "Tags"),
    ]
    tree = page[page.index('<ul class="tag-tree">') : page.index("</main>")]
    assert re.findall(
        r'<a href="([^"]+)"><code>([^<]+)</code></a> <span class="n">(\d+)', tree
    ) == [
        ("a.html", "a", "2"),
        ("a.b.html", "a:b", "2"),
        ("a.b.c.html", "a:b:c", "1"),
        ("x.html", "x", "1"),
    ]
    assert tree.count('<ul class="tag-tree">') == 3
    assert '<span class="s">AB</span>' in tree


def test_tag_page_lists_descendant_records_and_children(tmp_path: Path) -> None:
    files = _tag_site(tmp_path)
    page = files["s/tags/a.html"]
    assert isinstance(page, str)
    assert "<h1><code>a</code></h1>" in page
    assert '<p class="lead">A</p>' in page
    assert re.findall(r'<a class="t" href="([^"]+)">', page) == [
        "../../s/adr/0001-one.html",
        "../../s/adr/0002-two.html",
    ]
    assert '<a href="a.b.html"><code>a:b</code></a>' in page
    assert [label for label, _ in _facets(page)] == ["Needs"]
    assert '<div class="filters" data-default-sort="number">' in page


def test_deep_tag_page_crumbs_run_through_its_ancestors(tmp_path: Path) -> None:
    page = _tag_site(tmp_path)["s/tags/a.b.c.html"]
    assert isinstance(page, str)
    assert _crumbs(page) == [
        ("../../index.html", "Overview"),
        ("../index.html", "s"),
        ("index.html", "Tags"),
        ("a.html", "a"),
        ("a.b.html", "a:b"),
        (None, "a:b:c"),
    ]


def test_record_tags_link_their_pages_and_every_link_resolves(tmp_path: Path) -> None:
    files = _tag_site(tmp_path)
    one = files["s/adr/0001-one.html"]
    assert isinstance(one, str)
    assert '<a class="tag" href="../../s/tags/a.b.html">#a:b</a>' in one
    odd = files["s/value/0002-odd.html"]
    assert isinstance(odd, str)
    assert '<span class="tag">#q</span>' in odd
    assert not any(path.startswith("p/tags/") for path in files)
    assert _check_links(files) > 20


RAILED = (
    "---\n"
    "title: Railed\n"
    "---\n"
    "# Railed\n"
    "\n"
    "## Context\n"
    "\n"
    "We [unknown] this.\n"
    "\n"
    "### Detail\n"
    "\n"
    "Ask [clarify] here.\n"
    "\n"
    "## Decision\n"
)


def _toc_page(tmp_path: Path, body: str) -> str:
    _write(tmp_path / "proj" / "adr" / "0001-railed.md", body)
    files, _ = build_site(load_site([SiteRoot("proj", tmp_path / "proj")], TYPES), TYPES)
    page = files["proj/adr/0001-railed.html"]
    assert isinstance(page, str)
    return page


def _toc_blocks(key: str, shift: int = 0) -> str:
    return (
        f'<nav class="toc" aria-labelledby="{key}-toc">\n'
        f'<h4 id="{key}-toc">On this page</h4>\n'
        "<ul>\n"
        '<li><a href="#context">Context</a>\n'
        "<ul>\n"
        '<li><a href="#detail">Detail</a></li>\n'
        "</ul>\n"
        "</li>\n"
        '<li><a href="#decision">Decision</a>\n'
        "</li>\n"
        '<li><a href="#referenced-by">Referenced by</a>\n'
        "</li>\n"
        "</ul>\n"
        "</nav>\n"
        '<div class="q">\n'
        "<h4>2 open questions</h4>\n"
        "<ul>\n"
        f'<li><a class="mk-clarify" href="#L{12 + shift}"><svg class="ic" aria-hidden="true">'
        '<use href="#i-clarify"/></svg>Ask [clarify] here.</a></li>\n'
        f'<li><a class="mk-unknown" href="#L{8 + shift}"><svg class="ic" aria-hidden="true">'
        '<use href="#i-unknown"/></svg>We [unknown] this.</a></li>\n'
        "</ul>\n"
        "</div>\n"
    )


def test_record_rail_nests_the_toc_above_the_review_panel(tmp_path: Path) -> None:
    page = _toc_page(tmp_path, RAILED)
    rail = page[page.index('<aside class="rail rv-rail"') : page.index("</aside>")]
    assert rail.startswith(
        '<aside class="rail rv-rail" id="rv-panel">\n'
        '<details class="rv-toc" open>\n'
        "<summary>On this page</summary>\n" + _toc_blocks("rail") + "</details>\n"
        '<section class="rv" aria-labelledby="rv-h" '
    )
    assert 'class="body rv-page">' in page


def test_record_phone_details_hold_the_same_blocks_after_the_lead(tmp_path: Path) -> None:
    page = _toc_page(tmp_path, RAILED.replace("title: Railed\n", "title: Railed\nsummary: Lead.\n"))
    details = page[page.index('<details class="toc-m">') : page.index("</details>")]
    assert details == (
        '<details class="toc-m">\n'
        "<summary>On this page · 2 open questions</summary>\n" + _toc_blocks("toc-m", 1)
    )
    assert page.index('<p class="lead">Lead.</p>') < page.index('<details class="toc-m">')


def test_record_with_one_heading_and_no_marks_has_only_the_panel(tmp_path: Path) -> None:
    page = _toc_page(tmp_path, "---\ntitle: Solo\n---\n# Solo\n\nText.\n")
    assert '<aside class="rail rv-rail" id="rv-panel">\n<section class="rv" ' in page
    assert "toc-m" not in page
    assert "rv-toc" not in page
    assert 'class="body rv-page rv-notoc"' in page


def test_record_header_holds_the_search_combobox_and_script(site: Site) -> None:
    page = _texts(site)["proj/adr/0001-pick.html"]
    assert (
        '<form class="search" role="search" action="../../search.html" data-prefix="../../"' in page
    )
    assert (
        '<input type="search" name="q" role="combobox" aria-label="Search"'
        ' aria-autocomplete="list" aria-expanded="false" aria-controls="search-list"'
        ' autocomplete="off" placeholder="Search the specs">'
    ) in page
    assert "<kbd>/</kbd>" in page
    assert '<ul id="search-list" role="listbox" aria-label="Search" hidden></ul>' in page
    assert '<button class="iconbtn search-btn" type="button" aria-label="Search"' in page
    assert '<script src="../../search.js" defer></script>' in page
    assert '<script src="search.js" defer></script>' in _texts(site)["index.html"]


def test_search_page_loads_both_data_files_and_says_it_needs_js(site: Site) -> None:
    page = _texts(site)["search.html"]
    assert '<script src="search-index.js" defer></script>' in page
    assert '<script src="search-body.js" defer></script>' in page
    assert page.index("search-body.js") < page.index('<script src="search.js"')
    assert "<h1>Search</h1>" in page
    assert (
        '<p class="needs-js">Search needs JavaScript. <a href="records.html">All records</a></p>'
        in page
    )
    assert '<form class="search" role="search" action="search.html"' in page


def test_site_index_has_no_search() -> None:
    page = build_index([Project("a", "https://a.example/", "A")], "Group")["index.html"]
    assert isinstance(page, str)
    assert 'class="search' not in page
    assert "search.js" not in page


def test_search_labels_resolve_in_russian(tmp_path: Path) -> None:
    files = _record_page(tmp_path, "ru")
    assert 'placeholder="Поиск по спекам"' in files["records.html"]
    assert 'aria-label="Поиск"' in files["records.html"]
    page = files["search.html"]
    assert "<h1>Поиск</h1>" in page
    assert "Для поиска нужен JavaScript." in page
    assert 'data-forms="[&#34;{n} результат&#34;' in page
    assert "Ничего не найдено" in page


def _comment_site(tmp_path: Path, lang: str = "en") -> dict[str, str]:
    _write(
        tmp_path / "s" / "adr" / "0007-elka.md",
        '---\ntitle: Ёлка "A" & B\n---\n## Почему\n\nНужна.\n',
    )
    labels, lang, _ = load_labels({"lang": lang})
    files, _ = build_site(load_site([SiteRoot("s", tmp_path / "s")], TYPES), TYPES, labels, lang)
    return {path: text for path, text in files.items() if isinstance(text, str)}


def test_record_article_carries_its_ref_title_and_page(tmp_path: Path) -> None:
    page = _comment_site(tmp_path)["s/adr/0007-elka.html"]
    assert (
        '<article data-ref="adr/0007" data-title="Ёлка &#34;A&#34; &amp; B"'
        ' data-page="s/adr/0007-elka.html">'
    ) in page


def test_record_page_holds_the_review_panel_and_its_header_button(tmp_path: Path) -> None:
    page = _comment_site(tmp_path)["s/adr/0007-elka.html"]
    header = page[page.index('<header class="top">') : page.index("</header>")]
    assert (
        '<button class="iconbtn rv-btn" type="button" aria-controls="rv-panel"'
        ' aria-expanded="false" aria-label="Comments" title="Comments">'
        '<svg class="ic" aria-hidden="true"><use href="#i-comment"/></svg>'
        '<span class="n"></span></button>'
    ) in header
    assert "<dialog" not in page
    panel = page[page.index('<section class="rv"') : page.index("</section>")]
    assert 'data-note="Note" data-delete="Delete"' in panel
    assert 'data-copied-forms="[&#34;{n} item copied&#34;, &#34;{n} items copied&#34;]"' in panel
    assert '<h2 id="rv-h">Comments</h2>' in panel
    assert 'class="iconbtn rv-close" type="button" aria-label="Close"' in panel
    assert (
        '<label class="rv-reviewed"><input type="checkbox" id="rv-reviewed"> Reviewed</label>'
    ) in panel
    # The free-form input comes first, the cards' list after it.
    assert panel.index('<textarea id="rv-new" rows="3"></textarea>') < panel.index(
        '<ul class="rv-list"></ul>'
    )
    assert '<label class="rv-label" for="rv-new">Comment on the whole record</label>' in panel
    assert '<button class="rv-add" type="button" disabled>Add</button>' in panel
    assert '<p class="rv-hint">Select text in the record to comment on it.</p>' in panel
    assert '<script src="../../comments-format.js" defer></script>' in page
    assert '<script src="../../comments.js" defer></script>' in page


def test_every_page_has_the_outbox_link_and_only_records_the_panel(tmp_path: Path) -> None:
    page = _comment_site(tmp_path)["records.html"]
    header = page[page.index('<header class="top">') : page.index("</header>")]
    assert (
        '<a class="iconbtn outbox" href="comments.html" aria-label="Outbox" title="Outbox">'
        '<svg class="ic" aria-hidden="true"><use href="#i-outbox"/></svg>'
        '<span class="l">Outbox</span><span class="n"></span></a>'
    ) in header
    assert "comments.html" not in _side(page)
    assert "rv-btn" not in page
    assert '<section class="rv"' not in page
    assert '<script src="comments.js" defer></script>' in page


def test_outbox_page_is_a_shell_with_copy_all_and_clear(tmp_path: Path) -> None:
    page = _comment_site(tmp_path)["comments.html"]
    main = page[page.index('<main id="main">') :]
    assert "<h1>Outbox</h1>" in main
    assert "Stored in this browser only; copying marks nothing" in main
    assert '<p class="needs-js">Comments need JavaScript.</p>' in main
    assert '<p class="cmt-nostore">Comments need browser storage.</p>' in main
    assert '<div class="ob-groups"></div>' in main
    assert '<button class="ob-copy" type="button">Copy all</button>' in main
    assert '<button class="ob-clear" type="button">Clear</button>' in main
    assert '<p class="cmt-empty">Nothing to send.</p>' in main
    assert (
        '<div class="ob-confirm" role="group" aria-labelledby="ob-confirm-q" hidden>\n'
        '<p id="ob-confirm-q">Remove every comment and reviewed mark from this browser?</p>\n'
        '<button class="ob-clear-yes" type="button">Remove all</button>\n'
        '<button class="ob-clear-no" type="button">Cancel</button>\n'
        "</div>"
    ) in main
    assert '<section class="rv"' not in main
    assert '<a class="iconbtn outbox" href="comments.html" aria-current="page"' in page


def test_comment_labels_resolve_in_russian(tmp_path: Path) -> None:
    files = _comment_site(tmp_path, "ru")
    page = files["s/adr/0007-elka.html"]
    assert 'aria-label="Комментарии"' in page
    assert 'aria-label="К отправке"' in page
    assert "> Ревью пройдено</label>" in page
    assert ">Комментарий ко всей записи</label>" in page
    assert (
        'data-cleared-forms="[&#34;{n} удалён&#34;, &#34;{n} удалено&#34;, &#34;{n} удалено&#34;]"'
    ) in page
    assert 'data-note="Заметка"' in page
    assert ">Ждут ревью<" in _side(page)
    outbox = files["comments.html"]
    assert "<h1>К отправке</h1>" in outbox
    assert ">Скопировать всё</button>" in outbox
    assert ">Очистить</button>" in outbox
    assert "Хранятся только в этом браузере" in outbox
    assert "Для комментариев нужен JavaScript." in outbox
    assert "Для комментариев нужно хранилище браузера." in outbox


def test_machine_and_search_files_carry_no_comment_markup(tmp_path: Path) -> None:
    files = _comment_site(tmp_path)
    for name in ("search-body.js", "search-index.js", "index.json", "llms.txt"):
        assert "cmt-" not in files[name], name
        assert "rv-" not in files[name], name
        assert "Outbox" not in files[name], name
        assert "comments.js" not in files[name], name
        assert "comments-format.js" not in files[name], name
