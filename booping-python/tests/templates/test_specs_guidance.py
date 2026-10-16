from __future__ import annotations

import re
from pathlib import Path

from booping.context import Context
from booping.rendering import get_plugin_root, render
from booping.specs.values import SpecValue

PARTIAL = "src/templates/_partials/_specs_guidance.j2"
PLAYBOOK_SKILL = "src/templates/skills/playbook.md.j2"

# Lines of the block without its values; each value adds exactly one line on top (adr/0034).
FIXED_BUDGET = 18
VALUE_LINE = re.compile(r"^- (?:\S+:)?value/\d{4} — ")

GUIDANCE = (
    "\n"
    "## Specs\n"
    "\n"
    "The project's specs hold what the code cannot show. Recognise spec material in your work "
    "and in what the user says:\n"
    "\n"
    "- why the project exists, what it is like → `value`\n"
    "- always / never → `rule`\n"
    "- values pulling apart → `conflict`\n"
    "- a choice between options, with a reason → `adr`\n"
    "- who wants what and why, a usage scenario → `story`\n"
    '- an unproven "what if" → `idea`\n'
    "- facts the code does not show → `reference`\n"
    "- an operator procedure → `runbook`\n"
    "\n"
    "Apply them where they add quality or knowledge of decisions already made; skip them "
    "otherwise. When the work produces spec material — a decision, a scenario, a departure, a "
    "record made untrue — have it drafted: values and anything dropping or weakening a rule stay "
    "owner drafts, other drafts follow `autonomy`.\n"
    "Every read or write goes through a subagent running `/booping:playbook specs` with the "
    "material or the question; keep only its short answer. A departure from a record is shown to "
    "the user, or in an autonomous run recorded with the record's ref and `[clarify]` — never "
    "silently overridden.\n"
)

VALUES = [
    SpecValue(ref="anton:value/0001", title="Calm", summary="Nothing shouts."),
    SpecValue(ref="value/0002", title="Speed", summary="Ship fast."),
    SpecValue(ref="value/0003", title="Polish", summary="Not optimised.", non_value=True),
]

VALUES_SECTION = (
    "\n"
    "Values:\n"
    "\n"
    "- anton:value/0001 — Calm: Nothing shouts.\n"
    "- value/0002 — Speed: Ship fast.\n"
    "- value/0003 — Polish (non-value): Not optimised.\n"
)


def _context(vault: Path, *, project_specs: bool, values: list[SpecValue]) -> Context:
    ctx = Context.assemble(start=vault, plugin_root=get_plugin_root(), vault_override=vault)
    return ctx.model_copy(update={"project_specs": project_specs, "spec_values": values})


def _render(ctx: Context, template: str) -> str:
    plugin_root = get_plugin_root()
    return render(
        template_path=plugin_root / template,
        context=ctx,
        config=ctx.config,
        tools={},
        kwargs={},
        plugin_root=plugin_root,
    )


def test_block_lists_guidance_then_one_line_per_value(tmp_path: Path) -> None:
    ctx = _context(tmp_path, project_specs=True, values=VALUES)
    assert _render(ctx, PARTIAL) == GUIDANCE + VALUES_SECTION


def test_block_without_values_carries_the_guidance_only(tmp_path: Path) -> None:
    ctx = _context(tmp_path, project_specs=True, values=[])
    assert _render(ctx, PARTIAL) == GUIDANCE


def test_no_project_specs_leaves_the_playbook_skill_unchanged(tmp_path: Path) -> None:
    without = _render(_context(tmp_path, project_specs=False, values=VALUES), PLAYBOOK_SKILL)
    with_specs = _render(_context(tmp_path, project_specs=True, values=VALUES), PLAYBOOK_SKILL)
    assert "## Specs" not in without
    assert with_specs.replace(GUIDANCE + VALUES_SECTION, "") == without


def test_block_for_this_repo_stays_within_budget() -> None:
    plugin_root = get_plugin_root()
    ctx = Context.assemble(
        start=plugin_root, plugin_root=plugin_root, vault_override=plugin_root / "vault"
    )
    assert ctx.project_specs
    assert ctx.spec_values

    lines = _render(ctx, PARTIAL).strip("\n").splitlines()
    value_lines = [line for line in lines if VALUE_LINE.match(line)]
    assert len(value_lines) == len(ctx.spec_values)
    assert len(lines) - len(value_lines) <= FIXED_BUDGET
