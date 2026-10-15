from __future__ import annotations

import posixpath
import re
from collections.abc import Callable
from html.parser import HTMLParser
from pathlib import Path

import pytest

from booping.specs.site import pages as site_pages
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


def test_every_relative_link_lands_on_a_page_and_id(site: Site) -> None:
    files = build_site(site, TYPES)[0]
    pages = {
        path: _parse(text)
        for path, text in files.items()
        if path.endswith(".html") and isinstance(text, str)
    }
    checked = 0
    for path, parsed in pages.items():
        text = files[path]
        assert isinstance(text, str)
        assert parsed.scripts == (3 if 'class="filters"' in text else 2), path
        for href in parsed.hrefs:
            assert "://" not in href and not href.startswith("/"), (path, href)
            target, _, fragment = href.partition("#")
            if target:
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                # Written by later milestones: the review page and the tag pages.
                if target == "review.html" or "/tags/" in f"/{target}":
                    continue
                assert target in files, (path, href)
            else:
                target = path
            # A `key=value` fragment is list filter state, not an element id.
            if fragment and "=" not in fragment:
                assert fragment in pages[target].ids, (path, href)
            checked += 1
    assert checked > 20


def test_page_map_paths(site: Site) -> None:
    files, _ = build_site(site, TYPES)
    assert sorted(files) == [
        "core/index.html",
        "core/value/0001-clarity.html",
        "core/value/0001-clarity.md",
        "core/value/index.html",
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
        "site.js",
        "style.css",
    ]


def test_build_is_repeatable(site: Site, roots: list[SiteRoot]) -> None:
    assert build_site(site, TYPES) == build_site(load_site(roots, TYPES), TYPES)


def test_root_page_lists_types_with_counts_and_marks_with_links(site: Site) -> None:
    files = _texts(site)
    root = files["proj/index.html"]
    assert (
        '<ul class="types">\n<li><a href="adr/index.html">ADRs</a>'
        ' <span class="n">Records: 1</span>\n<p>why it was decided so</p>\n</li>\n</ul>'
    ) in root
    rows = re.findall(r'<li class="row">.*?<a class="t" href="([^"]+)">([^<]+)</a>', root)
    assert rows == [("adr/0001-pick.html#L10", "Pick")]
    assert '<span class="s">We [clarify] this.</span>' in root
    target, _, fragment = rows[0][0].partition("#")
    assert fragment in _parse(files[f"proj/{target}"]).ids


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
    assert re.findall(r"<h2>([^<]+)</h2>", home) == ["core", "proj"]
    assert '<li><a href="core/value/index.html">Values</a>' in home
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


def test_icon_sprite_holds_thirteen_unique_symbols() -> None:
    labels, lang, _ = load_labels({})
    sprite = environment(labels, lang, "Specs").get_template("_icons.html.j2").render()
    ids = re.findall(r'<symbol id="([^"]+)"', sprite)
    assert len(ids) == 13
    assert len(set(ids)) == 13
    assert {"i-sun", "i-auto", "i-moon", "i-clarify"} <= set(ids)


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
        ("../../review.html", "Review", "2"),
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
    side = _side(_texts(load_site(_roots(tmp_path), TYPES))["index.html"])
    assert re.findall(r"<h4>([^<]+)</h4>", side) == ["Types", "Tags", "Sources"]
    assert re.findall(r"<h5>([^<]+)</h5>", side) == ["core", "proj"]
    tags = side[side.index("<h4>Tags</h4>") : side.index("<h4>Sources</h4>")]
    assert _side_links(tags) == [
        ("core/tags/ux.html", "ux", "2"),
        ("core/tags/index.html", "All tags", ""),
        ("proj/tags/ops.html", "ops", "1"),
        ("proj/tags/index.html", "All tags", ""),
    ]


def test_sidebar_tags_have_no_root_heading_with_one_tagged_root(tmp_path: Path) -> None:
    _write(tmp_path / "core" / "value" / "0001-a.md", "---\ntitle: A\ntags: [ux]\n---\nx\n")
    _write(tmp_path / "proj" / "adr" / "0001-c.md", "---\ntitle: C\n---\nx\n")
    side = _side(_texts(load_site(_roots(tmp_path), TYPES))["index.html"])
    assert "<h5>" not in side
    assert '<a href="core/tags/ux.html"><code>ux</code><span class="n">1</span></a>' in side


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
    for english in ("Navigation", "Review", "All records", "Tags", "All tags", "Sources"):
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
    assert re.findall(r"<dt>([^<]+)</dt>", facts) == ["Автор", "Изменено", "Ревью"]
    assert "<dd>агент</dd>" in facts
    assert '<dd><time datetime="2026-10-15">15 октября 2026</time></dd>' in facts
    assert "<dd>ещё не было</dd>" in facts
    assert (
        '<dt>Служит ценностям</dt>\n<dd><ul class="rel">\n'
        '<li><a href="../../s/value/0001-craft.html">Craft</a> <code class="ref">value/0001</code>'
    ) in page
    assert '<span class="tag">#robot</span>' in page
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
    "relations",
    "rel",
    "types",
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
    for ul in ("ul.rows", "ul.rel", "ul.types"):
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
    assert loading == filtered == ["core/value/index.html", "proj/adr/index.html", "records.html"]
    assert '<script src="../../filter.js" defer></script>' in files["proj/adr/index.html"]


def test_russian_filter_labels(tmp_path: Path) -> None:
    page = _record_page(tmp_path, "ru")["records.html"]
    assert [label for label, _ in _facets(page)] == ["Раздел", "Статус", "Пометки"]
    assert ">Показаны 3 записи</p>" in page
    assert "Ничего не подходит под фильтр." in page
    for english in ("Sort", "By number", "Recently updated", "By title", "Unreviewed", "Needs"):
        assert f">{english}<" not in page
