from __future__ import annotations

import shutil
from pathlib import Path

from booping.specs.site.model import SiteRoot

MARKER = ".booping-site"
MARKER_TEXT = "booping specs site\n"


class SiteError(Exception):
    pass


def _check(out: Path, roots: list[SiteRoot]) -> None:
    if out.exists() and not out.is_dir():
        raise SiteError(f"out path {out} is a file")
    resolved = out.resolve()
    for root in roots:
        if resolved.is_relative_to(root.path.resolve()):
            raise SiteError(f"out path {out} is inside root {root.name} ({root.path})")
        if root.path.resolve().is_relative_to(resolved):
            raise SiteError(f"out path {out} contains root {root.name} ({root.path})")
    if out.is_dir() and any(out.iterdir()) and not (out / MARKER).is_file():
        raise SiteError(f"out path {out} is not empty and has no {MARKER} marker")


def write_site(files: dict[str, str | bytes], out: Path, roots: list[SiteRoot]) -> None:
    _check(out, roots)
    if out.is_dir():
        # The marker stays through the clear, so a run that dies here is still clearable.
        for child in out.iterdir():
            if child.name == MARKER:
                continue
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        out.mkdir(parents=True)
    (out / MARKER).write_text(MARKER_TEXT, newline="\n")
    for path in sorted(files):
        target = out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        content = files[path]
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, newline="\n")
