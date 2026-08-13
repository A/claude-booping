from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from jinja2 import Environment

from booping.query import QueryError, QuerySpec, Row, as_dict, run
from booping.rendering import LenientUndefined, make_query_filter

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
