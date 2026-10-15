from __future__ import annotations

from pathlib import Path

import pytest

from booping.context import Context
from booping.rendering import get_plugin_root, render
from booping.specs.rules import TargetedRule
from booping.specs.targets import parse_target

PARTIAL = "src/templates/_partials/_targeted_rules.j2"
PLAYBOOK_SKILL = "src/templates/skills/playbook.md.j2"

SECTION = (
    "## Rules\n"
    "\n"
    "The following 1 rule(s) apply to this skill. Never silently violate one. "
    "Read a rule's record when its brief is not enough.\n"
    "\n"
    "- Show the step table before the first step. "
    "[rule/0003](vault/specs/rule/0003-announce-steps.md)\n"
    "\n"
)


def _rule(target: str) -> TargetedRule:
    parsed = parse_target(target)
    assert not hasattr(parsed, "reason")
    return TargetedRule(
        ref="rule/0003",
        title="Announce steps",
        brief="Show the step table before the first step.",
        link="vault/specs/rule/0003-announce-steps.md",
        tier="project",
        path=Path("/repo/vault/specs/rule/0003-announce-steps.md"),
        parsed_targets=[parsed],  # pyright: ignore[reportArgumentType]
    )


def _context(vault: Path, rules: list[TargetedRule]) -> Context:
    plugin_root = get_plugin_root()
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    return ctx.model_copy(update={"targeted_rules": rules})


def _render(ctx: Context, template: str, kwargs: dict[str, str]) -> str:
    plugin_root = get_plugin_root()
    return render(
        template_path=plugin_root / template,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs=kwargs,
        plugin_root=plugin_root,
    )


@pytest.mark.parametrize(
    ("targets", "expected"),
    [
        pytest.param(["skill:playbook"], SECTION, id="matching-skill"),
        pytest.param(["skill:code-review"], "", id="other-skill"),
        pytest.param(["agent:playbook"], "", id="agent-of-same-name"),
        pytest.param(["playbook"], "", id="playbook-of-same-name"),
        pytest.param([], "", id="no-rules"),
    ],
)
def test_skill_rules_section_renders_for_targeted_skill_only(
    tmp_path: Path, targets: list[str], expected: str
) -> None:
    ctx = _context(tmp_path, [_rule(t) for t in targets])
    out = _render(ctx, PARTIAL, {"kind": "skill", "id": "playbook"})
    assert out == expected


def test_skill_body_closes_with_rules_and_carries_no_lessons(tmp_path: Path) -> None:
    lessons = tmp_path / "_lessons"
    lessons.mkdir()
    (lessons / "0001_x.md").write_text("---\ntitle: X\ntargets:\n  - skill:playbook\n---\nBody.\n")
    baseline = _render(_context(tmp_path, []), PLAYBOOK_SKILL, {})
    assert _render(_context(tmp_path, [_rule("skill:code-review")]), PLAYBOOK_SKILL, {}) == baseline

    result = _render(_context(tmp_path, [_rule("skill:playbook")]), PLAYBOOK_SKILL, {})
    assert result.count("## Rules\n") == baseline.count("## Rules\n") + 1
    assert "## Lessons" not in result
    assert result.rstrip("\n").endswith(SECTION.rstrip("\n"))
