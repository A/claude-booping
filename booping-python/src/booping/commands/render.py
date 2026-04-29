import argparse

from booping.rendering import render


def add_render_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", help="Path to the Jinja2 template to render")


def handle(args: argparse.Namespace) -> int:
    output = render(args.path)
    print(output)
    return 0