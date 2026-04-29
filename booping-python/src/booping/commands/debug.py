from __future__ import annotations

import argparse
import sys

import yaml

from booping.context import Context


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("debug-context", help="Dump assembled context as YAML")
    p.set_defaults(func=_run_context)

    subparsers.add_parser("debug-template", help="Not implemented yet").set_defaults(
        func=_not_implemented
    )


def _run_context(args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    data = ctx.model_dump(mode="json")
    data["skills"] = sorted(data.get("skills", {}))
    data["agents"] = sorted(data.get("agents", {}))
    sys.stdout.write(yaml.dump(data, allow_unicode=True, sort_keys=True))


def _not_implemented(args: argparse.Namespace) -> None:
    print("not implemented: debug-template", file=sys.stderr)
    sys.exit(1)
