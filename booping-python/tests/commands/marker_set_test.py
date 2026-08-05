from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"

MARKER = (
    "# booping project marker\n"
    'project_name: "demo"  # quoted on purpose\n'
    "vault_path: ./booping\n"
)


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(BOOPING_BIN), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text(MARKER)
    return repo


def test_sets_value_and_prints_one_stderr_line(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    result = _run("marker-set", "latest_migration=3", cwd=repo)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == "marker: latest_migration=3\n"
    assert yaml.safe_load((repo / ".booping").read_text())["latest_migration"] == 3


def test_changes_only_the_target_line(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    assert _run("marker-set", "latest_migration=3", cwd=repo).returncode == 0

    text = (repo / ".booping").read_text()
    assert text == MARKER + "latest_migration: 3\n"


def test_value_is_absolute_never_incremented(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    assert _run("marker-set", "latest_migration=3", cwd=repo).returncode == 0
    assert _run("marker-set", "latest_migration=9", cwd=repo).returncode == 0

    assert yaml.safe_load((repo / ".booping").read_text())["latest_migration"] == 9


def test_runs_from_a_subdirectory(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    nested = repo / "src" / "deep"
    nested.mkdir(parents=True)

    result = _run("marker-set", "latest_migration=1", cwd=nested)

    assert result.returncode == 0
    assert yaml.safe_load((repo / ".booping").read_text())["latest_migration"] == 1


def test_at_latest_resolves_to_the_highest_shipped_id(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    shipped = max(
        yaml.safe_load(path.read_text().split("---")[1])["id"]
        for path in (PLUGIN_ROOT / "migrations").glob("*/migration.md")
    )

    result = _run("marker-set", "latest_migration=@latest", cwd=repo)

    assert result.returncode == 0
    assert result.stderr == f"marker: latest_migration={shipped}\n"
    assert yaml.safe_load((repo / ".booping").read_text())["latest_migration"] == shipped


def test_malformed_pair_exits_1(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    result = _run("marker-set", "latest_migration", cwd=repo)

    assert result.returncode == 1
    assert "malformed" in result.stderr
    assert (repo / ".booping").read_text() == MARKER


def test_non_integer_id_exits_1(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    result = _run("marker-set", "latest_migration=three", cwd=repo)

    assert result.returncode == 1
    assert "integer" in result.stderr
    assert (repo / ".booping").read_text() == MARKER


def test_no_marker_exits_2(tmp_path: Path) -> None:
    bare = tmp_path / "bare"
    bare.mkdir()

    result = _run("marker-set", "latest_migration=3", cwd=bare)

    assert result.returncode == 2
    assert ".booping" in result.stderr


def test_logs_the_invocation(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    assert _run("marker-set", "latest_migration=3", cwd=repo).returncode == 0

    log = (repo / "booping" / "_booping" / ".booping.log").read_text()
    assert "[marker-set]" in log
    assert "latest_migration=3" in log
