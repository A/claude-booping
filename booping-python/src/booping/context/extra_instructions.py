from __future__ import annotations

from pathlib import Path


def load(vault: Path) -> dict[str, str]:
    booping_dir = vault / "_booping"
    if not booping_dir.is_dir():
        return {}
    result: dict[str, str] = {}
    for pattern in ("skill_*.md", "agent_*.md"):
        for p in sorted(booping_dir.glob(pattern)):
            result[p.stem] = p.read_text()
    return result
