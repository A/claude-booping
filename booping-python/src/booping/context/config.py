import os
from pathlib import Path
from typing import Any

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


def _merge(merged: dict[str, Any], path: Path) -> dict[str, Any]:
    override = safe_load_path(path)
    # `agents` is shallow-merged: each agent entry is atomic — an override
    # flipping one field must restate the rest of that entry.
    return deep_merge(merged, override, shallow_merge_keys=["agents"])


def load(plugin_root: Path, override_paths: list[Path]) -> dict[str, Any]:
    core_path = plugin_root / "src" / "config.yaml"
    merged: dict[str, Any] = safe_load_str(core_path.read_text())
    for path in override_paths:
        if path.exists():
            merged = _merge(merged, path)
    return merged
