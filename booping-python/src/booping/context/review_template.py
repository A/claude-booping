from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, get_args

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter

Layer = Literal["generic", "language", "framework"]
_VALID_LAYERS: tuple[str, ...] = get_args(Layer)


class ReviewTemplate(BaseModel):
    name: str
    description: str
    path: Path
    body: str
    source: Literal["core", "project"]
    layer: Layer
    applies_to: list[str] = []

    @classmethod
    def _build(cls, path: Path, source: Literal["core", "project"]) -> ReviewTemplate:
        fm, body = parse_frontmatter(path)
        name = str(fm.get("name", path.stem))
        description = str(fm.get("description", ""))
        layer_raw = fm.get("layer")
        if layer_raw not in _VALID_LAYERS:
            raise ValueError(
                f"{path}: invalid or missing 'layer' frontmatter (got {layer_raw!r}); "
                f"expected one of {_VALID_LAYERS}"
            )
        applies_to_raw: Any = fm.get("applies_to", [])
        if applies_to_raw is None:
            applies_to: list[str] = []
        elif isinstance(applies_to_raw, list):
            applies_to = [str(x) for x in applies_to_raw]  # type: ignore[reportUnknownVariableType]
        else:
            raise ValueError(f"{path}: 'applies_to' must be a list when present")
        return cls(
            name=name,
            description=description,
            path=path,
            body=body,
            source=source,
            layer=layer_raw,
            applies_to=applies_to,
        )

    @classmethod
    def load_all(cls, plugin_root: Path, vault: Path) -> list[ReviewTemplate]:
        core_dir = plugin_root / "docs" / "review_templates"
        core_templates: list[ReviewTemplate] = []
        core_by_name: dict[str, int] = {}

        if core_dir.is_dir():
            for p in sorted(core_dir.glob("*.md")):
                t = cls._build(p, source="core")
                core_by_name[t.name] = len(core_templates)
                core_templates.append(t)

        project_dir = vault / "review_templates"
        if not project_dir.is_dir():
            return core_templates

        result = list(core_templates)
        for p in sorted(project_dir.glob("*.md")):
            t = cls._build(p, source="project")
            if t.name in core_by_name:
                result[core_by_name[t.name]] = t
            else:
                result.append(t)

        return result
