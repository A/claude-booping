"""Run records — one `{vault}/{core.run.dir}/{id}.md` per `booping run`, its log beside it.

Every read and write of a record lives here; nothing prints. `booping.commands.run`
launches the child, `booping.status` reads the records back.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from booping.context import Context
from booping.context._yaml import parse_frontmatter_only, update_frontmatter
from booping.rendering import build_source_env

STATUSES = ("running", "finished", "paused", "failed", "lost")
RUNNING, FINISHED, PAUSED, FAILED, LOST = STATUSES
MODES = ("autonomous", "supervised")
ID_DATE = "+%Y%m%d-%H%M%S"
STAMP_DATE = "+%Y-%m-%d %H:%M"
GITIGNORE = "*.log\n"


class RunError(Exception):
    pass


@dataclass(frozen=True)
class Run:
    id: str
    session_id: str
    record: Path
    log: Path
    rel_record: str
    rel_log: str


def settings(ctx: Context) -> dict[str, Any]:
    return ctx.config.get("core", {}).get("run", {})


def _vault(ctx: Context) -> Path:
    if ctx.vault is None:
        raise RunError("no booping project here; run records live in its vault")
    return ctx.vault


def runs_dir(ctx: Context) -> Path:
    return _vault(ctx) / str(settings(ctx).get("dir"))


def _now(ctx: Context, fmt: str) -> str:
    env = build_source_env(context=ctx, config=ctx.config)
    return env.from_string("{{ macro('core.macros.date', fmt) }}").render(fmt=fmt).strip()


def session_id(run_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"booping-run:{run_id}"))


def allocate(ctx: Context, playbook: str) -> Run:
    """The next free id for *playbook* at the current date macro: `-2`, `-3` … appended
    while a record of that id exists."""
    directory = runs_dir(ctx)
    base = f"{_now(ctx, ID_DATE)}-{playbook}"
    run_id, n = base, 1
    while (directory / f"{run_id}.md").exists():
        n += 1
        run_id = f"{base}-{n}"
    rel_dir = str(settings(ctx).get("dir"))
    return Run(
        id=run_id,
        session_id=session_id(run_id),
        record=directory / f"{run_id}.md",
        log=directory / f"{run_id}.log",
        rel_record=f"{rel_dir}/{run_id}.md",
        rel_log=f"{rel_dir}/{run_id}.log",
    )


def prepare_dir(ctx: Context) -> Path:
    """The runs directory, created with its `.gitignore` on first use. Raises `OSError`."""
    directory = runs_dir(ctx)
    if not directory.is_dir():
        directory.mkdir(parents=True)
        (directory / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    return directory


def create(
    ctx: Context,
    run: Run,
    *,
    playbook: str,
    autonomous: bool,
    target: list[str],
    plan: str | None,
    items: list[str],
    pid: int,
    prompt: str,
    baseline_7d: int | None = None,
) -> None:
    """Write *run*'s record as `running`; `usage_baseline_7d` only when *baseline_7d* is
    given. Raises `OSError`."""
    frontmatter: dict[str, Any] = {
        "id": run.id,
        "playbook": playbook,
        "mode": MODES[0] if autonomous else MODES[1],
        "target": list(target),
        "plan": plan,
        "items": list(items),
        "status": RUNNING,
        "pid": pid,
        "session_id": run.session_id,
        "log": run.rel_log,
        "started_at": _now(ctx, STAMP_DATE),
        "ended_at": None,
        "exit_code": None,
        "acked_at": None,
    }
    if baseline_7d is not None:
        frontmatter["usage_baseline_7d"] = baseline_7d
    head = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True, width=4096)
    body = f"# {run.id}\n\n```text\n{prompt}\n```\n"
    run.record.write_text(f"---\n{head}---\n\n{body}", encoding="utf-8")


def finish(ctx: Context, run: Run, exit_code: int) -> str:
    """Write the outcome of *run*; returns its status — `paused` when the child exited 0
    after the budget gate stamped `paused_reason` on the record."""
    if exit_code != 0:
        status = FAILED
    elif read(run.record).get("paused_reason"):
        status = PAUSED
    else:
        status = FINISHED
    update_frontmatter(
        run.record,
        {
            "status": status,
            "exit_code": exit_code,
            "ended_at": _now(ctx, STAMP_DATE),
            "pid": None,
        },
    )
    return status


def read(path: Path) -> dict[str, Any]:
    return parse_frontmatter_only(path)


def records(ctx: Context) -> list[dict[str, Any]]:
    """Every record's frontmatter, by id; none without a runs directory."""
    directory = runs_dir(ctx)
    if not directory.is_dir():
        return []
    return [read(path) for path in sorted(directory.glob("*.md"))]


def _alive(pid: Any) -> bool:
    if not isinstance(pid, int):
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def effective_status(record: dict[str, Any]) -> str:
    """The stored status, except a `running` record whose wrapper is gone reads `lost`."""
    status = str(record.get("status"))
    if status == RUNNING and not _alive(record.get("pid")):
        return LOST
    return status


def ack(ctx: Context, ids: list[str]) -> None:
    """Mark ended runs seen. Every id is checked before the first write."""
    directory = runs_dir(ctx)
    checked: list[tuple[Path, str]] = []
    for run_id in ids:
        path = directory / f"{run_id}.md"
        if not path.is_file():
            raise RunError(f"unknown run {run_id}")
        status = effective_status(read(path))
        if status == RUNNING:
            raise RunError(f"run {run_id} is still running")
        checked.append((path, status))
    stamp = _now(ctx, STAMP_DATE)
    for path, status in checked:
        updates: dict[str, object] = {"acked_at": stamp}
        if status == LOST:
            updates["status"] = LOST
        update_frontmatter(path, updates)
