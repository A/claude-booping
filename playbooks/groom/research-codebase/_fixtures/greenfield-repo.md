# Input — tallyd (local-first CLI time tracker)

Intake is confirmed: the framing below is the one the user signed off on, scope questions
answered and boundaries agreed. Map the blast radius of this work in the attached repository.

The repository sits on disk in the current working directory, together with the run workdir —
the plan directory `plans/{slug}/`, holding the run's `index.md` and its `plan.md`. None of it
is inlined here and none of it is summarised: read what the work touches before writing
anything, and follow the references out of the files you are pointed at first.

## Context files

<file path="plans/20260731-remote-entry-sync/index.md">
---
status: researching
---
# Push tracked entries to the team API

## Framing

### Request

> tallyd has been mine alone so far — everything lands in a local file and stays there. The team
> now runs a hosted timesheet service, and I want `tallyd sync` to push my finished entries to
> its API so I stop re-typing them into the web form at the end of the week.

### Restated problem

Every entry tallyd records lives only on the machine that recorded it. The team's hosted service
is the system of record for billing, so the same hours are entered twice — once by the tool,
once by hand. The work is to give tallyd a way to send finished entries to that service over the
network, on demand, and to know afterwards which entries have already gone so a second run does
not send them again.

### Task type

`feature` — a new user-facing capability with its own command, its own configuration and its own
failure modes. Not a bug (nothing recorded is wrong today) and not a refactoring (the tool gains
behaviour it does not have).

### Scope boundaries

**In scope**

- a command that sends finished entries to the configured service
- the configuration the command needs to reach that service, and where the credential for it
  comes from
- knowing afterwards which entries were already sent, so a repeated run is safe
- the failure story: an unreachable service, a rejected entry, a half-finished run

**Out of scope**

- the pull direction — the service never writes back into the local store; this is push-only
- the reporting commands and their output format, which stay exactly as they are

### Web research

Not requested — the request asks for no deep web research, and the user asked for none when the scope questions came back.

### Scope challenge

- [x] Should a partially failed push leave the successful entries marked as sent, or roll the
      whole run back? — answered: keep the successful ones marked; a retry must not re-send them.
- [x] Is a running (unfinished) entry ever pushed? — answered: no, only finished entries.
- [x] Any dependency or config surface you already know this must not pull in? — answered: no
      opinion yet, that is exactly the call I want the design to make.
</file>

<file path="CLAUDE.md">
# tallyd — project guide

A local-first command-line time tracker. `tallyd start` opens an entry, `tallyd stop` closes it,
`tallyd report` prints what the week looked like. Everything it knows lives in one file under
the user's data directory; the tool has never talked to anything outside the machine.

## Layout

- `src/tallyd/cli.py` — argument parsing and the command table. Every command is a function
  registered in `COMMANDS`; nothing is dispatched any other way.
- `src/tallyd/storage.py` — the only module that touches the entry store. Nothing else opens
  that file, reads it or writes it.
- `src/tallyd/config.py` — settings, read once at startup from a TOML file.
- `src/tallyd/errors.py` — the error hierarchy. Every failure the user can cause is a
  `TallydError` subclass carrying the exit code the CLI returns.
- `src/tallyd/report.py` — the formatters behind `tallyd report`.
- `tests/` — pytest, one module per source module.

## Conventions

- **Standard library only at runtime.** `pyproject.toml` has an empty `dependencies` list and it
  is meant to stay that way: tallyd is installed with `uv tool install` on machines nobody
  administers, and every runtime dependency is a thing that can fail to install there. Dev tools
  (ruff, pytest) are the only exception and live in the dev group.
- **All persistence goes through `storage.py`.** A module that needs entries asks for them; it
  never opens the store itself. This is what keeps the on-disk format changeable.
- **Failures are `TallydError` subclasses.** Raise one with a message written for the user; the
  CLI's top-level handler prints it and exits with the code the class carries. Never print an
  error and return, and never let a raw exception reach the top level.
- **Tests are hermetic.** No network, no clock reads outside a fixture, no writes outside
  `tmp_path`. A test that cannot be run on a plane is a broken test.
- **Commands are registered, not discovered.** Adding a command means adding a function and an
  entry in `COMMANDS` — there is no plugin loader and no naming convention that auto-registers.

## Commands

- `just lint` — ruff check + format.
- `just test` — pytest.
</file>

<file path="pyproject.toml">
[project]
name = "tallyd"
version = "0.4.1"
requires-python = ">=3.12"
description = "Local-first command-line time tracker"
dependencies = []

[project.scripts]
tallyd = "tallyd.cli:main"

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.6"]

[tool.ruff]
line-length = 88

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
</file>

<file path="src/tallyd/cli.py">
from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from tallyd import report, storage
from tallyd.config import Config, load_config
from tallyd.errors import TallydError

Command = Callable[[argparse.Namespace, Config], None]


def cmd_start(args: argparse.Namespace, config: Config) -> None:
    storage.open_entry(config, project=args.project, note=args.note)


def cmd_stop(args: argparse.Namespace, config: Config) -> None:
    storage.close_open_entry(config)


def cmd_report(args: argparse.Namespace, config: Config) -> None:
    entries = storage.read_entries(config)
    sys.stdout.write(report.week(entries, since=args.since))


COMMANDS: dict[str, Command] = {
    "start": cmd_start,
    "stop": cmd_stop,
    "report": cmd_report,
}


def main() -> None:
    parser = argparse.ArgumentParser(prog="tallyd")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("project")
    p_start.add_argument("--note", default="")
    sub.add_parser("stop")
    p_report = sub.add_parser("report")
    p_report.add_argument("--since", default="monday")

    args = parser.parse_args()
    config = load_config()
    try:
        COMMANDS[args.command](args, config)
    except TallydError as exc:
        print(f"tallyd: {exc}", file=sys.stderr)
        raise SystemExit(exc.exit_code) from exc
</file>

<file path="src/tallyd/storage.py">
from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from tallyd.config import Config
from tallyd.errors import NoOpenEntry, StoreCorrupt


@dataclass(frozen=True)
class Entry:
    id: str
    project: str
    note: str
    started: str
    stopped: str | None

    @property
    def finished(self) -> bool:
        return self.stopped is not None


def store_path(config: Config) -> Path:
    return config.data_dir / "entries.jsonl"


def read_entries(config: Config) -> list[Entry]:
    """Read the whole store. The file is append-only: one JSON object per line, and a
    later line for the same id supersedes an earlier one."""
    path = store_path(config)
    if not path.exists():
        return []
    latest: dict[str, Entry] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            latest[json.loads(line)["id"]] = Entry(**json.loads(line))
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise StoreCorrupt(f"{path}:{line_no} is not a readable entry") from exc
    return list(latest.values())


def append(config: Config, entry: Entry) -> None:
    with store_path(config).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(entry)) + "\n")


def open_entry(config: Config, *, project: str, note: str) -> Entry:
    entry = Entry(
        id=_mint_id(), project=project, note=note,
        started=datetime.now(UTC).isoformat(), stopped=None,
    )
    append(config, entry)
    return entry


def close_open_entry(config: Config) -> Entry:
    for entry in reversed(read_entries(config)):
        if not entry.finished:
            closed = Entry(**{**asdict(entry), "stopped": datetime.now(UTC).isoformat()})
            append(config, closed)
            return closed
    raise NoOpenEntry("no entry is running")


def finished_entries(config: Config) -> Iterator[Entry]:
    yield from (e for e in read_entries(config) if e.finished)
</file>

<file path="src/tallyd/config.py">
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from tallyd.errors import ConfigInvalid

CONFIG_NAME = "tallyd.toml"


@dataclass(frozen=True)
class Config:
    data_dir: Path
    week_starts_on: str
    round_to_minutes: int


def config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / "tallyd" / CONFIG_NAME


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    root = Path(base) if base else Path.home() / ".local" / "share"
    return root / "tallyd"


def load_config() -> Config:
    """Read the TOML config, filling defaults for anything absent. The file is plain text
    the user edits by hand; it is the only configuration surface tallyd has."""
    path = config_path()
    raw: dict[str, object] = {}
    if path.exists():
        try:
            raw = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            raise ConfigInvalid(f"{path} is not valid TOML") from exc

    directory = raw.get("data_dir")
    return Config(
        data_dir=Path(str(directory)).expanduser() if directory else data_dir(),
        week_starts_on=str(raw.get("week_starts_on", "monday")),
        round_to_minutes=int(raw.get("round_to_minutes", 1)),
    )
</file>

<file path="src/tallyd/errors.py">
from __future__ import annotations


class TallydError(Exception):
    """Base for every failure the user can cause. Carries the CLI's exit code."""

    exit_code = 1


class NoOpenEntry(TallydError):
    exit_code = 2


class StoreCorrupt(TallydError):
    exit_code = 3


class ConfigInvalid(TallydError):
    exit_code = 4
</file>

<file path="src/tallyd/report.py">
from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from tallyd.storage import Entry


def week(entries: list[Entry], *, since: str) -> str:
    """Group finished entries by project and print a fixed-width table."""
    totals: dict[str, float] = defaultdict(float)
    for entry in entries:
        if not entry.finished:
            continue
        started = datetime.fromisoformat(entry.started)
        stopped = datetime.fromisoformat(entry.stopped or entry.started)
        totals[entry.project] += (stopped - started).total_seconds() / 3600

    width = max((len(p) for p in totals), default=7)
    lines = [f"{project.ljust(width)}  {hours:5.2f}h" for project, hours in sorted(totals.items())]
    lines.append(f"{'total'.ljust(width)}  {sum(totals.values()):5.2f}h")
    return "\n".join(lines) + "\n"
</file>

<file path="tests/test_storage.py">
from __future__ import annotations

import pytest

from tallyd import storage
from tallyd.config import Config
from tallyd.errors import NoOpenEntry, StoreCorrupt


@pytest.fixture
def config(tmp_path) -> Config:
    return Config(data_dir=tmp_path, week_starts_on="monday", round_to_minutes=1)


def test_a_later_line_supersedes_an_earlier_one(config):
    opened = storage.open_entry(config, project="atlas", note="")
    closed = storage.close_open_entry(config)
    entries = storage.read_entries(config)
    assert len(entries) == 1
    assert entries[0].id == opened.id
    assert entries[0].stopped == closed.stopped


def test_close_without_an_open_entry_raises(config):
    with pytest.raises(NoOpenEntry):
        storage.close_open_entry(config)


def test_a_broken_line_names_its_line_number(config):
    storage.store_path(config).write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(StoreCorrupt, match=r":1 "):
        storage.read_entries(config)
</file>

<file path="justfile">
default:
    @just --list

lint:
    uv run ruff check src tests
    uv run ruff format --check src tests

test:
    uv run pytest -q

install:
    uv tool install --force .
</file>
