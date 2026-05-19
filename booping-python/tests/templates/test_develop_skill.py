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


def test_phase_1_contains_worker_pick_clause() -> None:
    body = _render_develop(get_fixture_path("vault-empty"))
    phase1 = _phase_slice(body, "## Phase 1 Plan groupings", "## Phase 2 Branch")

    assert (
        "**Worker selection**: if the rendered Available Agents table contains "
        "more than one entry, present them via `AskUserQuestion` and **hold the "
        "selected worker id in-session** — `/develop` is a single continuous "
        "session, no persistence to the plan file. Use the same worker id for "
        "every milestone group in this sprint. If only one entry is present, use it."
    ) in phase1


def test_phase_3_step_3_has_both_type_branches() -> None:
    body = _render_develop(get_fixture_path("vault-empty"))
    phase3 = _phase_slice(body, "## Phase 3 Execute", "## Phase 4 Finalize")

    assert "`type: agent`" in phase3
    assert "`type: cli`" in phase3
    assert "subagent_type=<id>" in phase3
    assert "booping run-agent <id>" in phase3
    assert "docs/cli_agent_delegation.md" in phase3
