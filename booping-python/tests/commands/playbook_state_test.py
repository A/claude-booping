from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from booping.commands import playbook_state as cmd
from booping.commands import playbook_transition as transition_cmd
from tests.helpers import get_fixture_path


def _plant(name: str = "runner") -> None:
    """Copy a fixture playbook into the isolated HOME's global playbooks root."""
    src = get_fixture_path("playbook-transition-home") / "_playbooks" / name
    dst = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(src), str(dst)], check=True)


def _state(
    playbook: str = "runner",
    workdir: Path | None = None,
    target: str | None = None,
) -> argparse.Namespace:
    return argparse.Namespace(
        playbook=playbook,
        target=target,
        workdir=str(workdir) if workdir is not None else None,
    )


def _move(
    to: str,
    *,
    state: str | None = None,
    instance: str | None = None,
    workdir: Path,
) -> None:
    transition_cmd._run(  # type: ignore[reportPrivateUsage]
        argparse.Namespace(
            playbook="runner",
            to_status=to,
            state=state,
            instance=instance,
            target=None,
            workdir=str(workdir),
        )
    )


def _report(
    workdir: Path,
    capsys: pytest.CaptureFixture[str],
    playbook: str = "runner",
    target: str | None = None,
) -> dict[str, Any]:
    cmd._run(_state(playbook, workdir, target))  # type: ignore[reportPrivateUsage]
    out = capsys.readouterr().out
    parsed = yaml.safe_load(out)
    assert isinstance(parsed, dict)
    return parsed  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Shape + statuses
# ---------------------------------------------------------------------------

def test_missing_artifact_reports_not_started_with_bootstrap_edge(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    report = _report(tmp_path, capsys)

    assert report["playbook"] == "runner"
    assert report["workdir"] == str(tmp_path)
    main = report["states"]["main"]
    assert main["artifact"] == "index.md"
    assert main["status"] == "not-started"
    assert [e["to"] for e in main["next"]] == ["intaking"]
    assert "gates" not in main["next"][0]


def test_outer_state_reports_status_and_next_edges(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _move("intaking", workdir=tmp_path)
    capsys.readouterr()

    main = _report(tmp_path, capsys)["states"]["main"]
    assert main["status"] == "intaking"
    edges = {e["to"]: e for e in main["next"]}
    assert set(edges) == {"researching", "broken", "weird"}
    assert edges["researching"]["when"] == "intake step complete"
    assert edges["researching"]["gates"] == ["request captured in the artifact"]
    assert "gates" not in edges["broken"]


def test_terminal_status_has_no_next(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _move("intaking", workdir=tmp_path)
    _move("researching", workdir=tmp_path)
    _move("done", workdir=tmp_path)
    capsys.readouterr()

    main = _report(tmp_path, capsys)["states"]["main"]
    assert main["status"] == "done"
    assert "next" not in main


def test_outer_state_is_reported_first(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    assert list(_report(tmp_path, capsys)["states"]) == ["main", "step"]


# ---------------------------------------------------------------------------
# Instances
# ---------------------------------------------------------------------------

def test_instance_state_is_empty_before_any_instance_exists(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    step = _report(tmp_path, capsys)["states"]["step"]
    assert step["artifact"] == "steps/{instance}/index.md"
    assert step["instances"] == {}


def test_instances_keyed_by_slug_and_sorted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    for slug in ("zulu", "alpha", "mike"):
        _move("spec-ing", state="step", instance=slug, workdir=tmp_path)
    _move("done", state="step", instance="mike", workdir=tmp_path)
    capsys.readouterr()

    instances = _report(tmp_path, capsys)["states"]["step"]["instances"]
    assert list(instances) == ["alpha", "mike", "zulu"]
    assert instances["mike"] == {"status": "done"}
    assert instances["alpha"]["status"] == "spec-ing"
    assert instances["alpha"]["next"] == [{"to": "done", "when": "spec written"}]


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

def test_degenerate_artifact_without_frontmatter_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    (tmp_path / "index.md").write_text("no frontmatter here\n")
    with pytest.raises(SystemExit) as exc:
        cmd._run(_state(workdir=tmp_path))  # type: ignore[reportPrivateUsage]
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert str(tmp_path / "index.md") in err
    assert "status:" in err


def test_degenerate_artifact_without_status_key_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    (tmp_path / "index.md").write_text("---\ntitle: Run\n---\n\nbody\n")
    with pytest.raises(SystemExit) as exc:
        cmd._run(_state(workdir=tmp_path))  # type: ignore[reportPrivateUsage]
    assert exc.value.code == 1
    assert "status:" in capsys.readouterr().err


def test_unknown_playbook_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    with pytest.raises(SystemExit) as exc:
        cmd._run(_state("nope", tmp_path))  # type: ignore[reportPrivateUsage]
    assert exc.value.code == 1
    assert "playbook not found" in capsys.readouterr().err


def test_playbook_without_states_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant("graphonly")
    with pytest.raises(SystemExit) as exc:
        cmd._run(_state("graphonly", tmp_path))  # type: ignore[reportPrivateUsage]
    assert exc.value.code == 1
    assert "declares no states" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Read-only
# ---------------------------------------------------------------------------

def test_report_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _move("intaking", workdir=tmp_path)
    _move("spec-ing", state="step", instance="alpha", workdir=tmp_path)
    capsys.readouterr()

    def snapshot() -> dict[str, tuple[float, int]]:
        return {
            str(p): (p.stat().st_mtime, p.stat().st_size)
            for p in sorted(tmp_path.rglob("*"))
        }

    before = snapshot()
    _report(tmp_path, capsys)
    assert snapshot() == before


def test_workdir_defaults_to_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _move("intaking", workdir=tmp_path)
    capsys.readouterr()
    monkeypatch.chdir(tmp_path)

    cmd._run(_state())  # type: ignore[reportPrivateUsage]
    report = yaml.safe_load(capsys.readouterr().out)
    assert report["states"]["main"]["status"] == "intaking"


# ---------------------------------------------------------------------------
# Explicit --target
# ---------------------------------------------------------------------------

def test_target_reports_that_files_frontier(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    (tmp_path / "review.md").write_text("---\nstatus: intaking\n---\n")

    report = _report(tmp_path, capsys, target="review.md")

    main = report["states"]["main"]
    assert main["artifact"] == str(tmp_path / "review.md")
    assert main["status"] == "intaking"
    assert {e["to"] for e in main["next"]} == {"researching", "broken", "weird"}


def test_absolute_target_is_honoured(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    artifact = elsewhere / "review.md"
    artifact.write_text("---\nstatus: researching\n---\n")

    report = _report(tmp_path, capsys, target=str(artifact))

    main = report["states"]["main"]
    assert main["artifact"] == str(artifact)
    assert main["status"] == "researching"


def test_missing_target_reports_not_started(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    report = _report(tmp_path, capsys, target="review.md")

    main = report["states"]["main"]
    assert main["status"] == "not-started"
    assert [e["to"] for e in main["next"]] == ["intaking"]


def test_machine_without_artifact_needs_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant("targetless")
    with pytest.raises(SystemExit) as exc:
        cmd._run(_state("targetless", tmp_path))  # type: ignore[reportPrivateUsage]
    assert exc.value.code == 1
    assert "--target" in capsys.readouterr().err


def test_machine_without_artifact_reports_with_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant("targetless")
    (tmp_path / "review.md").write_text("---\nstatus: reviewing\n---\n")

    report = _report(tmp_path, capsys, playbook="targetless", target="review.md")

    main = report["states"]["main"]
    assert main["artifact"] == str(tmp_path / "review.md")
    assert main["status"] == "reviewing"
    assert [e["to"] for e in main["next"]] == ["reviewed"]
