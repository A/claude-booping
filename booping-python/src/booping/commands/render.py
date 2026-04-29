from __future__ import annotations

import argparse
import sys
from pathlib import Path

from booping.context import Context
from booping.rendering import render


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("render", help="Render a Jinja2 template to stdout")
    p.add_argument("path", type=Path, help="Path to the .j2 template file")
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    result = render(
        template_path=args.path,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
    )
    sys.stdout.write(result)
