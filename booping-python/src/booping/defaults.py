"""Defaults — what a run decided without the user, logged to `defaults.md` beside
its artefact.

`booping.commands.defaults` is the argparse shell over this module. Every check
runs before the single write, so an error never leaves a partial entry.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from booping import sidecar
from booping.context import Context
from booping.sidecar import Sidecar, normalise

SIDECAR = "defaults.md"
HEADING = "# Defaults"
PREFIX = "D"


class DefaultsError(Exception):
    pass


@dataclass(frozen=True)
class Added:
    sidecar: str
    number: int


def render_entry(
    log: Sidecar,
    *,
    step: str,
    when: str,
    asked: str,
    default: str,
    why: str | None,
    target_rel: PurePosixPath,
) -> str:
    lines = [
        log.header(step, when),
        "",
        f"**Asked:** {asked}",
        "",
        f"**Default:** {default}",
        "",
        f"**Why:** {why if why else 'not stated'}",
        "",
        log.artifact_line(target_rel),
    ]
    return "\n".join(lines) + "\n"


def add(
    ctx: Context,
    *,
    target: str,
    step: str,
    asked: str,
    default: str,
    why: str | None,
) -> Added:
    if ctx.vault is None:
        raise DefaultsError("no booping project here; defaults live in its vault")
    vault = ctx.vault.resolve()
    resolved = (vault / target).resolve()
    if not resolved.is_relative_to(vault):
        raise DefaultsError(f"target outside the vault: {target}")
    if not resolved.is_file():
        raise DefaultsError(f"target not found: {target}")
    asked = normalise(asked)
    default = normalise(default)
    if not asked:
        raise DefaultsError("--asked must not be empty")
    if not default:
        raise DefaultsError("--default must not be empty")
    why = normalise(why) if why is not None else None

    target_rel = PurePosixPath(resolved.relative_to(vault).as_posix())
    log = Sidecar.open(vault, target_rel, name=SIDECAR, heading=HEADING, prefix=PREFIX)
    entry = render_entry(
        log,
        step=step,
        when=sidecar.now(ctx),
        asked=asked,
        default=default,
        why=why,
        target_rel=target_rel,
    )
    log.append(entry)
    return Added(sidecar=log.rel.as_posix(), number=log.number)
