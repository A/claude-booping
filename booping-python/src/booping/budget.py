"""The subscription usage gate — a reading, the verdict over it, and the run-record stamp.

Nothing prints; `booping.commands.budget` and `booping.commands.run` format. A reading is
the last `rate_limit_event` stream line of the newest fresh run log, else of
`core.budget.probe`'s stdout.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from datetime import time as clock
from pathlib import Path
from typing import Any, cast

from booping import runs
from booping.context import Context
from booping.context._yaml import parse_frontmatter_only, update_frontmatter

RUN_ID_ENV = "BOOPING_RUN_ID"
STAMP = "%Y-%m-%d %H:%M"
EVENT = "rate_limit_event"
WINDOW_ERROR = "core.budget.window must be {start: HH:MM, end: HH:MM}"
_HHMM = re.compile(r"([01]\d|2[0-3]):([0-5]\d)")
DONE = "done"


class BudgetError(Exception):
    """A config error."""


class NoReading(Exception):
    """No usage reading; the message is the why."""


@dataclass(frozen=True)
class Usage:
    pct: int
    resets_at: datetime


@dataclass(frozen=True)
class Reading:
    five_hour: Usage
    seven_day: Usage
    source: str


@dataclass(frozen=True)
class Window:
    start: clock
    end: clock


@dataclass(frozen=True)
class Verdict:
    allow: bool
    reason: str
    resume_after: datetime | None = None

    @property
    def line(self) -> str:
        return f"{'allow' if self.allow else 'pause'} — {self.reason}"


def settings(ctx: Context) -> dict[str, Any]:
    return ctx.config.get("core", {}).get("budget", {})


def _usage(raw: Any) -> Usage:
    return Usage(
        pct=math.floor(float(raw["utilization"]) * 100 + 0.5),
        resets_at=datetime.fromtimestamp(int(raw["resetsAt"])),
    )


def _event(line: str, source: str) -> Reading | None:
    try:
        obj = json.loads(line)
    except ValueError:
        return None
    if not isinstance(obj, dict):
        return None
    event = cast("dict[str, Any]", obj)
    if event.get("type") != EVENT:
        return None
    info: dict[str, Any] = event.get("rate_limit_info") or {}
    windows: dict[str, Any] = info.get("unifiedWindows") or {}
    try:
        return Reading(_usage(windows["five_hour"]), _usage(windows["seven_day"]), source)
    except (KeyError, TypeError, ValueError):
        return None


def parse_stream(lines: Iterable[str], source: str) -> Reading | None:
    """The reading of the last usable `rate_limit_event` line, or None."""
    last = None
    for line in lines:
        last = _event(line, source) or last
    return last


def _repo(ctx: Context) -> Path:
    project = ctx.project
    if project is not None and project.repo_directory is not None:
        return project.repo_directory
    return Path.cwd()


def _from_log(ctx: Context) -> Reading | None:
    if ctx.vault is None:
        return None
    directory = runs.runs_dir(ctx)
    logs = list(directory.glob("*.log")) if directory.is_dir() else []
    if not logs:
        return None
    newest = max(logs, key=lambda p: p.stat().st_mtime)
    if time.time() - newest.stat().st_mtime > float(settings(ctx).get("max_age_s") or 0):
        return None
    rel = newest.relative_to(ctx.vault).as_posix()
    with newest.open(encoding="utf-8", errors="replace") as fh:
        return parse_stream(fh, rel)


def _from_probe(ctx: Context) -> Reading:
    probe: list[Any] = settings(ctx).get("probe") or []
    argv = [str(a) for a in probe]
    try:
        proc = subprocess.run(
            argv,
            cwd=_repo(ctx),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise NoReading(f"cannot run probe: {argv[0]}") from exc
    if proc.returncode != 0:
        raise NoReading(f"probe exited {proc.returncode}")
    reading = parse_stream(proc.stdout.splitlines(), "probe")
    if reading is None:
        raise NoReading("no rate_limit_event in probe output")
    return reading


def read(ctx: Context) -> Reading:
    """The current reading. Raises `NoReading`."""
    return _from_log(ctx) or _from_probe(ctx)


def window(ctx: Context) -> Window | None:
    """`core.budget.window`, parsed. Raises `BudgetError`."""
    raw = settings(ctx).get("window")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise BudgetError(WINDOW_ERROR)
    bounds: list[clock] = []
    for key in ("start", "end"):
        value: object = cast("dict[str, object]", raw).get(key)
        match = _HHMM.fullmatch(value) if isinstance(value, str) else None
        if match is None:
            raise BudgetError(WINDOW_ERROR)
        bounds.append(clock(int(match[1]), int(match[2])))
    return Window(bounds[0], bounds[1])


def _open(now: datetime, win: Window) -> bool:
    t = now.time()
    if win.start <= win.end:
        return win.start <= t < win.end
    return t >= win.start or t < win.end


def _next_start(now: datetime, win: Window) -> datetime:
    start = datetime.combine(now.date(), win.start)
    return start if start > now else start + timedelta(days=1)


def early_verdict(gated: bool, now: datetime, win: Window | None) -> Verdict | None:
    """The verdict decided before any reading — not gated, or a closed window — else None."""
    if not gated:
        return Verdict(True, "not gated: supervised session")
    if win is not None and not _open(now, win):
        return Verdict(
            False,
            f"outside window {win.start:%H:%M}-{win.end:%H:%M}",
            _next_start(now, win),
        )
    return None


def verdict(
    *,
    gated: bool,
    now: datetime,
    win: Window | None,
    reading: Reading | NoReading,
    ceiling_5h: int,
    ceiling_7d: int,
    run_pct: int | None,
    baseline: int | None,
) -> Verdict:
    """The gate's check order, first match wins."""
    early = early_verdict(gated, now, win)
    if early is not None:
        return early
    if isinstance(reading, NoReading):
        return Verdict(False, f"no usage reading: {reading}")
    five, seven = reading.five_hour, reading.seven_day
    if five.pct >= ceiling_5h:
        return Verdict(False, f"5h usage {five.pct}% ≥ ceiling {ceiling_5h}%", five.resets_at)
    if seven.pct >= ceiling_7d:
        return Verdict(False, f"7d usage {seven.pct}% ≥ ceiling {ceiling_7d}%", seven.resets_at)
    line = f"5h {five.pct}%, 7d {seven.pct}%"
    if run_pct is not None and baseline is not None:
        spent = seven.pct - baseline
        if spent >= run_pct:
            return Verdict(False, f"run allowance spent: {spent} ≥ {run_pct} (7d points)")
        line += f", run {spent}/{run_pct}"
    return Verdict(True, line)


def gated(ctx: Context) -> bool:
    return (
        bool(os.environ.get(RUN_ID_ENV))
        or ctx.config.get("core", {}).get("autonomy") == "autonomous"
    )


def now(ctx: Context) -> datetime:
    return datetime.strptime(runs._now(ctx, runs.STAMP_DATE), STAMP)  # pyright: ignore[reportPrivateUsage]


def evaluate(
    ctx: Context, *, is_gated: bool, baseline: int | None
) -> tuple[Verdict, Reading | None]:
    """The verdict from config, the date macro and — only when the early checks pass — a
    reading. Raises `BudgetError`."""
    cfg = settings(ctx)
    current = now(ctx)
    win = window(ctx)
    early = early_verdict(is_gated, current, win)
    if early is not None:
        return early, None
    try:
        reading: Reading | NoReading = read(ctx)
    except NoReading as exc:
        reading = exc
    run_pct = cfg.get("run_pct")
    result = verdict(
        gated=is_gated,
        now=current,
        win=win,
        reading=reading,
        ceiling_5h=int(cfg["ceiling_5h_pct"]),
        ceiling_7d=int(cfg["ceiling_7d_pct"]),
        run_pct=None if run_pct is None else int(run_pct),
        baseline=baseline,
    )
    return result, reading if isinstance(reading, Reading) else None


def run_record(ctx: Context) -> Path | None:
    """The registered run's record, when this process runs inside one."""
    run_id = os.environ.get(RUN_ID_ENV)
    if not run_id or ctx.vault is None:
        return None
    path = runs.runs_dir(ctx) / f"{run_id}.md"
    return path if path.is_file() else None


def baseline(record: Path | None) -> int | None:
    if record is None:
        return None
    value = parse_frontmatter_only(record).get("usage_baseline_7d")
    return None if value is None else int(value)


def next_milestone(ctx: Context, plan: str | None) -> str | None:
    """The stem of the first milestone file of *plan*, by `id`, whose status is not done."""
    if not plan or ctx.vault is None:
        return None
    pattern = str(ctx.config.get("core", {}).get("plans", {}).get("milestones", {}).get("glob"))
    files = [(parse_frontmatter_only(p), p) for p in (ctx.vault / plan).parent.glob(pattern)]
    for fm, path in sorted(files, key=lambda f: str(f[0].get("id"))):
        if fm.get("status") != DONE:
            return path.stem
    return None


def stamp(ctx: Context, record: Path, result: Verdict) -> None:
    """Write a `pause` verdict onto the run *record*."""
    plan = parse_frontmatter_only(record).get("plan")
    update_frontmatter(
        record,
        {
            "paused_reason": result.reason,
            "resume_after": None
            if result.resume_after is None
            else result.resume_after.strftime(STAMP),
            "next_milestone": next_milestone(ctx, plan),
        },
    )
