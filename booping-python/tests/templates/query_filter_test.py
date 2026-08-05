from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from booping.context import Context
from booping.query import QueryError, Row, as_table
from booping.rendering import build_source_env, get_plugin_root, render

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"

VAULT_CONFIG = """
plans:
  glob:
    - plans/*/index.md
    - plans/*.md
  all:
    sort: '-created'
  done:
    where:
      status: done
"""


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
        root / "plans" / "beta.md",
        "---\nstatus: done\ntitle: Beta | piped\ncreated: 20260303\n---\n\nbody\n",
    )
    _write(root / "config.yaml", VAULT_CONFIG)
    return root


def _context(vault: Path) -> Context:
    return Context.assemble(start=vault, plugin_root=get_plugin_root(), vault_override=vault)


def _render_source(vault: Path, tmp_path: Path, source: str) -> str:
    """Render *source* the way a skill body renders — through `rendering.render`."""
    ctx = _context(vault)
    template = tmp_path / "body.md.j2"
    template.write_text(source)
    return render(
        template_path=template,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
        plugin_root=get_plugin_root(),
    )


SLUGS = "{{ ('plans.all' | query) | map(attribute='slug') | join(',') }}"
DONE_SLUGS = (
    "{{ ('plans.all' | query(where={'status': 'done'}))"
    " | map(attribute='slug') | join(',') }}"
)


class TestQueryFilterSurfaces:
    def test_skill_body_gets_rows(self, vault: Path, tmp_path: Path) -> None:
        assert _render_source(vault, tmp_path, SLUGS).strip() == "beta,alpha"

    def test_rows_expose_frontmatter_as_attributes(
        self, vault: Path, tmp_path: Path
    ) -> None:
        source = "{% set r = ('plans.all' | query) | first %}{{ r.title }}/{{ r.path }}"
        assert _render_source(vault, tmp_path, source) == "Beta | piped/plans/beta.md"

    def test_scaffold_seed_string_gets_rows(self, vault: Path) -> None:
        """The scaffold seed path: build_source_env + from_string."""
        ctx = _context(vault)
        env = build_source_env(context=ctx, config=ctx.config)
        assert env.from_string(SLUGS).render().strip() == "beta,alpha"

    def test_playbook_body_gets_rows(self, vault: Path, tmp_path: Path) -> None:
        pb = vault / "_playbooks" / "queryish"
        _write(
            pb / "playbook.md",
            "---\n"
            "name: queryish\n"
            "title: Queryish\n"
            "summary: Query from a playbook body.\n"
            "trigger: never — a fixture\n"
            "jinja: true\n"
            "---\n\n"
            "# Queryish\n\n" + SLUGS + "\n",
        )
        _write(pb / "playbook.yaml", "graph:\n  only: []\n")
        _write(
            pb / "only" / "prompt.md",
            "---\nsummary: Do nothing.\nreview_gate: false\n---\n\nNothing.\n",
        )
        result = subprocess.run(
            [str(BOOPING_BIN), "render-playbook", "queryish", "--project", str(vault)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "STOP" not in result.stdout, result.stdout
        assert "beta,alpha" in result.stdout


class TestInlineNarrowing:
    def test_kwargs_narrow_the_declared_spec(self, vault: Path, tmp_path: Path) -> None:
        source = DONE_SLUGS
        assert _render_source(vault, tmp_path, source).strip() == "beta"

    def test_narrowing_does_not_leak_into_later_calls(
        self, vault: Path, tmp_path: Path
    ) -> None:
        source = DONE_SLUGS + "|" + SLUGS
        assert _render_source(vault, tmp_path, source).strip() == "beta|beta,alpha"

    def test_declared_where_survives_a_narrowing_on_another_key(
        self, vault: Path, tmp_path: Path
    ) -> None:
        source = "{{ ('plans.done' | query(sort='slug')) | map(attribute='slug') | join(',') }}"
        assert _render_source(vault, tmp_path, source).strip() == "beta"


class TestAsTableFilter:
    def test_matches_the_command_table_for_the_same_rows(
        self, vault: Path, tmp_path: Path
    ) -> None:
        source = "{{ ('plans.all' | query) | as_table(columns=['status', 'title']) }}"
        rendered = _render_source(vault, tmp_path, source)
        command = subprocess.run(
            [
                str(BOOPING_BIN), "query", "--project", str(vault),
                "--config", "plans.all", "--columns", "status,title",
                "--output", "table",
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert command.returncode == 0, command.stderr
        assert rendered == command.stdout

    def test_escapes_pipes_and_keeps_declared_column_order(
        self, vault: Path, tmp_path: Path
    ) -> None:
        source = "{{ ('plans.all' | query) | as_table(columns=['title', 'status']) }}"
        lines = _render_source(vault, tmp_path, source).splitlines()
        assert lines[0] == "| title | status | path | slug |"
        assert lines[2].startswith("| Beta \\| piped | done |")

    def test_column_free_call_uses_the_row_keys(self) -> None:
        rows = [Row({"a": 1, "b": None})]
        assert as_table(rows) == "| a | b |\n| --- | --- |\n| 1 |  |\n"


class TestFailureIsLoud:
    def test_unresolvable_path_raises_naming_it(self, vault: Path, tmp_path: Path) -> None:
        with pytest.raises(QueryError, match="plans.nope"):
            _render_source(vault, tmp_path, "{{ 'plans.nope' | query }}")

    def test_non_mapping_value_raises_naming_the_path(
        self, vault: Path, tmp_path: Path
    ) -> None:
        with pytest.raises(QueryError, match="plans.glob"):
            _render_source(vault, tmp_path, "{{ 'plans.glob' | query }}")
