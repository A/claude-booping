from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def log(vault: Path | None, subcommand: str, message: str) -> None:
    if vault is None:
        return
    vault.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts}: [{subcommand}] {message}\n" if message else f"{ts}: [{subcommand}]\n"
    with (vault / ".booping.log").open("a", encoding="utf-8") as f:
        f.write(line)
