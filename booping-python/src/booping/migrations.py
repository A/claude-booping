from __future__ import annotations

from pathlib import Path

import yaml

from booping.context import config as config_mod
from booping.context._yaml import parse_frontmatter_only
from booping.context.project import Project
from booping.rendering import get_plugin_root

# The playbook that is the remedy; it never traverses its own gate.
MIGRATE_PLAYBOOK = "migrate"

_BEHIND = (
    "**STOP — tell the user:** this project is behind on booping migrations"
    " (recorded id {recorded}, latest shipped {latest}). Run `/playbook migrate`"
    " to bring the vault current, then retry."
)

_AUTO = (
    "**Auto-migrate:** this project is behind on booping migrations"
    " (recorded id {recorded}, latest shipped {latest}). Run `/playbook migrate` now"
    " without asking the user — `core.auto_migrate` is on, so its approval is taken as"
    " given — then continue with the original request."
)


def find_marker(start: Path | None = None) -> Path | None:
    """Walk up from `start` (default cwd) to the nearest `.booping`, or None."""
    candidate = (start or Path.cwd()).resolve()
    while True:
        marker = candidate / ".booping"
        if marker.is_file():
            return marker
        parent = candidate.parent
        if parent == candidate:
            return None
        candidate = parent


def recorded_id(marker: Path) -> int:
    """The marker's `latest_migration`, `-1` when it cannot be read as an integer.

    A forward-compatible subset read, deliberately independent of
    `Project.latest_migration`: that one is strict and raises on a non-integer, which
    is precisely the vault most in need of being told to migrate. Anything unreadable
    here counts as behind, so a corrupt marker yields the remedy, never a stack trace.
    """
    try:
        data = yaml.safe_load(marker.read_text())
    except Exception:
        return -1
    if not isinstance(data, dict):
        return -1
    raw = data.get("latest_migration")  # type: ignore[reportUnknownMemberType]
    if isinstance(raw, bool) or not isinstance(raw, int):
        return -1
    return raw


def latest_shipped_id(plugin_root: Path | None = None) -> int:
    """The highest `id` across the migrations the plugin ships, `-1` when none.

    Read from `migration.md` frontmatter; the `NNN_` directory prefix is a sort hint
    with no authority.
    """
    root = plugin_root if plugin_root is not None else get_plugin_root()
    ids: list[int] = []
    for path in sorted(root.glob("migrations/*/migration.md")):
        try:
            frontmatter = parse_frontmatter_only(path)
        except Exception:
            continue
        raw = frontmatter.get("id")
        if isinstance(raw, bool) or not isinstance(raw, int):
            continue
        ids.append(raw)
    return max(ids, default=-1)


def auto_migrate(
    start: Path | None = None,
    plugin_root: Path | None = None,
    vault_override: Path | None = None,
) -> bool:
    """The merged `core.auto_migrate`, `True` when no tier sets it.

    Tiers resolve the way `Context.assemble` does — a pinned vault drops the global
    tier. Config that cannot be read yields `False`: a vault that broken gets the
    STOP notice for the user rather than an unattended migration.
    """
    try:
        root = plugin_root if plugin_root is not None else get_plugin_root()
        if vault_override is not None:
            tiers = [vault_override / "config.yaml"]
        else:
            tiers = [config_mod.global_config_path()]
            project = Project.load_cwd_configured(start=start, plugin_root=root)
            if project is not None:
                tiers.append(project.directory / "config.yaml")
        cfg = config_mod.load(root, tiers)
    except Exception:
        return False
    core = cfg.get("core")
    if not isinstance(core, dict):
        return True
    return core.get("auto_migrate", True) is True  # type: ignore[reportUnknownMemberType]


def render_gate(
    playbook: str | None = None,
    start: Path | None = None,
    plugin_root: Path | None = None,
    vault_override: Path | None = None,
) -> str | None:
    """The notice a render surface must print *instead of* its output, or None.

    `playbook` is the requested playbook name — the single site the exemption is
    consulted, keyed on the name rather than a resolved `Playbook` so it holds even
    for a vault so far behind that context assembly would fail. No marker means no
    vault to bring current, so nothing is gated. With `core.auto_migrate` on the
    notice orders the driving agent to migrate and resume; off, it stops for the user.
    """
    if playbook == MIGRATE_PLAYBOOK:
        return None
    latest = latest_shipped_id(plugin_root)
    if latest < 0:
        return None
    marker = find_marker(start)
    if marker is None:
        return None
    recorded = recorded_id(marker)
    if recorded >= latest:
        return None
    template = _AUTO if auto_migrate(start, plugin_root, vault_override) else _BEHIND
    return template.format(recorded=recorded, latest=latest)
