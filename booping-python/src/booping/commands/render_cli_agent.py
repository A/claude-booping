from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from booping.commands.run_agent import resolve_agent
from booping.context import Context
from booping.rendering import LenientUndefined, get_plugin_root
from booping.tools import Tools

WRAPPER_TEMPLATE = "agents/_cli_wrapper.md.j2"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "render-cli-agent",
        help="Render the native-wrapper body for a type: cli agent",
        description=(
            "Resolve <id> across all skills.*.agents (first match wins), require "
            "type: cli, and render the wrapper template with project context baked in. "
            "Prints the complete agent body to stdout."
        ),
    )
    p.add_argument("id", help="cli agent id declared under skills.*.agents.<id>")
    p.set_defaults(func=_run)


def die(msg: str) -> None:
    sys.stderr.write(msg.rstrip() + "\n")
    sys.exit(2)


def render_cli_agent(ctx: Context, agent_id: str, plugin_root: Path) -> str:
    resolved = resolve_agent(ctx.config, agent_id)
    if resolved is None:
        die(f"agent '{agent_id}' not found in any skill's agents block")
        raise AssertionError  # unreachable; die exits

    spec = resolved[1]
    if spec.get("type") != "cli":
        entry_type = spec.get("type", "agent")
        die(f"agent '{agent_id}' has type '{entry_type}'; only cli agents have a wrapper")
        raise AssertionError  # unreachable

    templates_dir = plugin_root / "src" / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=LenientUndefined,
        keep_trailing_newline=True,
    )
    tools = Tools(
        env=env,
        context=ctx,
        config=ctx.config,
        plugin_root=plugin_root,
        render_stack=[],
    )
    template = env.get_template(WRAPPER_TEMPLATE)
    return template.render(
        context=ctx,
        config=ctx.config,
        tools=tools,
        kwargs={},
        agent_id=agent_id,
        spec=spec,
    )


def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    plugin_root = get_plugin_root()
    sys.stdout.write(render_cli_agent(ctx, args.id, plugin_root))
