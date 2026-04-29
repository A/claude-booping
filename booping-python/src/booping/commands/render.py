from __future__ import annotations

from pathlib import Path

from booping.context import Context
from booping.tools import Tools
from booping.rendering import render


def add_parser(subparsers) -> None:
    p = subparsers.add_parser("render", help="Render a Jinja2 template")
    p.add_argument("path", help="Template path")
    p.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Output file (default: stdout)"
    )
    p.set_defaults(func=_run)


def _run(args) -> None:
    ctx = Context.assemble()
    tools_ns = Tools(plugin_root=ctx._assembled_plugin_root, context=ctx, config=ctx.config)
    result = render(
        template_path=args.path,
        context=ctx,
        config=ctx.config,
        tools=tools_ns,
        kwargs={},
        plugin_root=ctx._assembled_plugin_root,
    )
    if args.output:
        args.output.write_text(result)
    else:
        print(result)