from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from booping.specs.site.labels import load_labels
from booping.specs.site.model import SiteRoot, load_site
from booping.specs.site.pages import build_site
from booping.specs.site.plans import Work, load_work

TYPES = ["rule"]
PLAN_GLOBS = ["plans/*/index.md"]
MILESTONES = "milestones/*/M*.md"
RETROS = ["retrospectives/*.md"]
BASE = "proj/plans/20261002-alpha"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    """Two directory plans (alpha with two milestones, a request and develop defaults; beta
    bare), one single-file plan, a stray file no glob claims, and two retrospectives —
    one naming alpha by its pre-directory path."""
    v = tmp_path / "vault"
    _write(v / "rule" / "0001-linear.md", "---\ntitle: Linear\nstatus: accepted\n---\n")
    _write(
        v / "plans" / "20261002-alpha" / "index.md",
        "---\ntitle: Alpha plan\nstatus: in-progress\nsp: 5\ntype: feature\n"
        "created: 2026-10-02 10:00\n---\n\n# Alpha plan\n\n"
        "See [first](milestones/M01-first/M01-first.md) and [linear](../../rule/0001-linear.md).\n",
    )
    _write(
        v / "plans" / "20261002-alpha" / "milestones" / "M01-first" / "M01-first.md",
        '---\nid: "01"\ntitle: First step\nsp: 2\nstatus: done\n---\n\n# M01: First step\n',
    )
    _write(
        v / "plans" / "20261002-alpha" / "milestones" / "M02-second" / "M02-second.md",
        '---\nid: "02"\ntitle: Second step\nsp: 3\nstatus: open\n---\n\n# M02\n',
    )
    _write(v / "plans" / "20261002-alpha" / "milestones" / "M02-second" / "notes.md", "x\n")
    _write(v / "plans" / "20261002-alpha" / "request.md", "# Request\n\nDo it.\n")
    _write(v / "plans" / "20261002-alpha" / "develop-defaults.md", "# Defaults\n")
    _write(v / "plans" / "20261002-alpha" / "template-cuts.md", "# Not a page\n")
    _write(
        v / "plans" / "20261005-beta" / "index.md",
        "---\ntitle: Beta plan\nstatus: done\nsp: 1\ncreated: 2026-10-05\n---\n",
    )
    _write(v / "plans" / "20260401-old.md", "---\nstatus: done\n---\n\n# Old single file\n")
    _write(v / "plans" / "20260301-stray" / "plan.md", "---\ntitle: Stray\n---\n")
    _write(
        v / "retrospectives" / "20261003-alpha.md",
        "---\ndate: 2026-10-03\nplans:\n  - plans/20261002-alpha.md\n"
        "goal_summary: Alpha went fine.\n---\n\n# Retro — alpha\n",
    )
    _write(v / "retrospectives" / "20260402-old.md", "---\ndate: 2026-04-02\n---\n\n# Retro old\n")
    return v


def _work(vault: Path) -> Work:
    return load_work(vault, "proj", PLAN_GLOBS, MILESTONES, RETROS)


def _build(vault: Path, work: Work | None, lang: str = "en") -> dict[str, str]:
    site = load_site([SiteRoot("proj", vault)], TYPES)
    labels, lang, _ = load_labels({"lang": lang})
    files, _ = build_site(site, TYPES, labels, lang, "proj", home="proj", work=work)
    return {path: text for path, text in files.items() if isinstance(text, str)}


@pytest.fixture
def pages(vault: Path) -> dict[str, str]:
    return _build(vault, _work(vault))


def _main(page: str) -> str:
    return page.split('<main id="main">', 1)[1]


def _side(page: str) -> str:
    return page.split('<nav class="side"', 1)[1].split("</nav>", 1)[0]


def _crumbs(page: str) -> list[str]:
    crumbs = page.split('<nav class="crumbs"', 1)[1].split("</nav>", 1)[0]
    return re.findall(r"<li[^>]*>(?:<a [^>]+>|<span[^>]*>)([^<]+)<", crumbs)


def test_load_work_orders_plans_newest_first_and_reads_milestones_and_siblings(
    vault: Path,
) -> None:
    work = _work(vault)
    assert [(p.slug, p.date, p.index.title) for p in work.plans] == [
        ("20261005-beta", "2026-10-05", "Beta plan"),
        ("20261002-alpha", "2026-10-02", "Alpha plan"),
        ("20260401-old", "2026-04-01", "Old single file"),
    ]
    alpha = work.plans[1]
    assert [m.name for m in alpha.milestones] == ["M01-first", "M02-second"]
    assert [s.name for s in alpha.siblings] == ["request", "develop-defaults"]
    assert work.plans[2].milestones == [] and work.plans[2].siblings == []
    assert [(r.slug, r.doc.title) for r in work.retros] == [
        ("20261003-alpha", "Retro — alpha"),
        ("20260402-old", "Retro old"),
    ]


def test_a_directory_plan_wins_over_a_single_file_of_the_same_slug(vault: Path) -> None:
    _write(vault / "plans" / "20261005-beta.md", "---\ntitle: Shadow\n---\n")
    titles = [p.index.title for p in _work(vault).plans]
    assert "Shadow" not in titles and "Beta plan" in titles


def test_plan_list_shows_title_status_sp_milestones_and_date_newest_first(
    pages: dict[str, str],
) -> None:
    rows = re.findall(
        r'<li class="row" data-status="([^"]*)" data-date="([^"]*)"[^>]*>'
        r'<code class="ref">([^<]+)</code><a class="t" href="([^"]+)">([^<]+)</a>'
        r'.*?(?:<span class="s">([^<]+)</span>)?</li>',
        _main(pages["proj/plans/index.html"]),
    )
    assert rows == [
        ("done", "2026-10-05", "2026-10-05", "../../proj/plans/20261005-beta/index.html",
         "Beta plan", "1 SP"),
        ("in-progress", "2026-10-02", "2026-10-02", f"../../{BASE}/index.html", "Alpha plan",
         "5 SP · 2 milestones"),
        ("done", "2026-04-01", "2026-04-01", "../../proj/plans/20260401-old/index.html",
         "Old single file", ""),
    ]  # fmt: skip
    chips = re.findall(r'data-key="status" data-value="([^"]+)"', pages["proj/plans/index.html"])
    assert chips == ["done", "in-progress"]


def test_plan_page_links_its_milestones_siblings_and_retro_and_resolves_body_links(
    pages: dict[str, str],
) -> None:
    page = pages[f"{BASE}/index.html"]
    main = _main(page)
    assert _crumbs(page) == ["Overview", "Plans", "Alpha plan"]
    assert '<article data-ref="20261002-alpha" data-title="Alpha plan"' in main
    milestones = main.split('id="plan-milestones"', 1)[1].split("</table>", 1)[0]
    assert re.findall(r'<td>(\d+)</td><td><a href="([^"]+)">([^<]+)</a></td><td>(\d+)</td>',
                      milestones) == [
        ("01", "M01-first.html", "First step", "2"),
        ("02", "M02-second.html", "Second step", "3"),
    ]  # fmt: skip
    files = main.split('id="plan-files"', 1)[1].split("</ul>", 1)[0]
    assert re.findall(r'<a href="([^"]+)">([^<]+)</a>', files) == [
        ("request.html", "Request"),
        ("develop-defaults.html", "Develop defaults"),
    ]
    assert '<a href="M01-first.html">first</a>' in main
    assert '<a href="../../rule/0001-linear.html">linear</a>' in main
    assert '<a href="../../retrospectives/20261003-alpha.html">Retro — alpha</a>' in main
    for target in ("M01-first", "M02-second", "request", "develop-defaults"):
        assert f"{BASE}/{target}.html" in pages
    assert f"{BASE}/template-cuts.html" not in pages
    assert f"{BASE}/notes.html" not in pages
    assert not any("20260301-stray" in path for path in pages)


def test_milestone_and_sibling_pages_sit_under_their_plan(pages: dict[str, str]) -> None:
    milestone = pages[f"{BASE}/M01-first.html"]
    assert _crumbs(milestone) == ["Overview", "Plans", "Alpha plan", "First step"]
    assert 'data-ref="20261002-alpha/M01-first"' in milestone
    assert '<a href="index.html">Alpha plan</a>' in _main(milestone)
    request = pages[f"{BASE}/request.html"]
    assert _crumbs(request) == ["Overview", "Plans", "Alpha plan", "Request"]
    assert 'data-ref="20261002-alpha/request"' in request
    assert '<section class="rv"' in request
    assert 'id="rv-accepted"' not in request
    assert 'id="rv-accepted"' not in pages[f"{BASE}/index.html"]


def test_retro_page_links_a_plan_named_by_its_old_single_file_path(
    pages: dict[str, str],
) -> None:
    page = pages["proj/retrospectives/20261003-alpha.html"]
    assert _crumbs(page) == ["Overview", "Retrospectives", "Retro — alpha"]
    assert '<p class="lead">Alpha went fine.</p>' in page
    assert '<a href="../plans/20261002-alpha/index.html">Alpha plan</a>' in page
    assert 'data-ref="retrospectives/20261003-alpha"' in page
    listing = pages["proj/retrospectives/index.html"]
    rows = re.findall(r'<a class="t" href="[^"]+">([^<]+)</a>', listing)
    assert rows == ["Retro — alpha", "Retro old"]


def test_sidebar_and_overview_carry_plans_and_retros(pages: dict[str, str]) -> None:
    side = _side(pages["index.html"])
    assert re.findall(r"<h4>(Plans|Retrospectives)</h4>", side) == ["Plans", "Retrospectives"]
    links = r'<a href="(proj/[a-z]+/index.html[^"]*)">([^<]+)<span class="n">(\d+)'
    assert re.findall(links, side) == [
        ("proj/rule/index.html", "Rules", "1"),
        ("proj/plans/index.html", "All plans", "3"),
        ("proj/plans/index.html#status=in-progress", "in progress", "1"),
        ("proj/retrospectives/index.html", "All retrospectives", "2"),
    ]  # fmt: skip
    recent = _main(pages["index.html"]).split("Recent plans", 1)[1].split("</ul>", 1)[0]
    assert re.findall(r'</span></span><a href="([^"]+)">', recent) == [
        "proj/plans/20261005-beta/index.html",
        f"{BASE}/index.html",
        "proj/plans/20260401-old/index.html",
    ]


def test_overview_lists_at_most_five_recent_plans(vault: Path) -> None:
    for day in range(10, 17):
        _write(vault / "plans" / f"202610{day}-p" / "index.md", f"---\ntitle: P{day}\n---\n")
    recent = _main(_build(vault, _work(vault))["index.html"]).split("Recent plans", 1)[1]
    titles = re.findall(r'index.html">(P\d+)</a>', recent.split("</ul>", 1)[0])
    assert titles == ["P16", "P15", "P14", "P13", "P12"]


def test_search_index_carries_plan_and_retro_titles(pages: dict[str, str]) -> None:
    text = pages["search-index.js"]
    entries = json.loads(text.removeprefix("window.SPECS_INDEX = ").rstrip(";\n"))
    assert [(e["id"], e["title"], e["url"]) for e in entries if e["type"] != "rule"] == [
        ("plan:20261005-beta", "Beta plan", "proj/plans/20261005-beta/index.html"),
        ("plan:20261002-alpha", "Alpha plan", f"{BASE}/index.html"),
        ("plan:20260401-old", "Old single file", "proj/plans/20260401-old/index.html"),
        ("retro:20261003-alpha", "Retro — alpha", "proj/retrospectives/20261003-alpha.html"),
        ("retro:20260402-old", "Retro old", "proj/retrospectives/20260402-old.html"),
    ]


def test_russian_labels_name_the_plan_sections(vault: Path) -> None:
    pages = _build(vault, _work(vault), "ru")
    side = _side(pages["index.html"])
    assert "<h4>Планы</h4>" in side and "<h4>Ретроспективы</h4>" in side
    assert "в работе" in side
    plan = _main(pages[f"{BASE}/index.html"])
    assert ">Этапы<" in plan and ">Запрос</a>" in plan
    assert "2 этапа" in pages["proj/plans/index.html"]


def test_a_vault_without_plans_renders_as_before(vault: Path, tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    _write(empty / "rule" / "0001-linear.md", "---\ntitle: Linear\nstatus: accepted\n---\n")
    work = load_work(empty, "proj", PLAN_GLOBS, MILESTONES, RETROS)
    assert not work
    with_empty = _build(empty, work)
    without = _build(empty, None)
    assert with_empty == without
    assert "Plans" not in with_empty["index.html"]
    assert not any("/plans/" in path for path in with_empty)
