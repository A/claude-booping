from __future__ import annotations

import posixpath
import re
from collections.abc import Callable, Collection
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from markupsafe import Markup

from booping.specs.site.labels import Labels
from booping.specs.site.markdown import LinkRenderer, Rendered, render_body
from booping.specs.site.model import Site
from booping.specs.site.plans import Doc, Plan, Retro, Work
from booping.specs.site.state import RecordState

_URI_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
_MARK_KINDS = ("clarify", "unknown")
_RECENT_PLANS = 5
PLAN_SORTS = ("date", "title")
PageFn = Callable[..., None]


def plans_href(home: str) -> str:
    return f"{home}/plans/index.html"


def retros_href(home: str) -> str:
    return f"{home}/retrospectives/index.html"


def _state(status: Any) -> RecordState:
    return RecordState(
        status=None if status is None else str(status),
        kind=None,
        clarify=0,
        unknown=0,
        not_accepted=False,
        first_mark=None,
    )


def _rel(target: str, page: str) -> str:
    return posixpath.relpath(target, posixpath.dirname(page))


def _link_renderer(site: Site, pages: dict[Path, str], doc: Doc) -> LinkRenderer:
    records = {r.path: r for r in reversed(site.records)}

    def link(dest: str) -> tuple[str | None, str | None]:
        if _URI_SCHEME.match(dest) or dest.startswith(("/", "#")):
            return dest, None
        local, _, anchor = dest.partition("#")
        try:
            target = (doc.path.parent / unquote(local)).resolve()
            exists = target.exists()
        except (OSError, RuntimeError):
            return None, "unresolved"
        suffix = f"#{anchor}" if anchor else ""
        record = records.get(target)
        if record is not None:
            return _rel(record.page, doc.page) + suffix, None
        page = pages.get(target)
        if page is not None:
            return _rel(page, doc.page) + suffix, None
        return None, "offsite" if exists else "unresolved"

    return link


def _toc(rendered: Rendered) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for heading in rendered.headings:
        entry: dict[str, Any] = {"href": f"#{heading.id}", "text": heading.text, "children": []}
        if heading.level == 2 or (heading.level == 3 and not entries):
            entries.append(entry)
        elif heading.level == 3:
            entries[-1]["children"].append(entry)
    return entries if len(entries) >= 2 else []


def _questions(rendered: Rendered) -> list[dict[str, Any]]:
    return [
        {"href": f"#L{m.line}", "kind": m.kind, "text": m.text}
        for kind in _MARK_KINDS
        for m in rendered.marks
        if m.kind == kind
    ]


def _text(value: Any) -> dict[str, Any]:
    return {"text": str(value), "href": None, "datetime": None}


def _date(labels: Labels, iso: str) -> dict[str, Any]:
    return {"text": labels.date(iso), "href": None, "datetime": iso}


def _fact(labels: Labels, key: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"label": labels.fact(key), "items": items}


def _plan_rows(plans: list[Plan], labels: Labels) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for order, plan in enumerate(plans):
        sp = plan.index.frontmatter.get("sp")
        parts = [] if sp is None else [labels.ui("sp_n", n=sp)]
        if plan.milestones:
            parts.append(labels.plural("milestones_n", len(plan.milestones)))
        rows.append(
            {
                "ref": plan.date or plan.slug,
                "page": plan.index.page,
                "title": plan.index.title,
                "summary": " · ".join(parts) or None,
                "state": _state(plan.status),
                "data": {
                    "status": plan.status or "",
                    "date": plan.date,
                    "title": plan.index.title,
                    "order": str(order),
                },
            }
        )
    return rows


def _retro_rows(retros: list[Retro]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for order, retro in enumerate(retros):
        fm = retro.doc.frontmatter
        summary = fm.get("goal_summary", fm.get("summary"))
        rows.append(
            {
                "ref": retro.date or retro.slug,
                "page": retro.doc.page,
                "title": retro.doc.title,
                "summary": None if summary is None else str(summary),
                "state": _state(fm.get("status")),
                "data": {
                    "status": "" if fm.get("status") is None else str(fm["status"]),
                    "date": retro.date,
                    "title": retro.doc.title,
                    "order": str(order),
                },
            }
        )
    return rows


def work_nav(work: Work, labels: Labels, home: str) -> dict[str, Any] | None:
    """The sidebar's Plans and Retrospectives groups; None for a vault holding neither."""
    if not work:
        return None
    active = sum(1 for p in work.plans if p.status == "in-progress")
    return {
        "plans": (
            [{"label": labels.ui("all_plans"), "count": len(work.plans), "href": plans_href(home)}]
            if work.plans
            else []
        )
        + (
            [
                {
                    "label": labels.status("in-progress"),
                    "count": active,
                    "href": f"{plans_href(home)}#status=in-progress",
                }
            ]
            if active
            else []
        ),
        "retros": [
            {
                "label": labels.ui("all_retros"),
                "count": len(work.retros),
                "href": retros_href(home),
            }
        ]
        if work.retros
        else [],
    }


def recent_plans(work: Work, labels: Labels) -> list[dict[str, Any]]:
    return [
        {
            "page": plan.index.page,
            "title": plan.index.title,
            "state": _state(plan.status),
            "datetime": plan.date,
            "date": labels.date(plan.date) if plan.date else "",
        }
        for plan in work.plans[:_RECENT_PLANS]
    ]


def work_search_entries(work: Work, labels: Labels) -> list[dict[str, Any]]:
    """Plan and retrospective titles for `window.SPECS_INDEX`; bodies stay unindexed."""
    entries: list[dict[str, Any]] = []
    for plan in work.plans:
        summary = plan.index.frontmatter.get("summary")
        entries.append(
            {
                "id": f"plan:{plan.slug}",
                "ref": plan.slug,
                "root": "",
                "type": "plan",
                "type_label": labels.ui("plan"),
                "title": plan.index.title,
                "summary": None if summary is None else str(summary),
                "status": plan.status,
                "status_label": None if plan.status is None else labels.status(plan.status),
                "tags": [],
                "url": plan.index.page,
                "flags": [],
            }
        )
    for retro in work.retros:
        entries.append(
            {
                "id": f"retro:{retro.slug}",
                "ref": retro.slug,
                "root": "",
                "type": "retrospective",
                "type_label": labels.ui("retro"),
                "title": retro.doc.title,
                "summary": None,
                "status": None,
                "status_label": None,
                "tags": [],
                "url": retro.doc.page,
                "flags": [],
            }
        )
    return entries


def _plan_link(plan: Plan, page: str) -> dict[str, Any]:
    return {"text": plan.index.title, "href": _rel(plan.index.page, page), "datetime": None}


def render_work(
    site: Site,
    work: Work,
    labels: Labels,
    home: str,
    statuses: Collection[str],
    page: PageFn,
    filters: Callable[..., dict[str, Any]],
    crumb: Callable[[str, str | None], Any],
) -> None:
    """Every plan, milestone, sibling and retrospective page plus the two list pages.
    `page` is build_site's page writer, `filters` its filter-bar builder, `crumb` Crumb."""
    pages = {doc.path: doc.page for doc in work.docs()}
    plan_by_path = {plan.index.path: plan for plan in work.plans}
    plan_by_slug = {plan.slug: plan for plan in work.plans}
    retro_by_path = {retro.doc.path: retro for retro in work.retros}

    def vault_path(rel: str) -> Path:
        return (work.vault / rel).resolve()

    def find_plan(rel: str) -> Plan | None:
        # A retro written before plans became directories names `plans/{slug}.md`.
        found = plan_by_path.get(vault_path(rel))
        if found is not None:
            return found
        path = Path(rel)
        return plan_by_slug.get(path.parent.name if path.stem == "index" else path.stem)

    retro_of: dict[int, Retro] = {}
    for plan in work.plans:
        named = plan.index.frontmatter.get("retro")
        retro = retro_by_path.get(vault_path(named)) if isinstance(named, str) else None
        if retro is not None:
            retro_of[id(plan)] = retro
    for retro in work.retros:
        for rel in retro.plan_paths:
            target = find_plan(rel)
            if target is not None:
                retro_of.setdefault(id(target), retro)

    def render(doc: Doc) -> Rendered:
        return render_body(
            doc.body,
            first_line=doc.body_first_line,
            link=_link_renderer(site, pages, doc),
            statuses=statuses,
            labels=labels,
        )

    def doc_page(
        doc: Doc,
        comment_ref: str,
        crumbs: list[Any],
        facts: list[dict[str, Any]],
        status: Any,
        summary: Any = None,
        milestones: list[dict[str, Any]] | None = None,
        siblings: list[dict[str, Any]] | None = None,
    ) -> None:
        own = render(doc)
        page(
            "doc.html.j2",
            doc.page,
            doc.title,
            crumbs,
            doc={
                "title": doc.title,
                "ref": comment_ref,
                "page": doc.page,
                "state": _state(status),
                "summary": None if summary is None else str(summary),
                "facts": facts,
                "body": Markup(own.html),
                "toc": _toc(own),
                "questions": _questions(own),
                "milestones": milestones or [],
                "siblings": siblings or [],
            },
        )

    def overview(page_path: str) -> Any:
        return crumb(labels.ui("overview"), _rel("index.html", page_path))

    for plan in work.plans:
        fm = plan.index.frontmatter
        list_crumb = crumb(labels.ui("plans"), _rel(plans_href(home), plan.index.page))
        facts: list[dict[str, Any]] = []
        for key in ("type", "sp"):
            if fm.get(key) is not None:
                facts.append(_fact(labels, f"plan_{key}", [_text(fm[key])]))
        if plan.milestones:
            facts.append(_fact(labels, "milestones", [_text(len(plan.milestones))]))
        for key in ("created", "started", "completed"):
            iso = plan.date if key == "created" else ""
            if key != "created":
                value = fm.get(key)
                iso = "" if value is None else str(value)[:10]
            if iso:
                facts.append(_fact(labels, key, [_date(labels, iso)]))
        if fm.get("goal") is not None:
            facts.append(_fact(labels, "goal", [_text(fm["goal"])]))
        retro = retro_of.get(id(plan))
        if retro is not None:
            facts.append(
                _fact(
                    labels,
                    "retro",
                    [
                        {
                            "text": retro.doc.title,
                            "href": _rel(retro.doc.page, plan.index.page),
                            "datetime": None,
                        }
                    ],
                )
            )
        milestone_rows = [
            {
                "id": "" if m.frontmatter.get("id") is None else str(m.frontmatter["id"]),
                "title": m.title,
                "href": _rel(m.page, plan.index.page),
                "sp": "" if m.frontmatter.get("sp") is None else str(m.frontmatter["sp"]),
                "state": _state(m.frontmatter.get("status")),
            }
            for m in plan.milestones
        ]
        sibling_links = [
            {
                "label": labels.ui(f"doc_{s.name.replace('-', '_')}"),
                "href": _rel(s.page, plan.index.page),
            }
            for s in plan.siblings
        ]
        doc_page(
            plan.index,
            plan.slug,
            [overview(plan.index.page), list_crumb, crumb(plan.index.title, None)],
            facts,
            plan.status,
            fm.get("summary"),
            milestone_rows,
            sibling_links,
        )
        for child in [*plan.milestones, *plan.siblings]:
            cfm = child.frontmatter
            child_facts: list[dict[str, Any]] = [
                _fact(labels, "plan", [_plan_link(plan, child.page)])
            ]
            if cfm.get("sp") is not None:
                child_facts.append(_fact(labels, "plan_sp", [_text(cfm["sp"])]))
            title = (
                child.title
                if child in plan.milestones
                else labels.ui(f"doc_{child.name.replace('-', '_')}")
            )
            doc_page(
                child,
                f"{plan.slug}/{child.name}",
                [
                    overview(child.page),
                    list_crumb,
                    crumb(plan.index.title, _rel(plan.index.page, child.page)),
                    crumb(title, None),
                ],
                child_facts,
                cfm.get("status") if child in plan.milestones else None,
            )

    for retro in work.retros:
        fm = retro.doc.frontmatter
        facts = []
        if retro.date:
            facts.append(_fact(labels, "date", [_date(labels, retro.date)]))
        linked: list[dict[str, Any]] = []
        for rel in retro.plan_paths:
            target = find_plan(rel)
            linked.append(_plan_link(target, retro.doc.page) if target else _text(rel))
        if linked:
            facts.append(_fact(labels, "plans", linked))
        doc_page(
            retro.doc,
            f"retrospectives/{retro.slug}",
            [
                overview(retro.doc.page),
                crumb(labels.ui("retros"), _rel(retros_href(home), retro.doc.page)),
                crumb(retro.doc.title, None),
            ],
            facts,
            fm.get("status"),
            fm.get("goal_summary", fm.get("summary")),
        )

    if work.plans:
        rows = _plan_rows(work.plans, labels)
        page(
            "work.html.j2",
            plans_href(home),
            labels.ui("plans"),
            [crumb(labels.ui("overview"), "../../index.html"), crumb(labels.ui("plans"), None)],
            heading=labels.ui("plans"),
            rows=rows,
            filters=filters(rows, labels, "date", PLAN_SORTS, ("status",), ()),
        )
    if work.retros:
        rows = _retro_rows(work.retros)
        page(
            "work.html.j2",
            retros_href(home),
            labels.ui("retros"),
            [crumb(labels.ui("overview"), "../../index.html"), crumb(labels.ui("retros"), None)],
            heading=labels.ui("retros"),
            rows=rows,
            filters=filters(rows, labels, "date", PLAN_SORTS, ("status",), ()),
        )
