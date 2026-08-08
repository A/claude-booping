from __future__ import annotations

from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render

RESEARCHER = "src/templates/agents/booping-researcher.md.j2"
DEVELOPER = "src/templates/agents/booping-developer.md.j2"


def _write_lesson(vault: Path, name: str, title: str, target: str, body: str) -> None:
    lessons = vault / "_lessons"
    lessons.mkdir(parents=True, exist_ok=True)
    (lessons / name).write_text(
        f"---\ntitle: {title}\ntargets:\n  - {target}\n---\n{body}\n"
    )


def _render_agent(vault: Path, template: str) -> str:
    plugin_root = get_plugin_root()
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    return render(
        template_path=plugin_root / template,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
        plugin_root=plugin_root,
    )


def test_agent_lessons_matching_target_renders(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    baseline = _render_agent(vault, RESEARCHER)
    _write_lesson(
        vault,
        "0001_cite.md",
        "Cite sources",
        "agent:booping-researcher",
        "Always include a URL for web findings.",
    )
    result = _render_agent(vault, RESEARCHER)

    assert result != baseline
    assert "## Lessons" in result
    assert "The following 1 lesson(s) apply to this agent." in result
    assert "### 0001_cite — Cite sources" in result
    assert "Always include a URL for web findings." in result


def test_agent_lessons_non_matching_targets_render_nothing(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    baseline = _render_agent(vault, RESEARCHER)
    _write_lesson(vault, "0001_playbook.md", "Playbook", "groom", "Playbook-scoped.")
    _write_lesson(vault, "0002_step.md", "Step", "groom/intake", "Step-scoped.")
    _write_lesson(
        vault, "0003_dev.md", "Dev", "agent:booping-developer", "Developer-scoped."
    )
    (vault / "lessons").mkdir()
    (vault / "lessons" / "0004_legacy.md").write_text("---\n---\nLegacy lesson.\n")

    assert _render_agent(vault, RESEARCHER) == baseline


def test_agent_lessons_none_contributes_zero_bytes(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    plugin_root = get_plugin_root()
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    partial = render(
        template_path=plugin_root / "src/templates/_partials/_agent_lessons.j2",
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={"agent_id": "booping-researcher"},
        plugin_root=plugin_root,
    )
    assert partial == ""


def test_agent_lessons_developer_body(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    baseline = _render_agent(vault, DEVELOPER)
    _write_lesson(
        vault, "0001_dev.md", "Small diffs", "agent:booping-developer", "Keep it small."
    )
    result = _render_agent(vault, DEVELOPER)

    assert result != baseline
    assert "### 0001_dev — Small diffs" in result
    assert "Keep it small." in result
