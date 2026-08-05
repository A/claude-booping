from __future__ import annotations

import subprocess
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"

TREE = """
demo:
  README.md: "hello {{ name }}\\n"
  src:
    main.py: "print(1)\\n"
  _references:
    type: dir
"""


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(BOOPING_BIN), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def _write_global_config(xdg: Path, body: str) -> None:
    cfg_dir = xdg / "booping"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "config.yaml").write_text(body)


def _scaffold(
    tmp_path: Path,
    xdg: Path,
    *args: str,
    tree: str = TREE,
) -> subprocess.CompletedProcess[str]:
    _write_global_config(xdg, tree)
    return _run("scaffold", *args, cwd=tmp_path)


# --- Task 2.1: command surface, destination semantics -----------------------


def test_help_lists_positionals_and_flags(tmp_path: Path) -> None:
    result = _run("scaffold", "--help", cwd=tmp_path)
    assert result.returncode == 0
    assert "config-path" in result.stdout
    assert "dest" in result.stdout
    assert "--force" in result.stdout
    assert "--set" in result.stdout
    assert "Dotted path into the merged config" in result.stdout
    assert "never deletes a directory" in result.stdout


def test_missing_destination_is_created_with_parents(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "a" / "b" / "out"
    result = _scaffold(tmp_path, isolated_xdg_config_home, "demo", str(dest))
    assert result.returncode == 0, result.stderr
    assert (dest / "README.md").read_text() == "hello \n"
    assert (dest / "src" / "main.py").read_text() == "print(1)\n"
    assert (dest / "_references").is_dir()


def test_existing_empty_destination_written_without_force(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    result = _scaffold(tmp_path, isolated_xdg_config_home, "demo", str(dest))
    assert result.returncode == 0, result.stderr
    assert (dest / "README.md").exists()


def test_non_empty_destination_without_force_exits_1_writing_nothing(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / "keep.txt").write_text("keep\n")
    result = _scaffold(tmp_path, isolated_xdg_config_home, "demo", str(dest))
    assert result.returncode == 1
    assert str(dest) in result.stderr
    assert sorted(p.name for p in dest.iterdir()) == ["keep.txt"]


def test_force_overwrites_named_files_and_leaves_others(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / "README.md").write_text("old\n")
    (dest / "keep.txt").write_text("keep\n")
    result = _scaffold(tmp_path, isolated_xdg_config_home, "demo", str(dest), "--force")
    assert result.returncode == 0, result.stderr
    assert (dest / "README.md").read_text() == "hello \n"
    assert (dest / "keep.txt").read_text() == "keep\n"


def test_force_never_removes_a_directory(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    (dest / "src").mkdir(parents=True)
    (dest / "src" / "other.py").write_text("other\n")
    (dest / "unrelated").mkdir()
    (dest / "unrelated" / "f.txt").write_text("f\n")
    result = _scaffold(tmp_path, isolated_xdg_config_home, "demo", str(dest), "--force")
    assert result.returncode == 0, result.stderr
    assert (dest / "src" / "other.py").read_text() == "other\n"
    assert (dest / "unrelated" / "f.txt").read_text() == "f\n"


# --- Task 2.2: seed rendering ----------------------------------------------


def test_set_pair_is_a_bare_template_variable(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    result = _scaffold(
        tmp_path, isolated_xdg_config_home, "demo", str(dest), "--set", "name=world"
    )
    assert result.returncode == 0, result.stderr
    assert (dest / "README.md").read_text() == "hello world\n"


def test_plain_seed_is_byte_identical_with_trailing_newline(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    result = _scaffold(
        tmp_path,
        isolated_xdg_config_home,
        "demo",
        str(dest),
        tree='demo:\n  a.txt: "line one\\nline two\\n"\n',
    )
    assert result.returncode == 0, result.stderr
    assert (dest / "a.txt").read_bytes() == b"line one\nline two\n"


def test_seed_can_reference_config_and_context_globals(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    result = _scaffold(
        tmp_path,
        isolated_xdg_config_home,
        "demo",
        str(dest),
        tree=(
            "demo:\n"
            '  a.txt: "{{ config.sprint.default_threshold_sp }}|'
            '{{ context.project is none }}\\n"\n'
        ),
    )
    assert result.returncode == 0, result.stderr
    assert (dest / "a.txt").read_text() == "35|True\n"


def test_jinja_error_aborts_before_any_write(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    result = _scaffold(
        tmp_path,
        isolated_xdg_config_home,
        "demo",
        str(dest),
        tree='demo:\n  ok.txt: "fine\\n"\n  bad.txt: "{% if %}"\n',
    )
    assert result.returncode == 1
    assert "bad.txt" in result.stderr
    assert not (dest / "ok.txt").exists()


def test_malformed_set_pair_exits_1_matching_render_message(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    result = _scaffold(
        tmp_path, isolated_xdg_config_home, "demo", str(dest), "--set", "nope"
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "malformed --set pair" in result.stderr
    assert "nope" in result.stderr
    assert not dest.exists()


# --- Task 2.3: report, exit codes, logging ---------------------------------


def test_report_lines_and_summary(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / "README.md").write_text("old\n")
    result = _scaffold(tmp_path, isolated_xdg_config_home, "demo", str(dest), "--force")
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert f"overwrote file {dest / 'README.md'}" in lines
    assert f"created file {dest / 'src' / 'main.py'}" in lines
    assert f"created dir {dest / '_references'}" in lines
    assert lines[-1] == (
        "scaffolded 4 paths — 2 dirs created, 1 files created, 1 files overwritten"
    )
    assert result.stderr == ""


def test_unknown_config_path_exits_1(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    result = _scaffold(tmp_path, isolated_xdg_config_home, "no.such.tree", str(tmp_path / "out"))
    assert result.returncode == 1
    assert result.stdout == ""
    assert "no.such.tree" in result.stderr


def test_non_tree_value_exits_1(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    result = _scaffold(
        tmp_path,
        isolated_xdg_config_home,
        "home_dir",
        str(tmp_path / "out"),
    )
    assert result.returncode == 1
    assert "not a tree" in result.stderr


def test_invalid_node_exits_1(tmp_path: Path, isolated_xdg_config_home: Path) -> None:
    result = _scaffold(
        tmp_path,
        isolated_xdg_config_home,
        "demo",
        str(tmp_path / "out"),
        tree="demo:\n  a.txt: null\n",
    )
    assert result.returncode == 1
    assert "demo.a.txt" in result.stderr


def test_unsafe_filename_exits_1(tmp_path: Path, isolated_xdg_config_home: Path) -> None:
    dest = tmp_path / "out"
    result = _scaffold(
        tmp_path,
        isolated_xdg_config_home,
        "demo",
        str(dest),
        tree='demo:\n  "../escape.txt": "x\\n"\n',
    )
    assert result.returncode == 1
    assert "escape.txt" in result.stderr
    assert not (tmp_path / "escape.txt").exists()


def test_oserror_during_write_exits_2(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    # A read-only destination makes the first file write fail at the OS level.
    (dest / "README.md").write_text("old\n")
    dest.chmod(0o500)
    try:
        result = _scaffold(
            tmp_path, isolated_xdg_config_home, "demo", str(dest), "--force"
        )
    finally:
        dest.chmod(0o700)
    assert result.returncode == 2
    assert str(dest) in result.stderr


def test_core_playbook_scaffold_tree(tmp_path: Path) -> None:
    dest = tmp_path / "demo"
    result = _run("scaffold", "playbook.scaffold", str(dest), "--set", "name=demo", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert sorted(str(p.relative_to(dest)) for p in dest.rglob("*")) == [
        "_references",
        "playbook.md",
        "playbook.yaml",
    ]
    assert (dest / "_references").is_dir()
    assert "\nname: demo\n" in (dest / "playbook.md").read_text()
    assert "graph:" in (dest / "playbook.yaml").read_text()


def test_core_vault_scaffold_seeds_sprints_base_fence(tmp_path: Path) -> None:
    import yaml

    dest = tmp_path / "vault"
    result = _run("scaffold", "vault.scaffold", str(dest), cwd=tmp_path)
    assert result.returncode == 0, result.stderr

    text = (dest / "sprints.md").read_text()
    assert text.startswith("```base\n")
    fence = text.split("```base\n", 1)[1].split("\n```", 1)[0]
    spec = yaml.safe_load(fence)

    # Scoped to the booping vault holding this sprints.md, so it stays correct when
    # the booping vault is nested inside a larger Obsidian vault.
    assert spec["filters"] == {
        "and": [
            "file.inFolder(this.file.folder)",
            'file.path.contains("plans/")',
            'file.name == "index.md"',
        ]
    }
    view = spec["views"][0]
    assert view["type"] == "table"
    assert view["order"] == [
        "status",
        "sp",
        "title",
        "summary",
        "created",
        "completed",
    ]
    assert view["sort"] == [{"property": "created", "direction": "DESC"}]


def test_core_vault_scaffold_non_empty_destination_aborts(tmp_path: Path) -> None:
    dest = tmp_path / "vault"
    dest.mkdir()
    (dest / "stray.md").write_text("x\n")

    result = _run("scaffold", "vault.scaffold", str(dest), cwd=tmp_path)
    assert result.returncode == 1
    assert not (dest / "sprints.md").exists()


def test_logs_one_scaffold_line_when_project_attached(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    repo = tmp_path / "repo"
    vault = repo / "vault"
    vault.mkdir(parents=True)
    (repo / ".booping").write_text("project_name: probe\nvault_path: ./vault\n")
    (vault / "config.yaml").write_text(TREE)

    dest = repo / "out"
    result = _run("scaffold", "demo", str(dest), cwd=repo)
    assert result.returncode == 0, result.stderr
    log = (vault / "_booping" / ".booping.log").read_text()
    assert log.count("[scaffold]") == 1
    assert "demo" in log
