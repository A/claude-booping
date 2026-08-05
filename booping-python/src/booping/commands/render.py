from __future__ import annotations

import argparse
import sys
from pathlib import Path

from booping import logger, migrations
from booping.context import Context
from booping.macros import parse_stub_overrides
from booping.rendering import get_plugin_root, render
from booping.utils import deep_merge, parse_set_overrides


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("render", help="Render a Jinja2 template to stdout")
    p.add_argument("path", type=Path, help="Path to the .j2 template file")
    p.add_argument("--output", type=Path, default=None, help="Write output to file; skip stdout")
    p.add_argument(
        "--set",
        action="append",
        dest="set_overrides",
        default=None,
        metavar="KEY=VALUE",
        help=(
            "Override a config value for this render (dotted key, e.g."
            " core.sprint.default_threshold_sp=3); repeatable, later pairs win, and the"
            " value wins over every config tier"
        ),
    )
    p.add_argument(
        "--stub-macro",
        action="append",
        dest="stub_macros",
        default=None,
        metavar="DOTTED.PATH=LITERAL",
        help=(
            "Make a macro return LITERAL without executing it (e.g."
            " core.macros.date=19700101-00-00); repeatable, later pairs win"
        ),
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> None:
    set_pairs: list[str] = args.set_overrides or []
    try:
        overrides = parse_set_overrides(set_pairs)
    except ValueError as exc:
        print(
            f"error: malformed --set pair (expected KEY=VALUE): {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        overrides = deep_merge(
            overrides, parse_stub_overrides(args.stub_macros or [])
        )
    except ValueError as exc:
        print(
            f"error: malformed --stub-macro pair (expected DOTTED.PATH=LITERAL): {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    notice = migrations.render_gate()
    if notice is not None:
        _emit(notice + "\n", args.output)
        return

    ctx = Context.assemble()
    if overrides:
        ctx = ctx.model_copy(
            update={
                "config": deep_merge(
                    ctx.config, overrides, shallow_merge_keys=["agents"]
                )
            }
        )

    message = str(args.path)
    if args.output is not None:
        message = f"{message} → {args.output}"
    logger.log(
        vault=ctx.project.directory if ctx.project is not None else None,
        subcommand="render",
        message=message,
    )

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
    _emit(result, args.output)


def _emit(text: str, output: Path | None) -> None:
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text)
    else:
        sys.stdout.write(text)
