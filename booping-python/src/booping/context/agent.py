from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter_only


def _str_list(val: Any) -> list[str]:
    # Agent frontmatter accepts `tools` as either a YAML list or a comma-separated string.
    if isinstance(val, list):
        return [str(item) for item in val]  # type: ignore[reportUnknownVariableType, reportUnknownArgumentType]
    if isinstance(val, str):
        return [item.strip() for item in val.split(",") if item.strip()]
    return []


class Agent(BaseModel):
    name: str
    description: str
    path: Path
    effort: str | None = None
    model: str | None = None
    allowed_tools: list[str] = []
    color: str | None = None
    debug_enabled: bool = False

    @classmethod
    def load_all(cls, plugin_root: Path) -> dict[str, Agent]:
        agents_dir = plugin_root / "agents"
        if not agents_dir.is_dir():
            return {}
        result: dict[str, Agent] = {}
        for p in sorted(agents_dir.glob("*.md")):
            fm = parse_frontmatter_only(p)
            name = str(fm.get("name", p.stem))
            effort_val = fm.get("effort")
            model_val = fm.get("model")
            color_val = fm.get("color")
            result[name] = cls(
                name=name,
                description=str(fm.get("description", "")),
                path=p,
                effort=str(effort_val) if effort_val is not None else None,
                model=str(model_val) if model_val is not None else None,
                allowed_tools=_str_list(fm.get("tools") or fm.get("allowed-tools")),
                color=str(color_val) if color_val is not None else None,
                debug_enabled=bool(fm.get("debug-enabled", False)),
            )
        return result
