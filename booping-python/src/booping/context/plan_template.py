from __future__ import annotations

from pathlib import Path

import yaml


class PlanTemplate:
    """Plan template loaded from plugin_root/docs/plan_templates/ or vault/plan_templates/."""

    def __init__(
        self,
        name: str,
        description: str,
        path: Path,
        body: str,
        source: str,  # "core" or "project"
    ):
        self.name = name
        self.description = description
        self.path = path
        self.body = body
        self.source = source

    @classmethod
    def load_all(cls, plugin_root: Path, vault: Path | None) -> list[PlanTemplate]:
        templates = []
        seen_names: set[str] = set()

        # Core templates
        core_dir = plugin_root / "docs" / "plan_templates"
        if core_dir.exists():
            for md_file in sorted(core_dir.glob("*.md")):
                front, body = _read_frontmatter(md_file)
                name = front.get("name", md_file.stem)
                templates.append(cls(
                    name=name,
                    description=front.get("description", ""),
                    path=md_file,
                    body=body,
                    source="core",
                ))
                seen_names.add(name)

        # Project templates (override core with same name)
        if vault:
            pt_dir = vault / "plan_templates"
            if pt_dir.exists():
                for md_file in sorted(pt_dir.glob("*.md")):
                    front, body = _read_frontmatter(md_file)
                    name = front.get("name", md_file.stem)
                    # Remove core entry with same name
                    templates = [t for t in templates if t.name != name]
                    templates.append(cls(
                        name=name,
                        description=front.get("description", ""),
                        path=md_file,
                        body=body,
                        source="project",
                    ))
                    seen_names.add(name)

        return templates


def _read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    if text.startswith("---"):
        end = text.find("\n---", 4)
        if end != -1:
            front = yaml.safe_load(text[4:end]) or {}
            body = text[end + 4:].lstrip("\n")
            return front, body
    return {}, text