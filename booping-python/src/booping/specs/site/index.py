from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from booping.specs.site.pages import Crumb, environment

_HERE = Path(__file__).parent
_KEYS = ("name", "url", "description")


class ProjectsError(Exception):
    pass


@dataclass(frozen=True)
class Project:
    name: str
    url: str
    description: str


def _project(i: int, entry: Any) -> Project:
    where = f"projects[{i}]"
    if not isinstance(entry, dict):
        raise ProjectsError(f"{where}: not a mapping")
    fields = cast(dict[Any, Any], entry)
    unknown = sorted(str(key) for key in fields if key not in _KEYS)
    if unknown:
        raise ProjectsError(f"{where}: unknown key `{unknown[0]}`")
    name = fields.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ProjectsError(f"{where}: `name` must be a non-empty string")
    url = fields.get("url")
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        raise ProjectsError(f"{where}: `url` must be an http:// or https:// URL")
    description = fields.get("description")
    if description is not None and not isinstance(description, str):
        raise ProjectsError(f"{where}: `description` must be a string or null")
    return Project(name=name, url=url, description=" ".join((description or "").split()))


def load_projects(data: Any) -> list[Project]:
    """Validate an already-parsed project list; the first problem raises, its entry
    named by 0-based input index."""
    if not isinstance(data, list):
        raise ProjectsError("projects: not a list")
    projects: list[Project] = []
    seen: dict[str, int] = {}
    for i, entry in enumerate(cast(list[Any], data)):
        project = _project(i, entry)
        first = seen.get(project.name)
        if first is not None:
            raise ProjectsError(
                f"projects[{i}]: duplicate name `{project.name}` (also projects[{first}])"
            )
        seen[project.name] = i
        projects.append(project)
    return projects


def build_index(projects: list[Project], title: str) -> dict[str, str]:
    """Out-root-relative path → file content of the group index page."""
    ordered = sorted(projects, key=lambda p: (p.name.casefold(), p.name))
    html = (
        environment()
        .get_template("site_index.html.j2")
        .render(title=title, prefix="", crumbs=[Crumb(title, None)], projects=ordered)
    )
    return {"index.html": html, "style.css": (_HERE / "style.css").read_text()}
