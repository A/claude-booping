from __future__ import annotations

import subprocess
from pathlib import Path


def test_render_resolves_relative_path_against_plugin_root_not_cwd(
    tmp_path: Path,
) -> None:
    """Skill-load shells invoke `booping render src/templates/...` with cwd anywhere
    (typically the user's project repo or vault). The relative path must resolve
    against the plugin root, never the caller's cwd.
    """
    plugin_root = Path(__file__).resolve().parents[3]
    booping_bin = plugin_root / "bin" / "booping"

    result = subprocess.run(
        [str(booping_bin), "render", "src/templates/skills/chat.md.j2"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "# booping — /chat" in result.stdout
