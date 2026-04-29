from pathlib import Path
from typing import Any

import yaml


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    @staticmethod
    def load(
        plugin_root: Path,
        override_paths: list[Path] | None = None,
    ) -> dict[str, Any]:
        config_path = plugin_root / "src" / "config.yaml"
        config: dict[str, Any] = {}
        if config_path.exists():
            config = yaml.safe_load(config_path.read_text()) or {}

        if override_paths is None:
            override_paths = []

        for path in override_paths:
            if path.exists():
                override = yaml.safe_load(path.read_text()) or {}
                config = _deep_merge(config, override)

        return config