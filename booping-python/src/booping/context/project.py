from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel

from booping.context._yaml import safe_load_path


class Project(BaseModel):
    name: str
    directory: Path
    repo_directory: Path
    git_commit: str | None = None

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
                    repo_directory=candidate,
                    git_commit=_resolve_git_commit(candidate),
                )
            parent = candidate.parent
            if parent == candidate:
                return None
            candidate = parent


def _resolve_git_commit(repo_directory: Path) -> str | None:
    """Return current git HEAD as 40-char hex, or None when git is missing / repo invalid."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_directory,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha or None
