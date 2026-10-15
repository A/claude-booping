"""Defaults — what a run decided without the user, logged to `defaults.md` beside
its artefact.

`booping.commands.defaults` is the argparse shell over this module. Every check
runs before the single write, so an error never leaves a partial entry.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from booping.context import Context
from booping.rendering import build_source_env

SIDECAR = "defaults.md"
HEADING = "# Defaults"

_ENTRY = re.compile(r"^## D(\d+) ", re.MULTILINE)


class DefaultsError(Exception):
    pass


@dataclass(frozen=True)
class Added:
    sidecar: str
    number: int


def normalise(text: str) -> str:
    return " ".join(text.split())


def next_number(text: str) -> int:
    return max((int(n) for n in _ENTRY.findall(text)), default=0) + 1


def _now(ctx: Context) -> str:
    env = build_source_env(context=ctx, config=ctx.config)
    return env.from_string("{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}").render().strip()


def render_entry(
    *, number: int, step: str, when: str, asked: str, default: str, why: str | None, artifact: str
) -> str:
    lines = [
        f"## D{number} — {step} — {when}",
        "",
        f"**Asked:** {asked}",
        "",
        f"**Default:** {default}",
        "",
        f"**Why:** {why if why else 'not stated'}",
        "",
        f"**Artifact:** [{PurePosixPath(artifact).name}]({artifact})",
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
    sidecar_rel = target_rel.parent / SIDECAR
    sidecar: Path = vault / sidecar_rel
    existing = sidecar.read_text(encoding="utf-8") if sidecar.is_file() else f"{HEADING}\n"
    number = next_number(existing)
    entry = render_entry(
        number=number,
        step=step,
        when=_now(ctx),
        asked=asked,
        default=default,
        why=why,
        artifact=PurePosixPath(os.path.relpath(target_rel, sidecar_rel.parent)).as_posix(),
    )
    sidecar.write_text(existing.rstrip("\n") + "\n\n" + entry, encoding="utf-8")
    return Added(sidecar=sidecar_rel.as_posix(), number=number)
