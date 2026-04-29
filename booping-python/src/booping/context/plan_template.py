from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter


class PlanTemplate(BaseModel):
    name: str
    description: str
    path: Path
    body: str
    source: Literal["core", "project"]

    @classmethod
    def load_all(cls, plugin_root: Path, vault: Path) -> list[PlanTemplate]:
        core_dir = plugin_root / "docs" / "plan_templates"
        core_templates: list[PlanTemplate] = []
        core_by_name: dict[str, int] = {}

        if core_dir.is_dir():
            for p in sorted(core_dir.glob("*.md")):
                fm, body = parse_frontmatter(p)
                name = str(fm.get("name", p.stem))
                description = str(fm.get("description", ""))
                t = cls(name=name, description=description, path=p, body=body, source="core")
                core_by_name[name] = len(core_templates)
                core_templates.append(t)

        project_dir = vault / "plan_templates"
        if not project_dir.is_dir():
            return core_templates

        result = list(core_templates)
        for p in sorted(project_dir.glob("*.md")):
            fm, body = parse_frontmatter(p)
            name = str(fm.get("name", p.stem))
            description = str(fm.get("description", ""))
            t = cls(name=name, description=description, path=p, body=body, source="project")
            if name in core_by_name:
                result[core_by_name[name]] = t
            else:
                result.append(t)

        return result
