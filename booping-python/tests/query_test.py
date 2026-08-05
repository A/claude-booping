from __future__ import annotations

from pathlib import Path

import pytest
from jinja2 import Environment

from booping.query import QuerySpec, Row, as_dict, discover, run, slug_for
from booping.rendering import LenientUndefined

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
        assert as_dict(rows["bare"]) == {"path": "plans/bare.md", "slug": "bare"}

    def test_no_matches_is_an_empty_list(self, tmp_path: Path) -> None:
        assert run(QuerySpec(glob=PLAN_GLOBS), tmp_path) == []


@pytest.fixture
def dated_vault(tmp_path: Path) -> Path:
    _plan(tmp_path, "plans/alpha/index.md", status="ready-for-dev", created="20260103")
    _plan(tmp_path, "plans/mid.md", status="in-progress", created="20260101")
    _plan(tmp_path, "plans/zeta/index.md", status="done", created="20260102")
    _plan(tmp_path, "plans/undated/index.md", status="done")
    return tmp_path


def _slugs(vault: Path, **spec: object) -> list[str]:
    rows = run(QuerySpec.model_validate({"glob": PLAN_GLOBS, **spec}), vault)
    return [r["slug"] for r in rows]


class TestWhere:
    def test_equality_keeps_only_matching_rows(self, vault: Path) -> None:
        assert _slugs(vault, where={"status": "ready-for-dev"}) == ["alpha"]

    def test_inequality_drops_matching_rows(self, vault: Path) -> None:
        assert _slugs(vault, where={"status!": "done"}) == ["alpha", "mid"]

    def test_in_keeps_rows_matching_any_option(self, vault: Path) -> None:
        assert _slugs(vault, where={"status:in": ["done", "ready-for-dev"]}) == ["alpha", "zeta"]

    def test_clauses_are_conjunctive(self, vault: Path) -> None:
        assert _slugs(vault, where={"status": "done", "title": "Mid"}) == []

    @pytest.mark.parametrize(
        "where",
        [{"sp": "3"}, {"sp!": "5"}, {"sp:in": ["3"]}],
    )
    def test_a_row_missing_the_field_is_excluded_by_every_operator(
        self, vault: Path, where: dict[str, object]
    ) -> None:
        _plan(vault, "plans/sized/index.md", status="done", sp="3")
        assert _slugs(vault, where=where) == ["sized"]

    def test_no_where_keeps_every_row(self, vault: Path) -> None:
        assert _slugs(vault, where={}) == ["alpha", "mid", "zeta"]


class TestSort:
    def test_ascending_by_field(self, dated_vault: Path) -> None:
        assert _slugs(dated_vault, sort="created")[:3] == ["mid", "zeta", "alpha"]

    def test_descending_by_field(self, dated_vault: Path) -> None:
        assert _slugs(dated_vault, sort="-created")[:3] == ["alpha", "zeta", "mid"]

    def test_rows_missing_the_field_come_last_in_both_directions(self, dated_vault: Path) -> None:
        assert _slugs(dated_vault, sort="created")[-1] == "undated"
        assert _slugs(dated_vault, sort="-created")[-1] == "undated"

    def test_null_counts_as_missing(self, dated_vault: Path) -> None:
        _write(dated_vault / "plans" / "nulled.md", "---\nstatus: done\ncreated: null\n---\n")
        assert _slugs(dated_vault, sort="created")[-2:] == ["nulled", "undated"]


class TestColumns:
    def test_projection_keeps_declared_keys_plus_path_and_slug(self, vault: Path) -> None:
        rows = run(QuerySpec(glob=PLAN_GLOBS, columns=["status", "title"]), vault)
        assert list(as_dict(rows[0])) == ["status", "title", "path", "slug"]

    def test_a_declared_path_column_is_not_duplicated(self, vault: Path) -> None:
        rows = run(QuerySpec(glob=PLAN_GLOBS, columns=["path", "status"]), vault)
        assert list(as_dict(rows[0])) == ["path", "status", "slug"]

    def test_empty_columns_leaves_only_path_and_slug(self, vault: Path) -> None:
        rows = run(QuerySpec(glob=PLAN_GLOBS, columns=[]), vault)
        assert as_dict(rows[0]) == {"path": "plans/alpha/index.md", "slug": "alpha"}


class TestRow:
    def test_frontmatter_keys_are_attributes(self, vault: Path) -> None:
        row = run(QuerySpec(glob=PLAN_GLOBS), vault)[0]
        assert row.status == "ready-for-dev"
        assert row.path == "plans/alpha/index.md"
        assert row.slug == "alpha"

    def test_a_dict_method_name_returns_the_frontmatter_value(self, vault: Path) -> None:
        _plan(vault, "plans/colliding/index.md", items="two", keys="three", get="four")
        rows = {r["slug"]: r for r in run(QuerySpec(glob=PLAN_GLOBS), vault)}
        row = rows["colliding"]
        assert row.items == "two"
        assert row.keys == "three"
        assert row.get == "four"

    def test_nested_mappings_are_attribute_accessible(self, vault: Path) -> None:
        _write(vault / "plans" / "nested.md", "---\nmeta:\n  owner: anton\n---\n")
        rows = {r["slug"]: r for r in run(QuerySpec(glob=PLAN_GLOBS), vault)}
        assert rows["nested"].meta.owner == "anton"

    def test_mappings_inside_lists_are_attribute_accessible(self, vault: Path) -> None:
        _write(vault / "plans" / "listed.md", "---\ntasks:\n  - id: 1\n---\n")
        rows = {r["slug"]: r for r in run(QuerySpec(glob=PLAN_GLOBS), vault)}
        assert rows["listed"].tasks[0].id == 1

    def test_an_absent_key_raises_attribute_error(self, vault: Path) -> None:
        row = run(QuerySpec(glob=PLAN_GLOBS), vault)[0]
        with pytest.raises(AttributeError):
            _ = row.absent

    def test_as_dict_unwraps_recursively(self, vault: Path) -> None:
        _write(vault / "plans" / "nested.md", "---\nmeta:\n  owner: anton\n---\n")
        rows = {r["slug"]: r for r in run(QuerySpec(glob=PLAN_GLOBS), vault)}
        assert as_dict(rows["nested"])["meta"] == {"owner": "anton"}


class TestRowUnderJinja:
    def _render(self, source: str, row: Row) -> str:
        env = Environment(undefined=LenientUndefined, autoescape=False)
        return env.from_string(source).render(row=row)

    def test_attribute_lookup_wins_over_dict_methods(self, vault: Path) -> None:
        _plan(vault, "plans/colliding/index.md", items="two")
        rows = {r["slug"]: r for r in run(QuerySpec(glob=PLAN_GLOBS), vault)}
        assert self._render("{{ row.items }}", rows["colliding"]) == "two"

    def test_an_absent_key_renders_empty(self, vault: Path) -> None:
        row = run(QuerySpec(glob=PLAN_GLOBS), vault)[0]
        assert self._render("{{ row.absent }}", row) == ""
        assert self._render("{{ row.absent.deeper }}", row) == ""


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
