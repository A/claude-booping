"""Numbered-entry sidecars — the markdown log a run keeps beside its artefact.

`corrections.md` (`R{n}`) and `defaults.md` (`D{n}`) share one shape: an H1, then one
`## {prefix}{n} — {step} — {when}` entry per write, each ending in a link back to the
artefact. This module owns that shape; the callers own their fields and checks.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from booping.context import Context
from booping.rendering import build_source_env


def normalise(text: str) -> str:
    return " ".join(text.split())


def relative(path: PurePosixPath, start: PurePosixPath) -> str:
    return PurePosixPath(os.path.relpath(path, start)).as_posix()


def now(ctx: Context) -> str:
    env = build_source_env(context=ctx, config=ctx.config)
    return env.from_string("{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}").render().strip()


def next_number(text: str, prefix: str) -> int:
    entry = re.compile(rf"^## {re.escape(prefix)}(\d+) ", re.MULTILINE)
    return max((int(n) for n in entry.findall(text)), default=0) + 1


@dataclass(frozen=True)
class Sidecar:
    """One sidecar opened for an append: its next number is fixed before the write."""

    vault: Path
    rel: PurePosixPath
    prefix: str
    existing: str
    number: int

    @classmethod
    def open(
        cls, vault: Path, target_rel: PurePosixPath, *, name: str, heading: str, prefix: str
    ) -> Sidecar:
        rel = target_rel.parent / name
        path = vault / rel
        existing = path.read_text(encoding="utf-8") if path.is_file() else f"{heading}\n"
        return cls(vault, rel, prefix, existing, next_number(existing, prefix))

    def header(self, step: str, when: str) -> str:
        return f"## {self.prefix}{self.number} — {step} — {when}"

    def artifact_line(self, target_rel: PurePosixPath) -> str:
        link = relative(target_rel, self.rel.parent)
        return f"**Artifact:** [{PurePosixPath(link).name}]({link})"

    def append(self, entry: str) -> None:
        text = self.existing.rstrip("\n") + "\n\n" + entry
        (self.vault / self.rel).write_text(text, encoding="utf-8")
