from __future__ import annotations

from pathlib import Path

import pytest

from booping.specs.site.markdown import Heading, Mark, render_body, slug
from booping.specs.site.model import (
    LinkTarget,
    RefMiss,
    Site,
    SiteRecord,
    SiteRoot,
    load_site,
)
from booping.specs.site.state import RecordState, record_state

CLARIFY_ICON = '<svg class="ic" aria-hidden="true"><use href="#i-clarify"/></svg>'
UNKNOWN_ICON = '<svg class="ic" aria-hidden="true"><use href="#i-unknown"/></svg>'


def _no_link(dest: str) -> tuple[str | None, str | None]:
    return dest, None


def _render(text: str, first_line: int = 1, statuses: set[str] | None = None) -> str:
    return render_body(text, first_line=first_line, link=_no_link, statuses=statuses or set()).html


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
        link=_no_link,
        statuses=set(),
    ).html
    assert html == (
        '<h1 id="notes">Notes</h1>\n'
        '<h2 id="notes-1">Notes<a class="anchor" href="#notes-1"'
        ' aria-label="Link to this section: Notes">§</a></h2>\n'
        '<h3 id="notes-2">Notes<a class="anchor" href="#notes-2"'
        ' aria-label="Link to this section: Notes">§</a></h3>\n'
    )


def _anchor(id_: str, text: str) -> str:
    return f'<a class="anchor" href="#{id_}" aria-label="Link to this section: {text}">§</a>'


def test_headings_are_listed_and_h2_to_h4_end_with_a_section_anchor() -> None:
    body = "# Title\n\n## Why\n\n### Open [clarify] point\n\n#### Deep\n\n## Why\n\n##### Tiny\n"
    rendered = render_body(body, first_line=5, link=_no_link, statuses=set())
    assert rendered.headings == [
        Heading(level=1, text="Title", id="title", line=5),
        Heading(level=2, text="Why", id="why", line=7),
        Heading(level=3, text="Open [clarify] point", id="open-clarify-point", line=9),
        Heading(level=4, text="Deep", id="deep", line=11),
        Heading(level=2, text="Why", id="why-1", line=13),
        Heading(level=5, text="Tiny", id="tiny", line=15),
    ]
    assert rendered.html == (
        '<h1 id="title">Title</h1>\n'
        '<h2 id="why">Why' + _anchor("why", "Why") + "</h2>\n"
        '<h3 id="open-clarify-point">Open <mark id="L9" class="mk mk-clarify">'
        + CLARIFY_ICON
        + "[clarify]</mark> point"
        + _anchor("open-clarify-point", "Open [clarify] point")
        + "</h3>\n"
        '<h4 id="deep">Deep' + _anchor("deep", "Deep") + "</h4>\n"
        '<h2 id="why-1">Why' + _anchor("why-1", "Why") + "</h2>\n"
        '<h5 id="tiny">Tiny</h5>\n'
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
            '<p>intro</p>\n<p id="L12">we <mark class="mk mk-clarify">'
            + CLARIFY_ICON
            + "[clarify]</mark> this</p>\n",
            [Mark(line=12, kind="clarify", text="we [clarify] this")],
        ),
        (
            "- first\n- second [unknown]\n",
            '<ul>\n<li>first</li>\n<li id="L11">second <mark class="mk mk-unknown">'
            + UNKNOWN_ICON
            + "[unknown]"
            "</mark></li>\n</ul>\n",
            [Mark(line=11, kind="unknown", text="second [unknown]")],
        ),
        (
            "| a | b |\n|---|---|\n| x | [clarify] |\n",
            "<table>\n<thead>\n<tr>\n<th>a</th>\n<th>b</th>\n</tr>\n</thead>\n<tbody>\n"
            '<tr id="L12">\n<td>x</td>\n<td><mark class="mk mk-clarify">'
            + CLARIFY_ICON
            + "[clarify]</mark></td>\n"
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
    rendered = render_body(text, first_line=10, link=_no_link, statuses=set())
    assert rendered.html == html
    assert rendered.marks == marks


def test_mark_text_is_collapsed_and_cut() -> None:
    body = "[clarify] " + "word " * 40 + "\nmore\n"
    rendered = render_body(body, first_line=3, link=_no_link, statuses=set())
    expected = ("[clarify] " + "word " * 40 + "more")[:160] + "…"
    assert rendered.marks == [Mark(line=3, kind="clarify", text=expected)]
    assert rendered.html.startswith('<p id="L3">')


def test_one_anchor_per_block_with_both_kinds() -> None:
    rendered = render_body("a [clarify] b [unknown]\n", first_line=1, link=_no_link, statuses=set())
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
        ("obsidian://open?vault=x", "external", None, None),
        ("tel:+123", "external", None, None),
        ("0010-late.md#a:b", "record", "proj/rule/0010-late.html", "a:b"),
        ("../rule/0010-late.md#a:b", "record", "proj/rule/0010-late.html", "a:b"),
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


@pytest.fixture
def related(tmp_path: Path) -> Site:
    proj = tmp_path / "proj"
    booping = tmp_path / "booping"
    _write(proj / "value" / "0001-v.md", "---\ntitle: V\n---\nv\n")
    _write(proj / "mechanic" / "0001-dash.md", "---\ntitle: Dash\n---\nd\n")
    _write(
        proj / "adr" / "0001-old.md",
        "---\nvalues: [value/0001, value/0001, value/0099]\nmechanics: [mechanic/0001]\n"
        "rules: [booping:rule/0002]\ntags: [x]\n---\nold\n",
    )
    _write(proj / "adr" / "0002-new.md", "---\nsupersedes: [adr/0001]\n---\nnew\n")
    _write(booping / "rule" / "0002-r.md", "---\ntitle: R\n---\nr\n")
    return load_site(
        [SiteRoot(name="proj", path=proj), SiteRoot(name="booping", path=booping)],
        ["value", "rule", "adr", "mechanic"],
    )


def test_relations_resolve_dedupe_and_sort_keys(related: Site) -> None:
    relations = related.relations(_record(related, "proj", "adr/0001"))
    assert {key: [r.page for r in targets] for key, targets in relations.items()} == {
        "mechanics": ["proj/mechanic/0001-dash.html"],
        "rules": ["booping/rule/0002-r.html"],
        "values": ["proj/value/0001-v.html"],
    }
    assert list(relations) == ["mechanics", "rules", "values"]
    assert related.relations(_record(related, "proj", "value/0001")) == {}


def test_superseded_by_follows_direct_supersedes(related: Site) -> None:
    old = _record(related, "proj", "adr/0001")
    new = _record(related, "proj", "adr/0002")
    assert related.superseded_by(old) == [new]
    assert related.superseded_by(new) == []


def test_record_state_counts_marks_and_review(related: Site) -> None:
    record = SiteRecord(
        root="proj",
        type="adr",
        number=3,
        slug="s",
        path=Path("/x/0003-s.md"),
        frontmatter={
            "status": "proposed",
            "kind": None,
            "review": "accepted",
            "review_evidence": "site review — 2026-10-01",
        },
        body="",
        body_first_line=1,
    )
    marks = render_body(
        "a [clarify]\n\nb [unknown] [clarify]\n",
        first_line=7,
        link=_no_link,
        statuses=set(),
    ).marks
    assert record_state(record, marks) == RecordState(
        status="proposed",
        kind=None,
        clarify=2,
        unknown=1,
        not_accepted=False,
        first_mark="L7",
        first_clarify="L7",
        first_unknown="L9",
        reasons=("clarify", "unknown", "proposed"),
        review="accepted",
    )
    unread = _record(related, "proj", "adr/0002")
    assert record_state(unread, []) == RecordState(
        status=None,
        kind=None,
        clarify=0,
        unknown=0,
        not_accepted=True,
        first_mark=None,
        reasons=("not_accepted",),
        review="none",
    )
