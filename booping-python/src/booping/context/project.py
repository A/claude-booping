from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from booping.context._yaml import safe_load_path


class Project(BaseModel):
    name: str
    directory: Path
    repo_directory: Path
    # Watermark: everything at or below this id has been applied. -1 = nothing yet.
    latest_migration: int = -1

    @property
    def is_local_vault(self) -> bool:
        """True when the resolved vault lives under the repo (vs a ~/Claude vault)."""
        return self.directory.resolve().is_relative_to(self.repo_directory.resolve())

    @classmethod
    def load_cwd_configured(
        cls,
        start: Path | None = None,
        plugin_root: Path | None = None,
        global_path: Path | None = None,
    ) -> Project | None:
        """Resolve the project/vault the way Context.assemble does.

        Loads core + global config to read `home_dir` (the vault base) before
        delegating to `load_cwd`. Command call sites must use this rather than
        the bare `load_cwd()` so they honour the configured vault base; a bare
        `load_cwd()` silently resolves against the built-in `~/Claude` default.
        """
        # Local imports avoid a config/rendering ↔ project import cycle at module load.
        from booping.context import config as config_mod
        from booping.rendering import get_plugin_root

        root = plugin_root if plugin_root is not None else get_plugin_root()
        gpath = global_path if global_path is not None else config_mod.global_config_path()
        base_cfg = config_mod.load(root, [gpath])
        home_dir = str(base_cfg.get("home_dir", "~/Claude"))
        return cls.load_cwd(start=start, home_dir=home_dir)

    @classmethod
    def load_cwd(cls, start: Path | None = None, home_dir: str = "~/Claude") -> Project | None:
        """Walk up from start (default cwd) looking for .booping; return None on miss.

        home_dir is the raw (unexpanded) vault-home string from config; it is the
        default vault base when the marker carries no `vault_path:`. Precedence:
        `.booping` `vault_path:` > `home_dir` > built-in default.
        """
        candidate = (start or Path.cwd()).resolve()
        while True:
            marker = candidate / ".booping"
            if marker.is_file():
                data = safe_load_path(marker)
                project_name = str(data.get("project_name", candidate.name))
                return cls(
                    name=project_name,
                    directory=_resolve_vault_dir(
                        data.get("vault_path"), candidate, project_name, home_dir
                    ),
                    repo_directory=candidate,
                    latest_migration=_resolve_latest_migration(data, marker),
                )
            parent = candidate.parent
            if parent == candidate:
                return None
            candidate = parent


def _resolve_vault_dir(
    vault_path: object, candidate: Path, project_name: str, home_dir: str = "~/Claude"
) -> Path:
    """Resolve the vault directory.

    Precedence: marker `vault_path:` (absolute / ~ / relative-to-repo) > `home_dir`
    base (raw string from config, `~`-expanded here — the single normalization site)
    joined with the project name. This function owns all path normalization; the
    config dict keeps the raw `home_dir` value for display surfaces.
    """
    if not vault_path:
        return Path(home_dir).expanduser() / project_name
    path = Path(str(vault_path)).expanduser()
    if path.is_absolute():
        return path
    return (candidate / path).resolve()


def _resolve_latest_migration(data: dict[str, object], marker: Path) -> int:
    """Read `latest_migration` off the marker, defaulting to -1 (nothing applied).

    A forward-compatible subset read: only this key is looked at, so a marker whose
    schema a later migration changed still loads. A value that is not an integer is
    a user error naming the marker, raised at load time rather than mid-render.
    """
    raw = data.get("latest_migration")
    if raw is None:
        return -1
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ValueError(
            f"invalid latest_migration in {marker}: expected an integer, got {raw!r}"
        )
    return raw
