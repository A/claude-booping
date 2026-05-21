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


def _phase_slice(body: str, phase_header: str, next_header: str) -> str:
    start = body.index(phase_header)
    end = body.index(next_header, start)
    return body[start:end]


def test_phase_3_step_3_no_hardcoded_booping_developer() -> None:
    body = _render_develop(get_fixture_path("vault-empty"))
    phase3 = _phase_slice(body, "## Phase 3 Execute", "## Phase 4 Finalize")
    assert "booping-developer" not in phase3


def test_phase_1_omits_worker_selection() -> None:
    body = _render_develop(get_fixture_path("vault-empty"))
    phase1 = _phase_slice(body, "## Phase 1 Plan groupings", "## Phase 2 Branch")

    # Worker-selection logic lives in Available Agents, not Phase 1.
    assert "Worker selection" not in phase1
    assert "AskUserQuestion" not in phase1


def test_phase_3_delegates_via_available_agents_section() -> None:
    body = _render_develop(get_fixture_path("vault-empty"))
    phase3 = _phase_slice(body, "## Phase 3 Execute", "## Phase 4 Finalize")

    # Phase 3 no longer spells out per-type invocation mechanics.
    assert "`type: agent`" not in phase3
    assert "`type: cli`" not in phase3
    assert "subagent_type=<id>" not in phase3
    assert "booping run-agent <id>" not in phase3
    # It points at the Available Agents section.
    assert "Available Agents" in phase3


def test_available_agents_section_carries_invocation_mechanics() -> None:
    body = _render_develop(get_fixture_path("vault-empty"))
    start = body.index("## Available Agents")
    end = body.index("\n## ", start + 1)
    aa = body[start:end]

    # Native agents render via the Agent tool.
    assert 'Invoke via the `Agent` tool with `subagent_type="booping-developer"`' in aa
    # The "always delegate / use only listed agents" rule lives here.
    assert "Always delegate" in aa
