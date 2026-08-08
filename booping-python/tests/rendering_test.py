from __future__ import annotations

import re
from datetime import datetime

import pytest
from jinja2 import Environment, FileSystemLoader

from booping.context import Context
from booping.context.project import Project
from booping.rendering import (
    LenientUndefined,
    RenderCycleError,
    RenderDepthExceededError,
    build_source_env,
    render,
)
from booping.tools import Tools
from tests.helpers import get_fixture_path


def test_render_hello_smoke() -> None:
    fixture = get_fixture_path("plugin-root-minimal")
    template_path = fixture / "src" / "templates" / "hello.j2"
    result = render(
        template_path=template_path,
        context={},
        config={},
        tools={},
        kwargs={},
        plugin_root=fixture,
    )
    assert "Hello" in result


def _make_tools(fixture_path: object) -> Tools:
    from pathlib import Path

    fp = fixture_path if isinstance(fixture_path, Path) else Path(str(fixture_path))
    templates_dir = fp / "src" / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=LenientUndefined,
        keep_trailing_newline=True,
    )
    return Tools(env=env, context={}, config={}, plugin_root=fp, render_stack=[])


def test_tools_render_same_output_as_include() -> None:
    """tools.render of an idempotent partial produces same output as direct render."""
    fixture = get_fixture_path("plugin-root-minimal")
    partial_path = fixture / "src" / "templates" / "partial.j2"

    direct = render(
        template_path=partial_path,
        context={},
        config={},
        tools={},
        kwargs={},
        plugin_root=fixture,
    )
    tools = _make_tools(fixture)
    via_tools = tools.render("src/templates/partial.j2")

    assert via_tools.strip() == direct.strip()


def test_tools_render_kwargs_available() -> None:
    """tools.render(path, foo='bar') makes kwargs.foo available; bare foo is undefined."""
    fixture = get_fixture_path("plugin-root-minimal")
    tools = _make_tools(fixture)
    result = tools.render("src/templates/uses_kwargs.j2", foo="bar")

    assert "kwarg foo = bar" in result
    # bare foo should NOT resolve to "bar" (lenient undefined renders as empty)
    assert "bare foo = bar" not in result


def test_tools_render_self_reference_raises_cycle_error() -> None:
    fixture = get_fixture_path("plugin-root-minimal")
    self_ref = fixture / "src" / "templates" / "self_ref.j2"

    with pytest.raises(RenderCycleError):
        render(
            template_path=self_ref,
            context={},
            config={},
            tools={},
            kwargs={},
            plugin_root=fixture,
        )


def test_tools_render_mutual_reference_raises_cycle_error() -> None:
    fixture = get_fixture_path("plugin-root-minimal")
    mutual_a = fixture / "src" / "templates" / "mutual_a.j2"

    with pytest.raises(RenderCycleError):
        render(
            template_path=mutual_a,
            context={},
            config={},
            tools={},
            kwargs={},
            plugin_root=fixture,
        )


def test_macro_global_runs_a_declared_argv() -> None:
    fixture = get_fixture_path("plugin-root-minimal")
    env = build_source_env(
        context={},
        config={"macros": {"now": ["date", "+%Y%m%d"]}},
        plugin_root=fixture,
    )

    rendered = env.from_string("{{ macro('macros.now') }}").render()

    assert rendered == datetime.now().strftime("%Y%m%d")


def test_macro_stubbed_by_config_returns_the_literal() -> None:
    fixture = get_fixture_path("plugin-root-minimal")
    env = build_source_env(
        context={},
        config={
            "macros": {"now": ["date", "+%Y%m%d"]},
            "macro_stubs": {"macros.now": "19700101-00-00"},
        },
        plugin_root=fixture,
    )

    rendered = env.from_string("{{ macro('macros.now') }}").render()

    assert rendered == "19700101-00-00"


def test_macro_default_shape_from_core_config() -> None:
    fixture = get_fixture_path("plugin-root-minimal")
    env = build_source_env(
        context={},
        config={"macros": {"date": ["date"]}},
        plugin_root=fixture,
    )

    rendered = env.from_string("{{ macro('macros.date', '+%Y%m%d-%H-%M') }}").render()

    assert re.fullmatch(r"\d{8}-\d{2}-\d{2}", rendered)


def _project_context(latest_migration: int) -> Context:
    from pathlib import Path

    return Context(
        project=Project(
            name="p",
            directory=Path("/tmp/vault"),
            repo_directory=Path("/tmp/repo"),
            latest_migration=latest_migration,
        )
    )


def test_booping_global_in_render(tmp_path: object) -> None:
    from pathlib import Path

    fixture = get_fixture_path("plugin-root-minimal")
    scratch = Path(str(tmp_path)) / "scratch.j2"
    scratch.write_text("{{ booping.latest_migration }}")

    result = render(
        template_path=scratch,
        context=_project_context(4),
        config={},
        tools={},
        kwargs={},
        plugin_root=fixture,
    )

    assert result == "4"


def test_booping_global_in_source_env() -> None:
    """The scaffold seed path: build_source_env + from_string."""
    fixture = get_fixture_path("plugin-root-minimal")
    env = build_source_env(
        context=_project_context(9), config={}, plugin_root=fixture
    )

    assert env.from_string("{{ booping.latest_migration }}").render() == "9"


def test_booping_global_defaults_to_minus_one_without_project() -> None:
    fixture = get_fixture_path("plugin-root-minimal")
    env = build_source_env(context=Context(), config={}, plugin_root=fixture)

    assert env.from_string("{{ booping.latest_migration }}").render() == "-1"


def test_booping_global_in_playbook_env() -> None:
    from booping.commands.render_playbook import build_env

    env = build_env(context=_project_context(3))

    assert env.from_string("{{ booping.latest_migration }}").render() == "3"


def test_playbook_env_without_context_has_no_booping_global_or_query_filter() -> None:
    """The lesson-rendering branch: neither surface is wired.

    `booping` is an undefined name and renders empty; `query` is an absent filter and
    so fails at compile time — Jinja has no undefined-filter fallback.
    """
    from jinja2 import TemplateAssertionError

    from booping.commands.render_playbook import build_env

    env = build_env()

    assert env.from_string("[{{ booping.latest_migration }}]").render() == "[]"
    with pytest.raises(TemplateAssertionError):
        env.from_string("[{{ 'a.b' | query }}]")


def test_tools_render_depth_limit() -> None:
    fixture = get_fixture_path("plugin-root-minimal")
    deep_a = fixture / "src" / "templates" / "deep_a.j2"

    with pytest.raises(RenderDepthExceededError):
        render(
            template_path=deep_a,
            context={},
            config={},
            tools={},
            kwargs={},
            plugin_root=fixture,
        )
