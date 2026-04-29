from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from booping.context._yaml import safe_load_path


class Project(BaseModel):
    name: str
    directory: Path

    @classmethod
    def load_cwd(cls, start: Path | None = None) -> Project | None:
        """Walk up from start (default cwd) looking for .booping; return None on miss."""
        candidate = (start or Path.cwd()).resolve()
        while True:
            marker = candidate / ".booping"
            if marker.is_file():
                data = safe_load_path(marker)
                project_name = str(data.get("project_name", candidate.name))
                return cls(
                    name=project_name,
                    directory=Path.home() / "Claude" / project_name,
                )
            parent = candidate.parent
            if parent == candidate:
                return None
            candidate = parent
