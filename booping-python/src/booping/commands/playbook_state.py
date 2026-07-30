"""Playbook run reporter — read the current status of every run artifact.

Read-only counterpart of `playbook-transition`: resolves the same artifacts against
the run workdir and prints, per `states:` entry, the current status plus the edges
leaving it. Nothing is written except the standard `.booping.log` line.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, NoReturn

import yaml

from booping import logger
from booping.commands.playbook_transition import NOT_STARTED
from booping.context import Context
from booping.context._yaml import parse_frontmatter_only
from booping.context.lifecycle import resolve_edges
from booping.context.playbook import Playbook, StateMachine

BOOTSTRAP_WHEN = "run not started — bootstrap the artifact"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "playbook-state",
        help="Report the current status of every playbook run artifact",
    )
    p.add_argument("playbook", help="Playbook name")
    p.add_argument(
        "--workdir",
        type=str,
        default=None,
        metavar="PATH",
        help="Run workspace the artifact paths resolve against (default: cwd)",
    )
    p.set_defaults(func=_run)


def _fail(message: str, code: int = 1) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def _resolve_playbook(ctx: Context, name: str) -> Playbook:
    pb = next((p for p in ctx.playbooks if p.name == name), None)
    if pb is None:
        known = ", ".join(sorted(p.name for p in ctx.playbooks)) or "(none)"
        _fail(f"playbook not found: {name} (known: {known})")
    return pb


def _ordered_states(pb: Playbook) -> list[str]:
    """States entries in report order: the outer graph's entry first, then the rest."""
    order: list[str] = []
    outer = pb.state_refs.get("")
    if outer is not None and outer in pb.states:
        order.append(outer)
    order.extend(name for name in pb.states if name not in order)
    return order


def _read_status(artifact: Path) -> str:
    try:
        fm = parse_frontmatter_only(artifact)
    except ValueError:
        fm = {}
    status = fm.get("status")
    if status is None or str(status) == "":
        _fail(f"{artifact}: no frontmatter `status:` key; run state is not readable")
    return str(status)


def _next_edges(status: str, machine: StateMachine) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for edge in resolve_edges(status, machine.raw):
        item: dict[str, Any] = {"to": edge.to}
        if edge.when:
            item["when"] = edge.when
        if edge.gates:
            item["gates"] = edge.gates
        out.append(item)
    return out


def _report_status(artifact: Path, machine: StateMachine) -> dict[str, Any]:
    if not artifact.exists():
        return {
            "status": NOT_STARTED,
            "next": [{"to": machine.initial, "when": BOOTSTRAP_WHEN}],
        }
    status = _read_status(artifact)
    report: dict[str, Any] = {"status": status}
    edges = _next_edges(status, machine)
    if edges:
        report["next"] = edges
    return report


def _instances(machine: StateMachine, workdir: Path) -> dict[str, Any]:
    """Enumerate on-disk instances of a `{instance}` artifact path, keyed by slug —
    the path component the placeholder occupies, sorted."""
    parts = machine.artifact.split("/")
    slug_index = next(i for i, part in enumerate(parts) if "{instance}" in part)
    found: dict[str, Path] = {}
    for match in workdir.glob(machine.artifact.replace("{instance}", "*")):
        found[match.relative_to(workdir).parts[slug_index]] = match
    return {
        slug: _report_status(found[slug], machine) for slug in sorted(found)
    }


def _run(args: argparse.Namespace) -> None:
    workdir_arg: str | None = args.workdir
    workdir = (
        Path(workdir_arg).expanduser().resolve()
        if workdir_arg is not None
        else Path.cwd()
    )
    if not workdir.is_dir():
        _fail(f"workdir not found: {workdir}")

    ctx = Context.assemble(start=workdir)
    pb = _resolve_playbook(ctx, args.playbook)
    if not pb.states:
        _fail(f"playbook '{pb.name}' declares no states")

    states: dict[str, Any] = {}
    for name in _ordered_states(pb):
        machine = pb.states[name]
        entry: dict[str, Any] = {"artifact": machine.artifact}
        if "{instance}" in machine.artifact:
            entry["instances"] = _instances(machine, workdir)
        else:
            entry.update(_report_status(workdir / machine.artifact, machine))
        states[name] = entry

    logger.log(
        vault=ctx.project.directory if ctx.project is not None else None,
        subcommand="playbook-state",
        message=f"{pb.name} @ {workdir}",
    )

    print(
        yaml.safe_dump(
            {"playbook": pb.name, "workdir": str(workdir), "states": states},
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        ),
        end="",
    )
