from __future__ import annotations

from pathlib import Path

import pytest

from booping.specs.site.backlinks import (
    Backlink,
    Backlinks,
    SectionGroup,
    TypeGroup,
    backlink_groups,
)
from booping.specs.site.labels import load_labels
from booping.specs.site.markdown import Heading, Rendered, render_body
from booping.specs.site.model import Site, SiteRecord, SiteRoot, load_site

TYPES = ["value", "rule", "adr"]

FILES = {
    "value/0001-x.md": "---\ntitle: X\n---\n# X\n\n## Why\n\nBecause.\n",
    "rule/0001-r.md": "---\ntitle: R\nvalues: [value/0001]\n---\n# R\n\nNo body link.\n",
    "rule/0002-two.md": (
        "---\ntitle: Two\n---\nIntro [x](../value/0001-x.md).\n\n## Later\n\nNothing.\n"
    ),
    "adr/0001-a.md": (
        "---\ntitle: A\n---\n# A\n\n"
        "## Decision\n\nSee [x](../value/0001-x.md#why).\n\n"
        "## Consequences\n\n[x](../value/0001-x.md) and [y](../value/0001-x.md#nowhere).\n"
        "\nAgain [x](../value/0001-x.md).\n"
    ),
}


@pytest.fixture
def site(tmp_path: Path) -> Site:
    for name, text in FILES.items():
        path = tmp_path / "proj" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return load_site([SiteRoot("proj", tmp_path / "proj")], TYPES)


def _rendered(site: Site) -> dict[int, Rendered]:
    return {
        id(r): render_body(
            r.body, first_line=r.body_first_line, link=lambda d: (d, None), statuses=set()
        )
        for r in site.records
    }


def _get(site: Site, ref: str) -> SiteRecord:
    return next(r for r in site.records if r.ref == ref)


def test_value_backlinks_group_by_type_with_via_and_by_section(site: Site) -> None:
    labels = load_labels({})[0]
    value = _get(site, "value/0001")
    groups = backlink_groups(site, value, _rendered(site), labels, TYPES)
    assert groups == Backlinks(
        by_type=[
            TypeGroup(
                "rule",
                "Rules",
                [
                    Backlink(_get(site, "rule/0001"), ["Serves values"]),
                    Backlink(_get(site, "rule/0002"), ["Two"]),
                ],
            ),
            TypeGroup(
                "adr", "ADRs", [Backlink(_get(site, "adr/0001"), ["Decision", "Consequences"])]
            ),
        ],
        by_section=[
            SectionGroup(Heading(level=2, text="Why", id="why", line=6), [_get(site, "adr/0001")])
        ],
    )


def test_record_nobody_cites_has_no_groups(site: Site) -> None:
    labels = load_labels({})[0]
    groups = backlink_groups(site, _get(site, "adr/0001"), _rendered(site), labels, TYPES)
    assert groups == Backlinks(by_type=[], by_section=[])
