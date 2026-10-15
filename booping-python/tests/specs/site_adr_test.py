from __future__ import annotations

import re
from pathlib import Path

import pytest

from booping.specs.site.markdown import Rendered, render_body
from booping.specs.site.model import SiteRoot, load_site
from booping.specs.site.pages import build_site

STATUSES = {"accepted", "rejected", "proposed"}
TABLE = (
    "| Option | Status | Complexity | Reversibility | Verdict |\n"
    "|---|---|---|---|---|\n"
    "| [First](#first) | rejected | low | high | Too small |\n"
    "| [Second](#second) | accepted | medium | medium | Fits |\n"
    "| [Third](#third) | proposed | high | low | Later |\n"
)
OPTIONS = (
    "### First\n\nOne.\n\n- **Pros:** cheap.\n\n"
    "### Second\n\nTwo.\n\n- **Pros:** fits.\n- **Cons:** work.\n\n"
    "### Third\n\nThree.\n\n"
    "### Fourth\n\nOrphan.\n\n"
)
ADR = (
    "## Context\n\nWhy [clarify].\n\n## Alternatives\n\n"
    + TABLE
    + "\n"
    + OPTIONS
    + "## Consequences\n\nDone.\n"
)
CHOSEN = (
    '<span class="b ok"><svg class="ic" aria-hidden="true"><use href="#i-accepted"/></svg>'
    "chosen</span>"
)


def _render(text: str, alternatives: bool) -> Rendered:
    return render_body(
        text, first_line=1, link=lambda d: (d, None), statuses=STATUSES, alternatives=alternatives
    )


def _anchor(id_: str, text: str) -> str:
    return f'<a class="anchor" href="#{id_}" aria-label="Link to this section: {text}">§</a>'


def test_options_render_as_cards_with_the_accepted_one_first_and_open() -> None:
    rendered = _render(ADR, alternatives=True)
    html = rendered.html
    assert '<table class="alts">' in html
    assert html.count('<tr class="chosen">') == 1
    assert (
        '<tr class="chosen">\n<td><a href="#second">Second</a></td>\n'
        '<td><span class="badge st-accepted">accepted</span> ' + CHOSEN + "</td>"
    ) in html
    cards = re.findall(r'<details class="([^"]*)"( open)?>\n<summary><h3 id="([^"]+)"', html)
    assert cards == [
        ("opt chosen", " open", "second"),
        ("opt", "", "first"),
        ("opt", "", "third"),
        ("opt", "", "fourth"),
    ]
    assert (
        '<summary><h3 id="second">Second' + _anchor("second", "Second") + "</h3>\n"
        '<span class="meta">' + CHOSEN + '<span class="b plain">complexity: medium</span>'
        '<span class="b plain">reversibility: medium</span></span></summary>\n'
        '<div class="in">\n<p class="verdict">Fits</p>\n<p>Two.</p>\n<ul>\n'
        "<li><strong>Pros:</strong> fits.</li>\n<li><strong>Cons:</strong> work.</li>\n</ul>\n"
        "</div>\n</details>\n"
    ) in html
    assert (
        '<span class="meta"><span class="b plain"><svg class="ic" aria-hidden="true">'
        '<use href="#i-rejected"/></svg>rejected</span><span class="b plain">complexity: low'
        '</span><span class="b plain">reversibility: high</span></span></summary>\n'
        '<div class="in">\n<p class="verdict">Too small</p>\n<p>One.</p>'
    ) in html
    assert (
        '<span class="meta"><span class="b warn"><svg class="ic" aria-hidden="true">'
        '<use href="#i-planned"/></svg>proposed</span><span class="b plain">complexity: high'
        '</span><span class="b plain">reversibility: low</span></span></summary>\n'
        '<div class="in">\n<p class="verdict">Later</p>\n<p>Three.</p>'
    ) in html
    assert (
        '<summary><h3 id="fourth">Fourth' + _anchor("fourth", "Fourth") + "</h3>\n"
        '</summary>\n<div class="in">\n<p>Orphan.</p>\n</div>\n</details>\n'
        '<h2 id="consequences">'
    ) in html
    plain = _render(ADR, alternatives=False)
    assert rendered.headings == plain.headings
    assert rendered.marks == plain.marks


@pytest.mark.parametrize(
    "body",
    [
        "## Context\n\nNo alternatives.\n\n" + OPTIONS,
        "## Alternatives\n\nProse first.\n\n" + TABLE + "\n" + OPTIONS,
        "## Alternatives\n\n" + TABLE.replace("Verdict", "Why") + "\n" + OPTIONS,
        "## Alternatives\n\n" + TABLE + "\n## Alternatives\n\n" + OPTIONS,
    ],
    ids=["no-section", "no-table-first", "other-columns", "two-sections"],
)
def test_a_shape_that_does_not_match_renders_as_without_cards(body: str) -> None:
    assert _render(body, alternatives=True).html == _render(body, alternatives=False).html


def test_only_adr_records_get_cards(tmp_path: Path) -> None:
    body = "---\ntitle: T\nstatus: accepted\n---\n" + ADR
    for type_ in ("adr", "rule"):
        path = tmp_path / "proj" / type_ / "0001-t.md"
        path.parent.mkdir(parents=True)
        path.write_text(body)
    types = ["rule", "adr"]
    files, _ = build_site(load_site([SiteRoot("proj", tmp_path / "proj")], types), types)
    adr, rule = files["proj/adr/0001-t.html"], files["proj/rule/0001-t.html"]
    assert isinstance(adr, str) and isinstance(rule, str)
    assert adr.count('<details class="opt') == 4
    assert "<details" not in rule.replace('<details class="toc-m">', "")
    assert '<table class="alts">' not in rule
