from __future__ import annotations

from pathlib import Path

import yaml

from booping.context._yaml import parse_frontmatter_only
from booping.rendering import get_plugin_root

# The playbook that is the remedy; it never traverses its own gate.
MIGRATE_PLAYBOOK = "migrate"

_BEHIND = (
    "**STOP — tell the user:** this project is behind on booping migrations"
    " (recorded id {recorded}, latest shipped {latest}). Run `/playbook migrate`"
    " to bring the vault current, then retry."
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


def render_gate(
    playbook: str | None = None,
    start: Path | None = None,
    plugin_root: Path | None = None,
) -> str | None:
    """The notice a render surface must print *instead of* its output, or None.

    `playbook` is the requested playbook name — the single site the exemption is
    consulted, keyed on the name rather than a resolved `Playbook` so it holds even
    for a vault so far behind that context assembly would fail. No marker means no
    vault to bring current, so nothing is gated.
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
    return _BEHIND.format(recorded=recorded, latest=latest)
