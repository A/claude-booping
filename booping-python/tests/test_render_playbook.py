from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from booping.commands.render_playbook import compose
from booping.context.playbook import Playbook
from tests.helpers import get_fixture_path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"


def _load(name: str) -> Playbook:
    home = get_fixture_path("render-playbook-home")
    pbs = Playbook.load_all(vault=None, home_dir=home)
    return next(pb for pb in pbs if pb.name == name)


def _composed() -> str:
    return compose(_load("composed"))


def _section(out: str, heading: str) -> str:
    """The slice of `out` from `heading` up to the next `## ` heading (or end)."""
    start = out.index(heading)
    rest = out.find("\n## ", start + 1)
    return out[start:] if rest == -1 else out[start:rest]


def test_inline_step_body_present() -> None:
    out = _composed()
    assert "Just do the plain thing directly." in out
    assert "Draft the artifact from the gathered inputs." in out


def test_reference_step_link_present_and_body_absent() -> None:
    out = _composed()
    gather = _load("composed").steps[
        [s.name for s in _load("composed").steps].index("gather")
    ]
    assert f"Read [Gather]({gather.path}) for content." in out
    assert "Gather the raw model-agent inputs" not in out


def test_gate_directive_verbatim() -> None:
    out = _composed()
    assert (
        '- Review gate: stop after this step — "confirm the draft before continuing";'
        " continue only on explicit user confirmation." in out
    )


def test_model_agent_directive() -> None:
    out = _composed()
    assert "- Run in a sub-agent — model sonnet, effort medium." in out


def test_named_agent_directive() -> None:
    out = _composed()
    assert "- Run in sub-agent: booping-researcher." in out


def test_plain_step_has_no_instructions_block() -> None:
    out = _composed()
    plain = _section(out, "## Plain")
    assert "Instructions:" not in plain
    assert "Run in" not in plain
    assert "Review gate:" not in plain


def test_call_order_drives_section_order() -> None:
    out = _composed()
    # Composition order is plain → gather → named-step → draft, which is NOT the
    # sorted glob order (draft, gather, named-step, plain, uncalled).
    order = [out.index(h) for h in ("## Plain", "## Gather", "## Named Step", "## Draft")]
    assert order == sorted(order)
    # Sanity: draft (last called) really does come after plain (first called),
    # inverting glob order where draft sorts first.
    assert out.index("## Plain") < out.index("## Draft")


def test_uncalled_step_absent() -> None:
    out = _composed()
    assert "## Uncalled" not in out
    assert "This uncalled step body must never appear" not in out


def test_unknown_step_name_raises() -> None:
    pb = _load("composed")
    pb = pb.model_copy(update={"body": "{{ inline_step('does-not-exist') }}"})
    with pytest.raises(ValueError, match="unknown step 'does-not-exist'"):
        compose(pb)


def test_requires_project_without_project_exits_1(tmp_path: Path) -> None:
    # HOME is isolated (autouse fixture); plant a requires_project playbook in its
    # default global root. tmp cwd has no `.booping` — no project attached.
    pb_dir = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / "gated"
    (pb_dir / "steps").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: gated\ntitle: Gated\nrequires_project: true\n---\n"
        "{{ inline_step('only') }}\n"
    )
    (pb_dir / "steps" / "only.md").write_text("---\nname: only\n---\nstep body\n")
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "gated"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "requires a booping project" in result.stderr


def test_missing_playbook_exits_1(tmp_path: Path) -> None:
    # tmp cwd has no `.booping` and HOME is isolated (autouse fixture) — no playbooks.
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "definitely-nonexistent"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "definitely-nonexistent" in result.stderr
