from __future__ import annotations

import datetime
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from booping.context._yaml import UnclosedFrontmatterError, safe_load_str, split_frontmatter
from booping.query import discover

# Sibling files of a plan's index.md rendered as pages, in page order.
SIBLINGS = ("request", "clarifications", "develop-defaults", "defaults")
_SLUG_DATE = re.compile(r"(\d{4})(\d{2})(\d{2})")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_H1 = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.MULTILINE)


@dataclass(frozen=True, eq=False)
class Doc:
    """One vault markdown file rendered as a site page; `page` is out-root-relative."""

    path: Path
    page: str
    name: str
    frontmatter: dict[str, Any]
    body: str
    body_first_line: int

    @property
    def title(self) -> str:
        title = self.frontmatter.get("title")
        if title:
            return str(title)
        match = _H1.search(self.body)
        return match.group(1) if match else self.name


@dataclass(frozen=True, eq=False)
class Plan:
    slug: str
    index: Doc
    milestones: list[Doc] = field(default_factory=lambda: [])
    siblings: list[Doc] = field(default_factory=lambda: [])

    @property
    def date(self) -> str:
        return doc_date(self.index.frontmatter.get("created"), self.slug)

    @property
    def status(self) -> str | None:
        status = self.index.frontmatter.get("status")
        return None if status is None else str(status)


@dataclass(frozen=True, eq=False)
class Retro:
    slug: str
    doc: Doc

    @property
    def date(self) -> str:
        return doc_date(self.doc.frontmatter.get("date"), self.slug)

    @property
    def plan_paths(self) -> list[str]:
        fm = self.doc.frontmatter
        value: Any = fm.get("plans", fm.get("plan"))
        items: list[Any] = value if isinstance(value, list) else [value]  # pyright: ignore[reportUnknownVariableType]
        return [str(i) for i in items if isinstance(i, str)]


@dataclass
class Work:
    """The home registry's plans, newest first, and retrospectives, newest first."""

    vault: Path = Path(".")
    plans: list[Plan] = field(default_factory=lambda: [])
    retros: list[Retro] = field(default_factory=lambda: [])

    def __bool__(self) -> bool:
        return bool(self.plans or self.retros)

    def docs(self) -> list[Doc]:
        out: list[Doc] = []
        for plan in self.plans:
            out += [plan.index, *plan.milestones, *plan.siblings]
        out += [retro.doc for retro in self.retros]
        return out


def doc_date(value: Any, slug: str) -> str:
    """ISO date of a frontmatter date value, else of the slug's leading `YYYYMMDD`, else ""."""
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    text = "" if value is None else str(value)[:10]
    if _ISO_DATE.fullmatch(text):
        return text
    match = _SLUG_DATE.match(slug)
    return f"{match[1]}-{match[2]}-{match[3]}" if match else ""


def _doc(path: Path, page: str, name: str) -> Doc:
    text = path.read_text()
    try:
        yaml_text, body = split_frontmatter(text)
    except UnclosedFrontmatterError:
        yaml_text, body = None, text
    frontmatter: dict[str, Any] = {}
    if yaml_text is not None:
        try:
            loaded: Any = safe_load_str(yaml_text)
        except yaml.YAMLError:
            loaded = {}
        frontmatter = loaded if isinstance(loaded, dict) else {}  # pyright: ignore[reportUnknownVariableType]
    return Doc(
        path=path.resolve(),
        page=page,
        name=name,
        frontmatter=frontmatter,
        body=body,
        body_first_line=text[: len(text) - len(body)].count("\n") + 1,
    )


def _legacy_globs(plan_globs: Sequence[str]) -> list[str]:
    """`plans/*.md` beside every `plans/*/index.md`: the single-file plans older vaults hold."""
    out: list[str] = []
    for pattern in plan_globs:
        head, _, tail = pattern.rpartition("/*/")
        if head and "/" not in tail and "*" not in tail:
            out.append(f"{head}/*.md")
    return out


def load_work(
    vault: Path,
    home: str,
    plan_globs: Sequence[str],
    milestone_glob: str | None,
    retro_globs: Sequence[str],
) -> Work:
    """Plans claimed by `plan_globs` (then the single-file `plans/*.md` beside them, never
    overriding a directory plan), their milestones and sibling files, and the
    retrospectives `retro_globs` claim; pages under `{home}/plans/` and
    `{home}/retrospectives/`."""
    plans: list[Plan] = []
    claimed = dict(discover(vault, plan_globs))
    single = {
        slug: path
        for slug, path in discover(vault, _legacy_globs(plan_globs))
        if slug not in claimed
    }
    for slug, path in sorted({**claimed, **single}.items()):
        base = f"{home}/plans/{slug}"
        index = _doc(path, f"{base}/index.html", slug)
        milestones: list[Doc] = []
        siblings: list[Doc] = []
        if slug in claimed:
            plan_dir = path.parent
            if milestone_glob:
                milestones = [
                    _doc(p, f"{base}/{p.stem}.html", p.stem)
                    for p in sorted(plan_dir.glob(milestone_glob))
                    if p.is_file()
                ]
            siblings = [
                _doc(plan_dir / f"{name}.md", f"{base}/{name}.html", name)
                for name in SIBLINGS
                if (plan_dir / f"{name}.md").is_file()
            ]
        plans.append(Plan(slug, index, milestones, siblings))
    plans.sort(key=lambda p: (p.date, p.slug), reverse=True)
    retros = [
        Retro(slug, _doc(path, f"{home}/retrospectives/{slug}.html", slug))
        for slug, path in discover(vault, retro_globs)
    ]
    retros.sort(key=lambda r: (r.date, r.slug), reverse=True)
    return Work(vault=vault, plans=plans, retros=retros)
