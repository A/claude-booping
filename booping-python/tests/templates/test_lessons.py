from __future__ import annotations

from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render
from tests.helpers import get_fixture_path

PARTIAL = "src/templates/_partials/_lessons.j2"


def _render_partial(vault: Path) -> str:
    plugin_root = get_plugin_root()
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    return render(
        template_path=plugin_root / PARTIAL,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
        plugin_root=plugin_root,
    )


def test_lessons_block_structure() -> None:
    vault = get_fixture_path("vault-full")
    result = _render_partial(vault)

    assert "## Lessons" in result
    assert "The following 1 lesson(s) are loaded" in result
    assert "Keep them in context; never silently violate a loaded lesson." in result
    assert "### Index" in result
    assert "`2026-01-20-prefer-explicit-over-implicit.md`" in result
    assert "### 2026-01-20-prefer-explicit-over-implicit — " in result
    assert "Prefer explicit return types on public functions." in result


def test_lessons_empty_vault_emits_nothing() -> None:
    vault = get_fixture_path("vault-empty")
    result = _render_partial(vault)
    assert result.strip() == ""


def test_lessons_index_entry_format() -> None:
    vault = get_fixture_path("vault-full")
    result = _render_partial(vault)
    # Each index entry: `<filename>` — <title>
    assert "— 2026-01-20-prefer-explicit-over-implicit" in result
