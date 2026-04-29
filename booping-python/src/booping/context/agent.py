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


class Agent(BaseModel):
    name: str
    description: str = ""
    path: Path
    effort: str | None = None
    model: str | None = None
    allowed_tools: list[str] = []
    color: str | None = None

    @classmethod
    def load_all(cls, plugin_root: Path) -> dict[str, "Agent"]:
        agents_dir = plugin_root / "agents"
        if not agents_dir.is_dir():
            return {}
        agents: dict[str, Agent] = {}
        for md_file in sorted(agents_dir.glob("*.md")):
            text = md_file.read_text()
            fm = _parse_frontmatter_only(text)
            name = fm.get("name", md_file.stem)
            tools = fm.get("tools", "")
            if isinstance(tools, str):
                allowed_tools = [t.strip() for t in tools.split(",") if t.strip()]
            elif isinstance(tools, list):
                allowed_tools = tools
            else:
                allowed_tools = []
            agents[name] = cls(
                name=name,
                description=fm.get("description", ""),
                path=md_file,
                effort=fm.get("effort"),
                model=fm.get("model"),
                allowed_tools=allowed_tools,
                color=fm.get("color"),
            )
        return agents