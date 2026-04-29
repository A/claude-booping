from __future__ import annotations

from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render
from tests.helpers import get_fixture_path  # noqa: I001

PARTIAL = "src/templates/_partials/_extra_instructions.j2"


def _render_partial(vault: Path, key: str) -> str:
    plugin_root = get_plugin_root()
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    return render(
        template_path=plugin_root / PARTIAL,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={"extra_instruction_key": key},
        plugin_root=plugin_root,
    )


def test_extra_instructions_present() -> None:
    vault = get_fixture_path("vault-full")
    result = _render_partial(vault, "skill_groom")

    assert "## User-specific instructions" in result
    assert (
        "These instructions come from prior coding sessions and user feedback "
        "in this project. They override the skill instructions above — where "
        "they disagree, follow these."
    ) in result
    assert "Always link new plans to an existing epic when one exists." in result
    assert "Prefer splitting plans over 8 SP rather than leaving them large." in result


def test_extra_instructions_absent_key_emits_nothing() -> None:
    vault = get_fixture_path("vault-full")
    result = _render_partial(vault, "skill_chat")
    assert result.strip() == ""


def test_extra_instructions_empty_vault_emits_nothing() -> None:
    vault = get_fixture_path("vault-empty")
    result = _render_partial(vault, "skill_groom")
    assert result.strip() == ""
