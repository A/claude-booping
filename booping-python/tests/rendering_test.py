from pathlib import Path

from booping.cli import main
from booping.rendering import render

FIXTURES = Path(__file__).resolve().parent / "__fixtures__"


def get_fixture_path(name: str) -> Path:
    return FIXTURES / name


def test_render_smoke() -> None:
    template_path = (
        get_fixture_path("plugin-root-minimal")
        / "src"
        / "templates"
        / "skills"
        / "help.md.j2"
    )
    output = render(str(template_path))
    assert "Sprint threshold: 35" in output
    assert "feature: New user-facing capability" in output


def test_render_command_smoke() -> None:
    template_path = (
        get_fixture_path("plugin-root-minimal")
        / "src"
        / "templates"
        / "skills"
        / "help.md.j2"
    )
    rc = main(["render", str(template_path)])
    assert rc == 0