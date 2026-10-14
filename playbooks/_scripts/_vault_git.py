"""Shared vault-commit helper for the plugin-shipped hook scripts.

Not a hook: hooks resolve by exact name and nothing names this file. The hooks import
it by prepending this directory to `sys.path`. Standard library only, like the hooks.
"""

import subprocess
from pathlib import Path


def inside_git_worktree(vault: Path) -> bool:
    """The vault may be a subdirectory of a larger repository, so a `.git` at its root
    is not the test — ask git."""
    result = subprocess.run(
        ["git", "-C", str(vault), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def commit_paths(vault: Path, paths: list[str], message: str) -> str | None:
    """None when the vault is in no git work tree; otherwise "ok" or "nothing to commit".
    Stages `paths` (vault-relative), then commits only them."""
    if not inside_git_worktree(vault):
        return None
    subprocess.run(["git", "-C", str(vault), "add", "--", *paths], check=True)
    # `--only` keeps whatever else is staged in an enclosing repo out of the vault commit.
    result = subprocess.run(
        ["git", "-C", str(vault), "commit", "-q", "-m", message, "--only", "--", *paths],
        capture_output=True,
    )
    return "ok" if result.returncode == 0 else "nothing to commit"
