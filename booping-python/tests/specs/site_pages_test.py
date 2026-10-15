from __future__ import annotations

import posixpath
import re
from collections.abc import Callable
from html.parser import HTMLParser
from pathlib import Path

import pytest

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
    files = _texts(site)
    pages = {path: _parse(text) for path, text in files.items() if path.endswith(".html")}
    checked = 0
    for path, parsed in pages.items():
        assert parsed.scripts == 2
        for href in parsed.hrefs:
            assert "://" not in href and not href.startswith("/"), (path, href)
            target, _, fragment = href.partition("#")
            if target:
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                assert target in files, (path, href)
            else:
                target = path
            if fragment:
                assert fragment in pages[target].ids, (path, href)
            checked += 1
    assert checked > 20


def test_page_map_paths(site: Site) -> None:
    files, _ = build_site(site, TYPES)
    assert sorted(files) == [
        "core/index.html",
        "core/value/0001-clarity.html",
        "core/value/index.html",
        "fonts.css",
        "fonts/OFL-golos-text.txt",
        "fonts/OFL-jetbrains-mono.txt",
        "index.html",
        "proj/adr/0001-pick.html",
        "proj/adr/index.html",
        "proj/index.html",
        "site.js",
        "style.css",
    ]


def test_build_is_repeatable(site: Site, roots: list[SiteRoot]) -> None:
    assert build_site(site, TYPES) == build_site(load_site(roots, TYPES), TYPES)


def test_marks_list_links_to_the_marked_line(site: Site) -> None:
    files = _texts(site)
    assert (
        '<li><a href="adr/0001-pick.html#L10"><code>adr/0001</code> Pick</a>'
        " — We [clarify] this.</li>"
    ) in files["proj/index.html"]
    assert "<h3>[unknown]</h3>\n<p>None.</p>" in files["proj/index.html"]
    assert 'id="L10"' in files["proj/adr/0001-pick.html"]
    assert 'id="0001-pick--L10"' in files["proj/adr/index.html"]


def test_value_page_lists_cross_root_backlink(site: Site) -> None:
    files = _texts(site)
    assert (
        '<a href="../../proj/adr/0001-pick.html"><code>proj:adr/0001</code> Pick</a>'
        in files["core/value/0001-clarity.html"]
    )
    assert "Nothing references this record." in files["proj/adr/0001-pick.html"]


def test_record_page_links_refs_and_body(site: Site) -> None:
    page = _texts(site)["proj/adr/0001-pick.html"]
    assert '<a href="../../core/value/0001-clarity.html"><code>core:value/0001</code></a>' in page
    assert '<code class="unresolved">core:value/0009</code>' in page
    assert '<a href="../../core/value/0001-clarity.html#why">why</a>' in page
    assert '<span class="unresolved">gone</span>' in page
    assert '<span class="badge st-accepted">accepted</span>' in page
    assert '<span class="badge unreviewed">unreviewed</span>' in page
    assert '<span class="chip mk-clarify">1 question for you</span>' in page


def test_type_page_prefixes_in_page_anchors(site: Site) -> None:
    page = _texts(site)["proj/adr/index.html"]
    assert '<a href="#0001-pick--decision">top</a>' in page
    assert '<h2 id="0001-pick--decision">Decision</h2>' in page


def test_value_badge_uses_kind_and_reviewed_hides_unreviewed(site: Site) -> None:
    page = _texts(site)["core/value/0001-clarity.html"]
    assert '<span class="badge st-value">value</span>' in page
    assert 'class="badge unreviewed"' not in page


def test_top_index_counts(site: Site) -> None:
    index = _texts(site)["index.html"]
    assert (
        '<tr><td><a href="core/index.html">core</a></td><td>1</td>'
        '<td><a href="core/value/index.html">1</a></td><td></td>'
        "<td></td><td></td><td></td></tr>"
    ) in index
    assert (
        '<tr><td><a href="proj/index.html">proj</a></td><td>1</td>'
        '<td></td><td><a href="proj/adr/index.html">1</a></td>'
        "<td>1</td><td></td><td>1</td></tr>"
    ) in index


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


def test_sidebar_lists_both_roots_and_marks_the_current_type(site: Site) -> None:
    page = _texts(site)["proj/adr/index.html"]
    side = page[page.index('<nav class="side"') : page.index("</nav>", page.index('class="side"'))]
    assert re.findall(r"<h4>([^<]+)</h4>", side) == ["core", "proj"]
    assert '<a href="../../core/value/index.html">Values<span class="n">1</span></a>' in side
    assert (
        '<a href="../../proj/adr/index.html" aria-current="page">ADRs<span class="n">1</span></a>'
        in side
    )
    assert side.count('aria-current="page"') == 1


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
