from __future__ import annotations

import os
import subprocess
from pathlib import Path

from booping.commands.render_playbook import compose
from booping.context.playbook import Playbook
from tests.helpers import get_fixture_path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"


def _load(name: str) -> Playbook:
    home = get_fixture_path("render-playbook-home")
    pbs = Playbook.load_all(vault=None, home_dir=home)
    return next(pb for pb in pbs if pb.name == name)


def _render(name: str) -> str:
    return compose(_load(name))


def _composed() -> str:
    return _render("composed")


def _section(out: str, heading: str) -> str:
    """The slice of `out` from `heading` up to the next `## ` heading (or end)."""
    start = out.index(heading)
    rest = out.find("\n## ", start + 1)
    return out[start:] if rest == -1 else out[start:rest]


# --- happy path -------------------------------------------------------------


def test_section_order() -> None:
    out = _composed()
    order = [
        out.index("# Composed Procedure"),
        out.index("## Execution graph"),
        out.index("## Gather"),
        out.index("## Draft"),
        out.index("## Named Step"),
        out.index("## Plain"),
    ]
    assert order == sorted(order)


def test_verbatim_preamble_passes_through() -> None:
    out = _composed()
    # Body inserted verbatim: the literal Jinja token is NOT evaluated.
    assert "token: {{ leftover }} — no Jinja evaluation happens here." in out


def test_no_notices_on_happy_path() -> None:
    out = _composed()
    assert "**STOP" not in out
    assert "**Note" not in out


def test_mermaid_edges() -> None:
    graph = _section(_composed(), "## Execution graph")
    assert "flowchart TD" in graph
    assert "  gather --> draft" in graph
    assert "  gather --> named-step" in graph
    assert "  draft --> plain" in graph
    assert "  named-step --> plain" in graph


def test_wave_list_parallel_separator() -> None:
    graph = _section(_composed(), "## Execution graph")
    assert "1. `gather`" in graph
    assert "2. `draft` ∥ `named-step`" in graph
    assert "3. `plain`" in graph


def test_wave_one_body_embedded_no_after() -> None:
    gather = _section(_composed(), "## Gather")
    assert "Gather the raw model-agent inputs and return a bulleted list." in gather
    assert "- After:" not in gather
    assert "Read [Gather]" not in gather


def test_later_wave_read_link_and_after_and_parallel() -> None:
    out = _composed()
    draft = _section(out, "## Draft")
    step = _load("composed").steps
    draft_step = next(s for s in step if s.name == "draft")
    assert f"Read [Draft]({draft_step.path}) for content." in draft
    assert "Draft the artifact from the gathered inputs." not in draft
    assert "- After: gather" in draft
    assert "- Parallel with: named-step" in draft


def test_single_member_wave_has_after_no_parallel() -> None:
    plain = _section(_composed(), "## Plain")
    assert "- After: draft, named-step" in plain
    assert "- Parallel with:" not in plain


def test_summary_directive() -> None:
    # The step's own summary is surfaced to the driver: it is where a step declares
    # execution hints (e.g. "one agent per feature") in its own domain words.
    out = _composed()
    assert "- Summary: Gather inputs." in _section(out, "## Gather")
    assert "- Summary: Draft the artifact." in _section(out, "## Draft")
    assert "- Summary: A plain step with no agent and no gate." in _section(out, "## Plain")


def test_summary_leads_the_instructions_block() -> None:
    draft = _section(_composed(), "## Draft")
    assert draft.index("- Summary:") < draft.index("- After:")


def test_model_agent_directive() -> None:
    gather = _section(_composed(), "## Gather")
    assert "- Run in a sub-agent — model sonnet, effort medium." in gather


def test_named_agent_directive() -> None:
    named = _section(_composed(), "## Named Step")
    assert "- Run in sub-agent: booping-researcher." in named


def test_gate_directive_verbatim() -> None:
    draft = _section(_composed(), "## Draft")
    assert (
        '- Review gate: stop after this step — "confirm the draft before continuing";'
        " continue only on explicit user confirmation." in draft
    )


def test_no_orphan_note_when_all_wired() -> None:
    assert "**Note" not in _composed()


# --- notices ----------------------------------------------------------------


def _assert_blocking(out: str) -> None:
    assert "## Execution graph" not in out
    assert "\n## " not in out  # no step sections


def test_missing_step_notice() -> None:
    out = _render("missing-step")
    assert (
        "**STOP — tell the user:** step 'ghost' is referenced in the graph but"
        " steps/ghost.md does not exist. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_unknown_dep_notice() -> None:
    out = _render("unknown-dep")
    assert (
        "**STOP — tell the user:** 'ghost' is listed as a dependency of 'b' but is"
        " not a step in the graph. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_cycle_notice() -> None:
    out = _render("cycle")
    assert (
        "**STOP — tell the user:** the graph has a cycle: a → b → a."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_no_graph_notice() -> None:
    out = _render("no-graph")
    assert (
        "**STOP — tell the user:** playbook 'no-graph' has no graph: in its"
        " frontmatter. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_inline_in_parallel_notice() -> None:
    out = _render("inline-in-parallel")
    assert (
        "**STOP — tell the user:** step 'one' runs inline (agent: null) but shares a"
        " wave with other steps; inline steps cannot run in parallel."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_orphan_note_non_blocking() -> None:
    out = _render("orphan")
    assert (
        "**Note — tell the user:** step 'extra' exists in steps/ but is not wired"
        " into the graph; it will not run." in out
    )
    # Non-blocking: the graph + wired step section still render.
    assert "## Execution graph" in out
    assert "## A" in out
    assert "**STOP" not in out


# --- CLI-level --------------------------------------------------------------


def test_requires_project_without_project_exits_1(tmp_path: Path) -> None:
    # HOME is isolated (autouse fixture); plant a requires_project playbook in its
    # default global root. tmp cwd has no `.booping` — no project attached.
    pb_dir = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / "gated"
    (pb_dir / "steps").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: gated\ntitle: Gated\nrequires_project: true\n"
        "graph:\n  only: []\n---\nPreamble.\n"
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


def test_output_to_file(tmp_path: Path) -> None:
    # Plant the composed fixture in the isolated HOME's global root, render to a file.
    src = get_fixture_path("render-playbook-home") / "_playbooks" / "composed"
    dst = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / "composed"
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(src), str(dst)], check=True)
    out_file = tmp_path / "out.md"
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "composed", "--output", str(out_file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == ""
    text = out_file.read_text()
    assert "## Execution graph" in text
    assert "token: {{ leftover }}" in text


def test_cli_renders_to_stdout(tmp_path: Path) -> None:
    src = get_fixture_path("render-playbook-home") / "_playbooks" / "composed"
    dst = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / "composed"
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(src), str(dst)], check=True)
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "composed"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "## Execution graph" in result.stdout
