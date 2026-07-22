from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter


def _warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr)


class Step(BaseModel):
    name: str
    summary: str = ""
    agent: str | None = None
    model: str | None = None
    effort: str | None = None
    review_gate: str | None = None
    body: str = ""
    path: Path


class Playbook(BaseModel):
    name: str
    title: str
    summary: str = ""
    trigger: str = ""
    scope: Literal["global", "local"]
    path: Path
    steps: list[Step] = []

    @classmethod
    def load_all(cls, vault: Path | None, home_dir: Path) -> list[Playbook]:
        """Discover playbooks from the global root (`home_dir/_playbooks`) and, when a
        vault is attached, the local root (`vault/_playbooks`). Local shadows global on
        name collision. `_`-prefixed entries (e.g. `_lib`) are skipped. Missing roots
        yield nothing; missing/partial frontmatter degrades with a warning, not a crash.
        """
        result: list[Playbook] = []
        by_name: dict[str, int] = {}

        for scope, root in (
            ("global", home_dir / "_playbooks"),
            ("local", vault / "_playbooks" if vault is not None else None),
        ):
            if root is None or not root.is_dir():
                continue
            for pb_dir in sorted(root.iterdir()):
                if not pb_dir.is_dir() or pb_dir.name.startswith("_"):
                    continue
                pb = _load_one(pb_dir, scope)  # type: ignore[arg-type]
                if pb is None:
                    continue
                if pb.name in by_name:
                    result[by_name[pb.name]] = pb
                else:
                    by_name[pb.name] = len(result)
                    result.append(pb)

        return result


def _load_one(pb_dir: Path, scope: Literal["global", "local"]) -> Playbook | None:
    manifest = pb_dir / "playbook.md"
    if not manifest.is_file():
        _warn(f"playbook {pb_dir.name}: no playbook.md, skipping")
        return None

    fm, _ = parse_frontmatter(manifest)
    name = str(fm.get("name", pb_dir.name))
    title = str(fm.get("title", name))
    summary = str(fm.get("summary", ""))
    trigger = str(fm.get("trigger", ""))

    steps_raw = fm.get("steps")
    step_names: list[str] = []
    if isinstance(steps_raw, list):
        step_names = [str(s) for s in steps_raw]  # type: ignore[misc]
    elif steps_raw is not None:
        _warn(f"playbook {name}: `steps` is not a list, ignoring")

    steps: list[Step] = []
    for step_name in step_names:
        step = _load_step(pb_dir, name, step_name)
        if step is not None:
            steps.append(step)

    return Playbook(
        name=name,
        title=title,
        summary=summary,
        trigger=trigger,
        scope=scope,
        path=manifest,
        steps=steps,
    )


def _load_step(pb_dir: Path, pb_name: str, step_name: str) -> Step | None:
    step_path = pb_dir / "steps" / f"{step_name}.md"
    if not step_path.is_file():
        _warn(f"playbook {pb_name}: step `{step_name}` file missing, skipping")
        return None
    fm, body = parse_frontmatter(step_path)
    return Step(
        name=str(fm.get("name", step_name)),
        summary=str(fm.get("summary", "")),
        agent=_opt_str(fm.get("agent")),
        model=_opt_str(fm.get("model")),
        effort=_opt_str(fm.get("effort")),
        review_gate=_opt_str(fm.get("review_gate")),
        body=body,
        path=step_path,
    )


def _opt_str(val: Any) -> str | None:
    return str(val) if val is not None else None
