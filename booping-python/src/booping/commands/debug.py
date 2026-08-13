from __future__ import annotations

import argparse
import sys

import yaml

from booping.context import Context


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("debug-context", help="Dump assembled context as YAML")
    p.set_defaults(func=_run_context)


def _summarize_body(text: str) -> str:
    return f"<{text.count(chr(10)) + 1 if text else 0} lines>"


def _run_context(args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    data = ctx.model_dump(mode="json")
    data["skills"] = sorted(data.get("skills", {}))
    data["agents"] = sorted(data.get("agents", {}))
    for key in ("plans", "lessons", "plan_templates", "review_templates"):
        for item in data.get(key, []):
            if "body" in item:
                item["body"] = _summarize_body(item["body"])
    sys.stdout.write(yaml.dump(data, allow_unicode=True, sort_keys=True))
