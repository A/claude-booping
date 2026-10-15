"""Open items — one file per specs-to-code gap under `{vault}/{core.specs.open_items.dir}`.

Numbering, the item scaffold, ADR confirmation extraction and the index live here;
`booping.commands.specs` is the argparse shell over them. Status moves go through
the `open_item` machine of the `specs` playbook, never a direct `status:` write.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Any, cast

from booping.commands.playbook_transition import (
    format_frontmatter_line,
    read_status,
    transition,
)
from booping.commands.scaffold import _plan  # pyright: ignore[reportPrivateUsage]
from booping.context import Context
from booping.context._yaml import update_frontmatter
from booping.context.lifecycle import resolve_edges
from booping.context.playbook import StateMachine
from booping.context.scaffold import ScaffoldError, load
from booping.query import QueryError, as_dict, build_spec, cell, resolve_spec, run
from booping.rendering import build_source_env
from booping.specs.records import Record

DIRECTIONS = ("code-to-spec", "spec-to-code", "conflict", "clarify")
SOURCES = ("manual", "adr", "mark", "check", "sync")
PLAYBOOK = "specs"
STATE = "open_item"
SCAFFOLD_PATH = "core.specs.open_items.scaffold"
INDEX_PATH = "core.specs.open_items.index"
TITLE_LIMIT = 100

_ITEM_FILE = re.compile(r"OI-(\d+)\.md")
_ADR_REF = re.compile(r"adr/(\d{4})")
_SENTENCE_END = re.compile(r"[.!?](?=\s|$)")
_BULLET = re.compile(r"[-*]\s+")


class OpenItemError(Exception):
    pass


def _settings(ctx: Context) -> dict[str, Any]:
    return ctx.config.get("core", {}).get("specs", {}).get("open_items", {})


def require_vault(ctx: Context) -> Path:
    if ctx.vault is None:
        raise OpenItemError("no booping project here; open items live in its vault")
    return ctx.vault


def items_dir(ctx: Context) -> Path:
    return require_vault(ctx) / str(_settings(ctx).get("dir"))


def item_path(ctx: Context, item_id: str) -> Path:
    return items_dir(ctx) / f"{item_id}.md"


def vault_relative(ctx: Context, path: Path) -> str:
    return path.relative_to(require_vault(ctx)).as_posix()


def next_id(directory: Path) -> str:
    numbers = (
        [int(m.group(1)) for p in directory.iterdir() if (m := _ITEM_FILE.fullmatch(p.name))]
        if directory.is_dir()
        else []
    )
    return f"OI-{max(numbers, default=0) + 1:04d}"


def truncate(text: str, limit: int = TITLE_LIMIT) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def first_sentence(text: str) -> str:
    match = _SENTENCE_END.search(text)
    return (text[: match.start()] if match else text).strip()


def _section(body: str, heading: str) -> list[str]:
    lines = body.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == heading), None)
    if start is None:
        return []
    section: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        section.append(line)
    return section


def _bullets(lines: list[str]) -> list[str]:
    """Top-level bullets, each joined with its indented continuation lines."""
    bullets: list[list[str]] = []
    open_bullet = False
    for line in lines:
        bullet = _BULLET.match(line)
        if bullet is not None:
            bullets.append([line[bullet.end() :].strip()])
            open_bullet = True
        elif open_bullet and line.startswith((" ", "\t")) and line.strip():
            bullets[-1].append(line.strip())
        else:
            open_bullet = False
    return [" ".join(parts) for parts in bullets]


def confirmation_title(adr: Record) -> str | None:
    for bullet in _bullets(_section(adr.body, "## Consequences")):
        if bullet.startswith("Confirmation:"):
            return truncate(first_sentence(bullet.removeprefix("Confirmation:").strip()))
    return None


def find_adr(records: list[Record], ref: str) -> Record:
    match = _ADR_REF.fullmatch(ref)
    number = int(match.group(1)) if match else None
    adr = next((r for r in records if r.type == "adr" and r.number == number), None)
    if adr is None:
        raise OpenItemError(f"unknown ADR `{ref}` in the project tier")
    return adr


def is_adr_ref(ref: str) -> bool:
    return _ADR_REF.fullmatch(ref) is not None


def check_choice(flag: str, value: str, allowed: tuple[str, ...]) -> None:
    if value not in allowed:
        raise OpenItemError(f"{flag} `{value}` is not one of: {', '.join(allowed)}")


def today(ctx: Context) -> str:
    env = build_source_env(context=ctx, config=ctx.config)
    return env.from_string("{{ macro('core.macros.date', '+%Y-%m-%d') }}").render().strip()


def write_item(
    ctx: Context,
    *,
    title: str,
    direction: str,
    record: str | None,
    source: str,
    body: str | None,
) -> Path:
    """Scaffold the next numbered item file through `core.specs.open_items.scaffold`."""
    directory = items_dir(ctx)
    item_id = next_id(directory)
    env = build_source_env(context=ctx, config=ctx.config)
    globals_: dict[str, Any] = env.globals  # type: ignore[assignment]
    globals_.update(
        id=item_id,
        title=title,
        direction=direction,
        record=record,
        source=source,
        created_at=today(ctx),
        body=body,
    )
    try:
        writes = _plan(load(ctx.config, SCAFFOLD_PATH), directory, env)
    except ScaffoldError as exc:
        raise OpenItemError(str(exc)) from exc
    for write in writes:
        if write.content is None:
            write.path.mkdir(parents=True, exist_ok=True)
        else:
            write.path.write_text(write.content, encoding="utf-8")
    return item_path(ctx, item_id)


def machine(ctx: Context) -> StateMachine:
    pb = next((p for p in ctx.playbooks if p.name == PLAYBOOK), None)
    if pb is None or STATE not in pb.states:
        raise OpenItemError(f"playbook `{PLAYBOOK}` declares no `{STATE}` machine")
    return pb.states[STATE]


def open_statuses(state: StateMachine) -> list[str]:
    """The machine's non-terminal statuses — the default `list` filter."""
    return [
        name
        for name, raw in state.statuses.items()
        if not (isinstance(raw, dict) and cast("dict[str, Any]", raw).get("terminal"))
    ]


def index_rows(ctx: Context, where: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Rows of `core.specs.open_items.index` narrowed by *where*, and its columns."""
    vault = require_vault(ctx)
    try:
        spec = build_spec(ctx.config, resolve_spec(ctx.config, INDEX_PATH), {"where": where})
    except QueryError as exc:
        raise OpenItemError(str(exc)) from exc
    rows = [as_dict(row) for row in run(spec, vault)]
    return rows, list(spec.columns or [])


def index_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    def text(value: Any) -> str:
        return cell(value) or "—"

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines += ["| " + " | ".join(text(row.get(col)) for col in columns) + " |" for row in rows]
    return "\n".join(lines)


def vault_path(ctx: Context, raw: str) -> str:
    """*raw* as a vault-relative posix path; an absolute path must lie inside the vault."""
    vault = require_vault(ctx)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        return PurePosixPath(raw).as_posix()
    try:
        return path.resolve().relative_to(vault.resolve()).as_posix()
    except ValueError as exc:
        raise OpenItemError(f"{raw} is outside the vault {vault}") from exc


def planned_for(ctx: Context, plan: str) -> list[str]:
    """Ids of the `planned` items whose `plan:` is *plan*, in index order."""
    rows, _ = index_rows(ctx, {"status": "planned", "plan": plan})
    return [str(row["id"]) for row in rows]


def move(ctx: Context, item_id: str, to: str, fields: dict[str, str] | None = None) -> list[str]:
    """Write *fields*, then move the item to *to* through the `open_item` machine.
    The edge is checked against the machine first so nothing is written for a move
    it refuses. Returns the item's path plus the engine's mutation report."""
    path = item_path(ctx, item_id)
    if not path.is_file():
        raise OpenItemError(f"unknown open item {item_id}")
    state = machine(ctx)
    current = read_status(path)
    allowed: set[str] = (
        {edge.to for edge in resolve_edges(current, state.raw)} if current else set()
    )
    if to not in allowed:
        if current == state.initial and to == "done":
            raise OpenItemError(f"{item_id} is open; plan it first or close it with --dropped")
        raise OpenItemError(f"{item_id} is {current}; it cannot move to {to}")
    report = [vault_relative(ctx, path)]
    if fields:
        update_frontmatter(path, dict(fields))
        report.append(format_frontmatter_line(fields))
    report += transition(
        PLAYBOOK, to, state=STATE, instance=item_id, workdir=str(require_vault(ctx))
    )
    return report
