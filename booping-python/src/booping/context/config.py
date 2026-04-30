from __future__ import annotations

from pathlib import Path
from typing import Any

from booping.context._yaml import safe_load_path, safe_load_str


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
