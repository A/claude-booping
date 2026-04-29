from __future__ import annotations

import pytest
from jinja2 import Environment, FileSystemLoader

from booping.rendering import LenientUndefined, RenderCycleError, RenderDepthExceededError, render
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
