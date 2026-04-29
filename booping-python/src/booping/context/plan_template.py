from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end]
    body = text[end + 3 :]
    if body.startswith("\n"):
        body = body[1:]
    return yaml.safe_load(fm_text) or {}, body


class PlanTemplate(BaseModel):
    name: str
    description: str = ""
    path: Path
    body: str = ""
    source: Literal["core", "project"]

    @classmethod
    def load_all(cls, plugin_root: Path, vault: Path | None) -> list["PlanTemplate"]:
        templates: list[PlanTemplate] = []

        core_dir = plugin_root / "docs" / "plan_templates"
        if core_dir.is_dir():
            for md_file in sorted(core_dir.glob("*.md")):
                text = md_file.read_text()
                fm, body = _parse_frontmatter(text)
                templates.append(
                    cls(
                        name=fm.get("name", md_file.stem),
                        description=fm.get("description", ""),
                        path=md_file,
                        body=body,
                        source="core",
                    )
                )

        if vault is not None:
            project_dir = vault / "plan_templates"
            if project_dir.is_dir():
                for md_file in sorted(project_dir.glob("*.md")):
                    text = md_file.read_text()
                    fm, body = _parse_frontmatter(text)
                    templates.append(
                        cls(
                            name=fm.get("name", md_file.stem),
                            description=fm.get("description", ""),
                            path=md_file,
                            body=body,
                            source="project",
                        )
                    )

        seen: dict[str, int] = {}
        result: list[PlanTemplate] = []
        for tmpl in templates:
            if tmpl.name in seen:
                result[seen[tmpl.name]] = tmpl
            else:
                seen[tmpl.name] = len(result)
                result.append(tmpl)

        return result