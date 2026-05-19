from __future__ import annotations

from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render
from tests.helpers import get_fixture_path  # noqa: I001

SKILL_TEMPLATE = "src/templates/skills/develop.md.j2"


def _render_develop(vault: Path) -> str:
    plugin_root = get_plugin_root()
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    return render(
        template_path=plugin_root / SKILL_TEMPLATE,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
        plugin_root=plugin_root,
    )


def test_default_config_renders_native_invocation_lines() -> None:
    vault = get_fixture_path("vault-empty")
    result = _render_develop(vault)

    assert 'Invoke via the `Agent` tool with `subagent_type="booping-developer"`.' in result
    assert 'Invoke via the `Agent` tool with `subagent_type="booping-researcher"`.' in result

    # Each native entry still renders its good_for block; researcher carries a bad_for.
    assert "### `booping-developer`" in result
    assert "### `booping-researcher`" in result
    assert "**Good for:**" in result
    assert "**Bad for:**" in result


def test_cli_override_filters_internal_and_renders_cli_invocation() -> None:
    vault = get_fixture_path("vault-with-cli-agent")
    result = _render_develop(vault)

    # disable_internal_agents: true drops native entries
    assert "### `booping-developer`" not in result
    assert "### `booping-researcher`" not in result

    # pi-mesh cli entry rendered with cli invocation line
    assert "### `pi-mesh`" in result
    assert (
        "This is a `cli` agent. To run it, execute: `booping run-agent pi-mesh` "
        "(pipe the briefing on stdin)."
    ) in result

    # Underlying command never leaks into rendered skill prose
    assert "pi --print" not in result
