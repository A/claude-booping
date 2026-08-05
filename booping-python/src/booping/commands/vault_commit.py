from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from booping import logger
from booping.context.project import Project
from booping.utils import DIR_PLAN_NAMES


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "vault-commit",
        help="Stage and commit plan + sprints.md in the vault",
    )
    p.add_argument(
        "to_status",
        metavar="to-status",
        help="Target status string (used in commit message)",
    )
    p.add_argument("plan_path", type=Path, help="Path to the plan markdown file")
    p.add_argument(
        "--also",
        dest="also",
        nargs="*",
        type=Path,
        default=[],
        metavar="PATH",
        help="Additional paths to stage",
    )
    p.set_defaults(func=_run)


def resolve_vault(plan_path: Path) -> Path:
    """Determine vault directory: from Project if available, else from plan path."""
    project = Project.load_cwd_configured()
    if project is not None:
        return project.directory
    # Heuristic: plans live at <vault>/plans/<name>.md or <vault>/plans/<slug>/{index,plan}.md
    parent = plan_path.resolve().parent
    if parent.name == "plans":
        return parent.parent
    if parent.parent.name == "plans":
        return parent.parent.parent
    # Final fallback: plan file's parent
    return parent


def plan_slug(plan_path: Path) -> str:
    if plan_path.name in DIR_PLAN_NAMES:
        return plan_path.resolve().parent.name
    return plan_path.stem


def _git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def _rel(vault: Path, path: Path) -> str:
    """Return path relative to vault, for git add."""
    try:
        return str(path.resolve().relative_to(vault.resolve()))
    except ValueError:
        # path is not under vault; use absolute path (will fail gracefully)
        return str(path)


def do_vault_commit(
    to_status: str,
    plan_path: Path,
    also: list[Path] | None = None,
    vault: Path | None = None,
) -> str | None:
    """Core vault-commit logic; callable from transition dispatcher.

    Args:
        to_status: target status string (used in commit message).
        plan_path: path to the plan markdown file.
        also: additional paths to stage.
        vault: vault directory override (for testing / transition inline use).

    Returns:
        The short sha of the commit, or ``None`` when there was nothing to commit.
    """
    also = also or []

    if not plan_path.is_file():
        print(f"error: plan not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    if vault is None:
        vault = resolve_vault(plan_path)
    sprints_path = vault / "sprints.md"

    # Build the list of paths to stage (explicit, never git add -A or .)
    # Use paths relative to vault for git add
    rel_paths: list[str] = []
    rel_paths.append(_rel(vault, plan_path))
    if sprints_path.exists():
        rel_paths.append(_rel(vault, sprints_path))
    for extra in also:
        if extra.exists():
            rel_paths.append(_rel(vault, extra))

    # Stage
    add_result = _git(vault, ["add"] + rel_paths)
    if add_result.returncode != 0:
        print(
            f"error: git add failed: {add_result.stderr.strip()}", file=sys.stderr
        )
        sys.exit(2)

    # Check if there is anything to commit (scoped to the plan paths only)
    status_result = _git(vault, ["status", "--porcelain", "--", *rel_paths])
    if status_result.returncode != 0:
        print(
            f"error: git status failed: {status_result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(2)

    if not status_result.stdout.strip():
        # Nothing staged — already committed
        print(f"nothing to commit for {plan_path}", file=sys.stderr)
        return None

    # Build commit message
    commit_msg = f"{to_status}: {plan_slug(plan_path)}"

    commit_result = _git(vault, ["commit", "-m", commit_msg, "--", *rel_paths])
    if commit_result.returncode != 0:
        print(
            f"error: git commit failed: {commit_result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(2)

    log_vault = vault if vault.exists() else None
    logger.log(
        vault=log_vault,
        subcommand="vault-commit",
        message=f"{plan_path} {to_status}",
    )

    sha_result = _git(vault, ["rev-parse", "--short", "HEAD"])
    if sha_result.returncode != 0:
        print(
            f"error: git rev-parse failed: {sha_result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(2)

    return sha_result.stdout.strip()


def _run(args: argparse.Namespace) -> None:
    plan_path: Path = args.plan_path
    to_status: str = args.to_status
    also: list[Path] = args.also

    sha = do_vault_commit(to_status=to_status, plan_path=plan_path, also=also)
    if sha is not None:
        print(f"{to_status}: {plan_slug(plan_path)}")