from __future__ import annotations

import argparse
import sys
from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("render-sprints", help="Render sprints.md from vault plans")
    p.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="PATH",
        help="Output path (default: <vault>/sprints.md); use - for stdout",
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble()

    if ctx.project is None:
        print(
            "error: no project resolved — run from a directory with a .booping marker",
            file=sys.stderr,
        )
        sys.exit(2)

    template_path = get_plugin_root() / "src/templates/sprints.md.j2"
    result = render(
        template_path=template_path,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
    )

    output_str: str | None = args.output
    if output_str == "-":
        sys.stdout.write(result)
    elif output_str is not None:
        output_path = Path(output_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result)
        print(f"wrote {len(ctx.plans)} plans to {output_path}", file=sys.stderr)
    else:
        output_path = ctx.project.directory / "sprints.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result)
        print(f"wrote {len(ctx.plans)} plans to {output_path}", file=sys.stderr)
