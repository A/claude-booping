from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from jinja2 import Environment
from pydantic import ValidationError

from booping.query import (
    QueryError,
    QuerySpec,
    Row,
    as_dict,
    discover,
    matches,
    run,
    slug_for,
)
from booping.rendering import LenientUndefined, get_plugin_root, make_query_filter

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


class TestOrderingOperators:
    def test_gt_is_strict(self) -> None:
        assert matches({"id": 10}, {"id:gt": 3})
        assert not matches({"id": 3}, {"id:gt": 3})

    def test_lt_is_strict(self) -> None:
        assert matches({"id": 3}, {"id:lt": 10})
        assert not matches({"id": 3}, {"id:lt": 3})

    def test_negative_operand_matches_every_number(self) -> None:
        assert matches({"id": 1}, {"id:gt": -1})
        assert matches({"id": 0}, {"id:gt": -1})

    @pytest.mark.parametrize("value", [10, 10.0, "10"])
    @pytest.mark.parametrize("operand", [10, "10", 10.0])
    def test_coercion_is_float_on_both_sides(self, value: object, operand: object) -> None:
        assert not matches({"id": value}, {"id:gt": operand})
        assert matches({"id": value}, {"id:gt": 9})
        assert matches({"id": value}, {"id:lt": 10.5})

    def test_fractional_values_compare_numerically(self) -> None:
        assert matches({"id": "10.5"}, {"id:gt": 10})
        assert not matches({"id": 10}, {"id:gt": "10.5"})

    @pytest.mark.parametrize("value", ["abc", None, "", [], {"a": 1}])
    def test_a_non_numeric_row_value_fails_the_clause(self, value: object) -> None:
        assert not matches({"id": value}, {"id:gt": 0})
        assert not matches({"id": value}, {"id:lt": 0})

    @pytest.mark.parametrize("operand", ["abc", None, "", []])
    def test_a_non_numeric_operand_fails_the_clause(self, operand: object) -> None:
        assert not matches({"id": 5}, {"id:gt": operand})
        assert not matches({"id": 5}, {"id:lt": operand})

    def test_a_jinja_undefined_operand_fails_the_clause(self) -> None:
        undefined = LenientUndefined(name="missing")
        assert not matches({"id": 5}, {"id:gt": undefined})
        assert not matches({"id": 5}, {"id:lt": undefined})

    def test_a_row_missing_the_field_fails_the_clause(self) -> None:
        assert not matches({"other": 5}, {"id:gt": 0})
        assert not matches({"other": 5}, {"id:lt": 0})

    def test_a_field_named_like_the_operator_cannot_shadow_it(self) -> None:
        # `x:gt` is dispatched as the operator, so the literal field is unreachable.
        assert not matches({"x:gt": 1}, {"x:gt": 0})
        assert matches({"x": 1}, {"x:gt": 0})

    def test_ordering_filters_rows_in_a_run(self, vault: Path) -> None:
        _plan(vault, "plans/small/index.md", status="done", sp="2")
        _plan(vault, "plans/large/index.md", status="done", sp="8")
        assert _slugs(vault, where={"sp:gt": 3}) == ["large"]
        assert _slugs(vault, where={"sp:lt": 3}) == ["small"]


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


class TestQueryFilterWithoutAVault:
    """The Jinja face resolves the root before it demands a vault."""

    def _rows(self, spec: dict[str, Any], source: str) -> str:
        env = Environment(undefined=LenientUndefined, autoescape=False)
        env.filters["query"] = make_query_filter({"specs": {"one": spec}})
        return env.from_string(source).render(context=None)

    SLUGS = "{{ ('specs.one' | query) | map(attribute='slug') | join(',') }}"

    def test_a_core_spec_runs(self) -> None:
        spec = {"glob": ["playbooks/*/playbook.md"], "root": "core"}
        assert "groom" in self._rows(spec, self.SLUGS).split(",")

    def test_a_vault_relative_spec_raises(self) -> None:
        with pytest.raises(QueryError, match="no vault resolved"):
            self._rows({"glob": PLAN_GLOBS}, self.SLUGS)


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

    def test_root_defaults_to_none(self) -> None:
        assert QuerySpec().root is None

    def test_root_core_is_accepted(self) -> None:
        assert QuerySpec.model_validate({"root": "core"}).root == "core"

    def test_an_unknown_root_names_the_value_and_the_legal_set(self) -> None:
        with pytest.raises(QueryError) as exc:
            QuerySpec.model_validate({"root": "plguin"})
        assert "plguin" in str(exc.value)
        assert "core" in str(exc.value)

    def test_an_unknown_key_is_rejected_rather_than_dropped(self) -> None:
        with pytest.raises(ValidationError) as exc:
            QuerySpec.model_validate({"glob": ["plans/*.md"], "rooot": "core"})
        assert "rooot" in str(exc.value)


class TestRoot:
    def test_core_globs_the_plugin_root(self, vault: Path) -> None:
        rows = run(QuerySpec(glob=["playbooks/*/playbook.md"], root="core"), vault)
        slugs = [row.slug for row in rows]
        assert "groom" in slugs
        assert (get_plugin_root() / "playbooks" / "groom" / "playbook.md").is_file()

    def test_a_core_row_path_is_plugin_root_relative(self, vault: Path) -> None:
        spec = QuerySpec(glob=["playbooks/*/playbook.md"], root="core")
        rows = {r.slug: r for r in run(spec, vault)}
        assert rows["groom"].path == "playbooks/groom/playbook.md"

    def test_core_needs_no_vault(self) -> None:
        rows = run(QuerySpec(glob=["playbooks/*/playbook.md"], root="core"), None)
        assert [r.slug for r in rows]

    def test_a_vault_relative_spec_without_a_vault_raises(self) -> None:
        with pytest.raises(QueryError):
            run(QuerySpec(glob=PLAN_GLOBS), None)

    def test_omitting_root_keeps_vault_resolution(self, vault: Path) -> None:
        rows = run(QuerySpec(glob=PLAN_GLOBS), vault)
        assert [r.path for r in rows] == [
            "plans/alpha/index.md",
            "plans/mid.md",
            "plans/zeta/index.md",
        ]
