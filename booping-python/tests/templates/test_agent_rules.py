from __future__ import annotations

from pathlib import Path

import pytest

from booping.context import Context
from booping.context.lesson import parse_target
from booping.rendering import get_plugin_root, render
from booping.specs.rules import TargetedRule

PARTIAL = "src/templates/_partials/_targeted_rules.j2"
RESEARCHER = "src/templates/agents/booping-researcher.md.j2"
DEVELOPER = "src/templates/agents/booping-developer.md.j2"

SECTION = (
    "## Rules\n"
    "\n"
    "The following 1 rule(s) apply to this agent. Never silently violate one. "
    "Read a rule's record when its brief is not enough.\n"
    "\n"
    "- **Cite sources** — Every web finding carries its URL. "
    "[booping:rule/0007](${CLAUDE_PLUGIN_ROOT}/src/specs/rule/0007-cite-sources.md)\n"
    "\n"
)


def _rule(target: str) -> TargetedRule:
    parsed = parse_target(target)
    assert not hasattr(parsed, "reason")
    return TargetedRule(
        ref="booping:rule/0007",
        title="Cite sources",
        brief="Every web finding carries its URL.",
        link="${CLAUDE_PLUGIN_ROOT}/src/specs/rule/0007-cite-sources.md",
        tier="core",
        path=Path("/plugin/src/specs/rule/0007-cite-sources.md"),
        parsed_targets=[parsed],  # pyright: ignore[reportArgumentType]
    )


def _context(vault: Path, rules: list[TargetedRule]) -> Context:
    plugin_root = get_plugin_root()
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    return ctx.model_copy(update={"targeted_rules": rules, "targeted_lessons": []})


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
        pytest.param(["agent:booping-researcher"], SECTION, id="matching-agent"),
        pytest.param(["agent:booping-developer"], "", id="other-agent"),
        pytest.param(["skill:booping-researcher"], "", id="skill-of-same-name"),
        pytest.param(["groom", "groom/intake"], "", id="playbook-and-step"),
        pytest.param([], "", id="no-rules"),
    ],
)
def test_agent_rules_section_renders_for_targeted_agent_only(
    tmp_path: Path, targets: list[str], expected: str
) -> None:
    ctx = _context(tmp_path, [_rule(t) for t in targets])
    out = _render(ctx, PARTIAL, {"kind": "agent", "id": "booping-researcher"})
    assert out == expected


@pytest.mark.parametrize(
    ("template", "agent", "other"),
    [
        pytest.param(RESEARCHER, "booping-researcher", "booping-developer", id="researcher"),
        pytest.param(DEVELOPER, "booping-developer", "booping-researcher", id="developer"),
    ],
)
def test_agent_body_places_rules_directly_before_lessons(
    tmp_path: Path, template: str, agent: str, other: str
) -> None:
    lessons = tmp_path / "_lessons"
    lessons.mkdir()
    (lessons / "0001_x.md").write_text(f"---\ntitle: X\ntargets:\n  - agent:{agent}\n---\nBody.\n")
    plain = Context.assemble(start=tmp_path, plugin_root=get_plugin_root(), vault_override=tmp_path)
    baseline = _render(plain.model_copy(update={"targeted_rules": []}), template, {})
    for_other = plain.model_copy(update={"targeted_rules": [_rule(f"agent:{other}")]})
    for_this = plain.model_copy(update={"targeted_rules": [_rule(f"agent:{agent}")]})

    assert _render(for_other, template, {}) == baseline
    result = _render(for_this, template, {})
    assert result == baseline.replace("## Lessons\n", SECTION + "## Lessons\n", 1)
