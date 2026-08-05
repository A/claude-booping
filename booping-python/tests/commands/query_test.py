from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from booping.commands.query import parse_where

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(BOOPING_BIN), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    root = tmp_path / "vault"
    _write(
        root / "plans" / "alpha" / "index.md",
        "---\nstatus: ready-for-dev\ntitle: Alpha\ncreated: 20260101\n---\n\nbody\n",
    )
    _write(
        root / "plans" / "beta" / "index.md",
        "---\nstatus: done\ntitle: Beta\ncreated: 20260303\n---\n\nbody\n",
    )
    _write(
        root / "plans" / "gamma" / "index.md",
        "---\nstatus: done\ntitle: Gamma\ncreated: 20260202\n---\n\nbody\n",
    )
    _write(
        root / "config.yaml",
        "queries:\n"
        "  done_plans:\n"
        "    glob:\n"
        "      - plans/*/index.md\n"
        "    where:\n"
        "      status: done\n"
        "    sort: '-created'\n"
        "not_a_spec: 7\n",
    )
    return root


class TestParseWhere:
    def test_equality(self) -> None:
        assert parse_where(["status=done"]) == {"status": "done"}

    def test_inequality_keeps_the_operator_suffix(self) -> None:
        assert parse_where(["status!=done"]) == {"status!": "done"}

    def test_membership_splits_on_commas(self) -> None:
        assert parse_where(["status:in=a, b"]) == {"status:in": ["a", "b"]}

    def test_value_may_contain_equals_signs(self) -> None:
        assert parse_where(["k=a=b"]) == {"k": "a=b"}

    @pytest.mark.parametrize("pair", ["status", "=done", "!=done", ":in=a,b"])
    def test_malformed_pairs_raise(self, pair: str) -> None:
        with pytest.raises(ValueError, match=".*"):
            parse_where([pair])


class TestAddressing:
    def test_config_path_resolves_and_runs(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--config", "queries.done_plans",
            "--output", "paths", cwd=tmp_path,
        )
        assert result.returncode == 0
        assert result.stdout == "plans/beta/index.md\nplans/gamma/index.md\n"

    def test_inline_globs_run_without_a_config_entry(
        self, vault: Path, tmp_path: Path
    ) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--where", "status=done", "--sort", "-created", "--output", "paths",
            cwd=tmp_path,
        )
        assert result.returncode == 0
        assert result.stdout == "plans/beta/index.md\nplans/gamma/index.md\n"

    def test_repeated_where_applies_both_clauses(
        self, vault: Path, tmp_path: Path
    ) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--where", "status=done", "--where", "title=Gamma", "--output", "paths",
            cwd=tmp_path,
        )
        assert result.returncode == 0
        assert result.stdout == "plans/gamma/index.md\n"

    def test_inline_flags_narrow_a_config_spec(
        self, vault: Path, tmp_path: Path
    ) -> None:
        result = _run(
            "query", "--project", str(vault), "--config", "queries.done_plans",
            "--where", "title=Beta", "--output", "paths", cwd=tmp_path,
        )
        assert result.returncode == 0
        assert result.stdout == "plans/beta/index.md\n"

    def test_no_matches_exits_zero(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--where", "status=nope", "--output", "json", cwd=tmp_path,
        )
        assert result.returncode == 0
        assert json.loads(result.stdout) == []

    def test_help_lists_every_flag(self, tmp_path: Path) -> None:
        result = _run("query", "--help", cwd=tmp_path)
        assert result.returncode == 0
        for flag in ("--config", "--glob", "--where", "--sort", "--columns",
                     "--output", "--project"):
            assert flag in result.stdout


class TestUserErrors:
    def test_malformed_where_pair(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--where", "status", cwd=tmp_path,
        )
        assert result.returncode == 1
        assert result.stdout == ""
        assert "--where" in result.stderr

    def test_unknown_config_path(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--config", "queries.nope", cwd=tmp_path
        )
        assert result.returncode == 1
        assert result.stdout == ""
        assert "no query spec at config path: queries.nope" in result.stderr

    def test_non_mapping_config_value(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--config", "not_a_spec", cwd=tmp_path
        )
        assert result.returncode == 1
        assert result.stdout == ""
        assert "not a query spec mapping" in result.stderr

    def test_distinct_messages_per_error(self, vault: Path, tmp_path: Path) -> None:
        malformed = _run(
            "query", "--project", str(vault), "--glob", "x/*.md", "--where", "k",
            cwd=tmp_path,
        ).stderr
        unknown = _run(
            "query", "--project", str(vault), "--config", "queries.nope", cwd=tmp_path
        ).stderr
        shape = _run(
            "query", "--project", str(vault), "--config", "not_a_spec", cwd=tmp_path
        ).stderr
        assert len({malformed, unknown, shape}) == 3

    def test_both_addressing_forms(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--config", "queries.done_plans",
            "--glob", "plans/*/index.md", cwd=tmp_path,
        )
        assert result.returncode == 1
        assert "mutually exclusive" in result.stderr

    def test_neither_addressing_form(self, vault: Path, tmp_path: Path) -> None:
        result = _run("query", "--project", str(vault), cwd=tmp_path)
        assert result.returncode == 1
        assert "one of --config or --glob is required" in result.stderr

    def test_unknown_output_format(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--output", "csv", cwd=tmp_path,
        )
        assert result.returncode == 1
        assert "unknown --output format" in result.stderr


class TestOutputFormats:
    def test_table_escapes_pipes_and_collapses_newlines(self, tmp_path: Path) -> None:
        root = tmp_path / "vault"
        _write(
            root / "plans" / "one" / "index.md",
            '---\ntitle: "A | B"\nsummary: |-\n  first\n  second\n---\n\nbody\n',
        )
        result = _run(
            "query", "--project", str(root), "--glob", "plans/*/index.md",
            "--columns", "title,summary", cwd=tmp_path,
        )
        assert result.returncode == 0
        lines = result.stdout.splitlines()
        assert lines[0] == "| title | summary | path | slug |"
        assert lines[1] == "| --- | --- | --- | --- |"
        assert lines[2] == "| A \\| B | first second | plans/one/index.md | one |"
        assert len(lines) == 3

    def test_table_is_the_default_format(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--columns", "title", cwd=tmp_path,
        )
        assert result.returncode == 0
        assert result.stdout.startswith("| title | path | slug |\n")

    def test_json_is_an_array_of_objects(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--output", "json", cwd=tmp_path,
        )
        assert result.returncode == 0
        parsed: list[dict[str, str]] = json.loads(result.stdout)
        assert isinstance(parsed, list)
        assert [row["slug"] for row in parsed] == ["alpha", "beta", "gamma"]
        assert parsed[0]["status"] == "ready-for-dev"

    def test_yaml_round_trips(self, vault: Path, tmp_path: Path) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--output", "yaml", cwd=tmp_path,
        )
        assert result.returncode == 0
        parsed: list[dict[str, str]] = yaml.safe_load(result.stdout)
        assert [row["slug"] for row in parsed] == ["alpha", "beta", "gamma"]

    def test_paths_emits_one_relative_path_per_line(
        self, vault: Path, tmp_path: Path
    ) -> None:
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--output", "paths", cwd=tmp_path,
        )
        assert result.returncode == 0
        assert result.stdout == (
            "plans/alpha/index.md\nplans/beta/index.md\nplans/gamma/index.md\n"
        )

    @pytest.mark.parametrize("output", ["table", "json", "yaml", "paths"])
    def test_warnings_go_to_stderr_only(
        self, vault: Path, tmp_path: Path, output: str
    ) -> None:
        _write(root_index := vault / "plans" / "broken" / "index.md", "---\n: :\n---\n")
        assert root_index.exists()
        result = _run(
            "query", "--project", str(vault), "--glob", "plans/*/index.md",
            "--output", output, cwd=tmp_path,
        )
        assert result.returncode == 0
        assert "broken" in result.stderr
        assert "broken" not in result.stdout
