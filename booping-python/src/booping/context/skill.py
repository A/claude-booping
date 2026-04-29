from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter_only


def _str_list(val: Any) -> list[str]:
    # val comes from dict[str, Any]; iteration yields Any/Unknown in strict mode
    if not isinstance(val, list):
        return []
    return [str(item) for item in val]  # type: ignore[reportUnknownVariableType, reportUnknownArgumentType]


class Skill(BaseModel):
    name: str
    description: str
    path: Path
    effort: str | None = None
    model: str | None = None
    allowed_tools: list[str] = []
    user_invocable: bool = False
    debug_enabled: bool = False

    @classmethod
    def load_all(cls, plugin_root: Path) -> dict[str, Skill]:
        skills_dir = plugin_root / "skills"
        if not skills_dir.is_dir():
            return {}
        result: dict[str, Skill] = {}
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue
            fm = parse_frontmatter_only(skill_md)
            name = str(fm.get("name", skill_dir.name))
            effort_val = fm.get("effort")
            model_val = fm.get("model")
            result[name] = cls(
                name=name,
                description=str(fm.get("description", "")),
                path=skill_md,
                effort=str(effort_val) if effort_val is not None else None,
                model=str(model_val) if model_val is not None else None,
                allowed_tools=_str_list(fm.get("allowed-tools")),
                user_invocable=bool(fm.get("user-invocable", False)),
                debug_enabled=(skill_dir / ".debug_enabled").exists(),
            )
        return result
