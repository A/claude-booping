"""Resolution of `core.tracker`.

The three-tier config merge stays single-sourced in booping: this shells to
`bin/booping config-get core.tracker` and parses the YAML it prints, unless
`--config-file` names a file to read instead.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

KNOWN_DRIVERS = ("cli", "linear")
BOOPING = Path(__file__).resolve().parents[3] / "bin" / "booping"


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class TrackerConfig:
    driver: str
    settings: dict[str, Any]

    def driver_settings(self) -> dict[str, Any]:
        block: Any = self.settings.get(self.driver)
        return cast("dict[str, Any]", block) if isinstance(block, dict) else {}


def config_get(key: str, cwd: Path | None = None) -> str | None:
    """Print of `booping config-get {key}`, or None when the key does not resolve."""
    try:
        proc = subprocess.run(
            [str(BOOPING), "config-get", key],
            capture_output=True,
            text=True,
            cwd=cwd,
        )
    except OSError as exc:
        raise ConfigError(f"could not run {BOOPING}: {exc}") from exc
    if proc.returncode != 0:
        return None
    return proc.stdout


def load(
    *,
    config_file: Path | None = None,
    driver_override: str | None = None,
    cwd: Path | None = None,
) -> TrackerConfig:
    if config_file is not None:
        raw = _read_config_file(config_file)
    else:
        raw = config_get("core.tracker", cwd)
    if raw is None:
        raise ConfigError("no core.tracker block in the resolved config")

    try:
        parsed: Any = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigError(f"could not parse tracker config: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ConfigError("tracker config is not a mapping")
    settings = cast("dict[str, Any]", parsed)

    driver = driver_override if driver_override is not None else settings.get("driver")
    if not isinstance(driver, str) or not driver:
        raise ConfigError("no tracker driver configured (core.tracker.driver)")
    if driver not in KNOWN_DRIVERS:
        raise ConfigError(f"unknown driver: {driver} (known: {', '.join(KNOWN_DRIVERS)})")

    config = TrackerConfig(driver=driver, settings=settings)
    _check_api_key(config)
    return config


def _read_config_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"could not read config file {path}: {exc}") from exc


def _check_api_key(config: TrackerConfig) -> None:
    if config.driver == "cli":
        return
    var = config.driver_settings().get("api_key_env")
    if not isinstance(var, str) or not var:
        raise ConfigError(f"no api_key_env configured for driver {config.driver}")
    if not os.environ.get(var):
        raise ConfigError(f"{var} is unset; the {config.driver} driver needs an API key")
