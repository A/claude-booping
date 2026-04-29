from __future__ import annotations

from pathlib import Path

import yaml


def load_config(plugin_root: Path, override_paths: list[Path] | None = None) -> dict:
    """
    Load config with deep-merge of override paths.
    Missing keys fall through to core; present keys override; lists replace wholesale.
    """
    if override_paths is None:
        override_paths = []

    core = plugin_root / "src" / "config.yaml"
    config = {}
    if core.exists():
        config = yaml.safe_load(core.read_text()) or {}

    for path in override_paths:
        if path.exists():
            override_data = yaml.safe_load(path.read_text()) or {}
            config = _deep_merge(config, override_data)

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override onto base. Dicts recurse; lists/scalars replace."""
    result = dict(base)
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result