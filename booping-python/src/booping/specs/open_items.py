"""Open items — one file per specs-to-code gap under `{vault}/{core.specs.open_items.dir}`.

Numbering, the item scaffold, ADR confirmation extraction and the index live here;
`booping.commands.items` is the argparse shell over them. Status moves go through
the `open_item` machine of the `specs` playbook, never a direct `status:` write.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, cast

from markdown_it import MarkdownIt
from markdown_it.token import Token

from booping.commands.playbook_transition import (
    format_frontmatter_line,
    read_status,
    transition,
)
from booping.commands.scaffold import _plan  # pyright: ignore[reportPrivateUsage]
from booping.context import Context
from booping.context._yaml import parse_frontmatter_only, update_frontmatter
from booping.context.lifecycle import resolve_edges
from booping.context.playbook import StateMachine
from booping.context.scaffold import ScaffoldError, load
from booping.query import QueryError, as_dict, build_spec, cell, resolve_spec, run
from booping.rendering import build_source_env
from booping.specs.check import Finding
from booping.specs.records import Record, parse_filename
from booping.specs.site.markdown import slug

DIRECTIONS = ("code-to-spec", "spec-to-code", "conflict", "clarify")
SOURCES = ("manual", "adr", "mark", "check", "sync", "correction", "request", "backlog")
REQUEST_SOURCES = ("request", "backlog")
PLAYBOOK = "specs"
STATE = "open_item"
SCAFFOLD_PATH = "core.specs.open_items.scaffold"
INDEX_PATH = "core.specs.open_items.index"
TITLE_LIMIT = 100
ID_ATTEMPTS = 100

_ITEM_FILE = re.compile(r"OI-(\d+)\.md")
_ADR_REF = re.compile(r"adr/(\d{4})")
_SENTENCE_END = re.compile(r"[.!?](?=\s|$)")
_BULLET = re.compile(r"[-*]\s+")
_MARK = re.compile(r"\[(clarify|unknown)\]")
_WS = re.compile(r"\s+")


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


def listed_names(directory: Path) -> list[str]:
    return [p.name for p in directory.iterdir()] if directory.is_dir() else []


def create_item(
    directory: Path,
    render: Callable[[str], tuple[Path, str]],
    listing: Callable[[Path], Iterable[str]] = listed_names,
) -> Path:
    """Write the item *render* produces for the next free id. The listing only picks
    the starting id; the exclusive create is what claims it, so a racing writer that
    took the id first sends this one on to the next."""
    numbers = [int(m.group(1)) for name in listing(directory) if (m := _ITEM_FILE.fullmatch(name))]
    number = max(numbers, default=0) + 1
    for _ in range(ID_ATTEMPTS):
        path, content = render(f"OI-{number:04d}")
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError:
            number += 1
            continue
        return path
    raise OpenItemError(f"could not allocate an item id under {directory}")


def truncate(text: str, limit: int = TITLE_LIMIT) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def first_sentence(text: str) -> str:
    match = _SENTENCE_END.search(text)
    return (text[: match.start()] if match else text).strip()


def derived_title(text: str) -> str:
    """The title of a request item filed without one: its text's first sentence."""
    first = next((line for line in text.splitlines() if line.strip()), "")
    return truncate(first_sentence(first))


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
    direction: str | None,
    record: str | None,
    source: str,
    body: str | None,
    listing: Callable[[Path], Iterable[str]] = listed_names,
) -> Path:
    """Scaffold the next numbered item file through `core.specs.open_items.scaffold`."""
    directory = items_dir(ctx)
    env = build_source_env(context=ctx, config=ctx.config)
    globals_: dict[str, Any] = env.globals  # type: ignore[assignment]
    globals_.update(
        title=title,
        direction=direction,
        record=record,
        source=source,
        created_at=today(ctx),
        body=body,
    )

    def render(item_id: str) -> tuple[Path, str]:
        globals_["id"] = item_id
        try:
            writes = _plan(load(ctx.config, SCAFFOLD_PATH), directory, env)
        except ScaffoldError as exc:
            raise OpenItemError(str(exc)) from exc
        for write in writes:
            if write.content is None:
                write.path.mkdir(parents=True, exist_ok=True)
        item = next(w for w in writes if w.content is not None)
        return item.path, cast(str, item.content)

    return create_item(directory, render, listing)


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
        raise OpenItemError(f"{item_id} is {current}; it cannot move to {to}")
    report = [vault_relative(ctx, path)]
    if fields:
        update_frontmatter(path, dict(fields))
        report.append(format_frontmatter_line(fields))
    report += transition(
        PLAYBOOK, to, state=STATE, instance=item_id, workdir=str(require_vault(ctx))
    )
    return report


@dataclass(frozen=True)
class Candidate:
    """An item `scan` would file; `(source, record, title)` is its dedup key."""

    source: str
    record: str
    title: str


def record_ref(tier_root: Path, path: Path) -> str:
    """`{type}/{NNNN}` when *path* is a well-named record, else its tier-relative path."""
    parsed = parse_filename(path.name)
    if parsed is not None and path.parent.parent.resolve() == tier_root.resolve():
        return f"{path.parent.name}/{parsed[0]:04d}"
    try:
        return path.resolve().relative_to(tier_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _inline_text(children: list[Token]) -> str:
    return "".join(
        " " if c.type in ("softbreak", "hardbreak") else c.content
        for c in children
        if c.type in ("text", "code_inline", "softbreak", "hardbreak")
    )


def _marks_in(children: list[Token]) -> list[tuple[str, str]]:
    """`(kind, title)` of the marks in one inline block that open it or open a
    sentence; code spans are separate tokens, so a quoted mark is never one."""
    marks: list[tuple[str, str]] = []
    for index, child in enumerate(children):
        if child.type != "text":
            continue
        for match in _MARK.finditer(child.content):
            before = (_inline_text(children[:index]) + child.content[: match.start()]).rstrip()
            if before and before[-1] not in ".!?":
                continue
            after = child.content[match.end() :] + _inline_text(children[index + 1 :])
            title = truncate(first_sentence(_WS.sub(" ", after).strip()))
            marks.append((match.group(1), title))
    return marks


@dataclass(frozen=True)
class Mark:
    """One `[clarify]`/`[unknown]` mark: its kind, the anchored record ref `scan`
    files it under, and its sentence."""

    kind: str
    record: str
    text: str


def marks(records: list[Record], tier_root: Path) -> list[Mark]:
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    found: list[Mark] = []
    for record in records:
        ref = record_ref(tier_root, record.path)
        heading: str | None = None
        tokens = md.parse(record.body)
        for index, token in enumerate(tokens):
            if token.type != "inline":
                continue
            children = token.children or []
            if index > 0 and tokens[index - 1].type == "heading_open":
                heading = slug(_inline_text(children))
                continue
            anchored = f"{ref}#{heading}" if heading else ref
            found += [Mark(kind, anchored, title) for kind, title in _marks_in(children)]
    return found


def mark_candidates(records: list[Record], tier_root: Path) -> list[Candidate]:
    return [Candidate("mark", m.record, m.text) for m in marks(records, tier_root)]


def finding_candidates(findings: list[Finding], tier_root: Path) -> list[Candidate]:
    return [
        Candidate("check", record_ref(tier_root, f.path), truncate(f"{f.check}: {f.message}"))
        for f in findings
    ]


def _tracked(ctx: Context) -> set[Candidate]:
    directory = items_dir(ctx)
    if not directory.is_dir():
        return set()
    keys: set[Candidate] = set()
    for path in sorted(directory.glob("OI-*.md")):
        fm = parse_frontmatter_only(path)
        keys.add(Candidate(str(fm.get("source")), str(fm.get("record")), str(fm.get("title"))))
    return keys


def scan(ctx: Context, candidates: list[Candidate]) -> tuple[list[Path], int]:
    """File every candidate not yet tracked by an item of any status; returns the
    created paths and the count already tracked."""
    tracked = _tracked(ctx)
    created: list[Path] = []
    skipped = 0
    for candidate in candidates:
        if candidate in tracked:
            skipped += 1
            continue
        created.append(
            write_item(
                ctx,
                title=candidate.title,
                direction="clarify",
                record=candidate.record,
                source=candidate.source,
                body=None,
            )
        )
        tracked.add(candidate)
    return created, skipped
