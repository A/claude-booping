"""End-to-end walk of a playbook run through the CLI entry points.

Drives `playbook-transition` + `playbook-state` as subprocesses against a tmp
workdir — no internals — and asserts the mid-run and final snapshots structurally.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import yaml

from tests.helpers import get_fixture_path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"


def _plant(name: str = "runner") -> None:
    src = get_fixture_path("playbook-transition-home") / "_playbooks" / name
    dst = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(src), str(dst)], check=True)


def _booping(*argv: str, cwd: Path) -> str:
    result = subprocess.run(
        [str(BOOPING_BIN), *argv],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def _move(to: str, workdir: Path, *extra: str) -> str:
    return _booping(
        "playbook-transition", "runner", to, "--workdir", str(workdir),
        *extra,
        cwd=workdir.parent,
    )


def _state(workdir: Path) -> dict[str, Any]:
    out = _booping("playbook-state", "runner", "--workdir", str(workdir), cwd=workdir.parent)
    parsed = yaml.safe_load(out)
    assert isinstance(parsed, dict)
    return parsed  # type: ignore[return-value]


def test_full_run_walk(tmp_path: Path) -> None:
    _plant()
    workdir = tmp_path / "run"
    workdir.mkdir()

    # Bootstrap the outer state machine, then advance it to the status that
    # covers the per-instance subgraph.
    _move("intaking", workdir)
    _move("researching", workdir)

    # Bootstrap two instances; drive one of them to terminal.
    _move("spec-ing", workdir, "--state", "step", "--instance", "beta")
    _move("spec-ing", workdir, "--state", "step", "--instance", "alpha")
    _move("done", workdir, "--state", "step", "--instance", "alpha")

    mid = _state(workdir)
    assert mid["playbook"] == "runner"
    assert mid["workdir"] == str(workdir)

    main = mid["states"]["main"]
    assert main["artifact"] == "index.md"
    assert main["status"] == "researching"
    assert main["next"] == [{"to": "done", "when": "research complete"}]

    step = mid["states"]["step"]
    assert step["artifact"] == "steps/{instance}/index.md"
    assert list(step["instances"]) == ["alpha", "beta"]
    assert step["instances"]["alpha"] == {"status": "done"}
    assert step["instances"]["beta"]["status"] == "spec-ing"
    assert step["instances"]["beta"]["next"] == [{"to": "done", "when": "spec written"}]

    # Finish the remaining instance, then the outer machine.
    _move("done", workdir, "--state", "step", "--instance", "beta")
    _move("done", workdir)

    final = _state(workdir)
    assert final["states"]["main"] == {"artifact": "index.md", "status": "done"}
    assert final["states"]["step"] == {
        "artifact": "steps/{instance}/index.md",
        "instances": {"alpha": {"status": "done"}, "beta": {"status": "done"}},
    }
