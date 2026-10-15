from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
from pathlib import Path
from types import FrameType
from typing import Any

from booping import logger, runs
from booping.commands.specs import (
    _assemble,  # pyright: ignore[reportPrivateUsage]
    _fail,  # pyright: ignore[reportPrivateUsage]
)
from booping.context import Context
from booping.runs import RunError
from booping.specs import open_items
from booping.specs.open_items import OpenItemError

_ITEM_ID = re.compile(r"OI-\d+")
_FORWARDED = (signal.SIGINT, signal.SIGTERM)


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "run",
        help="Launch a recorded headless groom or develop run from core.run, or ack finished runs",
    )
    verbs = p.add_subparsers(dest="run_verb", metavar="<verb>", required=True)

    groom = verbs.add_parser(
        "groom",
        help="Launch a groom run over open items, or over one parked plan",
    )
    groom.add_argument(
        "targets",
        nargs="+",
        metavar="TARGET",
        help="Open item id (OI-NNNN), or one plan's index.md or directory",
    )
    _add_autonomous(groom)
    groom.set_defaults(func=_run_groom)

    develop = verbs.add_parser("develop", help="Launch a develop run over one plan")
    develop.add_argument(
        "targets",
        nargs="+",
        metavar="PLAN",
        help="The plan's index.md or its directory, inside the vault",
    )
    _add_autonomous(develop)
    develop.set_defaults(func=_run_develop)

    ack = verbs.add_parser("ack", help="Mark finished, failed or lost runs as seen")
    ack.add_argument("ids", nargs="+", metavar="ID", help="Run id")
    ack.set_defaults(func=_run_ack)


def _add_autonomous(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--autonomous",
        action="store_true",
        help="Append core.run.preamble: the run settles its own gates and questions",
    )


def _plan(ctx: Context, raw: str) -> tuple[str, Path]:
    """*raw* (an index.md or its directory, absolute or cwd-relative) as the
    vault-relative and the absolute path of an existing plan inside the vault."""
    vault = open_items.require_vault(ctx).resolve()
    path = Path(raw).expanduser()
    path = (path if path.is_absolute() else Path.cwd() / path).resolve()
    if path.is_dir():
        path = path / "index.md"
    if not path.is_file() or not path.is_relative_to(vault):
        raise OpenItemError(f"plan not found: {raw}")
    return open_items.vault_path(ctx, str(path)), path


def _item(ctx: Context, item_id: str) -> Path:
    path = open_items.item_path(ctx, item_id)
    if not path.is_file():
        raise OpenItemError(f"unknown item {item_id}")
    return path.resolve()


def _run_develop(args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    targets: list[str] = args.targets
    try:
        open_items.require_vault(ctx)
        if len(targets) != 1:
            raise OpenItemError("develop takes exactly one plan")
        rel, path = _plan(ctx, targets[0])
        items = open_items.planned_for(ctx, rel)
    except OpenItemError as exc:
        _fail(str(exc))
    _launch(ctx, "develop", args.autonomous, [rel], rel, items, str(path))


def _run_groom(args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    targets: list[str] = args.targets
    ids = [t for t in targets if _ITEM_ID.fullmatch(t)]
    try:
        open_items.require_vault(ctx)
        if ids and len(ids) != len(targets) or len(targets) - len(ids) > 1:
            raise OpenItemError("groom takes item ids or one plan, not both")
        if ids:
            paths = [_item(ctx, item_id) for item_id in ids]
            target, plan, items = ids, None, ids
            prompt_target = ", ".join(f"{i} ({p})" for i, p in zip(ids, paths, strict=True))
        else:
            rel, path = _plan(ctx, targets[0])
            target, plan, items = [rel], rel, open_items.planned_for(ctx, rel)
            prompt_target = str(path)
    except OpenItemError as exc:
        _fail(str(exc))
    _launch(ctx, "groom", args.autonomous, target, plan, items, prompt_target)


def _launch(
    ctx: Context,
    playbook: str,
    autonomous: bool,
    target: list[str],
    plan: str | None,
    items: list[str],
    prompt_target: str,
) -> None:
    cfg = runs.settings(ctx)
    prompt = str(cfg.get("prompt")).format(playbook=playbook, target=prompt_target)
    if autonomous:
        prompt += f"\n\n{cfg.get('preamble')}"
    env: dict[str, Any] = cfg.get("env") or {}
    project = ctx.project
    repo = (
        project.repo_directory
        if project is not None and project.repo_directory is not None
        else Path.cwd()
    )
    try:
        run = runs.allocate(ctx, playbook)
        argv = [*map(str, cfg.get("command") or []), "--session-id", run.session_id, prompt]
        runs.prepare_dir(ctx)
        log = run.log.open("wb")
        runs.create(
            ctx,
            run,
            playbook=playbook,
            autonomous=autonomous,
            target=target,
            plan=plan,
            items=items,
            pid=os.getpid(),
            prompt=prompt,
        )
    except RunError as exc:
        _fail(str(exc))
    except OSError as exc:
        _fail(f"cannot write run record: {exc}")
    print(run.rel_record, flush=True)

    with log:
        try:
            child = subprocess.Popen(
                argv,
                cwd=repo,
                env=os.environ | {str(k): str(v) for k, v in env.items()},
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        except OSError as exc:
            print(f"error: cannot launch {argv[0]}: {exc}", file=sys.stderr)
            code = 127
        else:
            code = _wait(child)

    status = runs.finish(ctx, run, code)
    logger.log(vault=ctx.vault, subcommand="run", message=f"{playbook} {run.id} {status}")
    print(f"{run.id}: {status} (exit {code})", flush=True)
    sys.exit(code)


def _wait(child: subprocess.Popen[bytes]) -> int:
    """The child's exit code, 128+n when signal n ended it. SIGINT and SIGTERM to the
    wrapper are forwarded to the child's process group meanwhile — the child runs in
    its own session, so a terminal's signal never reaches it on its own."""

    def forward(signum: int, _frame: FrameType | None) -> None:
        try:
            os.killpg(child.pid, signum)
        except ProcessLookupError:
            pass

    previous = {sig: signal.signal(sig, forward) for sig in _FORWARDED}
    try:
        code = child.wait()
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return 128 - code if code < 0 else code


def _run_ack(args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    ids: list[str] = args.ids
    try:
        open_items.require_vault(ctx)
        runs.ack(ctx, ids)
    except (OpenItemError, RunError) as exc:
        _fail(str(exc))
    logger.log(vault=ctx.vault, subcommand="run", message=f"ack {' '.join(ids)}")
    for run_id in ids:
        print(f"{run_id}: acked")
