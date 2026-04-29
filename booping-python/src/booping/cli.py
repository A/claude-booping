import argparse
import sys

from booping.commands.render import add_render_args


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="booping")
    sub = parser.add_subparsers(dest="command")

    render_parser = sub.add_parser("render", help="Render a Jinja2 template")
    add_render_args(render_parser)

    sub.add_parser("plans", help="List and filter plans")
    sub.add_parser("debug-context", help="Debug assembled context")
    sub.add_parser("debug-template", help="Debug template resolution")

    args = parser.parse_args(argv)

    if args.command == "render":
        from booping.commands.render import handle

        return handle(args)
    if args.command in ("plans", "debug-context", "debug-template"):
        print(f"not implemented: {args.command}", file=sys.stderr)
        return 1
    parser.print_help(file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())