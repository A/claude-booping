from __future__ import annotations

from pathlib import Path

import pytest

from booping.query import QuerySpec, discover, run, slug_for

PLAN_GLOBS = ["plans/*/index.md", "plans/*.md"]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _plan(vault: Path, rel: str, **fm: str) -> None:
    lines = "\n".join(f"{k}: {v}" for k, v in fm.items())
    _write(vault / rel, f"---\n{lines}\n---\n\nbody\n")


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    # Filesystem order deliberately differs from slug order.
    _plan(tmp_path, "plans/zeta/index.md", status="done", title="Zeta")
    _plan(tmp_path, "plans/mid.md", status="in-progress", title="Mid")
    _plan(tmp_path, "plans/alpha/index.md", status="ready-for-dev", title="Alpha")
    return tmp_path


class TestSlugFor:
    def test_literal_final_segment_takes_the_directory_name(self) -> None:
        assert slug_for("plans/*/index.md", Path("plans/alpha/index.md")) == "alpha"

    def test_wildcard_final_segment_takes_the_stem(self) -> None:
        assert slug_for("plans/*.md", Path("plans/mid.md")) == "mid"

    def test_single_segment_pattern_takes_the_stem(self) -> None:
        assert slug_for("*.md", Path("mid.md")) == "mid"


class TestDiscover:
    def test_one_entry_per_slug_earlier_glob_wins(self, vault: Path) -> None:
        # A flat file shares the slug of a directory plan; the earlier glob claims it.
        _plan(vault, "plans/alpha.md", status="backlog", title="Alpha flat")
        found = dict(discover(vault, PLAN_GLOBS))
        assert found["alpha"] == vault / "plans" / "alpha" / "index.md"
        assert sorted(found) == ["alpha", "mid", "zeta"]

    def test_reversed_glob_order_flips_the_winner(self, vault: Path) -> None:
        _plan(vault, "plans/alpha.md", status="backlog", title="Alpha flat")
        found = dict(discover(vault, list(reversed(PLAN_GLOBS))))
        assert found["alpha"] == vault / "plans" / "alpha.md"

    def test_directories_are_not_rows(self, vault: Path) -> None:
        (vault / "plans" / "notes.md").mkdir(parents=True)
        assert "notes" not in dict(discover(vault, PLAN_GLOBS))


class TestRun:
    def test_rows_carry_frontmatter_path_and_slug(self, vault: Path) -> None:
        rows = run(QuerySpec(glob=PLAN_GLOBS), vault)
        alpha = rows[0]
        assert alpha["slug"] == "alpha"
        assert alpha["path"] == "plans/alpha/index.md"
        assert alpha["status"] == "ready-for-dev"
        assert alpha["title"] == "Alpha"

    def test_rows_are_slug_sorted_without_a_sort(self, vault: Path) -> None:
        rows = run(QuerySpec(glob=PLAN_GLOBS), vault)
        assert [r["slug"] for r in rows] == ["alpha", "mid", "zeta"]

    def test_one_row_per_slug_across_globs(self, vault: Path) -> None:
        _plan(vault, "plans/alpha.md", status="backlog", title="Alpha flat")
        rows = run(QuerySpec(glob=PLAN_GLOBS), vault)
        assert [r["slug"] for r in rows] == ["alpha", "mid", "zeta"]
        assert rows[0]["title"] == "Alpha"

    def test_malformed_file_is_skipped_with_a_warning(
        self, vault: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _write(vault / "plans" / "broken" / "index.md", "---\nstatus: [unterminated\n---\n")
        rows = run(QuerySpec(glob=PLAN_GLOBS), vault)
        assert [r["slug"] for r in rows] == ["alpha", "mid", "zeta"]
        err = capsys.readouterr().err
        assert "broken/index.md" in err
        assert "warning: skipping" in err

    def test_file_without_frontmatter_yields_path_and_slug_only(self, vault: Path) -> None:
        _write(vault / "plans" / "bare.md", "just a body\n")
        rows = {r["slug"]: r for r in run(QuerySpec(glob=PLAN_GLOBS), vault)}
        assert rows["bare"] == {"path": "plans/bare.md", "slug": "bare"}

    def test_no_matches_is_an_empty_list(self, tmp_path: Path) -> None:
        assert run(QuerySpec(glob=PLAN_GLOBS), tmp_path) == []


class TestQuerySpec:
    def test_defaults(self) -> None:
        spec = QuerySpec()
        assert spec.glob == []
        assert spec.where == {}
        assert spec.sort is None
        assert spec.columns is None

    def test_carries_where_sort_and_columns(self) -> None:
        spec = QuerySpec.model_validate(
            {
                "glob": ["plans/*.md"],
                "where": {"status": "done"},
                "sort": "-created",
                "columns": ["status", "title"],
            }
        )
        assert spec.glob == ["plans/*.md"]
        assert spec.where == {"status": "done"}
        assert spec.sort == "-created"
        assert spec.columns == ["status", "title"]
