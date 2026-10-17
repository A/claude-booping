"""Run reporter — read the current status of every run artifact beside a file.

Read-only counterpart of `transition`: resolves the playbook(s) whose machines the file
is an artifact of with the same matcher, takes the run workdir from the file, and
prints, per `states:` entry of each, the current status plus the edges leaving it.
Nothing is written except the standard `.booping.log` line.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, NoReturn

import yaml

from booping import logger
from booping.commands.transition import (
    NOT_STARTED,
    Match,
    read_status,
    resolve_matches,
)
from booping.context import Context
from booping.context.lifecycle import resolve_edges
from booping.context.playbook import Playbook, StateMachine

BOOTSTRAP_WHEN = "run not started — bootstrap the artifact"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "state",
        help="Report the frontier of every run artifact of the playbook(s) a file belongs to",
    )
    p.add_argument("file", help="A run artifact; its playbook(s) and run workdir follow from it")
    p.add_argument(
        "--playbook",
        type=str,
        default=None,
        metavar="NAME",
        help=(
            "Report only this playbook (required for a machine declaring no "
            "`artifact:`, where the file is the target)"
        ),
    )
    p.set_defaults(func=_run)


def _fail(message: str, code: int = 1) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def _ordered_states(pb: Playbook) -> list[str]:
    """States entries in report order: the outer graph's entry first, then the rest."""
    order: list[str] = []
    outer = pb.state_refs.get("")
    if outer is not None and outer in pb.states:
        order.append(outer)
    order.extend(name for name in pb.states if name not in order)
    return order


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
    status = read_status(artifact)
    if status is None:
        return {
            "status": NOT_STARTED,
            "next": [{"to": machine.initial, "when": BOOTSTRAP_WHEN}],
        }
    report: dict[str, Any] = {"status": status}
    edges = _next_edges(status, machine)
    if edges:
        report["next"] = edges
    return report


def _instances(machine: StateMachine, workdir: Path) -> dict[str, Any]:
    """Enumerate on-disk instances of a `{instance}` artifact path, keyed by slug —
    what the placeholder itself matched, sorted. The segment carrying it may add a
    prefix or suffix (`{instance}.md`); both are stripped off the matched segment."""
    parts = machine.artifact.split("/")
    slug_index = next(i for i, part in enumerate(parts) if "{instance}" in part)
    prefix, _, suffix = parts[slug_index].partition("{instance}")
    found: dict[str, Path] = {}
    for match in workdir.glob(machine.artifact.replace("{instance}", "*")):
        segment = match.relative_to(workdir).parts[slug_index]
        slug = segment[len(prefix) :]
        found[slug[: -len(suffix)] if suffix else slug] = match
    return {slug: _report_status(found[slug], machine) for slug in sorted(found)}


def _report(pb: Playbook, workdir: Path, target: Path | None) -> dict[str, Any]:
    states: dict[str, Any] = {}
    for name in _ordered_states(pb):
        machine = pb.states[name]
        if not machine.artifact:
            if target is None:
                _fail(f"state '{name}' declares no `artifact:`; pass a file it targets")
            states[name] = {"artifact": str(target), **_report_status(target, machine)}
            continue
        entry: dict[str, Any] = {"artifact": machine.artifact}
        if "{instance}" in machine.artifact:
            entry["instances"] = _instances(machine, workdir)
        else:
            entry.update(_report_status(workdir / machine.artifact, machine))
        states[name] = entry
    return {"playbook": pb.name, "workdir": str(workdir), "states": states}


def _run(args: argparse.Namespace) -> None:
    file = Path(args.file).expanduser().resolve()
    start = next(p for p in file.parents if p.is_dir())
    ctx = Context.assemble(start=start)
    playbook: str | None = args.playbook
    matches = resolve_matches(ctx, file, playbook, None)
    if not matches:
        if playbook is not None:
            _fail(f"{file} matches no machine artifact of playbook '{playbook}'")
        _fail(f"{file} matches no machine artifact; pass --playbook")

    by_playbook: dict[str, list[Match]] = {}
    for match in matches:
        by_playbook.setdefault(match.playbook.name, []).append(match)

    reports: list[dict[str, Any]] = []
    for group in by_playbook.values():
        anchored = next((m for m in group if m.machine.artifact), group[0])
        if not anchored.workdir.is_dir():
            _fail(f"workdir not found: {anchored.workdir}")
        target = file if any(not m.machine.artifact for m in group) else None
        reports.append(_report(anchored.playbook, anchored.workdir, target))

    for report in reports:
        logger.log(
            vault=ctx.project.directory if ctx.project is not None else None,
            subcommand="state",
            message=f"{report['playbook']} @ {report['workdir']}",
        )

    print(
        "---\n".join(
            yaml.safe_dump(report, sort_keys=False, default_flow_style=False, allow_unicode=True)
            for report in reports
        ),
        end="",
    )
