from pathlib import Path
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator

from booping.context._yaml import safe_load_path, safe_load_str


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["agent", "cli"] = "agent"
    command: str | None = None
    internal: bool = False
    good_for: list[str] = []
    bad_for: list[str] = []

    @model_validator(mode="after")
    def _command_required_for_cli(self) -> Self:
        if self.type == "cli" and not self.command:
            raise ValueError("agent entry with `type: cli` requires non-empty `command`")
        return self


class SkillConfig(BaseModel):
    # `extra=allow` because skill blocks carry other keys (e.g. `status`) not modelled here.
    model_config = ConfigDict(extra="allow")

    disable_internal_agents: bool = False
    agents: dict[str, AgentConfig] = {}


def validate_skills(cfg: dict[str, Any]) -> None:
    """Run each `skills.<name>` block through `SkillConfig.model_validate` for its
    side effects (raising on bad shape). Does not mutate cfg."""
    skills = cfg.get("skills", {})
    if not isinstance(skills, dict):
        return
    for name, block in skills.items():  # type: ignore[misc]
        if not isinstance(block, dict):
            continue
        try:
            SkillConfig.model_validate(block)
        except Exception as exc:
            raise ValueError(f"invalid config for skills.{name}: {exc}") from exc


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = dict(base)
    for key, val in override.items():
        base_val: Any = result.get(key)
        if isinstance(base_val, dict) and isinstance(val, dict):
            # Both are dicts — recurse. Use type: ignore because isinstance narrowing
            # produces dict[Unknown, Unknown] in basedpyright strict mode for Any values.
            result[key] = _deep_merge(base_val, val)  # type: ignore[arg-type]
        else:
            result[key] = val
    return result


def load(plugin_root: Path, override_paths: list[Path]) -> dict[str, Any]:
    core_path = plugin_root / "src" / "config.yaml"
    merged: dict[str, Any] = safe_load_str(core_path.read_text())
    for path in override_paths:
        if path.exists():
            override = safe_load_path(path)
            merged = _deep_merge(merged, override)
    return merged
