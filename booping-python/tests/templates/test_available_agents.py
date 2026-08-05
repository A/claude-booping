from __future__ import annotations

from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render
from tests.helpers import get_fixture_path  # noqa: I001

SKILL_TEMPLATE = "src/templates/skills/code-review.md.j2"


def _render_skill(vault: Path) -> str:
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


def test_default_config_renders_native_agent_rows() -> None:
    vault = get_fixture_path("vault-empty")
    result = _render_skill(vault)

    # Internal native agents are namespaced; bare forms must not appear.
    assert "| `booping:booping-developer` |" in result
    assert "| `booping:booping-researcher` |" in result
    assert "| `booping-developer` |" not in result
    assert "| `booping-researcher` |" not in result

    # Each native row still carries its good_for cell; researcher carries a bad_for.
    assert (
        "Applying user-approved non-trivial fixes surfaced by the review "
        "(BLOCKER or SUGGESTION)" in result
    )
    assert "Small greps or existence checks that fit in a few lines of output" in result


def test_non_internal_agent_renders_plain_agent_id() -> None:
    """A non-internal agent renders plainly as `<agent>` — no `booping:` prefix.
    disable_internal_agents drops internal entries, so the native pair is gone
    here but test-no-type stays."""
    vault = get_fixture_path("vault-disable-internal-agents")
    result = _render_skill(vault)

    # disable_internal_agents: true drops native entries
    assert "booping:booping-developer" not in result
    assert "booping:booping-researcher" not in result

    assert "| `test-no-type` |" in result
    assert "| `booping:test-no-type` |" not in result
