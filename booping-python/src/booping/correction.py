"""Corrections — the user's corrections of a run, logged to `corrections.md` beside
its artefact.

`booping.commands.correction` is the argparse shell over this module. Every check
runs before the single write, so an error never leaves a partial entry.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import cast

from booping.context import Context
from booping.context._yaml import parse_frontmatter_only
from booping.rendering import get_plugin_root
from booping.session_stats import locate_transcript, read_records, user_text
from booping.sidecar import Sidecar, normalise, now, relative
from booping.specs import open_items
from booping.specs.open_items import OpenItemError
from booping.specs.tiers import types

SIDECAR = "corrections.md"
HEADING = "# Corrections"
PREFIX = "R"
SESSION_ENV = "CLAUDE_CODE_SESSION_ID"

_RECORD = re.compile(r"(?:[^\s:/]+:)?([^\s:/]+)/\d{4}")


class CorrectionError(Exception):
    pass


@dataclass(frozen=True)
class Added:
    sidecar: str
    number: int
    item: str | None
    warnings: list[str]


def require_vault(ctx: Context) -> Path:
    if ctx.vault is None:
        raise CorrectionError("no booping project here; corrections live in its vault")
    return ctx.vault


def check_record(ctx: Context, ref: str) -> None:
    """Shape only — a cross-tier ref may not resolve on this machine."""
    specs_format = str(ctx.config.get("core", {}).get("specs", {}).get("format"))
    match = _RECORD.fullmatch(ref)
    if match is None or match.group(1) not in types(get_plugin_root() / specs_format):
        raise CorrectionError(f"--record must be [namespace:]type/NNNN: {ref}")


def resolve_session(flag: str | None) -> str | None:
    session = (flag or os.environ.get(SESSION_ENV, "")).strip()
    return session or None


def find_message(transcript: Path, said: str) -> tuple[int, str] | None:
    """Line number and uuid of the last user message whose text holds *said*."""
    needle = normalise(said)
    found: tuple[int, str] | None = None
    for number, record in read_records(transcript):
        if record is None:
            continue
        text = user_text(record)
        if text is not None and needle in normalise(text):
            found = (number, str(record.get("uuid") or ""))
    return found


def dialogue(session: str | None, said: str, projects_root: Path) -> tuple[str, str | None]:
    """The entry's `**Dialogue:**` value and the warning to print, if any."""
    if session is None:
        return "not found — no session id", "warning: no session id; dialogue not linked"
    transcript = locate_transcript(session, projects_root)
    if transcript is None:
        return (
            f"not found — no transcript for {session}",
            f"warning: no transcript for {session}; dialogue not linked",
        )
    found = find_message(transcript, said)
    if found is None:
        raise CorrectionError(f"--said is not verbatim in any user message of session {session}")
    number, uuid = found
    return f"`{session}` line {number} · `{uuid}`", None


def render_entry(
    log: Sidecar,
    *,
    step: str,
    when: str,
    did: str,
    said: str,
    why: str | None,
    dialogue: str,
    record: str | None,
    target_rel: PurePosixPath,
) -> str:
    quote = "\n".join(f"> {line}" if line else ">" for line in said.splitlines())
    lines = [
        log.header(step, when),
        "",
        f"**Did:** {did}",
        "",
        "**Said:**",
        "",
        quote,
        "",
        f"**Why:** {why if why else 'not stated'}",
        "",
        f"**Dialogue:** {dialogue}",
        "",
        *([record, ""] if record else []),
        log.artifact_line(target_rel),
    ]
    return "\n".join(lines) + "\n"


def add(
    ctx: Context,
    *,
    target: str,
    step: str,
    did: str,
    said: str,
    why: str | None,
    record: str | None,
    session: str | None,
    projects_root: Path,
) -> Added:
    vault = require_vault(ctx)
    target_rel = PurePosixPath(target)
    if not (vault / target_rel).is_file():
        raise CorrectionError(f"target not found: {target}")
    if not said.strip():
        raise CorrectionError("--said must not be empty")
    if record is not None:
        check_record(ctx, record)
    linked, warning = dialogue(session, said, projects_root)

    log = Sidecar.open(vault, target_rel, name=SIDECAR, heading=HEADING, prefix=PREFIX)
    sidecar_rel = log.rel
    number = log.number
    when = now(ctx)
    item_rel: PurePosixPath | None = None
    record_line: str | None = None
    if record is not None:
        items_rel = PurePosixPath(open_items.vault_relative(ctx, open_items.items_dir(ctx)))
        ref = f"{sidecar_rel.as_posix()}#R{number}"
        back = f"{relative(sidecar_rel, items_rel)}#R{number}"
        try:
            item = open_items.write_item(
                ctx,
                title=open_items.truncate(normalise(f"{step}: {said}")),
                direction="conflict",
                record=record,
                source="correction",
                body=f"Logged as [{ref}]({back})",
            )
        except OpenItemError as exc:
            raise CorrectionError(str(exc)) from exc
        item_rel = PurePosixPath(open_items.vault_relative(ctx, item))
        link = relative(item_rel, sidecar_rel.parent)
        record_line = f"**Record:** {record} → [{item_rel.stem}]({link})"
    entry = render_entry(
        log,
        step=step,
        when=when,
        did=did,
        said=said,
        why=why,
        dialogue=linked,
        record=record_line,
        target_rel=target_rel,
    )
    log.append(entry)
    return Added(
        sidecar=sidecar_rel.as_posix(),
        number=number,
        item=item_rel.as_posix() if item_rel else None,
        warnings=[warning] if warning else [],
    )


def _sidecars(vault: Path, plan_rel: PurePosixPath) -> list[PurePosixPath]:
    """The plan's own sidecar, then one per distinct `code_reviews:` directory."""
    raw = parse_frontmatter_only(vault / plan_rel).get("code_reviews")
    reviews = [str(r) for r in cast("list[object]", raw) if r] if isinstance(raw, list) else []
    dirs = [plan_rel.parent, *(PurePosixPath(r).parent for r in reviews)]
    return [d / SIDECAR for d in dict.fromkeys(dirs)]


def _below_h1(text: str) -> str:
    lines = text.splitlines()
    start = next((i + 1 for i, line in enumerate(lines) if line.startswith("# ")), 0)
    return "\n".join(lines[start:]).strip("\n")


def feed(ctx: Context, plan: str) -> str:
    vault = require_vault(ctx)
    plan_rel = PurePosixPath(plan)
    if not (vault / plan_rel).is_file():
        raise CorrectionError(f"plan not found: {plan}")
    blocks = [
        f"# {sidecar.as_posix()}\n\n{_below_h1((vault / sidecar).read_text(encoding='utf-8'))}\n"
        for sidecar in _sidecars(vault, plan_rel)
        if (vault / sidecar).is_file()
    ]
    return "\n".join(blocks) if blocks else f"no corrections for {plan}\n"
