from pathlib import Path

import yaml
from pydantic import BaseModel


class Project(BaseModel):
    name: str
    directory: Path

    @classmethod
    def load_cwd(cls) -> "Project | None":
        current = Path.cwd()
        while True:
            booping_file = current / ".booping"
            if booping_file.is_file():
                data = yaml.safe_load(booping_file.read_text())
                project_name = data.get("project_name")
                if project_name is None:
                    return None
                return cls(
                    name=project_name,
                    directory=Path.home() / "Claude" / project_name,
                )
            parent = current.parent
            if parent == current:
                return None
            current = parent