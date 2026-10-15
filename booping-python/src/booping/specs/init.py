from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from booping.specs.tiers import Tier

PROJECT_README = (
    "# specs/\n"
    "\n"
    "This project's specs tier: values, rules, ADRs and the other typed records,"
    " in booping's specs format — the guide is `src/specs/README.md` in the booping plugin."
    " Check with `booping specs check --tier project`.\n"
)

GLOBAL_README = (
    "# _specs/ — global tier (namespace `{namespace}`)\n"
    "\n"
    "One person's values and rules for every project, in booping's specs format"
    " — the guide is `src/specs/README.md` in the booping plugin."
    " Referenced from a project as `{namespace}:rule/NNNN`."
    " Check with `booping specs check --tier global`.\n"
)


class InitError(Exception):
    pass


@dataclass(frozen=True)
class Action:
    kind: Literal["dir", "file", "link"]
    path: Path
    content: str = ""
    target: Path | None = None


def _readme(tier: Tier) -> str:
    if tier.name == "global":
        return GLOBAL_README.format(namespace=tier.namespace)
    return PROJECT_README


def _missing_dirs(path: Path) -> list[Path]:
    missing: list[Path] = []
    while not path.exists():
        missing.append(path)
        path = path.parent
    return list(reversed(missing))


def plan(tier: Tier, *, repo: Path | None, vault: Path | None) -> list[Action]:
    """Every change `init` would make, in order; raises before anything is written."""
    if tier.name == "core":
        raise InitError("the core tier ships with the plugin; only global and project are created")
    if tier.vault_rooted:
        return []
    root = tier.root.absolute()
    if root.exists() and not root.is_dir():
        raise InitError(f"{root} exists and is not a directory")

    link: Action | None = None
    if tier.name == "project" and repo is not None and vault is not None:
        vault_specs = vault.absolute() / "specs"
        if not root.resolve().is_relative_to(vault.resolve()):
            if vault_specs.is_symlink():
                if vault_specs.resolve() != root.resolve():
                    raise InitError(f"{vault_specs} is a symlink not pointing to {root}")
            elif vault_specs.exists():
                raise InitError(f"{vault_specs} exists and is not a symlink to {root}")
            else:
                link = Action("link", vault_specs, target=root)

    actions = [Action("dir", d) for d in _missing_dirs(root)]
    readme = root / "README.md"
    if not readme.exists():
        actions.append(Action("file", readme, content=_readme(tier)))
    if link is not None:
        actions += [Action("dir", d) for d in _missing_dirs(link.path.parent)]
        actions.append(link)
    return actions


def apply(actions: list[Action]) -> list[str]:
    lines: list[str] = []
    for action in actions:
        if action.kind == "dir":
            action.path.mkdir()
            lines.append(f"created dir {action.path}")
        elif action.kind == "file":
            action.path.write_text(action.content, encoding="utf-8")
            lines.append(f"created file {action.path}")
        else:
            assert action.target is not None
            action.path.symlink_to(action.target, target_is_directory=True)
            lines.append(f"linked {action.path} -> {action.target}")
    return lines
