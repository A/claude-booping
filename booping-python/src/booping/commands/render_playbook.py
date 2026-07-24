from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, cast

from jinja2 import Environment, FileSystemLoader

from booping import logger
from booping.context import Context
from booping.context.playbook import Playbook, resolve_agent
from booping.rendering import LenientUndefined, get_plugin_root


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "render-playbook", help="Render a playbook's composed procedure to stdout"
    )
    p.add_argument("name", help="Playbook name to render")
    p.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="PATH",
        help="Output path (default: stdout); use - for stdout",
    )
    p.set_defaults(func=_run)


def compose(pb: Playbook, plugin_root: Path | None = None) -> str:
    """Render a playbook's manifest body with ``inline_step`` / ``reference_step``
    bound to that playbook's own steps. Call order in the body drives section order;
    an unknown step name raises ValueError."""
    root = plugin_root if plugin_root is not None else get_plugin_root()
    templates_dir = root / "src" / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=LenientUndefined,
        keep_trailing_newline=True,
    )

    steps_by_name = {s.name: s for s in pb.steps}

    def _render_step(name: str, mode: str) -> str:
        step = steps_by_name.get(name)
        if step is None:
            raise ValueError(f"playbook '{pb.name}': unknown step '{name}'")
        return env.get_template("_partials/_playbook_step.j2").render(step=step, mode=mode)

    def _inline_step(name: str) -> str:
        return _render_step(name, "inline")

    def _reference_step(name: str) -> str:
        return _render_step(name, "reference")

    # resolve_agent must be an env global so it is in scope during the nested partial render.
    globals_: dict[str, Any] = cast("dict[str, Any]", env.globals)
    globals_["resolve_agent"] = resolve_agent
    globals_["inline_step"] = _inline_step
    globals_["reference_step"] = _reference_step

    return env.from_string(pb.body).render()


def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble()

    pb = next((p for p in ctx.playbooks if p.name == args.name), None)
    if pb is None:
        known = ", ".join(sorted(p.name for p in ctx.playbooks)) or "(none)"
        print(
            f"error: playbook not found: {args.name} (known: {known})",
            file=sys.stderr,
        )
        sys.exit(1)

    if pb.requires_project and ctx.project is None:
        print(
            f"error: playbook '{args.name}' requires a booping project; none attached here",
            file=sys.stderr,
        )
        sys.exit(1)

    output_str: str | None = args.output
    message = args.name
    if output_str is not None and output_str != "-":
        message = f"{message} → {output_str}"
    logger.log(
        vault=ctx.project.directory if ctx.project is not None else None,
        subcommand="render-playbook",
        message=message,
    )

    result = compose(pb)

    if output_str is None or output_str == "-":
        sys.stdout.write(result)
    else:
        output_path = Path(output_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result)
