from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest
import yaml

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


def test_non_empty_destination_without_force_fills_the_gaps(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / "keep.txt").write_text("keep\n")
    result = _scaffold(tmp_path, isolated_xdg_config_home, "demo", str(dest))
    assert result.returncode == 0, result.stderr
    assert (dest / "README.md").read_text() == "hello \n"
    assert (dest / "keep.txt").read_text() == "keep\n"


def test_existing_file_without_force_is_skipped_and_reported(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / "README.md").write_text("old\n")
    result = _scaffold(tmp_path, isolated_xdg_config_home, "demo", str(dest))
    assert result.returncode == 0, result.stderr
    assert (dest / "README.md").read_text() == "old\n"
    assert f"skipped existing file {dest / 'README.md'}" in result.stdout.splitlines()
    assert f"+++ {dest / 'README.md'}" not in result.stdout


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
            '  a.txt: "{{ config.core.sprint.default_threshold_sp }}|'
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


class ReceiptCase(NamedTuple):
    """One scaffold receipt: destination state and flags in, stdout lines out.

    Expected lines carry `{dest}`, formatted with the run's destination.
    """

    existing: dict[str, str]
    args: tuple[str, ...]
    head: tuple[str, ...]
    contains: tuple[str, ...]
    summary: str
    tree: str = TREE
    line_count: int | None = None


RECEIPT_CASES = [
    pytest.param(
        ReceiptCase(
            existing={"README.md": "old\n"},
            args=("--force",),
            head=(),
            contains=(
                "--- {dest}/README.md",
                "+++ {dest}/README.md",
                "-old",
                "+hello ",
                "--- /dev/null",
                "+++ {dest}/src/main.py",
                "+print(1)",
                "created dir {dest}/_references",
            ),
            summary="scaffolded 4 paths — 2 dirs created, 1 files created, 1 files overwritten",
        ),
        id="diffs-dirs-and-summary",
    ),
    pytest.param(
        ReceiptCase(
            existing={},
            args=(),
            head=(
                "--- /dev/null",
                "+++ {dest}/a.txt",
                "@@ -0,0 +1,2 @@",
                "+one",
                "+two",
            ),
            contains=(),
            summary="scaffolded 1 paths — 0 dirs created, 1 files created, 0 files overwritten",
            tree='demo:\n  a.txt: "one\\ntwo\\n"\n',
        ),
        id="new-file-is-all-additions-from-dev-null",
    ),
    pytest.param(
        ReceiptCase(
            existing={"a.txt": "one\nold\nthree\n"},
            args=("--force",),
            head=(
                "--- {dest}/a.txt",
                "+++ {dest}/a.txt",
                "@@ -1,3 +1,3 @@",
                " one",
                "-old",
                "+two",
                " three",
            ),
            contains=(),
            summary="scaffolded 1 paths — 0 dirs created, 0 files created, 1 files overwritten",
            tree='demo:\n  a.txt: "one\\ntwo\\nthree\\n"\n',
        ),
        id="overwrite-carries-context-lines",
    ),
    pytest.param(
        ReceiptCase(
            existing={"a.txt": "same\n"},
            args=("--force",),
            head=(),
            contains=(),
            summary="scaffolded 0 paths — 0 dirs created, 0 files created, 0 files overwritten",
            tree='demo:\n  a.txt: "same\\n"\n',
            line_count=1,
        ),
        id="unchanged-file-prints-no-diff",
    ),
]


@pytest.mark.parametrize("case", RECEIPT_CASES)
def test_receipt_stdout(
    case: ReceiptCase, tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    for rel, body in case.existing.items():
        (dest / rel).write_text(body)

    result = _scaffold(
        tmp_path, isolated_xdg_config_home, "demo", str(dest), *case.args, tree=case.tree
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""

    lines = result.stdout.splitlines()
    head = [line.format(dest=dest) for line in case.head]
    assert lines[: len(head)] == head
    for line in case.contains:
        assert line.format(dest=dest) in lines
    assert lines[-1] == case.summary
    if case.line_count is not None:
        assert len(lines) == case.line_count


# --- Task 1.1: filename keys render through the seed env --------------------


class KeyCase(NamedTuple):
    """One scaffold run whose tree names files by template: tree and `--set` in,
    resulting paths and receipt out.

    `files` maps a path relative to the destination to its expected content.
    `stderr_contains` empty means the run is expected to succeed.
    """

    tree: str
    set_pairs: tuple[str, ...]
    files: dict[str, str]
    summary: str | None = None
    stderr_contains: tuple[str, ...] = ()
    absent: tuple[str, ...] = ()


KEY_CASES = [
    pytest.param(
        KeyCase(
            tree='demo:\n  "{{ slug }}.md": "body\\n"\n',
            set_pairs=("slug=my-plan",),
            files={"my-plan.md": "body\n"},
            summary="scaffolded 2 paths — 1 dirs created, 1 files created, 0 files overwritten",
        ),
        id="templated-file-key",
    ),
    pytest.param(
        KeyCase(
            tree='demo:\n  "{{ slug }}":\n    "{{ slug }}.md": "in {{ slug }}\\n"\n',
            set_pairs=("slug=nested",),
            files={"nested/nested.md": "in nested\n"},
            summary="scaffolded 3 paths — 2 dirs created, 1 files created, 0 files overwritten",
        ),
        id="templated-dir-key-nests",
    ),
    pytest.param(
        KeyCase(
            tree='demo:\n  "index.md": "body\\n"\n',
            set_pairs=("slug=unused",),
            files={"index.md": "body\n"},
            summary="scaffolded 2 paths — 1 dirs created, 1 files created, 0 files overwritten",
        ),
        id="literal-key-untouched",
    ),
    pytest.param(
        KeyCase(
            tree='demo:\n  "{{ slug }}.md": "body\\n"\n',
            set_pairs=("slug=../escape",),
            files={},
            stderr_contains=("demo.{{ slug }}.md", "unsafe filename key", "'../escape.md'"),
            absent=("../escape.md",),
        ),
        id="rendered-slash-is-rejected",
    ),
    pytest.param(
        KeyCase(
            tree='demo:\n  "{{ dots }}": "body\\n"\n',
            set_pairs=("dots=..",),
            files={},
            stderr_contains=("unsafe filename key", "'..'"),
        ),
        id="rendered-dotdot-is-rejected",
    ),
    pytest.param(
        KeyCase(
            tree='demo:\n  "{{ slug }}.md": "body\\n"\n',
            set_pairs=(),
            files={".md": "body\n"},
            summary="scaffolded 2 paths — 1 dirs created, 1 files created, 0 files overwritten",
        ),
        id="missing-set-variable-renders-empty",
    ),
]


@pytest.mark.parametrize("case", KEY_CASES)
def test_filename_keys_render(
    case: KeyCase, tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    dest = tmp_path / "out"
    args = [arg for pair in case.set_pairs for arg in ("--set", pair)]
    result = _scaffold(
        tmp_path, isolated_xdg_config_home, "demo", str(dest), *args, tree=case.tree
    )

    if case.stderr_contains:
        assert result.returncode == 1
        for fragment in case.stderr_contains:
            assert fragment in result.stderr
        assert not dest.exists()
    else:
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines()[-1] == case.summary

    for rel, content in case.files.items():
        assert (dest / rel).read_text() == content
    for rel in case.absent:
        assert not (dest / rel).exists()


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
    result = _run(
        "scaffold",
        "core.playbook_authoring_playbook.scaffold",
        str(dest),
        "--set",
        "name=demo",
        cwd=tmp_path,
    )
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
    dest = tmp_path / "vault"
    result = _run("scaffold", "core.setup_playbook.scaffold", str(dest), cwd=tmp_path)
    assert result.returncode == 0, result.stderr

    text = (dest / "sprints.md").read_text()
    assert text.startswith("```base\n")
    fence = text.split("```base\n", 1)[1].split("\n```", 1)[0]
    spec = yaml.safe_load(fence)

    # `In` re-adds both cached forms to `metrics_tokens_input`, which counts only what
    # was neither served from cache nor written to it — a few hundred tokens per run,
    # and misleading on its own as "everything sent in".
    assert spec["formulas"] == {
        "plan": "file.asLink(title)",
        "tokens_in": (
            "((metrics_tokens_input + metrics_tokens_cache_creation"
            ' + metrics_tokens_cache_read) / 1000000).round(1) + "M"'
        ),
        "tokens_out": '(metrics_tokens_output / 1000).round(0) + "k"',
        "cached": '(metrics_tokens_cache_read / 1000000).round(1) + "M"',
    }
    assert spec["properties"] == {
        "formula.plan": {"displayName": "Title"},
        "formula.tokens_in": {"displayName": "In"},
        "formula.tokens_out": {"displayName": "Out"},
        "formula.cached": {"displayName": "Cached"},
        "note.metrics_active_minutes": {"displayName": "Active min"},
        "note.metrics_models": {"displayName": "Models"},
    }
    # Scoped to the booping vault holding this sprints.md, so it stays correct when
    # the booping vault is nested inside a larger Obsidian vault.
    assert spec["filters"] == {
        "and": [
            'file.inFolder(this.file.folder + "/plans")',
            'file.name == "index"',
        ]
    }
    view = spec["views"][0]
    assert view["type"] == "table"
    assert view["order"] == [
        "status",
        "sp",
        "formula.plan",
        "summary",
        "created",
        "completed",
        "metrics_active_minutes",
        "metrics_models",
        "formula.tokens_in",
        "formula.tokens_out",
        "formula.cached",
    ]
    assert view["sort"] == [{"property": "created", "direction": "DESC"}]


def test_core_vault_scaffold_non_empty_destination_fills_the_gaps(
    tmp_path: Path,
) -> None:
    dest = tmp_path / "vault"
    dest.mkdir()
    (dest / "stray.md").write_text("x\n")

    result = _run("scaffold", "core.setup_playbook.scaffold", str(dest), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (dest / "sprints.md").exists()
    assert (dest / "stray.md").read_text() == "x\n"


def test_core_milestone_scaffold_seeds_the_milestone_contract(tmp_path: Path) -> None:
    plan = tmp_path / "vault" / "plans" / "demo"
    result = _run(
        "scaffold",
        "core.groom_playbook.milestone_scaffold",
        str(plan / "milestones"),
        "--set",
        "id=01",
        "--set",
        "slug=cli-surface",
        "--set",
        "title=Demo: it's \"fine\"",
        "--set",
        "sp=3",
        "--set",
        "plan=plans/demo/index.md",
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr

    text = (plan / "milestones" / "01-cli-surface.md").read_text()
    front, body = text.split("---\n", 2)[1:]
    assert list(yaml.safe_load(front).items()) == [
        ("id", "01"),
        ("title", "Demo: it's \"fine\""),
        ("sp", 3),
        ("status", "pending"),
        ("plan", "plans/demo/index.md"),
    ]
    assert body == (
        '\n# M01: Demo: it\'s "fine"\n'
        "\n## Tasks\n"
        "\n## Definition of Done\n"
        "\n## Verify\n"
    )


def test_scaffolded_milestones_query_by_the_shared_key(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    plan = vault / "plans" / "demo"
    result = _run(
        "scaffold", "core.groom_playbook.scaffold", str(plan),
        "--set", "title=Demo", "--set", "type=feature",
        "--stub-macro", "core.macros.date=20260810-00-00",
        "--stub-macro", "core.macros.git_commit=abc1234",
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert (plan / "milestones").is_dir()

    # 01 vs 08: unquoted zero-padded ids would land as int and str in one column.
    for id_, slug, sp in (("10", "third", "1"), ("01", "first", "3"), ("08", "second", "2")):
        result = _run(
            "scaffold", "core.groom_playbook.milestone_scaffold", str(plan / "milestones"),
            "--set", f"id={id_}", "--set", f"slug={slug}", "--set", f"title=M {id_}",
            "--set", f"sp={sp}", "--set", "plan=plans/demo/index.md", cwd=tmp_path,
        )
        assert result.returncode == 0, result.stderr

    result = _run(
        "query", "--project", str(vault), "--glob", "plans/demo/milestones/*.md",
        "--columns", "id,title,sp,status", "--sort", "id", "--output", "json",
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
    rows = [
        {k: v for k, v in row.items() if k not in ("path", "slug")}
        for row in json.loads(result.stdout)
    ]
    assert rows == [
        {"id": "01", "title": "M 01", "sp": 3, "status": "pending"},
        {"id": "08", "title": "M 08", "sp": 2, "status": "pending"},
        {"id": "10", "title": "M 10", "sp": 1, "status": "pending"},
    ]


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
    log = (vault / ".booping.log").read_text()
    assert log.count("[scaffold]") == 1
    assert "demo" in log
