"""One `[tracker {verb}]` line per invocation in the attached vault's log."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from booping_tracker.config import config_get

DEFAULT_HOME_DIR = "~/Claude"


def resolve_vault(start: Path | None = None) -> Path | None:
    """Vault the cwd is attached to, or None when no `.booping` marker is above it."""
    origin = (start or Path.cwd()).resolve()
    for candidate in (origin, *origin.parents):
        marker = candidate / ".booping"
        if marker.is_file():
            return _vault_of(marker, candidate)
    return None


def log(vault: Path | None, verb: str, message: str) -> None:
    if vault is None:
        return
    vault.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    with (vault / ".booping.log").open("a", encoding="utf-8") as f:
        f.write(f"{ts}: [tracker {verb}] {message}\n")


def _vault_of(marker: Path, repo: Path) -> Path | None:
    try:
        loaded: Any = yaml.safe_load(marker.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    data: dict[str, Any] = cast("dict[str, Any]", loaded) if isinstance(loaded, dict) else {}

    vault_path = data.get("vault_path")
    if vault_path:
        path = Path(str(vault_path)).expanduser()
        return path if path.is_absolute() else (repo / path).resolve()

    # Only the home-dir fallback needs booping: a marker naming its own vault_path
    # resolves without shelling out, which is what keeps --config-file runs offline.
    home_dir = config_get("home_dir", repo)
    base = (home_dir or DEFAULT_HOME_DIR).strip() or DEFAULT_HOME_DIR
    return Path(base).expanduser() / str(data.get("project_name", repo.name))
