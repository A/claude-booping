from __future__ import annotations

from pathlib import Path
from typing import Literal, cast, get_args

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter

Layer = Literal["generic", "language", "framework"]
_VALID_LAYERS: tuple[str, ...] = get_args(Layer)

Source = Literal["core", "global", "project"]


class ReviewTemplate(BaseModel):
    name: str
    description: str
    # Core templates carry a plugin-root-relative path so a render is machine-independent;
    # a reader prefixes ${CLAUDE_PLUGIN_ROOT}. Global and project templates stay absolute.
    path: Path
    body: str
    source: Source
    layer: Layer

    @classmethod
    def _build(
        cls,
        path: Path,
        source: Source,
        display: Path | None = None,
    ) -> ReviewTemplate:
        fm, body = parse_frontmatter(path)
        name = str(fm.get("name", path.stem))
        description = str(fm.get("description", ""))
        layer_raw = fm.get("layer")
        if layer_raw not in _VALID_LAYERS:
            raise ValueError(
                f"{path}: invalid or missing 'layer' frontmatter (got {layer_raw!r}); "
                f"expected one of {_VALID_LAYERS}"
            )
        return cls(
            name=name,
            description=description,
            path=display if display is not None else path,
            body=body,
            source=source,
            layer=cast(Layer, layer_raw),
        )

    @classmethod
    def load_all(
        cls,
        plugin_root: Path,
        vault: Path | None,
        home_dir: Path | None = None,
    ) -> list[ReviewTemplate]:
        """Three tiers, least → most specific: core `docs/review_templates/`, global
        `{home_dir}/review_templates/`, project `{vault}/review_templates/`. A later
        tier's same-`name` template replaces the earlier one in place."""
        tiers: list[tuple[Source, Path]] = [
            ("core", plugin_root / "docs" / "review_templates")
        ]
        if home_dir is not None:
            tiers.append(("global", home_dir / "review_templates"))
        if vault is not None:
            tiers.append(("project", vault / "review_templates"))

        result: list[ReviewTemplate] = []
        by_name: dict[str, int] = {}
        for source, directory in tiers:
            if not directory.is_dir():
                continue
            for p in sorted(directory.glob("*.md")):
                display = p.relative_to(plugin_root) if source == "core" else None
                t = cls._build(p, source=source, display=display)
                if t.name in by_name:
                    result[by_name[t.name]] = t
                else:
                    by_name[t.name] = len(result)
                    result.append(t)

        return result
