from __future__ import annotations

from pathlib import Path

import pytest

from booping.specs.site.labels import load_labels
from booping.specs.site.model import Site, SiteRoot, load_site
from booping.specs.site.pages import build_site

TYPES = ["value", "rule", "adr", "idea"]

RECORDS = {
    "core/value/0001-clarity.md": (
        "---\ntitle: Clarity\nsummary: Say what you mean.\n"
        "review: accepted\nreview_evidence: site review — 2026-10-01\n"
        "---\n"
        "# Clarity\n\nSay   what\nyou *mean*.\n"
    ),
    "proj/rule/0001-small.md": (
        "---\ntitle: Small steps\nstatus: accepted\n"
        "review: accepted\nreview_evidence: site review — 2026-10-01\n"
        "---\nUse `git add -p`.\n"
    ),
    "proj/adr/0001-elka.md": (
        "---\ntitle: Решение про ёлку\nsummary: Ставим ёлку.\nstatus: proposed\n"
        "tags: [зима, праздник]\n---\n"
        "## Почему\n\nЁлка нужна [clarify] к празднику.\n\n"
        "| Опция | Итог |\n|---|---|\n| [Ель](../rule/0001-small.md) | да |\n"
    ),
}


@pytest.fixture
def site(tmp_path: Path) -> Site:
    for rel, text in RECORDS.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    roots = [SiteRoot("core", tmp_path / "core"), SiteRoot("proj", tmp_path / "proj")]
    return load_site(roots, TYPES)


def _files(site: Site) -> dict[str, str | bytes]:
    labels, lang, _ = load_labels({"lang": "ru"})
    return build_site(site, TYPES, labels, lang)[0]


def test_search_index_js_matches_the_locked_format(site: Site) -> None:
    assert _files(site)["search-index.js"] == (
        "window.SPECS_INDEX = ["
        '{"id":"core:value/0001","ref":"value/0001","root":"core","type":"value",'
        '"type_label":"Ценность","title":"Clarity","summary":"Say what you mean.",'
        '"status":null,"status_label":null,"tags":[],'
        '"url":"core/value/0001-clarity.html","flags":[]},'
        '{"id":"proj:rule/0001","ref":"rule/0001","root":"proj","type":"rule",'
        '"type_label":"Правило","title":"Small steps","summary":null,'
        '"status":"accepted","status_label":"принято","tags":[],'
        '"url":"proj/rule/0001-small.html","flags":[]},'
        '{"id":"proj:adr/0001","ref":"adr/0001","root":"proj","type":"adr",'
        '"type_label":"Решение","title":"Решение про ёлку","summary":"Ставим ёлку.",'
        '"status":"proposed","status_label":"предложено","tags":["зима","праздник"],'
        '"url":"proj/adr/0001-elka.html","flags":["not_accepted","clarify"]}'
        "];\n"
    )


def test_search_body_js_maps_each_id_to_its_plain_text(site: Site) -> None:
    assert _files(site)["search-body.js"] == (
        "window.SPECS_BODY = {"
        '"core:value/0001":"Clarity Say what you mean.",'
        '"proj:rule/0001":"Use git add -p.",'
        '"proj:adr/0001":"Почему Ёлка нужна [clarify] к празднику. Опция Итог Ель да"'
        "};\n"
    )


def test_two_builds_give_identical_search_files(site: Site) -> None:
    first, second = _files(site), _files(site)
    assert first["search-index.js"] == second["search-index.js"]
    assert first["search-body.js"] == second["search-body.js"]
