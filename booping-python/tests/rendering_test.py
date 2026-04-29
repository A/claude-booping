from __future__ import annotations

from booping.rendering import render
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
    )
    assert "Hello" in result
