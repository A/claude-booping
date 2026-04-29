from __future__ import annotations

import argparse
import sys

import yaml
from jinja2 import Environment, FileSystemLoader

from booping.rendering import LenientUndefined, get_plugin_root


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "build",
        help="Render src/files/**/*.j2 to plugin-root destinations using src/config_files.yaml",
    )
    p.set_defaults(func=run)


def run(_args: argparse.Namespace) -> None:
    try:
        plugin_root = get_plugin_root()
    except RuntimeError as exc:
        sys.stderr.write(f"booping build: {exc}\n")
        sys.exit(2)

    files_root = plugin_root / "src" / "files"
    config_path = plugin_root / "src" / "config_files.yaml"

    if not files_root.is_dir():
        sys.stderr.write(f"booping build: missing {files_root}\n")
        sys.exit(2)
    if not config_path.is_file():
        sys.stderr.write(f"booping build: missing {config_path}\n")
        sys.exit(2)

    cfg: dict[str, object] = yaml.safe_load(config_path.read_text()) or {}

    env = Environment(
        loader=FileSystemLoader(str(files_root)),
        undefined=LenientUndefined,
        keep_trailing_newline=True,
    )

    written = 0
    for template_path in sorted(files_root.rglob("*.j2")):
        rel = template_path.relative_to(files_root)
        try:
            template = env.get_template(str(rel))
            rendered = template.render(**cfg)
        except Exception as exc:
            sys.stderr.write(f"booping build: failed to render {rel}: {exc}\n")
            sys.exit(2)

        dest = plugin_root / rel.with_suffix("")
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(rendered)
        except OSError as exc:
            sys.stderr.write(f"booping build: failed to write {dest}: {exc}\n")
            sys.exit(2)
        written += 1

    sys.stderr.write(f"wrote {written} files\n")
