from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

from jinja2 import Environment, TemplateError

from booping import logger
from booping.context import Context
from booping.context.scaffold import DirNode, FileNode, ScaffoldError, load
from booping.macros import parse_stub_overrides
from booping.rendering import build_source_env
from booping.utils import deep_merge, diff_report, parse_set_overrides


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "scaffold",
        help="Materialise a config-declared file/dir tree into a destination directory",
    )
    p.add_argument(
        "config_path",
        metavar="config-path",
        help=(
            "Dotted path into the merged config addressing the tree,"
            " e.g. core.setup_playbook.scaffold"
        ),
    )
    p.add_argument(
        "dest",
        type=Path,
        help="Destination directory; created if missing, parents included",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite the files the tree names when they already exist;"
            " never deletes a directory"
        ),
    )
    p.add_argument(
        "--set",
        action="append",
        dest="set_overrides",
        default=None,
        metavar="KEY=VALUE",
        help=(
            "Expose a value to seed content as a bare template variable"
            " (--set name=x renders {{ name }}); repeatable, later pairs win,"
            " values stay strings"
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


@dataclass(frozen=True)
class _Write:
    path: Path
    content: str | None


def _fail(message: str, code: int = 1) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def _render_seed(env: Environment, node: FileNode) -> str:
    try:
        return env.from_string(node.content).render()
    except TemplateError as exc:
        raise ScaffoldError(node.path, f"Jinja error in seed content: {exc}") from exc


def _plan(root: DirNode, dest: Path, env: Environment) -> list[_Write]:
    """The full tree rendered into memory, parents before children — nothing is
    written until every node has parsed and rendered."""
    writes: list[_Write] = [_Write(dest, None)]

    def walk(node: DirNode, base: Path) -> None:
        for child in node.children:
            path = base / child.name
            if isinstance(child, DirNode):
                writes.append(_Write(path, None))
                walk(child, path)
            elif isinstance(child, FileNode):
                writes.append(_Write(path, _render_seed(env, child)))

    walk(root, dest)
    return writes


def _apply(writes: list[_Write], force: bool) -> tuple[int, int, int]:
    created_dirs = created_files = overwritten = 0
    for write in writes:
        existed = write.path.exists()
        if write.content is None:
            write.path.mkdir(parents=True, exist_ok=True)
            if not existed:
                print(f"created dir {write.path}")
                created_dirs += 1
            continue

        if existed and not force:
            print(f"skipped existing file {write.path}")
            continue

        previous = write.path.read_text(encoding="utf-8") if existed else None
        if previous == write.content:
            continue

        write.path.write_text(write.content, encoding="utf-8")
        diff = diff_report(write.path, previous, write.content)
        if diff:
            print(diff)
        if existed:
            overwritten += 1
        else:
            created_files += 1
    return created_dirs, created_files, overwritten


def _run(args: argparse.Namespace) -> None:
    set_pairs: list[str] = args.set_overrides or []
    try:
        variables = parse_set_overrides(set_pairs)
    except ValueError as exc:
        _fail(f"malformed --set pair (expected KEY=VALUE): {exc}")

    try:
        stub_overrides = parse_stub_overrides(args.stub_macros or [])
    except ValueError as exc:
        _fail(f"malformed --stub-macro pair (expected DOTTED.PATH=LITERAL): {exc}")

    dest: Path = args.dest
    config_path: str = args.config_path

    ctx = Context.assemble()
    logger.log(
        vault=ctx.project.directory if ctx.project is not None else None,
        subcommand="scaffold",
        message=f"{config_path} → {dest}",
    )

    if dest.exists() and not dest.is_dir():
        _fail(f"destination {dest} exists and is not a directory")

    config = deep_merge(ctx.config, stub_overrides) if stub_overrides else ctx.config
    env = build_source_env(context=ctx, config=config)
    globals_: dict[str, Any] = env.globals  # type: ignore[assignment]
    globals_.update(variables)

    try:
        writes = _plan(load(ctx.config, config_path), dest, env)
    except ScaffoldError as exc:
        _fail(str(exc))

    try:
        created_dirs, created_files, overwritten = _apply(writes, args.force)
    except OSError as exc:
        _fail(f"failed to write scaffold into {dest}: {exc}", code=2)

    total = created_dirs + created_files + overwritten
    print(
        f"scaffolded {total} paths — {created_dirs} dirs created,"
        f" {created_files} files created, {overwritten} files overwritten"
    )
