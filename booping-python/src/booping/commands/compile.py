from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, cast

from booping.commands.render_cli_agent import render_cli_agent
from booping.context import Context
from booping.rendering import get_plugin_root

PREFIX = "cli_agent_"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "compile",
        help="Generate native wrapper agents for every type: cli agent",
        description=(
            "Static-generation entrypoint. Materializes a native wrapper agent at "
            "<repo>/.claude/agents/cli_agent_<id>.md for every type: cli agent in the "
            "merged config and prunes wrappers whose id is no longer configured."
        ),
    )
    p.set_defaults(func=_run)


def die(msg: str) -> None:
    sys.stderr.write(msg.rstrip() + "\n")
    sys.exit(2)


def cli_agent_ids(config: dict[str, Any]) -> list[str]:
    """Unique ids of every type: cli agent across all skills.*.agents, sorted."""
    ids: set[str] = set()
    skills_any: Any = config.get("skills", {})
    if not isinstance(skills_any, dict):
        return []
    skills = cast(dict[str, Any], skills_any)
    for block in skills.values():
        if not isinstance(block, dict):
            continue
        agents_any: Any = cast(dict[str, Any], block).get("agents", {})
        if not isinstance(agents_any, dict):
            continue
        for agent_id, spec in cast(dict[str, Any], agents_any).items():
            if isinstance(spec, dict):
                spec_d = cast(dict[str, Any], spec)
                if spec_d.get("type") == "cli":
                    ids.add(str(agent_id))
    return sorted(ids)


def compile_wrappers(ctx: Context, plugin_root: Path) -> list[str]:
    """Flush + regenerate cli wrappers under <repo>/.claude/agents/.

    Returns human-readable diff lines (created/removed)."""
    if ctx.project is None:
        die("no project resolved — run from a directory with a .booping marker")
        raise AssertionError  # unreachable

    agents_dir = ctx.project.repo_directory / ".claude" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    existing = {p.name for p in agents_dir.glob(f"{PREFIX}*.md")}
    ids = cli_agent_ids(ctx.config)
    wanted = {f"{PREFIX}{agent_id}.md": agent_id for agent_id in ids}

    diff: list[str] = []

    for name in sorted(existing - set(wanted)):
        (agents_dir / name).unlink()
        diff.append(f"removed {name}")

    for name, agent_id in sorted(wanted.items()):
        body = render_cli_agent(ctx, agent_id, plugin_root)
        dest = agents_dir / name
        prior = dest.read_text() if dest.is_file() else None
        dest.write_text(body)
        if prior is None:
            diff.append(f"created {name}")
        elif prior != body:
            diff.append(f"updated {name}")
        else:
            diff.append(f"unchanged {name}")

    return diff


def _run(_args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    plugin_root = get_plugin_root()
    diff = compile_wrappers(ctx, plugin_root)
    if diff:
        for line in diff:
            sys.stdout.write(line + "\n")
    else:
        sys.stdout.write("No cli agents configured; nothing to generate.\n")
    sys.stdout.write("\nRestart Claude Code to apply.\n")
