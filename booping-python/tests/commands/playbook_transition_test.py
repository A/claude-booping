from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

import pytest

from booping.commands import playbook_transition as cmd
from booping.context._yaml import parse_frontmatter_only
from tests.helpers import get_fixture_path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"


def _plant(name: str = "runner") -> None:
    """Copy a fixture playbook into the isolated HOME's global playbooks root."""
    src = get_fixture_path("playbook-transition-home") / "_playbooks" / name
    dst = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(src), str(dst)], check=True)


def _plant_shared_scripts() -> None:
    """Copy the fixture's root-level `_scripts/` into the isolated HOME's global root."""
    src = get_fixture_path("playbook-transition-home") / "_playbooks" / "_scripts"
    dst = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / "_scripts"
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(src), str(dst)], check=True)


def _args(
    playbook: str = "runner",
    to: str = "intaking",
    *,
    state: str | None = None,
    instance: str | None = None,
    target: str | None = None,
    workdir: Path | None = None,
) -> argparse.Namespace:
    return argparse.Namespace(
        playbook=playbook,
        to_status=to,
        state=state,
        instance=instance,
        target=target,
        workdir=str(workdir) if workdir is not None else None,
    )


def _run(args: argparse.Namespace) -> None:
    cmd._run(args)  # type: ignore[reportPrivateUsage]


def _bootstrap(workdir: Path) -> None:
    _run(_args(to="intaking", workdir=workdir))


# ---------------------------------------------------------------------------
# Task 3.1 — resolution, bootstrap, instances, edges
# ---------------------------------------------------------------------------

def test_bootstrap_creates_artifact_and_reports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _run(_args(to="intaking", workdir=tmp_path))

    artifact = tmp_path / "index.md"
    assert parse_frontmatter_only(artifact)["status"] == "intaking"
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "created index.md"
    assert lines[1] == "not-started → intaking"
    assert lines[2] == "frontmatter: status=intaking"


def test_bootstrap_creates_parent_dirs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _run(_args(to="spec-ing", state="step", instance="alpha", workdir=tmp_path))

    artifact = tmp_path / "steps" / "alpha" / "index.md"
    assert parse_frontmatter_only(artifact)["status"] == "spec-ing"
    assert capsys.readouterr().out.splitlines()[0] == "created steps/alpha/index.md"


def test_missing_artifact_with_non_initial_target_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    with pytest.raises(SystemExit) as exc:
        _run(_args(to="researching", workdir=tmp_path))
    assert exc.value.code == 1
    assert "initial status 'intaking'" in capsys.readouterr().err
    assert not (tmp_path / "index.md").exists()


def test_instance_required_for_instance_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    with pytest.raises(SystemExit) as exc:
        _run(_args(to="spec-ing", state="step", workdir=tmp_path))
    assert exc.value.code == 1
    assert "--instance" in capsys.readouterr().err


def test_instance_rejected_for_plain_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    with pytest.raises(SystemExit) as exc:
        _run(_args(to="intaking", instance="alpha", workdir=tmp_path))
    assert exc.value.code == 1
    assert "not accepted" in capsys.readouterr().err


def test_illegal_edge_exits_1_listing_allowed_targets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _bootstrap(tmp_path)
    capsys.readouterr()

    with pytest.raises(SystemExit) as exc:
        _run(_args(to="done", workdir=tmp_path))
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "cannot transition from 'intaking' to 'done'" in err
    assert "allowed targets: broken, researching, weird" in err


def test_idempotent_rerun_skips_edge_hooks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _bootstrap(tmp_path)
    _run(_args(to="researching", workdir=tmp_path))
    (tmp_path / "check-findings.env").unlink()
    capsys.readouterr()

    _run(_args(to="researching", workdir=tmp_path))

    lines = capsys.readouterr().out.splitlines()
    assert lines == ["researching → researching (idempotent)", "script post-note: ok"]
    # Edge hooks never fired a second time.
    assert not (tmp_path / "check-findings.env").exists()


def test_degenerate_artifact_without_frontmatter_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    (tmp_path / "index.md").write_text("no frontmatter here\n")
    with pytest.raises(SystemExit) as exc:
        _run(_args(to="researching", workdir=tmp_path))
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
        _run(_args(to="researching", workdir=tmp_path))
    assert exc.value.code == 1
    assert "status:" in capsys.readouterr().err


def test_workdir_defaults_to_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    monkeypatch.chdir(tmp_path)
    _run(_args(to="intaking"))
    assert parse_frontmatter_only(tmp_path / "index.md")["status"] == "intaking"
    assert capsys.readouterr().out.splitlines()[0] == "created index.md"


def test_unknown_playbook_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    with pytest.raises(SystemExit) as exc:
        _run(_args(playbook="nope", workdir=tmp_path))
    assert exc.value.code == 1
    assert "playbook not found" in capsys.readouterr().err


def test_unknown_state_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    with pytest.raises(SystemExit) as exc:
        _run(_args(to="intaking", state="nope", workdir=tmp_path))
    assert exc.value.code == 1
    assert "unknown state 'nope'" in capsys.readouterr().err


def test_playbook_without_states_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant("graphonly")
    with pytest.raises(SystemExit) as exc:
        _run(_args(playbook="graphonly", to="whatever", workdir=tmp_path))
    assert exc.value.code == 1
    assert "declares no states" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Task 3.2 — hook dispatch + report
# ---------------------------------------------------------------------------

def test_report_lines_for_a_normal_move(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _bootstrap(tmp_path)
    capsys.readouterr()

    _run(_args(to="researching", workdir=tmp_path))

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "intaking → researching"
    assert lines[1] == "frontmatter: status=researching"
    assert lines[2].startswith('frontmatter: researched="')
    assert lines[3] == "script check-findings: ok"
    assert lines[4] == "script post-note: ok"

    fm = parse_frontmatter_only(tmp_path / "index.md")
    assert fm["status"] == "researching"
    assert fm["researched"]


def test_script_hook_env_and_cwd(tmp_path: Path) -> None:
    _plant()
    _bootstrap(tmp_path)
    _run(_args(to="researching", workdir=tmp_path))

    recorded = dict(
        line.split("=", 1)
        for line in (tmp_path / "check-findings.env").read_text().splitlines()
    )
    assert recorded["artifact"] == str(tmp_path / "index.md")
    assert recorded["instance"] == ""
    assert recorded["workdir"] == str(tmp_path)
    assert recorded["cwd"] == str(tmp_path)


def test_script_hook_receives_instance_slug(tmp_path: Path) -> None:
    _plant()
    _run(_args(to="spec-ing", state="step", instance="alpha", workdir=tmp_path))
    _run(_args(to="done", state="step", instance="alpha", workdir=tmp_path))

    recorded = (tmp_path / "check-findings.env").read_text()
    assert "instance=alpha" in recorded
    assert f"artifact={tmp_path / 'steps' / 'alpha' / 'index.md'}" in recorded


def test_failing_script_hook_exits_2_and_relays_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _bootstrap(tmp_path)
    capsys.readouterr()

    with pytest.raises(SystemExit) as exc:
        _run(_args(to="broken", workdir=tmp_path))
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "hook says no" in err
    assert "exited 3" in err


def test_unknown_hook_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _bootstrap(tmp_path)
    capsys.readouterr()

    with pytest.raises(SystemExit) as exc:
        _run(_args(to="weird", workdir=tmp_path))
    assert exc.value.code == 2
    assert "unknown hook: 'teleport'" in capsys.readouterr().err


def test_instance_artifact_path_interpolated_and_moved(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _run(_args(to="spec-ing", state="step", instance="alpha", workdir=tmp_path))
    capsys.readouterr()

    _run(_args(to="done", state="step", instance="alpha", workdir=tmp_path))

    lines = capsys.readouterr().out.splitlines()
    assert lines[:2] == ["spec-ing → done", "frontmatter: status=done"]
    artifact = tmp_path / "steps" / "alpha" / "index.md"
    assert parse_frontmatter_only(artifact)["status"] == "done"


# ---------------------------------------------------------------------------
# Script hook resolution across discovery roots
# ---------------------------------------------------------------------------

def _scripter(to: str, workdir: Path) -> None:
    _run(_args(playbook="scripter", to=to, workdir=workdir))


def _scripter_start(tmp_path: Path) -> None:
    _plant("scripter")
    _plant_shared_scripts()
    _scripter("start", tmp_path)


def test_script_hook_falls_back_to_a_discovery_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _scripter_start(tmp_path)
    capsys.readouterr()

    _scripter("shared", tmp_path)

    assert "script shared-note: ok" in capsys.readouterr().out
    assert (tmp_path / "shared-note.log").is_file()


def test_script_hook_passes_trailing_tokens_as_argv(tmp_path: Path) -> None:
    _scripter_start(tmp_path)

    _scripter("shared", tmp_path)

    assert (tmp_path / "shared-note.log").read_text() == "shared --tag hello --stage a b\n"


def test_playbook_dir_script_shadows_the_root_copy(tmp_path: Path) -> None:
    _scripter_start(tmp_path)

    _scripter("shadowed", tmp_path)

    assert (tmp_path / "note.log").read_text() == "playbook\n"


def test_root_script_used_when_the_playbook_carries_none(tmp_path: Path) -> None:
    _scripter_start(tmp_path)
    home = Path(os.environ["HOME"]) / "Claude" / "_playbooks"
    (home / "scripter" / "_scripts" / "note").unlink()

    _scripter("shadowed", tmp_path)

    assert (tmp_path / "note.log").read_text() == "root\n"


def test_missing_script_names_every_probed_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _scripter_start(tmp_path)
    capsys.readouterr()

    with pytest.raises(SystemExit) as exc:
        _scripter("unfindable", tmp_path)
    assert exc.value.code == 2
    err = capsys.readouterr().err
    home = Path(os.environ["HOME"]) / "Claude" / "_playbooks"
    assert "script hook 'no-such-script' not found; probed:" in err
    assert str(home / "scripter" / "_scripts" / "no-such-script") in err
    assert str(home / "_scripts" / "no-such-script") in err
    assert str(PLUGIN_ROOT / "playbooks" / "_scripts" / "no-such-script") in err


# ---------------------------------------------------------------------------
# File-target frontmatter-update hooks
# ---------------------------------------------------------------------------

def _filer(
    to: str,
    workdir: Path,
    *,
    state: str | None = None,
    instance: str | None = None,
) -> None:
    _run(_args(playbook="filer", to=to, state=state, instance=instance, workdir=workdir))


def _filer_drafting(tmp_path: Path) -> None:
    _plant("filer")
    _filer("drafting", tmp_path)


def test_file_target_hook_updates_sibling_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _filer_drafting(tmp_path)
    (tmp_path / "brief.md").write_text("---\ntitle: Brief\n---\n\nbody\n")
    capsys.readouterr()

    _filer("filed", tmp_path)

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "drafting → filed"
    assert lines[1] == "frontmatter: status=filed"
    assert lines[2].startswith("frontmatter brief.md: reviewed=")
    brief = parse_frontmatter_only(tmp_path / "brief.md")
    assert brief["title"] == "Brief"
    assert brief["reviewed"]
    # The state artifact itself only carries the status move.
    assert "reviewed" not in parse_frontmatter_only(tmp_path / "index.md")


def test_file_target_hook_interpolates_instance(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant("filer")
    _filer("spec-ing", tmp_path, state="step", instance="alpha")
    notes = tmp_path / "steps" / "alpha" / "notes.md"
    notes.write_text("---\ntitle: Notes\n---\n\nbody\n")
    capsys.readouterr()

    _filer("filed", tmp_path, state="step", instance="alpha")

    lines = capsys.readouterr().out.splitlines()
    assert lines[2] == "frontmatter steps/alpha/notes.md: seen=recorded"
    assert parse_frontmatter_only(notes)["seen"] == "recorded"


def test_file_target_instance_without_instance_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _filer_drafting(tmp_path)
    capsys.readouterr()

    with pytest.raises(SystemExit) as exc:
        _filer("filed-instance", tmp_path)
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "steps/{instance}/notes.md carries {instance}" in err
    assert "no instance is in scope" in err


def test_file_target_missing_file_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _filer_drafting(tmp_path)
    capsys.readouterr()

    with pytest.raises(SystemExit) as exc:
        _filer("filed-missing", tmp_path)
    assert exc.value.code == 2
    assert "frontmatter-update failed:" in capsys.readouterr().err
    assert not (tmp_path / "nope.md").exists()


def test_file_target_without_frontmatter_block_bootstraps_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _filer_drafting(tmp_path)
    (tmp_path / "raw.md").write_text("no frontmatter here\n")
    capsys.readouterr()

    _filer("filed-raw", tmp_path)

    assert "frontmatter raw.md: reviewed=" in capsys.readouterr().out
    text = (tmp_path / "raw.md").read_text()
    assert text.startswith("---\nreviewed:")
    assert text.endswith("---\n\nno frontmatter here\n")


def test_no_target_hook_still_targets_the_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _filer_drafting(tmp_path)
    capsys.readouterr()

    _filer("done", tmp_path)

    lines = capsys.readouterr().out.splitlines()
    assert lines[1] == "frontmatter: status=done"
    assert lines[2].startswith("frontmatter: noted=")
    assert parse_frontmatter_only(tmp_path / "index.md")["noted"]


def test_cli_end_to_end(tmp_path: Path) -> None:
    _plant()
    workdir = tmp_path / "run"
    workdir.mkdir()
    result = subprocess.run(
        [str(BOOPING_BIN), "playbook-transition", "runner", "intaking",
         "--workdir", str(workdir)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "created index.md"
    assert parse_frontmatter_only(workdir / "index.md")["status"] == "intaking"


# ---------------------------------------------------------------------------
# Explicit --target
# ---------------------------------------------------------------------------

def test_relative_target_overrides_the_declared_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    (tmp_path / "review.md").write_text("---\nstatus: intaking\n---\n")
    capsys.readouterr()

    _run(_args(to="researching", target="review.md", workdir=tmp_path))

    assert parse_frontmatter_only(tmp_path / "review.md")["status"] == "researching"
    assert not (tmp_path / "index.md").exists()
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "intaking → researching"
    assert lines[1] == "frontmatter: status=researching"


def test_absolute_target_is_honoured(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    artifact = elsewhere / "review.md"
    artifact.write_text("---\nstatus: intaking\n---\n")
    capsys.readouterr()

    _run(_args(to="researching", target=str(artifact), workdir=tmp_path))

    assert parse_frontmatter_only(artifact)["status"] == "researching"


def test_target_bootstraps_a_missing_file_at_the_initial_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    _run(_args(to="intaking", target="reviews/one.md", workdir=tmp_path))

    artifact = tmp_path / "reviews" / "one.md"
    assert parse_frontmatter_only(artifact)["status"] == "intaking"
    assert capsys.readouterr().out.splitlines()[0] == f"created {artifact}"


def test_target_bootstrap_rejects_a_non_initial_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    with pytest.raises(SystemExit) as exc:
        _run(_args(to="researching", target="review.md", workdir=tmp_path))
    assert exc.value.code == 1
    assert "initial status 'intaking'" in capsys.readouterr().err
    assert not (tmp_path / "review.md").exists()


def test_target_and_instance_together_exit_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    with pytest.raises(SystemExit) as exc:
        _run(
            _args(
                to="spec-ing",
                state="step",
                instance="alpha",
                target="review.md",
                workdir=tmp_path,
            )
        )
    assert exc.value.code == 1
    assert "--target and --instance are mutually exclusive" in capsys.readouterr().err


def test_hooks_receive_the_resolved_target_as_booping_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant()
    (tmp_path / "review.md").write_text("---\nstatus: intaking\n---\n")
    capsys.readouterr()

    _run(_args(to="researching", target="review.md", workdir=tmp_path))

    recorded = dict(
        line.split("=", 1)
        for line in (tmp_path / "check-findings.env").read_text().splitlines()
    )
    assert recorded["artifact"] == str(tmp_path / "review.md")
    # The file-target-less frontmatter-update hook wrote to the target, not index.md.
    assert parse_frontmatter_only(tmp_path / "review.md")["researched"]


def test_machine_without_artifact_requires_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant("targetless")
    with pytest.raises(SystemExit) as exc:
        _run(_args(playbook="targetless", to="reviewing", workdir=tmp_path))
    assert exc.value.code == 1
    assert "--target" in capsys.readouterr().err


def test_machine_without_artifact_moves_with_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _plant("targetless")
    _run(_args(playbook="targetless", to="reviewing", target="review.md", workdir=tmp_path))
    capsys.readouterr()

    _run(_args(playbook="targetless", to="reviewed", target="review.md", workdir=tmp_path))

    artifact = tmp_path / "review.md"
    assert parse_frontmatter_only(artifact)["status"] == "reviewed"
    recorded = (tmp_path / "check-findings.env").read_text()
    assert f"artifact={artifact}" in recorded
