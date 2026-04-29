from __future__ import annotations

from pathlib import Path

import yaml


class Project:
    """Project loaded from .booping file in vault root."""

    def __init__(self, name: str, directory: Path):
        self.name = name
        self.directory = directory

    @classmethod
    def load_cwd(cls, vault: Path) -> Project | None:
        """Load project from vault's .booping file."""
        booping_file = vault / ".booping"
        if not booping_file.exists():
            return None
        data = yaml.safe_load(booping_file.read_text()) or {}
        project_name = data.get("project_name", "")
        return cls(
            name=project_name,
            directory=Path.home() / "Claude" / project_name,
        )