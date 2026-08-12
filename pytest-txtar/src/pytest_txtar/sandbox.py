"""Building the sandbox a case runs in, and running it there."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path

from pytest_txtar.case import Case, TxtarSpec
from pytest_txtar.compare import Outcome, normalizer


def run_case(case: Case, spec: TxtarSpec) -> Outcome:
    sandbox = Path(tempfile.mkdtemp(prefix="pytest-txtar-"))
    try:
        return execute(case, spec, sandbox)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def execute(case: Case, spec: TxtarSpec, sandbox: Path) -> Outcome:
    roots = {root: sandbox / root for root in spec.roots}
    for directory in roots.values():
        directory.mkdir()

    for name, data in case.fixtures:
        target = tree_target(roots, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data, encoding="utf-8")

    env = dict(os.environ)
    for variable, root in spec.env.items():
        env[variable] = str(roots[root])

    out_parts: list[str] = []
    err_parts: list[str] = []
    exit_code = 0
    early_exit: tuple[str, int] | None = None
    for index, line in enumerate(case.cmd):
        argv = shlex.split(line)
        if argv and argv[0] in spec.commands:
            argv[0] = str(spec.commands[argv[0]])
        completed = subprocess.run(
            argv,
            cwd=roots[spec.cwd_root],
            env=env,
            capture_output=True,
            text=True,
        )
        out_parts.append(completed.stdout)
        err_parts.append(completed.stderr)
        exit_code = completed.returncode
        if index < len(case.cmd) - 1 and exit_code != 0:
            early_exit = (line, exit_code)
            break

    files = {name: read_optional(tree_target(roots, name)) for name, _ in case.expected}
    normalize = normalizer(roots, spec.token_map)
    return Outcome(
        stdout=normalize("".join(out_parts)),
        stderr=normalize("".join(err_parts)),
        exit_code=exit_code,
        files={name: None if body is None else normalize(body) for name, body in files.items()},
        early_exit=early_exit,
    )


def tree_target(roots: Mapping[str, Path], name: str) -> Path:
    _, _, rest = name.partition("/")
    root, _, relative = rest.partition("/")
    return roots[root] / relative


def read_optional(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.is_file() else None
