import argparse
import sys

from booping.commands.render import add_render_args


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="booping")
    sub = parser.add_subparsers(dest="command")

    render_parser = sub.add_parser("render", help="Render a Jinja2 template")
    add_render_args(render_parser)

    sub.add_parser("plans", help="List and filter plans")

    debug_ctx = sub.add_parser(
        "debug-context", help="Debug assembled context"
    )
    debug_ctx.add_argument(
        "--full",
        action="store_true",
        help="Show full context instead of compact summary",
    )

    debug_tpl = sub.add_parser(
        "debug-template", help="Debug template resolution"
    )
    debug_tpl.add_argument(
        "path", help="Path to the Jinja2 template to render"
    )
    debug_tpl.add_argument(
        "--vault",
        type=str,
        default=None,
        help="Path to the project vault directory",
    )

    args = parser.parse_args(argv)

    if args.command == "render":
        from booping.commands.render import handle

        return handle(args)
    if args.command == "debug-context":
        from booping.commands.debug import handle as debug_handle

        return debug_handle(args)
    if args.command == "debug-template":
        from booping.commands.debug import handle_debug_template

        return handle_debug_template(args)
    if args.command == "plans":
        print(f"not implemented: {args.command}", file=sys.stderr)
        return 1
    parser.print_help(file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())