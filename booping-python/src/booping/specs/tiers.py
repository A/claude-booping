from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

TierName = Literal["core", "global", "project"]


class Tier(BaseModel):
    name: TierName
    # None for the project tier: no upper tier references a project record.
    namespace: str | None
    root: Path
    # Base a tier-relative path (`path`, a record's `sources`) resolves against.
    anchor: Path
    # The project tier rooted at the vault itself: only type directories hold records.
    vault_rooted: bool = False
    # Effective schema set: type stem → mdcheck rule file, shipped overlaid by `{root}/_schemas/`.
    schemas: dict[str, Path] = {}

    @property
    def types(self) -> list[str]:
        return sorted(self.schemas)

    def link(self, path: Path) -> str:
        """`path` as a rendered body shows it: core under `${CLAUDE_PLUGIN_ROOT}`, project
        relative to the repo, anything else absolute — so a pinned render stays reproducible."""
        absolute = _normalized(path)
        anchor = _normalized(self.anchor)
        if self.name != "global" and absolute.is_relative_to(anchor):
            relative = absolute.relative_to(anchor).as_posix()
            return f"${{CLAUDE_PLUGIN_ROOT}}/{relative}" if self.name == "core" else relative
        return absolute.as_posix()


def _normalized(path: Path) -> Path:
    return Path(os.path.normpath(path.absolute()))


def _tier_settings(config: dict[str, Any], name: str) -> dict[str, Any]:
    node: Any = config
    for key in ("core", "specs", "tiers", name):
        node = node.get(key) if isinstance(node, dict) else None  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    return node if isinstance(node, dict) else {}  # pyright: ignore[reportUnknownVariableType]


def _resolve_path(anchor: Path, path: str) -> Path:
    if path.startswith("~"):
        return Path(path).expanduser()
    candidate = Path(path)
    return candidate if candidate.is_absolute() else anchor / candidate


def project_root(path: str | None, repo: Path, vault: Path | None) -> Path:
    """Project tier root: an explicit `path` resolves against the repo; null means
    the vault root itself, wherever the vault lives, or `{repo}/specs` with no vault."""
    if path is not None:
        return _resolve_path(repo, path)
    if vault is not None:
        return vault
    return repo / "specs"


def resolve_tiers(
    config: dict[str, Any],
    *,
    plugin_root: Path,
    home_dir: Path,
    repo: Path | None,
    vault: Path | None,
    vault_override: bool = False,
) -> list[Tier]:
    """Tiers ordered core, global, project.

    `home_dir` is the core+global merge's value, as `Context.assemble()` resolves it.
    An explicit vault override drops the machine-local global tier so a pinned run
    stays reproducible; no attached repo drops the project tier.
    """
    tiers: list[Tier] = []
    specs = config.get("core", {}).get("specs", {})
    format_dir = plugin_root / str(specs.get("format"))

    core = _tier_settings(config, "core")
    tiers.append(
        Tier(
            name="core",
            namespace=core.get("namespace"),
            root=_resolve_path(plugin_root, str(core.get("path"))),
            anchor=plugin_root,
        )
    )

    if not vault_override:
        glob = _tier_settings(config, "global")
        namespace = glob.get("namespace")
        tiers.append(
            Tier(
                name="global",
                namespace=str(namespace) if namespace is not None else os.environ.get("USER"),
                root=_resolve_path(home_dir, str(glob.get("path"))),
                anchor=home_dir,
            )
        )

    if repo is not None:
        project = _tier_settings(config, "project")
        path = project.get("path")
        root = project_root(str(path) if path is not None else None, repo, vault)
        tiers.append(
            Tier(
                name="project",
                namespace=None,
                root=root,
                anchor=repo,
                vault_rooted=vault is not None and root.resolve() == vault.resolve(),
            )
        )

    return [t.model_copy(update={"schemas": schemas(format_dir, t.root)}) for t in tiers]


def schemas(format_dir: Path, root: Path) -> dict[str, Path]:
    """Type stem → schema path: `{format_dir}/schemas/*.yaml`, then `{root}/_schemas/*.yaml`
    replacing a same stem and adding new ones. No cascade between tiers."""
    found = {p.stem: p for p in sorted((format_dir / "schemas").glob("*.yaml"))}
    found.update(_own_schemas(root))
    return found


def _own_schemas(root: Path) -> dict[str, Path]:
    return {p.stem: p for p in sorted((root / "_schemas").glob("*.yaml"))}


def own_types(root: Path) -> list[str]:
    """The type stems `{root}/_schemas/` holds, sorted — the overlay without the shipped set."""
    return sorted(_own_schemas(root))


def types(format_dir: Path) -> list[str]:
    """Record type names: the stems of `{format_dir}/schemas/*.yaml`, sorted."""
    return sorted(p.stem for p in (format_dir / "schemas").glob("*.yaml"))
