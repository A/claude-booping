from __future__ import annotations

import argparse
import sys

from booping import budget
from booping.budget import STAMP, BudgetError, NoReading, Reading, Verdict
from booping.commands.specs import (
    _assemble,  # pyright: ignore[reportPrivateUsage]
    _fail,  # pyright: ignore[reportPrivateUsage]
)

NO_READING_EXIT = 4
PAUSE_EXIT = 3


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "budget",
        help="Read the subscription's usage, or gate autonomous work on it and core.budget",
    )
    verbs = p.add_subparsers(dest="budget_verb", metavar="<verb>", required=True)

    read_help = (
        "Print the 5-hour and 7-day usage and its source, from the newest fresh run log or"
        " core.budget.probe; exit 4 when there is no reading"
    )
    read = verbs.add_parser("read", help=read_help, description=read_help)
    read.set_defaults(func=_run_read)

    gate_help = (
        "Print allow (exit 0) or pause (exit 3, plus resume_after when known) from the"
        " window, the reading, the ceilings and the run allowance; exit 1 on a config error."
        " Inside a registered run a pause stamps its record"
    )
    gate = verbs.add_parser("gate", help=gate_help, description=gate_help)
    gate.set_defaults(func=_run_gate)


def reading_lines(reading: Reading) -> list[str]:
    return [
        f"5h: {reading.five_hour.pct}% (resets {reading.five_hour.resets_at.strftime(STAMP)})",
        f"7d: {reading.seven_day.pct}% (resets {reading.seven_day.resets_at.strftime(STAMP)})",
        f"source: {reading.source}",
    ]


def verdict_lines(result: Verdict) -> list[str]:
    lines = [result.line]
    if result.resume_after is not None:
        lines.append(f"resume_after: {result.resume_after.strftime(STAMP)}")
    return lines


def _run_read(_args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    try:
        reading = budget.read(ctx)
    except NoReading as exc:
        _fail(f"no usage reading: {exc}", NO_READING_EXIT)
    print("\n".join(reading_lines(reading)))


def _run_gate(_args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    record = budget.run_record(ctx)
    try:
        result, _ = budget.evaluate(
            ctx, is_gated=budget.gated(ctx), baseline=budget.baseline(record)
        )
    except BudgetError as exc:
        _fail(str(exc))
    if not result.allow and record is not None:
        budget.stamp(ctx, record, result)
    print("\n".join(verdict_lines(result)))
    sys.exit(0 if result.allow else PAUSE_EXIT)
