from __future__ import annotations

from pathlib import Path

import pytest

from booping.specs.site.markdown import Mark, render_body, slug
from booping.specs.site.model import (
    LinkTarget,
    RefMiss,
    Site,
    SiteRecord,
    SiteRoot,
    load_site,
)


def _no_link(dest: str) -> tuple[str | None, str | None]:
    return dest, None


def _render(text: str, first_line: int = 1, statuses: set[str] | None = None) -> str:
    return render_body(
        text, first_line=first_line, id_prefix="", link=_no_link, statuses=statuses or set()
    ).html


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello World", "hello-world"),
        ("What's new? (v2.0)", "whats-new-v20"),
        ("snake_case and-dash", "snake_case-and-dash"),
        ("Ünïcode Title", "ünïcode-title"),
    ],
)
def test_slug_follows_github_anchors(text: str, expected: str) -> None:
    assert slug(text) == expected


def test_repeated_headings_get_numbered_ids() -> None:
    html = render_body(
        "# Notes\n\n## Notes\n\n### Notes\n",
        first_line=1,
        id_prefix="r-",
        link=_no_link,
        statuses=set(),
    ).html
    assert html == (
        '<h1 id="r-notes">Notes</h1>\n'
        '<h2 id="r-notes-1">Notes</h2>\n'
        '<h3 id="r-notes-2">Notes</h3>\n'
    )


def test_raw_html_is_escaped() -> None:
    assert _render("hi <script>alert(1)</script>\n") == (
        "<p>hi &lt;script&gt;alert(1)&lt;/script&gt;</p>\n"
    )


@pytest.mark.parametrize(
    ("text", "html", "marks"),
    [
        (
            "intro\n\nwe [clarify] this\n",
            '<p>intro</p>\n<p id="L12">we <mark class="mk mk-clarify">[clarify]</mark> this</p>\n',
            [Mark(line=12, kind="clarify", text="we [clarify] this")],
        ),
        (
            "- first\n- second [unknown]\n",
            '<ul>\n<li>first</li>\n<li id="L11">second <mark class="mk mk-unknown">[unknown]'
            "</mark></li>\n</ul>\n",
            [Mark(line=11, kind="unknown", text="second [unknown]")],
        ),
        (
            "| a | b |\n|---|---|\n| x | [clarify] |\n",
            "<table>\n<thead>\n<tr>\n<th>a</th>\n<th>b</th>\n</tr>\n</thead>\n<tbody>\n"
            '<tr id="L12">\n<td>x</td>\n<td><mark class="mk mk-clarify">[clarify]</mark></td>\n'
            "</tr>\n</tbody>\n</table>\n",
            [Mark(line=12, kind="clarify", text="x [clarify]")],
        ),
        (
            "see `[clarify]` here\n",
            "<p>see <code>[clarify]</code> here</p>\n",
            [],
        ),
        (
            "```\n[unknown]\n```\n",
            "<pre><code>[unknown]\n</code></pre>\n",
            [],
        ),
    ],
    ids=["paragraph", "list-item", "table-row", "code-span", "fenced-block"],
)
def test_marks_wrap_text_outside_code(text: str, html: str, marks: list[Mark]) -> None:
    rendered = render_body(text, first_line=10, id_prefix="", link=_no_link, statuses=set())
    assert rendered.html == html
    assert rendered.marks == marks


def test_mark_text_is_collapsed_and_cut() -> None:
    body = "[clarify] " + "word " * 40 + "\nmore\n"
    rendered = render_body(body, first_line=3, id_prefix="x-", link=_no_link, statuses=set())
    expected = ("[clarify] " + "word " * 40 + "more")[:160] + "…"
    assert rendered.marks == [Mark(line=3, kind="clarify", text=expected)]
    assert rendered.html.startswith('<p id="x-L3">')


def test_one_anchor_per_block_with_both_kinds() -> None:
    rendered = render_body(
        "a [clarify] b [unknown]\n", first_line=1, id_prefix="", link=_no_link, statuses=set()
    )
    assert rendered.html.count('id="L1"') == 1
    assert [(m.line, m.kind) for m in rendered.marks] == [(1, "clarify"), (1, "unknown")]


def test_links_are_reported_and_rendered_through_the_callback() -> None:
    def link(dest: str) -> tuple[str | None, str | None]:
        if dest == "gone.md":
            return None, "broken"
        return f"page/{dest}.html", "rec"

    rendered = render_body(
        "first [a](rule/0001.md#why)\nsecond [b](gone.md)\n",
        first_line=7,
        id_prefix="",
        link=link,
        statuses=set(),
    )
    assert rendered.html == (
        '<p>first <a href="page/rule/0001.md#why.html" class="rec">a</a>\n'
        'second <span class="broken">b</span></p>\n'
    )
    assert rendered.links == [(7, "rule/0001.md#why"), (8, "gone.md")]


def test_status_cell_renders_as_badge() -> None:
    html = _render("| Option | Status |\n|---|---|\n| A | rejected |\n", statuses={"rejected"})
    assert '<td><span class="badge st-rejected">rejected</span></td>' in html
    assert "<td>A</td>" in html


def test_render_is_deterministic() -> None:
    text = "# T\n\n[clarify] x\n\n# T\n"
    assert _render(text) == _render(text)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


@pytest.fixture
def site(tmp_path: Path) -> Site:
    core = tmp_path / "core"
    proj = tmp_path / "proj"
    _write(core / "rule" / "0001-base.md", "---\nstatus: accepted\n---\n# Base\n")
    _write(core / "rule" / "0002-other.md", "---\nstatus: draft\n---\n[me](0002-other.md)\n")
    _write(core / "value" / "0001-v.md", "---\nstatus: accepted\n---\nv\n")
    _write(core / "README.md", "not a record\n")
    _write(core / "rule" / "notes.md", "skipped\n")
    _write(core / "stray" / "0001-s.md", "unknown type\n")
    _write(
        proj / "rule" / "0003-uses.md",
        "---\nstatus: accepted\nrelated:\n- core:rule/0001\n- core:rule/0001\n---\n"
        "See [base](../../core/rule/0001-base.md#base) and "
        "[again](../../core/rule/0001-base.md).\n",
    )
    _write(proj / "rule" / "0010-late.md", "---\n---\n[up](../../core/rule/0002-other.md)\n")
    _write(proj / "value" / "0002-pv.md", "no frontmatter\n")
    _write(tmp_path / "notes.txt", "plain file\n")
    (tmp_path / "linkdir").symlink_to(core / "rule")
    (proj / "loop").symlink_to(proj / "loop")
    return load_site(
        [SiteRoot(name="core", path=core), SiteRoot(name="proj", path=proj)],
        ["value", "rule"],
    )


def _record(site: Site, root: str, ref: str) -> SiteRecord:
    return next(r for r in site.records if r.root == root and r.ref == ref)


def test_load_site_orders_roots_types_numbers(site: Site) -> None:
    assert [r.page for r in site.records] == [
        "core/value/0001-v.html",
        "core/rule/0001-base.html",
        "core/rule/0002-other.html",
        "proj/value/0002-pv.html",
        "proj/rule/0003-uses.html",
        "proj/rule/0010-late.html",
    ]


def test_site_record_fields(site: Site, tmp_path: Path) -> None:
    record = _record(site, "proj", "rule/0003")
    assert (record.stem, record.slug, record.number, record.type) == (
        "0003-uses",
        "uses",
        3,
        "rule",
    )
    assert record.path == (tmp_path / "proj" / "rule" / "0003-uses.md").resolve()
    assert record.body_first_line == 7
    assert _record(site, "proj", "value/0002").body_first_line == 1
    assert site.statuses == {"accepted", "draft"}


@pytest.mark.parametrize(
    ("text", "from_root", "expected"),
    [
        ("rule/0002", "core", "core/rule/0002-other.html"),
        ("core:rule/0001", "proj", "core/rule/0001-base.html"),
        ("rule/0009", "core", RefMiss(warn=True)),
        ("proj:value/0001", "core", RefMiss(warn=True)),
        ("elsewhere:rule/0001", "core", RefMiss(warn=False)),
        ("not a ref", "core", None),
    ],
)
def test_resolve_ref(site: Site, text: str, from_root: str, expected: str | RefMiss | None) -> None:
    resolved = site.resolve_ref(text, from_root)
    if isinstance(resolved, SiteRecord):
        assert resolved.page == expected
    else:
        assert resolved == expected


@pytest.mark.parametrize(
    ("dest", "kind", "page", "anchor"),
    [
        ("../../core/rule/0001-base.md#base", "record", "core/rule/0001-base.html", "base"),
        ("0010-late.md", "record", "proj/rule/0010-late.html", None),
        ("../../linkdir/0002-other.md", "record", "core/rule/0002-other.html", None),
        ("../../linkdir/0002%2Dother.md", "record", "core/rule/0002-other.html", None),
        ("../../notes.txt", "offsite", None, None),
        ("missing.md", "unresolved", None, None),
        ("../loop/x.md", "unresolved", None, None),
        ("https://example.com/a.md", "external", None, None),
        ("mailto:a@b.c", "external", None, None),
        ("/abs/path.md", "external", None, None),
        ("#section", "anchor", None, None),
    ],
)
def test_resolve_link(
    site: Site, dest: str, kind: str, page: str | None, anchor: str | None
) -> None:
    target: LinkTarget = site.resolve_link(dest, _record(site, "proj", "rule/0003"))
    assert target.kind == kind
    assert (target.record.page if target.record else None) == page
    assert target.anchor == anchor


def test_backlinks_from_frontmatter_and_body_deduped(site: Site) -> None:
    base = _record(site, "core", "rule/0001")
    other = _record(site, "core", "rule/0002")
    assert [r.page for r in site.backlinks(base)] == ["proj/rule/0003-uses.html"]
    assert [r.page for r in site.backlinks(other)] == ["proj/rule/0010-late.html"]
    assert site.backlinks(_record(site, "proj", "rule/0003")) == []
