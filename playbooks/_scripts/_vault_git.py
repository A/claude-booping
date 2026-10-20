"""Shared vault-commit helper for the plugin-shipped hook scripts.

Not a hook: hooks resolve by exact name and nothing names this file. The hooks import
it by prepending this directory to `sys.path`. Standard library only, like the hooks.
"""

import subprocess
import sys
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


def _git(vault: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(vault), *args], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"vault-commit: git {args[0]} failed: {result.stderr.strip()}")
    return result.stdout


def commit_paths(vault: Path, paths: list[str], message: str) -> str | None:
    """None when the vault is in no git work tree; otherwise "ok" or "nothing to commit".
    Stages `paths` (vault-relative), then commits only them. A failing git command exits
    non-zero with git's stderr, aborting the transition."""
    if not inside_git_worktree(vault):
        return None
    # A pathspec matching no tracked or addable file (an empty dir, one holding only
    # ignored files) makes both `git add` and `git commit --only` fail, so expand the
    # pathspecs to the concrete files first; `--cached` keeps deleted tracked files.
    files = _git(
        vault, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *paths
    ).split("\0")
    files = [f for f in files if f]
    if not files:
        return "nothing to commit"
    _git(vault, "add", "--", *files)
    staged = _git(vault, "diff", "--cached", "--name-only", "-z", "--relative", "--", *files)
    staged = [f for f in staged.split("\0") if f]
    if not staged:
        return "nothing to commit"
    # `--only` keeps whatever else is staged in an enclosing repo out of the vault commit.
    _git(vault, "commit", "-q", "-m", message, "--only", "--", *staged)
    return "ok"
