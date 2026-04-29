"""Smoke test: render stub renders a fixture template without error."""
from pathlib import Path
from booping.rendering import render
from booping.context import Context


def get_fixture_path(name: str) -> Path:
    return Path(__file__).parent / "__fixtures__" / name


def test_render_stub():
    """Render an arbitrary Jinja2 template against empty context."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    ctx = Context.assemble(plugin_root=plugin_root, vault=None)

    result = render(
        template_path="hello.j2",
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
        plugin_root=plugin_root,
    )
    # Template uses {{ name | default('World') }}, so without name it outputs "Hello World!"
    assert "Hello" in result