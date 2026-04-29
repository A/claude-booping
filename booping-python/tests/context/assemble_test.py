from __future__ import annotations

from pathlib import Path

from booping.context import Context
from tests.helpers import get_fixture_path


def test_assemble_smoke() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-full")
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)

    assert ctx.project is not None
    assert ctx.project.name == "vault-full"

    assert len(ctx.plans) > 0
    assert len(ctx.lessons) > 0
    assert len(ctx.retros) > 0
    assert len(ctx.plan_templates) > 0
    assert len(ctx.skills) > 0
    assert len(ctx.agents) > 0
    assert ctx.config != {}
    assert "skill_groom" in ctx.extra_instructions


def test_assemble_no_project(tmp_path: Path) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    # tmp_path is outside the repo so no .booping walk-up will find one
    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root)

    assert ctx.project is None
    assert ctx.plans == []
    assert ctx.lessons == []
    assert ctx.retros == []
    # Plan templates still load from plugin root even with no project
    assert len(ctx.plan_templates) > 0
    assert len(ctx.skills) > 0
    assert len(ctx.agents) > 0
    assert ctx.config != {}
