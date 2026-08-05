import os
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from booping.context._yaml import safe_load_path, safe_load_str
from booping.utils import deep_merge


def global_config_path() -> Path:
    """Path to the global config tier: ${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml.

    The XDG_CONFIG_HOME env var is read at call time (not import time) so tests can
    redirect it per-run.
    """
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "booping" / "config.yaml"


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    internal: bool = False
    good_for: list[str] = []
    bad_for: list[str] = []


class SkillConfig(BaseModel):
    # `extra=allow` because skill blocks carry other keys (e.g. `status`) not modelled here.
    model_config = ConfigDict(extra="allow")

    disable_internal_agents: bool = False
    agents: dict[str, AgentConfig] = {}


def validate_skills(cfg: dict[str, Any]) -> None:
    """Run each `skills.<name>` block through `SkillConfig.model_validate` for its
    side effects (raising on bad shape). Unknown agent fields are downgraded to a
    stderr warning rather than an error. Does not mutate cfg."""
    known_fields = set(AgentConfig.model_fields)
    skills = cfg.get("skills", {})
    if not isinstance(skills, dict):
        return
    for name, block in skills.items():  # type: ignore[misc]
        if not isinstance(block, dict):
            continue
        agents = block.get("agents", {})  # type: ignore[misc]
        if isinstance(agents, dict):
            for agent_id, entry in agents.items():  # type: ignore[misc]
                if not isinstance(entry, dict):
                    continue
                unknown = set(entry) - known_fields  # type: ignore[arg-type]
                if unknown:
                    keys = ", ".join(sorted(unknown))  # type: ignore[arg-type]
                    print(
                        f"warning: skills.{name}.agents.{agent_id} has unknown "
                        f"field(s): {keys}",
                        file=sys.stderr,
                    )
        try:
            SkillConfig.model_validate(block)
        except Exception as exc:
            raise ValueError(f"invalid config for skills.{name}: {exc}") from exc


# Keys a project-tier config may not contribute. A project tier can arrive with a
# `git clone` of a repo carrying a local vault, and macros execute during rendering
# inside an already-approved Bash allowance, with no second permission decision.
UNTRUSTED_PROJECT_KEYS = ("macros",)


def _merge(merged: dict[str, Any], path: Path) -> dict[str, Any]:
    override = safe_load_path(path)
    # `agents` is shallow-merged: each agent entry is atomic — an override
    # flipping one field must restate the rest of that entry.
    return deep_merge(merged, override, shallow_merge_keys=["agents"])


def load(
    plugin_root: Path,
    override_paths: list[Path],
    *,
    project_tier: Path | None = None,
) -> dict[str, Any]:
    core_path = plugin_root / "src" / "config.yaml"
    merged: dict[str, Any] = safe_load_str(core_path.read_text())
    for path in override_paths:
        if path.exists():
            merged = _merge(merged, path)
    if project_tier is not None and project_tier.exists():
        override = safe_load_path(project_tier)
        for key in UNTRUSTED_PROJECT_KEYS:
            if key in override:
                del override[key]
                print(
                    f"warning: ignoring project-tier `{key}` in {project_tier} —"
                    f" `{key}` is honoured in the core and global tiers only",
                    file=sys.stderr,
                )
        merged = deep_merge(merged, override, shallow_merge_keys=["agents"])
    return merged
