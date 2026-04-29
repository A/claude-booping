from __future__ import annotations

from pathlib import Path

import yaml


class Skill:
    """Skill metadata loaded from <plugin_root>/skills/<name>/SKILL.md."""

    def __init__(
        self,
        name: str,
        description: str,
        path: Path,
        effort: str | None = None,
        user_invocable: bool | None = None,
        allowed_tools: list[str] | None = None,
        debug_enabled: bool = False,
    ):
        self.name = name
        self.description = description
        self.path = path
        self.effort = effort
        self.user_invocable = user_invocable
        self.allowed_tools = allowed_tools or []
        self.debug_enabled = debug_enabled

    @classmethod
    def load_all(cls, plugin_root: Path) -> dict[str, Skill]:
        skills = {}
        skills_dir = plugin_root / "skills"
        if not skills_dir.exists():
            return skills
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            sk_file = skill_dir / "SKILL.md"
            if not sk_file.exists():
                continue
            front, _ = _read_frontmatter(sk_file)
            name = front.get("name", skill_dir.name)
            skills[name] = cls(
                name=name,
                description=front.get("description", ""),
                path=sk_file,
                effort=front.get("effort"),
                user_invocable=front.get("user-invocable"),
                allowed_tools=front.get("allowed-tools", []),
                debug_enabled=(skill_dir / ".debug_enabled").exists(),
            )
        return skills


class Agent:
    """Agent metadata loaded from <plugin_root>/agents/*.md."""

    def __init__(
        self,
        name: str,
        description: str,
        path: Path,
        model: str | None = None,
        allowed_tools: list[str] | None = None,
        color: str | None = None,
    ):
        self.name = name
        self.description = description
        self.path = path
        self.model = model
        self.allowed_tools = allowed_tools or []
        self.color = color

    @classmethod
    def load_all(cls, plugin_root: Path) -> dict[str, Agent]:
        agents = {}
        agents_dir = plugin_root / "agents"
        if not agents_dir.exists():
            return agents
        for md_file in sorted(agents_dir.glob("*.md")):
            front, _ = _read_frontmatter(md_file)
            name = front.get("name", md_file.stem)
            agents[name] = cls(
                name=name,
                description=front.get("description", ""),
                path=md_file,
                model=front.get("model"),
                allowed_tools=front.get("allowed-tools", []),
                color=front.get("color"),
            )
        return agents


def _read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    if text.startswith("---"):
        end = text.find("\n---", 4)
        if end != -1:
            front = yaml.safe_load(text[4:end]) or {}
            body = text[end + 4:].lstrip("\n")
            return front, body
    return {}, text