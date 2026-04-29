import argparse
from pathlib import Path

from booping.rendering import render


def add_render_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", help="Path to the Jinja2 template to render")
    parser.add_argument(
        "--output",
        help="Write rendered output to this file instead of stdout",
    )


def handle(args: argparse.Namespace) -> int:
    output = render(args.path)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output)
    else:
        print(output)
    return 0