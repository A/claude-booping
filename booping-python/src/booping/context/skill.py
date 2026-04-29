from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


def _parse_frontmatter_only(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm_text = text[3:end]
    return yaml.safe_load(fm_text) or {}


class Skill(BaseModel):
    name: str
    description: str = ""
    path: Path
    effort: str | None = None
    model: str | None = None
    allowed_tools: list[str] = []
    user_invocable: bool = True
    debug_enabled: bool = False

    @classmethod
    def load_all(cls, plugin_root: Path) -> dict[str, "Skill"]:
        skills_dir = plugin_root / "skills"
        if not skills_dir.is_dir():
            return {}
        skills: dict[str, Skill] = {}
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue
            text = skill_md.read_text()
            fm = _parse_frontmatter_only(text)
            name = fm.get("name", skill_dir.name)
            debug_enabled = (skill_dir / ".debug_enabled").exists()
            allowed_tools = fm.get("allowed-tools", [])
            if isinstance(allowed_tools, str):
                allowed_tools = [allowed_tools]
            skills[name] = cls(
                name=name,
                description=fm.get("description", ""),
                path=skill_md,
                effort=fm.get("effort"),
                model=fm.get("model"),
                allowed_tools=allowed_tools,
                user_invocable=fm.get("user-invocable", True),
                debug_enabled=debug_enabled,
            )
        return skills