from __future__ import annotations

from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render

PLAYBOOK_SKILL = "src/templates/skills/playbook.md.j2"


def _write_lesson(vault: Path, name: str, title: str, target: str, body: str) -> None:
    lessons = vault / "_lessons"
    lessons.mkdir(parents=True, exist_ok=True)
    (lessons / name).write_text(
        f"---\ntitle: {title}\ntargets:\n  - {target}\n---\n{body}\n"
    )


def _render_skill(vault: Path, template: str) -> str:
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


def test_skill_lessons_matching_target_renders(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    baseline = _render_skill(vault, PLAYBOOK_SKILL)
    _write_lesson(
        vault,
        "0001_announce.md",
        "Announce steps",
        "skill:playbook",
        "Always announce the step table before starting.",
    )
    result = _render_skill(vault, PLAYBOOK_SKILL)

    assert result != baseline
    assert result.count("## Lessons") == baseline.count("## Lessons") + 1
    assert "The following 1 lesson(s) apply to this skill." in result
    assert "### 0001_announce — Announce steps" in result
    assert "Always announce the step table before starting." in result


def test_skill_lessons_non_matching_targets_render_nothing(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    baseline = _render_skill(vault, PLAYBOOK_SKILL)
    _write_lesson(vault, "0001_playbook.md", "Playbook", "groom", "Playbook-scoped.")
    _write_lesson(vault, "0002_step.md", "Step", "groom/intake", "Step-scoped.")
    _write_lesson(
        vault, "0003_other.md", "Other", "skill:code-review", "Other-skill-scoped."
    )

    assert _render_skill(vault, PLAYBOOK_SKILL) == baseline


def test_skill_lessons_none_contributes_zero_bytes(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    plugin_root = get_plugin_root()
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    partial = render(
        template_path=plugin_root / "src/templates/_partials/_skill_lessons.j2",
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={"skill_id": "playbook"},
        plugin_root=plugin_root,
    )
    assert partial == ""
