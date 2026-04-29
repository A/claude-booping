from __future__ import annotations

from pathlib import Path


def load_extra_instructions(vault: Path | None) -> dict[str, str]:
    """
    Eager-load <vault>/_booping/skill_*.md and <vault>/_booping/agent_*.md
    into a dict keyed by filename stem (e.g. 'skill_groom', 'agent_booping-developer').
    """
    result = {}
    if not vault or not (vault / "_booping").exists():
        return result
    for pattern, key_prefix in [("skill_*.md", "skill_"), ("agent_*.md", "agent_")]:
        for f in (vault / "_booping").glob(pattern):
            key = key_prefix + f.stem
            result[key] = f.read_text()
    return result