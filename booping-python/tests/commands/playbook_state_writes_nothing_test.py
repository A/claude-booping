"""The one `playbook-state` behaviour the txtar corpus cannot express.

A case reads only the files it names in an `expected/` section, so it can show
byte-identical content but cannot tell "not written" from "rewritten identically" —
which is the property under test for a read-only reporter. Everything else about
`playbook-state` lives in `e2e/cases/playbook-state/`.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import pytest

from booping.commands import playbook_state as cmd
from booping.commands import playbook_transition as transition_cmd

PLAYBOOK = "fx-writes-nothing"

MANIFEST = """\
state: main
graph:
  intake: []
  step-pipeline:
    dependencies: [intake]
    state: step
    graph:
      step-spec: []

states:
  main:
    artifact: index.md
    initial: intaking
    statuses:
      intaking:
        transitions:
          - to: done
            when: intake complete
      done: {terminal: true}
  step:
    artifact: steps/{instance}/index.md
    initial: spec-ing
    statuses:
      spec-ing:
        transitions:
          - to: done
            when: spec written
      done: {terminal: true}
"""


def _plant() -> None:
    root = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / PLAYBOOK
    root.mkdir(parents=True, exist_ok=True)
    (root / "playbook.md").write_text(
        f"---\nname: {PLAYBOOK}\ntitle: Writes Nothing\n"
        "summary: Two-machine fixture for the read-only report.\n---\n\nPreamble.\n"
    )
    (root / "playbook.yaml").write_text(MANIFEST)
    for step in ("intake", "step-spec"):
        (root / step).mkdir(exist_ok=True)
        (root / step / "prompt.md").write_text(
            f"---\nsummary: {step}.\n---\n\n{step} body.\n"
        )


def _move(to: str, workdir: Path, *, state: str | None = None,
          instance: str | None = None) -> None:
    transition_cmd._run(  # type: ignore[reportPrivateUsage]
        argparse.Namespace(
            playbook=PLAYBOOK,
            to_status=to,
            state=state,
            instance=instance,
            target=None,
            workdir=str(workdir),
        )
    )


def test_report_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _move("intaking", tmp_path)
    _move("spec-ing", tmp_path, state="step", instance="alpha")
    capsys.readouterr()

    def snapshot() -> dict[str, tuple[float, int]]:
        return {
            str(p): (p.stat().st_mtime, p.stat().st_size)
            for p in sorted(tmp_path.rglob("*"))
        }

    before = snapshot()
    cmd._run(  # type: ignore[reportPrivateUsage]
        argparse.Namespace(playbook=PLAYBOOK, target=None, workdir=str(tmp_path))
    )
    assert snapshot() == before
