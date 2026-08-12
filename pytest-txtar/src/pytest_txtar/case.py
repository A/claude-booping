"""Case model: the spec a consumer supplies, and loading a case file into it."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from pytest_txtar import txtar


class CaseError(Exception):
    """A malformed case file."""


@dataclass(frozen=True)
class TxtarSpec:
    """What a consumer must state to run cases: the tool, the sandbox, the tokens.

    ``commands`` maps a command word appearing first on a ``cmd`` line to the
    binary it stands for. ``roots`` names the sandbox subdirectories a case may
    address under ``fixtures/`` and ``expected/``; the process runs in
    ``cwd_root``, and ``env`` maps an environment variable to the root it points
    at. ``tokens`` maps a root to the token its path is normalized to, defaulting
    to the upper-cased root in braces.
    """

    commands: Mapping[str, Path]
    roots: tuple[str, ...]
    cwd_root: str
    env: Mapping[str, str] = field(default_factory=dict[str, str])
    tokens: Mapping[str, str] | None = None

    @property
    def token_map(self) -> Mapping[str, str]:
        if self.tokens is not None:
            return self.tokens
        return {root: "{" + root.upper() + "}" for root in self.roots}


@dataclass
class Case:
    path: Path
    archive: txtar.Archive
    cmd: list[str]
    exit_code: int = 0
    stdout: str | None = None
    stderr: str | None = None
    fixtures: list[tuple[str, str]] = field(default_factory=list)
    expected: list[tuple[str, str]] = field(default_factory=list)


def load_case(path: Path, spec: TxtarSpec) -> Case:
    try:
        archive = txtar.parse(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise CaseError(str(exc)) from exc

    case = Case(path=path, archive=archive, cmd=[])
    seen_cmd = False
    for name, data in archive.files:
        if name == "cmd":
            case.cmd = [line for line in data.splitlines() if line.strip()]
            seen_cmd = True
        elif name == "exit":
            case.exit_code = parse_exit(data)
        elif name == "stdout":
            case.stdout = data
        elif name == "stderr":
            case.stderr = data
        elif name.startswith("fixtures/"):
            case.fixtures.append((check_tree_path(name, spec.roots), data))
        elif name.startswith("expected/"):
            case.expected.append((check_tree_path(name, spec.roots), data))
        else:
            raise CaseError(f"unknown section: {name}")

    if not seen_cmd:
        raise CaseError("missing section: cmd")
    if not case.cmd:
        raise CaseError("empty section: cmd")
    return case


def parse_exit(data: str) -> int:
    text = data.strip()
    try:
        return int(text)
    except ValueError as exc:
        raise CaseError(f"exit is not an integer: {text!r}") from exc


def check_tree_path(name: str, roots: tuple[str, ...]) -> str:
    prefix, _, rest = name.partition("/")
    root, _, relative = rest.partition("/")
    if root not in roots or not relative:
        listed = ", ".join(f"{root}/" for root in roots)
        raise CaseError(f"{prefix}/ path must start with one of {listed}: {name}")
    if ".." in Path(relative).parts or Path(relative).is_absolute():
        raise CaseError(f"{prefix}/ path escapes its root: {name}")
    return name
