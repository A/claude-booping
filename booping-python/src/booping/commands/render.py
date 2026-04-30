from __future__ import annotations

import argparse
import sys
from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("render", help="Render a Jinja2 template to stdout")
    p.add_argument("path", type=Path, help="Path to the .j2 template file")
    p.add_argument("--output", type=Path, default=None, help="Write output to file; skip stdout")
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    template_path: Path = args.path
    if not template_path.is_absolute():
        template_path = get_plugin_root() / template_path
    result = render(
        template_path=template_path,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    else:
        sys.stdout.write(result)
