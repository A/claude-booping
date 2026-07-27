from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from booping import logger
from booping.commands.vault_commit import do_vault_commit
from booping.context import Context
from booping.context._yaml import parse_frontmatter_only, update_frontmatter
from booping.context.lifecycle import resolve_edges, resolve_hooks
from booping.context.project import Project
from booping.rendering import get_plugin_root, render


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "transition",
        help="Transition a plan to a new status, running all resolved hooks",
    )
    p.add_argument(
        "to_status", metavar="to", help="Target status to transition to"
    )
    p.add_argument("plan", type=Path, help="Path to the plan markdown file")
    p.add_argument(
        "--also",
        dest="also",
        action="append",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Vault artifact authored for this move (e.g. a retrospective "
            "file or sibling stub plan) to stage + commit alongside the "
            "plan in the same transition commit. Repeatable."
        ),
    )
    p.set_defaults(func=_run)


def _interpolate(value: str, repo_dir: Path | None) -> str:
    if value == "@now":
        return datetime.now(UTC).strftime("%Y%m%d %H:%M")
    if value == "@today":
        return datetime.now(UTC).strftime("%Y-%m-%d")
    if value == "@head":
        cwd = repo_dir if repo_dir is not None else Path.cwd()
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(
                f"error: git rev-parse HEAD failed: {result.stderr.strip()}",
                file=sys.stderr,
            )
            sys.exit(2)
        return result.stdout.strip()
    return value


def _parse_pairs(pairs: list[str]) -> dict[str, str]:
    updates: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            print(
                f"error: malformed key=value pair: {pair!r}", file=sys.stderr
            )
            sys.exit(1)
        key, _, value = pair.partition("=")
        if not key:
            print(f"error: empty key in pair: {pair!r}", file=sys.stderr)
            sys.exit(1)
        updates[key] = value
    return updates


def _dispatch_frontmatter_update(
    hook: str, plan_path: Path, project: Project | None
) -> None:
    """Parse and apply a frontmatter-update hook string.

    E.g. ``frontmatter-update status=ready-for-dev planned=@now``
    """
    parts = hook.split()
    # First token is the hook name; rest are key=val pairs
    pairs = parts[1:]
    updates = _parse_pairs(pairs)

    repo_dir = project.repo_directory if project is not None else None
    resolved: dict[str, object] = {}
    for key, value in updates.items():
        resolved[key] = _interpolate(value, repo_dir)

    try:
        update_frontmatter(plan_path, resolved)
    except Exception as exc:
        print(f"error: frontmatter-update failed: {exc}", file=sys.stderr)
        sys.exit(2)


def _dispatch_render_sprints(project: Project | None) -> None:
    """Run render-sprints inline (not subprocess)."""
    if project is None:
        print(
            "error: no project resolved — run from a directory with a "
            ".booping marker",
            file=sys.stderr,
        )
        sys.exit(2)

    ctx = Context.assemble()
    if ctx.project is None:
        print(
            "error: no project resolved — run from a directory with a "
            ".booping marker",
            file=sys.stderr,
        )
        sys.exit(2)

    output_path = ctx.project.directory / "sprints.md"
    template_path = get_plugin_root() / "src" / "templates" / "sprints.md.j2"
    result = render(
        template_path=template_path,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result)
    print(f"wrote {len(ctx.plans)} plans to {output_path}", file=sys.stderr)


def _dispatch_vault_commit(
    to_status: str, plan_path: Path, also: list[Path]
) -> None:
    """Run vault-commit inline."""
    do_vault_commit(to_status=to_status, plan_path=plan_path, also=also)


def _run(args: argparse.Namespace) -> None:
    to_status: str = args.to_status
    plan_path: Path = args.plan
    also: list[Path] = args.also or []

    if not plan_path.is_file():
        print(f"error: plan not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    # Read current status from plan frontmatter
    fm = parse_frontmatter_only(plan_path)
    from_status = str(fm.get("status", ""))

    # Resolve project for interpolation and vault ops
    project = Project.load_cwd_configured()

    # Load config
    plugin_root = get_plugin_root()
    from booping.context import config as config_mod

    config = config_mod.load(plugin_root, [])

    # Idempotent re-run: current status already equals target
    idempotent = from_status == to_status

    if not idempotent:
        # Validate transition
        edges = resolve_edges(from_status, config)
        allowed = {e.to for e in edges}
        if to_status not in allowed:
            allowed_list = ", ".join(sorted(allowed))
            print(
                f"error: cannot transition from {from_status!r} to "
                f"{to_status!r}; allowed targets: {allowed_list}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Get ordered hook list
        hooks = resolve_hooks(from_status, to_status, config)
    else:
        # Idempotent re-run: skip frontmatter-update, run remaining post hooks
        post_hooks = config.get("plan", {}).get("hooks", {}).get("post", [])
        hooks = [str(h) for h in post_hooks]

    # Dispatch each hook
    for hook in hooks:
        hook_name = hook.split()[0] if " " in hook else hook
        try:
            if hook_name == "frontmatter-update":
                _dispatch_frontmatter_update(hook, plan_path, project)
            elif hook_name == "render-sprints":
                _dispatch_render_sprints(project)
            elif hook_name == "vault-commit":
                _dispatch_vault_commit(to_status, plan_path, also)
            elif hook_name == "suggest":
                # suggest hooks are LLM-facing hints; skip in dispatcher
                continue
            else:
                print(f"error: unknown hook: {hook_name!r}", file=sys.stderr)
                sys.exit(2)
        except SystemExit as exc:
            # Re-raise exit(1) and exit(2) from hook dispatch
            if exc.code in (1, 2):
                print(f"hook {hook_name!r} failed", file=sys.stderr)
                raise
            raise

    # Log
    log_vault = project.directory if project is not None else None
    logger.log(
        vault=log_vault,
        subcommand="transition",
        message=f"{plan_path} {from_status}→{to_status}",
    )

    print(f"{from_status} → {to_status}")