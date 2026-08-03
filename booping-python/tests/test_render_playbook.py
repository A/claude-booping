from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from booping.commands.render_playbook import (
    build_env,
    compose,
    compose_step,
)
from booping.context import Context
from booping.context.lesson import Lesson
from booping.context.playbook import Playbook
from booping.utils import parse_set_overrides
from tests.helpers import get_fixture_path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"


FIXTURE_HOME = get_fixture_path("render-playbook-home")


def _load(name: str) -> Playbook:
    pbs = Playbook.load_all(
        vault=None, home_dir=FIXTURE_HOME, plugin_root=Path("/nonexistent/plugin-root")
    )
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
        out.index("## Playbook Steps"),
        out.index("## Step: Gather"),
        out.index("## Step: Draft"),
        out.index("## Step: Named Step"),
        out.index("## Step: Plain"),
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


def test_graph_table_rows_in_dependency_order() -> None:
    graph = _section(_composed(), "## Playbook Steps")
    assert "| Step | Dependencies | Summary | Review gate |" in graph
    rows = [line for line in graph.splitlines() if line.startswith("| `")]
    assert [" | ".join(row.split(" | ")[:2]) for row in rows] == [
        "| `gather` | —",
        "| `draft` | `gather`",
        "| `named-step` | `gather`",
        "| `plain` | `draft`, `named-step`",
    ]


def test_graph_table_states_dependency_driven_ordering() -> None:
    graph = _section(_composed(), "## Playbook Steps")
    assert "Execute the steps in the most effective order considering their dependencies." in graph


def test_detached_section_is_summary_then_delegation_order() -> None:
    # A delegated section carries no instruction bullets: its dependencies and wave
    # order already sit in the step table, so the driver needs the summary and the
    # order to spawn, nothing else.
    gather = _section(_composed(), "## Step: Gather")
    assert "Gather inputs." in gather
    assert "Gather the raw model-agent inputs and return a bulleted list." not in gather
    assert "Instructions:" not in gather
    assert "- After:" not in gather


def test_detached_section_drops_deps_and_siblings() -> None:
    draft = _section(_composed(), "## Step: Draft")
    assert "- After: gather" not in draft
    assert "Parallel with" not in draft


def test_single_member_wave_has_after_no_parallel() -> None:
    plain = _section(_composed(), "## Step: Plain")
    assert "- After: draft, named-step" in plain
    assert "- Parallel with:" not in plain


def test_summary_directive() -> None:
    # The step's own summary is surfaced to the driver: it is where a step declares
    # execution hints (e.g. "one agent per feature") in its own domain words.
    out = _composed()
    assert "Gather inputs." in _section(out, "## Step: Gather")
    assert "Draft the artifact." in _section(out, "## Step: Draft")
    plain = _section(out, "## Step: Plain")
    assert "- Summary: A plain step with no delegation and no gate." in plain


def test_summary_leads_the_delegation_order() -> None:
    draft = _section(_composed(), "## Step: Draft")
    assert draft.index("Draft the artifact.") < draft.index("Tell a sub-agent")


def test_model_detached_directive() -> None:
    gather = _section(_composed(), "## Step: Gather")
    assert (
        "Tell a sub-agent — model sonnet, effort medium — to get its instructions by"
        " calling this command: `booping render-playbook composed --step gather`."
        in gather
    )


def test_named_detached_directive() -> None:
    named = _section(_composed(), "## Step: Named Step")
    assert (
        "Tell the `booping-researcher` agent to get its instructions by calling this"
        " command: `booping render-playbook composed --step named-step`." in named
    )


def test_gate_directive_verbatim() -> None:
    draft = _section(_composed(), "## Step: Draft")
    assert (
        'Review gate: stop after this step — "confirm the draft before continuing";'
        " continue only on explicit user confirmation." in draft
    )


def test_no_orphan_note_when_all_wired() -> None:
    assert "**Note" not in _composed()


# --- notices ----------------------------------------------------------------


def _assert_blocking(out: str) -> None:
    assert "## Playbook Steps" not in out
    assert "\n## " not in out  # no step sections


def test_missing_step_notice() -> None:
    out = _render("missing-step")
    assert (
        "**STOP — tell the user:** step 'ghost' is referenced in the graph but"
        " ghost/prompt.md does not exist. Do not execute this playbook." in out
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
        "**STOP — tell the user:** step 'one' is not detached but shares a wave with"
        " other steps; a step sharing a wave must be `detached:`."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_legacy_agent_key_notice(tmp_path: Path) -> None:
    pb_dir = tmp_path / "_playbooks" / "legacy"
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: legacy\ntitle: Legacy\ngraph:\n  one: []\n---\nPreamble.\n"
    )
    (pb_dir / "one" / "prompt.md").write_text(
        "---\nsummary: one summary\nagent: opus:low\n---\none body\n"
    )
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    out = compose(next(p for p in pbs if p.name == "legacy"))
    assert (
        "**STOP — tell the user:** step 'one' declares `agent:` in its frontmatter;"
        " that key was renamed to `detached:`. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_orphan_note_non_blocking() -> None:
    out = _render("orphan")
    assert (
        "**Note — tell the user:** step 'extra' exists on disk but is not wired"
        " into the graph; it will not run." in out
    )
    # Non-blocking: the graph + wired step section still render.
    assert "## Playbook Steps" in out
    assert "## Step: A" in out
    assert "**STOP" not in out


# --- subgraphs --------------------------------------------------------------

_SG_GRAPH = """\
  manifest: []
  pipeline:
    dependencies: [manifest]
    repeat: once per step produced by manifest; instances may run in parallel
    graph:
      spec: []
      fixtures: [spec]
      tests: [spec]
  publish: [pipeline]
"""

_SG_STEPS = {
    "manifest": "sonnet:medium",
    "spec": "sonnet:medium",
    "fixtures": "haiku:low",
    "tests": "booping-researcher",
    "publish": "sonnet:medium",
}


def _detached_line(value: str) -> str:
    """Frontmatter line for a step's delegation; "null" means no `detached:` key."""
    return "" if value == "null" else f"detached: {value}\n"


def _build(
    tmp_path: Path,
    graph_yaml: str,
    steps: dict[str, str],
    name: str = "sg",
) -> Playbook:
    """A playbook planted in a tmp local root: `graph_yaml` verbatim under `graph:`,
    one step dir per `steps` entry (name → `detached:` frontmatter value; the
    sentinel "null" plants no `detached:` key at all)."""
    pb_dir = tmp_path / "_playbooks" / name
    pb_dir.mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        f"---\nname: {name}\ntitle: SG\ngraph:\n{graph_yaml}---\nPreamble.\n"
    )
    for step_name, detached in steps.items():
        (pb_dir / step_name).mkdir()
        (pb_dir / step_name / "prompt.md").write_text(
            f"---\nsummary: {step_name} summary\n{_detached_line(detached)}---\n"
            f"{step_name} body\n"
        )
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    return next(p for p in pbs if p.name == name)


def _sg(tmp_path: Path) -> Playbook:
    return _build(tmp_path, _SG_GRAPH, _SG_STEPS)


def _sg_out(tmp_path: Path) -> str:
    return compose(_sg(tmp_path))


def test_subgraph_happy_path_has_no_notices(tmp_path: Path) -> None:
    out = _sg_out(tmp_path)
    assert "**STOP" not in out
    assert "**Note" not in out


def test_subgraph_key_is_not_missing(tmp_path: Path) -> None:
    # `pipeline` is a grouping node — it has no step dir and must not be reported.
    assert "step 'pipeline' is referenced in the graph" not in _sg_out(tmp_path)


def test_missing_inner_step_dir_notice(tmp_path: Path) -> None:
    steps = {k: v for k, v in _SG_STEPS.items() if k != "fixtures"}
    out = compose(_build(tmp_path, _SG_GRAPH, steps))
    assert (
        "**STOP — tell the user:** step 'fixtures' is referenced in the graph but"
        " fixtures/prompt.md does not exist. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_inner_step_dir_is_not_an_orphan(tmp_path: Path) -> None:
    assert "**Note" not in _sg_out(tmp_path)


def test_unwired_step_dir_is_still_an_orphan(tmp_path: Path) -> None:
    out = compose(_build(tmp_path, _SG_GRAPH, {**_SG_STEPS, "stray": "sonnet:medium"}))
    assert (
        "**Note — tell the user:** step 'stray' exists on disk but is not wired"
        " into the graph; it will not run." in out
    )
    assert "## Playbook Steps" in out


def test_inline_steps_sharing_an_inner_wave_notice(tmp_path: Path) -> None:
    graph = (
        "  a: []\n"
        "  loop:\n    dependencies: [a]\n"
        "    graph:\n      one: []\n      two: []\n"
    )
    out = compose(
        _build(tmp_path, graph, {"a": "sonnet:medium", "one": "null", "two": "null"})
    )
    for name in ("one", "two"):
        assert (
            f"**STOP — tell the user:** step '{name}' is not detached but shares a"
            " wave with other steps; a step sharing a wave must be `detached:`."
            " Do not execute this playbook." in out
        )
    _assert_blocking(out)


def test_bad_node_notice(tmp_path: Path) -> None:
    out = compose(_build(tmp_path, "  a: []\n  g:\n    graph:\n      b: []\n", {"a": "null"}))
    assert (
        "**STOP — tell the user:** graph node 'g' is malformed: missing `dependencies`."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_bad_inner_node_notice_names_the_subgraph(tmp_path: Path) -> None:
    graph = "  g:\n    dependencies: []\n    graph:\n      b: nope\n"
    out = compose(_build(tmp_path, graph, {}))
    assert (
        "**STOP — tell the user:** in subgraph 'g': graph node 'b' is malformed:"
        " deps must be a list. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_nested_subgraph_notice(tmp_path: Path) -> None:
    graph = (
        "  outer:\n    dependencies: []\n    graph:\n"
        "      inner:\n        dependencies: []\n        graph:\n          deep: []\n"
    )
    out = compose(_build(tmp_path, graph, {}))
    assert (
        "**STOP — tell the user:** node 'inner' inside subgraph 'outer' is itself a"
        " subgraph; only one level of nesting is supported."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_duplicate_step_notice(tmp_path: Path) -> None:
    graph = "  draft: []\n  loop:\n    dependencies: []\n    graph:\n      draft: []\n"
    out = compose(_build(tmp_path, graph, {"draft": "null"}))
    assert (
        "**STOP — tell the user:** step 'draft' appears in more than one scope"
        " (subgraph 'loop'); step names must be unique across the playbook."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_inner_unknown_dep_notice_names_the_subgraph(tmp_path: Path) -> None:
    graph = "  loop:\n    dependencies: []\n    graph:\n      b: [ghost]\n"
    out = compose(_build(tmp_path, graph, {"b": "null"}))
    assert (
        "**STOP — tell the user:** in subgraph 'loop': 'ghost' is listed as a"
        " dependency of 'b' but is not a step in that subgraph."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_inner_cycle_notice_names_the_subgraph(tmp_path: Path) -> None:
    graph = "  loop:\n    dependencies: []\n    graph:\n      b: [c]\n      c: [b]\n"
    out = compose(_build(tmp_path, graph, {"b": "null", "c": "null"}))
    assert (
        "**STOP — tell the user:** in subgraph 'loop': the graph has a cycle: b → c → b."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_graph_table_carries_summary_and_gate() -> None:
    graph = _section(_composed(), "## Playbook Steps")
    plain = next(line for line in graph.splitlines() if line.startswith("| `plain`"))
    step = next(s for s in _load("composed").steps if s.name == "plain")
    assert step.summary in plain
    assert (step.review_gate or "—") in plain


def test_graph_table_lists_subgraph_then_its_inner_steps(tmp_path: Path) -> None:
    graph = _section(_sg_out(tmp_path), "## Playbook Steps")
    rows = [line for line in graph.splitlines() if line.startswith("| `")]
    assert [" | ".join(row.split(" | ")[:2]) for row in rows] == [
        "| `manifest` | —",
        "| `pipeline` *(subgraph)* | `manifest`",
        "| `spec` *(in pipeline)* | —",
        "| `fixtures` *(in pipeline)* | `spec`",
        "| `tests` *(in pipeline)* | `spec`",
        "| `publish` | `pipeline`",
    ]
    assert "once per step produced by manifest" in rows[1]


def test_subgraph_section_order(tmp_path: Path) -> None:
    out = _sg_out(tmp_path)
    order = [
        out.index("## Step: Manifest"),
        out.index("## Subgraph: pipeline"),
        out.index("## Step: Spec"),
        out.index("## Step: Fixtures"),
        out.index("## Step: Tests"),
        out.index("## Step: Publish"),
    ]
    assert order == sorted(order)


def test_subgraph_intro_bullets(tmp_path: Path) -> None:
    intro = _section(_sg_out(tmp_path), "## Subgraph: pipeline")
    assert "- After: manifest" in intro
    assert (
        "- Repeat: once per step produced by manifest; instances may run in parallel"
        in intro
    )
    assert "- Inner waves: 1. `spec` 2. `fixtures` ∥ `tests`" in intro


def test_subgraph_intro_without_repeat_has_no_repeat_bullet(tmp_path: Path) -> None:
    graph = "  a: []\n  group:\n    dependencies: [a]\n    graph:\n      b: []\n"
    intro = _section(
        compose(_build(tmp_path, graph, {"a": "null", "b": "null"})),
        "## Subgraph: group",
    )
    assert "- Repeat:" not in intro
    assert "- After: a" in intro
    assert "- Inner waves: 1. `b`" in intro


def test_inner_step_part_of_and_delegation_order(tmp_path: Path) -> None:
    pb = _sg(tmp_path)
    out = compose(pb)
    spec = _section(out, "## Step: Spec")
    assert spec.index("spec summary") < spec.index("Part of: pipeline (repeated)")
    assert "`booping render-playbook sg --step spec`" in spec
    assert "spec body" not in spec
    fixtures = _section(out, "## Step: Fixtures")
    assert "Part of: pipeline (repeated)" in fixtures
    assert "Parallel with" not in fixtures


def test_inner_step_part_of_without_repeat_has_no_suffix(tmp_path: Path) -> None:
    graph = "  a: []\n  group:\n    dependencies: [a]\n    graph:\n      b: []\n"
    b = _section(
        compose(_build(tmp_path, graph, {"a": "null", "b": "null"})), "## Step: B"
    )
    assert "- Part of: group\n" in b


def test_outer_steps_have_no_part_of_bullet(tmp_path: Path) -> None:
    out = _sg_out(tmp_path)
    assert "- Part of:" not in _section(out, "## Step: Manifest")
    assert "- Part of:" not in _section(out, "## Step: Publish")


def test_step_flag_on_inner_step_returns_bare_body(tmp_path: Path) -> None:
    pb = _sg(tmp_path)
    out = compose_step(pb, "fixtures")
    assert out == "fixtures body\n"
    assert "Part of:" not in out
    assert "## Step: Fixtures" not in out


# --- io frontmatter is not a thing --------------------------------------------


def _io(tmp_path: Path, extra_frontmatter: str) -> str:
    """The `## One` section of a single-step playbook whose step carries
    `extra_frontmatter` on top of the usual keys."""
    pb_dir = tmp_path / "_playbooks" / "io"
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: io\ntitle: IO\ngraph:\n  one: []\n---\nPreamble.\n"
    )
    (pb_dir / "one" / "prompt.md").write_text(
        f"---\nsummary: one summary\n{extra_frontmatter}---\none body\n"
    )
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    return _section(compose(next(p for p in pbs if p.name == "io")), "## Step: One")


@pytest.mark.parametrize(
    "extra_frontmatter",
    [
        "",
        "inputs:\n  - what: the brief\n    from: intake\n  - a bare input\n",
        "outputs:\n  - a draft\n  - a summary line\n",
    ],
)
def test_io_keys_are_never_rendered(tmp_path: Path, extra_frontmatter: str) -> None:
    section = _io(tmp_path, extra_frontmatter)
    assert "Inputs:" not in section
    assert "Outputs:" not in section


# --- state machines ---------------------------------------------------------

STATES_HOME = get_fixture_path("playbooks-yaml-manifest")


def _stateful() -> str:
    pbs = Playbook.load_all(
        vault=None, home_dir=STATES_HOME, plugin_root=Path("/nonexistent/plugin-root")
    )
    return compose(next(pb for pb in pbs if pb.name == "stateful"))


def test_no_state_section_without_states() -> None:
    assert "## State" not in _composed()


def test_state_section_follows_the_execution_graph() -> None:
    out = _stateful()
    assert out.index("## Playbook Steps") < out.index("## State") < out.index("## Step: Intake")


def test_state_section_outer_entry() -> None:
    state = _section(_stateful(), "## State")
    assert "booping playbook-state stateful --workdir <run workdir>" in state
    assert "### State: main" in state
    assert "- Referenced by: outer graph" in state
    assert "- Artifact: `index.md` (relative to the run workdir)" in state
    assert "- Initial status: `intaking`" in state
    assert (
        "- Advance: `booping playbook-transition stateful <to> --workdir <run workdir>`"
        in state
    )


def test_state_section_status_rows() -> None:
    state = _section(_stateful(), "## State")
    assert "| Status | To | When | Gates |" in state
    assert (
        "| `intaking` | `developing-steps` | intake step complete |"
        " request + scope captured in the artifact |"
        in state
    )
    assert "| `done` | *(terminal)* | — | — |" in state
    # Hooks are the transition command's business, not the driver's.
    assert "frontmatter-update intaken=@now" not in state


def test_state_section_instance_entry() -> None:
    state = _section(_stateful(), "## State")
    assert "### State: step" in state
    assert "- Referenced by: subgraph `step-pipeline`" in state
    assert "- Artifact: `steps/{instance}/index.md` (relative to the run workdir)" in state
    assert (
        "- Advance: `booping playbook-transition stateful <to> --state step"
        " --instance <slug> --workdir <run workdir>`" in state
    )


def _build_yaml(
    tmp_path: Path,
    manifest_yaml: str,
    steps: dict[str, str],
    fm_extra: str = "",
    name: str = "sy",
) -> Playbook:
    """A playbook planted in a tmp local root whose structure lives in `playbook.yaml`."""
    pb_dir = tmp_path / "_playbooks" / name
    pb_dir.mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        f"---\nname: {name}\ntitle: SY\n{fm_extra}---\nPreamble.\n"
    )
    (pb_dir / "playbook.yaml").write_text(manifest_yaml)
    for step_name, detached in steps.items():
        (pb_dir / step_name).mkdir()
        (pb_dir / step_name / "prompt.md").write_text(
            f"---\nsummary: {step_name} summary\n{_detached_line(detached)}---\n"
            f"{step_name} body\n"
        )
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    return next(p for p in pbs if p.name == name)


_ONE_STATE = """\
state: main
graph:
  a: []

states:
  main:
    artifact: index.md
    initial: start
    statuses:
      start:
        transitions:
          - to: done
            when: a returned
      done: {terminal: true}
"""


def test_graph_in_both_notice(tmp_path: Path) -> None:
    out = compose(
        _build_yaml(tmp_path, "graph:\n  a: []\n", {"a": "null"}, fm_extra="graph:\n  a: []\n")
    )
    assert (
        "**STOP — tell the user:** playbook 'sy' declares graph: in both playbook.yaml"
        " and playbook.md frontmatter; keep exactly one."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_bad_manifest_notice(tmp_path: Path) -> None:
    out = compose(_build_yaml(tmp_path, "- just\n- a list\n", {}))
    assert (
        "**STOP — tell the user:** playbook.yaml of playbook 'sy' is malformed:"
        " not a YAML mapping. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_bad_state_notice(tmp_path: Path) -> None:
    manifest = _ONE_STATE.replace("    artifact: index.md\n", "")
    out = compose(_build_yaml(tmp_path, manifest, {"a": "null"}))
    assert (
        "**STOP — tell the user:** states entry 'main' is malformed: missing `artifact`."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_unknown_state_notice(tmp_path: Path) -> None:
    manifest = _ONE_STATE.replace("state: main", "state: nope")
    out = compose(_build_yaml(tmp_path, manifest, {"a": "null"}))
    assert (
        "**STOP — tell the user:** the outer graph references state 'nope' but"
        " playbook.yaml declares no such states entry."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_unknown_inner_state_notice_names_the_subgraph(tmp_path: Path) -> None:
    manifest = (
        "graph:\n  a: []\n  loop:\n    dependencies: [a]\n    state: nope\n"
        "    graph:\n      b: []\n"
    )
    out = compose(_build_yaml(tmp_path, manifest, {"a": "null", "b": "null"}))
    assert (
        "**STOP — tell the user:** subgraph 'loop' references state 'nope' but"
        " playbook.yaml declares no such states entry."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_orphan_state_note_non_blocking(tmp_path: Path) -> None:
    manifest = _ONE_STATE + (
        "  stray:\n    artifact: stray.md\n    initial: x\n"
        "    statuses:\n      x: {terminal: true}\n"
    )
    out = compose(_build_yaml(tmp_path, manifest, {"a": "null"}))
    assert (
        "**Note — tell the user:** states entry 'stray' is declared but no graph scope"
        " references it; it will never be used." in out
    )
    assert "**STOP" not in out
    assert "## Playbook Steps" in out
    assert "## State" in out


# --- opt-in Jinja -----------------------------------------------------------


def _ctx() -> Context:
    return Context.assemble()


def _threshold(ctx: Context) -> str:
    return str(ctx.config["sprint"]["default_threshold_sp"])


def test_non_jinja_playbook_output_unchanged() -> None:
    # A non-jinja playbook renders identically with or without context (paths normalised).
    golden = (FIXTURE_HOME.parent / "composed-prejinja.golden.md").read_text()
    actual = compose(_load("composed"), context=_ctx()).replace(str(FIXTURE_HOME), "{HOME}")
    assert actual == golden


def test_jinja_preamble_renders_expression_and_include() -> None:
    ctx = _ctx()
    out = compose(_load("jinja-composed"), context=ctx)
    assert f"Preamble threshold: {_threshold(ctx)}" in out
    assert "## Project Context" in out


def test_jinja_wave_one_step_shows_step_command() -> None:
    first = _section(compose(_load("jinja-composed"), context=_ctx()), "## Step: First")
    assert "`booping render-playbook jinja-composed --step first`" in first
    assert "Wave-one body" not in first


def test_jinja_later_wave_step_shows_step_command() -> None:
    second = _section(compose(_load("jinja-composed"), context=_ctx()), "## Step: Second")
    assert "`booping render-playbook jinja-composed --step second`" in second
    assert "Read [Second]" not in second


def test_fetch_line_shape_is_uniform_across_jinja_modes() -> None:
    ctx = _ctx()
    plain = _section(compose(_load("composed"), context=ctx), "## Step: Draft")
    jinja = _section(compose(_load("jinja-composed"), context=ctx), "## Step: Second")
    order = "to get its instructions by calling this command:"
    assert f"{order} `booping render-playbook composed --step draft`." in plain
    assert f"{order} `booping render-playbook jinja-composed --step second`." in jinja


def test_no_read_link_form_anywhere() -> None:
    ctx = _ctx()
    outs = (
        compose(_load("composed"), context=ctx),
        compose(_load("jinja-composed"), context=ctx),
    )
    for out in outs:
        assert "`booping render-playbook" in out
        assert "](" not in out


# --- inline steps -----------------------------------------------------------


def test_inline_embeds_non_detached_body_and_drops_fetch() -> None:
    plain = _section(compose(_load("composed"), inline_steps=True), "## Step: Plain")
    assert "Just do the plain thing directly." in plain
    assert "for content." not in plain


def test_inline_keeps_fetch_form_for_detached_steps() -> None:
    out = compose(_load("composed"), inline_steps=True)
    for step in ("gather", "draft", "named-step"):
        assert (
            "to get its instructions by calling this command:"
            f" `booping render-playbook composed --step {step}`." in out
        )


def test_inline_jinja_body_renders_through_context(tmp_path: Path) -> None:
    pb_dir = tmp_path / "_playbooks" / "ij"
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: ij\ntitle: IJ\njinja: true\ngraph:\n  one: []\n---\nPreamble.\n"
    )
    (pb_dir / "one" / "prompt.md").write_text(
        "---\nsummary: one\n---\nThreshold {{ config.sprint.default_threshold_sp }}.\n"
    )
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    ctx = _ctx()
    out = compose(next(p for p in pbs if p.name == "ij"), context=ctx, inline_steps=True)
    assert f"Threshold {_threshold(ctx)}." in out
    assert "for content." not in out


def test_jinja_preamble_renders_now_stamp(tmp_path: Path) -> None:
    pb_dir = tmp_path / "_playbooks" / "nw"
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: nw\ntitle: NW\njinja: true\ngraph:\n  one: []\n---\n"
        'Stamp {{ now("%Y%m%d") }}.\n'
    )
    (pb_dir / "one" / "prompt.md").write_text("---\nsummary: one\n---\nOne body.\n")
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    out = compose(next(p for p in pbs if p.name == "nw"), context=_ctx())
    assert f"Stamp {datetime.now().strftime('%Y%m%d')}." in out


def _fm_playbook(tmp_path: Path, name: str, prompt_frontmatter: str) -> Playbook:
    pb_dir = tmp_path / "_playbooks" / name
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        f"---\nname: {name}\ntitle: {name}\njinja: true\ngraph:\n  one: []\n---\nPreamble.\n"
    )
    (pb_dir / "one" / "prompt.md").write_text(
        f"---\n{prompt_frontmatter}\n---\nOne body.\n"
    )
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    return next(p for p in pbs if p.name == name)


def test_jinja_step_summary_renders_through_context(tmp_path: Path) -> None:
    ctx = _ctx()
    pb = _fm_playbook(
        tmp_path, "fs", "summary: Split past {{ config.sprint.default_threshold_sp }} SP"
    )
    assert f"- Summary: Split past {_threshold(ctx)} SP" in compose(pb, context=ctx)


def test_jinja_step_detached_renders_through_context(tmp_path: Path) -> None:
    pb = _fm_playbook(
        tmp_path, "fd", "summary: one\ndetached: '{{ config.research_agent }}'"
    )
    ctx = _ctx()
    out = compose(pb, context=ctx)
    assert f"Tell the `{ctx.config['research_agent']}` agent to get its" in out


def test_jinja_step_detached_rendering_empty_falls_back_to_inline(
    tmp_path: Path,
) -> None:
    # The config key the step names is absent: the step is runner-performed rather
    # than delegated to an agent with an empty name.
    pb = _fm_playbook(
        tmp_path, "fe", "summary: one\ndetached: '{{ config.no_such_key.agent }}'"
    )
    out = compose(pb, context=_ctx())
    assert "Tell the `" not in out
    assert "- Summary: one" in out


def test_non_jinja_playbook_leaves_frontmatter_verbatim(tmp_path: Path) -> None:
    pb_dir = tmp_path / "_playbooks" / "fv"
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: fv\ntitle: FV\ngraph:\n  one: []\n---\nPreamble.\n"
    )
    (pb_dir / "one" / "prompt.md").write_text(
        "---\nsummary: Past {{ config.sprint.default_threshold_sp }} SP\n---\nOne body.\n"
    )
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    out = compose(next(p for p in pbs if p.name == "fv"), context=_ctx())
    assert "- Summary: Past {{ config.sprint.default_threshold_sp }} SP" in out


def test_jinja_step_frontmatter_error_is_in_band_stop(tmp_path: Path) -> None:
    pb = _fm_playbook(tmp_path, "fx", "summary: one\ndetached: '{{ oops('")
    out = compose(pb, context=_ctx())
    assert "**STOP — tell the user:** Jinja rendering of step 'one' frontmatter" in out
    assert "## Playbook Steps" not in out


def test_manifest_inline_steps_key_implies_inline(tmp_path: Path) -> None:
    pb_dir = tmp_path / "_playbooks" / "mi"
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: mi\ntitle: MI\ninline_steps: true\ngraph:\n  one: []\n---\nPreamble.\n"
    )
    (pb_dir / "one" / "prompt.md").write_text("---\nsummary: one\n---\nOne body.\n")
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    out = compose(next(p for p in pbs if p.name == "mi"))
    assert "One body." in out
    assert "for content." not in out


def test_inline_appends_step_targeted_lessons(tmp_path: Path) -> None:
    pb = _build(tmp_path, "  a: []\n", {"a": "null"}, name="il")
    lessons_dir = tmp_path / "_lessons"
    lessons_dir.mkdir()
    (lessons_dir / "0001_watch.md").write_text(
        "---\ntargets: [il/a]\n---\nWatch the seam.\n"
    )
    ctx = Context(targeted_lessons=Lesson.load_dir(lessons_dir, scope="project"))
    out = compose(pb, context=ctx, inline_steps=True)
    assert "Watch the seam." in out
    assert "Watch the seam." not in compose(
        pb, context=ctx, inline_steps=True, include_lessons=False
    )


def test_jinja_without_context_stops() -> None:
    out = compose(_load("jinja-composed"))
    assert (
        "**STOP — tell the user:** playbook 'jinja-composed' sets jinja: true but was"
        " rendered without project context. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_broken_step_body_does_not_break_compose() -> None:
    # Step bodies are never rendered at compose time — the error waits for the fetch.
    out = compose(_load("jinja-broken"), context=_ctx())
    assert "**STOP" not in out
    assert "## Playbook Steps" in out
    assert "# Broken" in out


def test_jinja_error_is_in_band_stop_notice_at_fetch_time() -> None:
    out = compose_step(_load("jinja-broken"), "only", _ctx())
    assert "**STOP — tell the user:** Jinja rendering of step 'only' failed:" in out
    assert "TemplateNotFound" in out
    assert "Traceback" not in out


def test_step_body_only_non_jinja() -> None:
    pb = _load("composed")
    step = next(s for s in pb.steps if s.name == "draft")
    out = compose_step(pb, "draft", _ctx())
    assert out == step.body
    assert "## Step: Draft" not in out
    assert "Review gate:" not in out
    assert "Parallel with:" not in out


def test_step_body_only_jinja_rendered() -> None:
    ctx = _ctx()
    out = compose_step(_load("jinja-composed"), "first", ctx)
    assert out.startswith(f"Wave-one body, threshold {_threshold(ctx)}.")
    assert "## Project Context" in out
    assert "## Step: First" not in out
    assert "Run in a sub-agent" not in out


# --- include search chain ---------------------------------------------------


def _includes() -> str:
    return compose(_load("jinja-includes"), context=_ctx())


def _includes_step(name: str) -> str:
    return compose_step(_load("jinja-includes"), name, _ctx())


def test_include_from_playbook_dir_by_bare_name() -> None:
    # Preamble pulls `_references/rules.md` sitting next to playbook.md.
    assert "RULES-OK" in _includes()


def test_include_from_step_dir_by_bare_name() -> None:
    assert "STEP-FIXTURE-OK" in _includes_step("first")


def test_include_from_playbook_root_by_root_relative_name() -> None:
    assert "ROOT-LIB-OK" in _includes_step("first")


def test_plugin_partials_still_reachable() -> None:
    first = _includes_step("first")
    assert first.index("## Project Context") > first.index("STEP-FIXTURE-OK")


def test_relative_includes_resolve_against_including_file() -> None:
    # rules.md → ./deep/one.md → ../plain.md (depth 3, both `./` and `../`).
    out = _includes()
    assert "DEEP-ONE-OK" in out
    assert "PLAIN-OK" in out


def test_later_wave_step_fetch_resolves_playbook_dir_include() -> None:
    assert "RULES-OK" in compose_step(_load("jinja-includes"), "second", _ctx())


def _plant_roots(tmp_path: Path, *scopes: str) -> tuple[Path, Path, Path]:
    """Core / global / local roots, each carrying `_lib/shared.md` for the named
    scopes, plus a jinja playbook in the local root that includes it.
    """
    core, home, vault = tmp_path / "core", tmp_path / "home", tmp_path / "vault"
    roots = {
        "core": core / "playbooks",
        "global": home / "_playbooks",
        "local": vault / "_playbooks",
    }
    for scope, root in roots.items():
        (root / "_lib").mkdir(parents=True)
        if scope in scopes:
            (root / "_lib" / "shared.md").write_text(f"MARKER-{scope}\n")
    pb_dir = roots["local"] / "inc"
    (pb_dir / "only").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: inc\ntitle: Inc\njinja: true\ngraph:\n  only: []\n---\nPreamble.\n"
    )
    (pb_dir / "only" / "prompt.md").write_text(
        '---\nsummary: only\ndetached: sonnet:medium\n---\n{% include "_lib/shared.md" %}\n'
    )
    return core, home, vault


def _render_inc(tmp_path: Path, *scopes: str) -> str:
    core, home, vault = _plant_roots(tmp_path, *scopes)
    pbs = Playbook.load_all(vault=vault, home_dir=home, plugin_root=core)
    pb = next(p for p in pbs if p.name == "inc")
    return compose_step(pb, "only", _ctx())


def test_root_relative_include_prefers_local(tmp_path: Path) -> None:
    assert "MARKER-local" in _render_inc(tmp_path, "core", "global", "local")


def test_root_relative_include_falls_back_to_global(tmp_path: Path) -> None:
    assert "MARKER-global" in _render_inc(tmp_path, "core", "global")


def test_root_relative_include_falls_back_to_core(tmp_path: Path) -> None:
    assert "MARKER-core" in _render_inc(tmp_path, "core")


def test_missing_include_is_blocking_notice(tmp_path: Path) -> None:
    out = _render_inc(tmp_path)
    assert "**STOP — tell the user:** Jinja rendering of step 'only' failed:" in out
    assert "TemplateNotFound" in out
    assert "Traceback" not in out


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
    assert "## Playbook Steps" in text
    assert "token: {{ leftover }}" in text


def _plant_vault(tmp_path: Path, *names: str) -> Path:
    """A bare vault dir (no `.booping` marker) carrying the named fixture playbooks."""
    vault = tmp_path / "vault"
    (vault / "_playbooks").mkdir(parents=True)
    for name in names:
        src = FIXTURE_HOME / "_playbooks" / name
        subprocess.run(["cp", "-r", str(src), str(vault / "_playbooks" / name)], check=True)
    return vault


def test_project_flag_satisfies_requires_project(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "requires-project")
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "requires-project", "--project", str(vault)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "## Playbook Steps" in result.stdout
    assert "Only body." not in result.stdout


def test_step_prints_body_only_and_logs(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "composed")
    body = next(s for s in _load("composed").steps if s.name == "draft").body
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "composed",
            "--step", "draft", "--project", str(vault),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == body
    assert "## Step: Draft" not in result.stdout
    log = (vault / "_booping" / ".booping.log").read_text()
    assert "[render-playbook] composed --step draft" in log


def test_step_renders_jinja_body(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "jinja-composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "jinja-composed",
            "--step", "first", "--project", str(vault),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "{{" not in result.stdout
    assert "## Project Context" in result.stdout


def test_unknown_step_exits_1(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "composed",
            "--step", "nope", "--project", str(vault),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "step not found" in result.stderr


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
    assert "## Playbook Steps" in result.stdout


# --- lessons ----------------------------------------------------------------


def _build_lessons(
    tmp_path: Path,
    *,
    lessons: dict[str, str] | None = None,
    jinja: bool = False,
    name: str = "les",
    base: Context | None = None,
) -> tuple[Playbook, Context]:
    """A one-step playbook in a tmp global root, plus a context whose
    `targeted_lessons` come from a tmp project `_lessons/` carrying the given files
    (mapping filename → full file text)."""
    root = tmp_path / "home" / "_playbooks"
    pb_dir = root / name
    (pb_dir / "s1").mkdir(parents=True)
    fm_jinja = "jinja: true\n" if jinja else ""
    (pb_dir / "playbook.md").write_text(
        f"---\nname: {name}\ntitle: Les\n{fm_jinja}graph:\n  s1: []\n---\nPreamble.\n"
    )
    (pb_dir / "s1" / "prompt.md").write_text("---\nsummary: s1\n---\nStep body.\n")
    lessons_dir = tmp_path / "vault" / "_lessons"
    lessons_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in (lessons or {}).items():
        (lessons_dir / filename).write_text(text)
    pbs = Playbook.load_all(
        vault=None, home_dir=tmp_path / "home", plugin_root=tmp_path / "nocore"
    )
    ctx = (base if base is not None else Context()).model_copy(
        update={
            "targeted_lessons": Lesson.load_dir(lessons_dir, scope="project"),
            "lessons": [],
        }
    )
    return next(p for p in pbs if p.name == name), ctx


_LESSON_A = "---\ntitle: Alpha rule\ntargets: [les]\n---\nAlpha body.\n"
_LESSON_B = "---\ntitle: Beta rule\ntargets: [les]\n---\nBeta body.\n"
_LESSON_STEP = "---\ntitle: Step rule\ntargets: [les/s1]\n---\nStep-scoped body.\n"
_LESSON_OTHER = "---\ntitle: Other rule\ntargets: [other, other/s1]\n---\nOther body.\n"


def test_lessons_section_locked_format(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(
        tmp_path, lessons={"0001_alpha.md": _LESSON_A, "0002_beta.md": _LESSON_B}
    )
    assert _section(compose(pb, context=ctx), "## Lessons") == (
        "## Lessons\n"
        "\n"
        "The following 2 lesson(s) apply to this playbook. Never silently violate one;"
        " conflict → stop and flag.\n"
        "\n"
        "### 0001_alpha — Alpha rule\n"
        "*(scope: project)*\n"
        "\n"
        "Alpha body.\n"
        "\n"
        "### 0002_beta — Beta rule\n"
        "*(scope: project)*\n"
        "\n"
        "Beta body.\n"
    )


def test_playbook_target_absent_from_step_surface(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(tmp_path, lessons={"0001_alpha.md": _LESSON_A})
    assert "## Lessons" in compose(pb, context=ctx)
    assert compose_step(pb, "s1", ctx) == "Step body.\n"


def test_step_target_absent_from_composed_section(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(tmp_path, lessons={"0002_step.md": _LESSON_STEP})
    out = compose(pb, context=ctx)
    assert "## Lessons" not in out
    assert "Step-scoped body." not in out


def test_other_playbook_target_renders_nowhere(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(tmp_path, lessons={"0001_other.md": _LESSON_OTHER})
    out = compose(pb, context=ctx)
    assert "Other body." not in out
    assert "## Lessons" not in out
    assert "Other body." not in compose_step(pb, "s1", ctx)
    assert "**Note" not in out


def test_no_lessons_no_section(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(tmp_path)
    assert "## Lessons" not in compose(pb, context=ctx)


def test_lessons_section_between_preamble_and_graph(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(tmp_path, lessons={"0001_alpha.md": _LESSON_A})
    out = compose(pb, context=ctx)
    order = [out.index("Preamble."), out.index("## Lessons"), out.index("## Playbook Steps")]
    assert order == sorted(order)


def test_lesson_body_is_not_jinja_rendered(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(
        tmp_path,
        lessons={
            "0001_alpha.md": "---\ntitle: Raw\ntargets: [les]\n---\nToken {{ leftover }} kept.\n"
        },
        jinja=True,
        base=_ctx(),
    )
    assert "Token {{ leftover }} kept." in compose(pb, context=ctx)


def test_step_lessons_locked_format(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(
        tmp_path, lessons={"0001_alpha.md": _LESSON_A, "0002_step.md": _LESSON_STEP}
    )
    assert compose_step(pb, "s1", ctx) == (
        "Step body.\n"
        "\n"
        "## Lessons\n"
        "\n"
        "The following 1 lesson(s) apply to this step. Never silently violate one.\n"
        "\n"
        "### 0002_step — Step rule\n"
        "\n"
        "Step-scoped body.\n"
    )


def test_step_lessons_on_jinja_playbook(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(
        tmp_path,
        lessons={
            "0002_step.md": "---\ntitle: Step rule\ntargets: [les/s1]\n---\n{{ raw }} kept.\n"
        },
        jinja=True,
        base=_ctx(),
    )
    out = compose_step(pb, "s1", ctx)
    assert out.startswith("Step body.\n\n## Lessons\n")
    assert "{{ raw }} kept." in out


def test_step_lessons_inline_surface(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(tmp_path, lessons={"0002_step.md": _LESSON_STEP})
    out = compose(pb, context=ctx, inline_steps=True)
    assert "Step-scoped body." in out
    assert out.index("Step body.") < out.index("Step-scoped body.")


def test_no_lessons_flag_suppresses_both_surfaces(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(
        tmp_path, lessons={"0001_alpha.md": _LESSON_A, "0002_step.md": _LESSON_STEP}
    )
    assert "## Lessons" not in compose(pb, context=ctx, include_lessons=False)
    assert compose_step(pb, "s1", ctx, include_lessons=False) == "Step body.\n"


def test_unknown_step_target_note_non_blocking(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(
        tmp_path,
        lessons={"0003_ghost.md": "---\ntitle: Ghost\ntargets: [les/nope]\n---\nGhost body.\n"},
    )
    out = compose(pb, context=ctx)
    assert (
        "**Note — tell the user:** lesson '0003_ghost.md' targets unknown step 'nope'"
        " in playbook 'les'; it is ignored." in out
    )
    assert "**STOP" not in out
    assert "## Playbook Steps" in out
    assert "## Lessons" not in out


def test_untargeted_lesson_note(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(
        tmp_path,
        lessons={
            "0004_bare.md": "---\ntitle: Bare\n---\nBare body.\n",
            "0005_bad.md": "---\ntitle: Bad\ntargets: ['les/*']\n---\nBad body.\n",
        },
    )
    out = compose(pb, context=ctx)
    assert (
        "**Note — tell the user:** lesson 0004_bare.md has no valid targets:"
        " — not injected." in out
    )
    assert (
        "**Note — tell the user:** lesson 0005_bad.md has no valid targets:"
        " — not injected." in out
    )
    assert "Bare body." not in out
    assert "Bad body." not in out
    assert "Bad body." not in compose_step(pb, "s1", ctx)


def test_legacy_lesson_dirs_note(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(tmp_path)
    legacy_root = tmp_path / "home" / "_playbooks" / "_lessons"
    legacy_root.mkdir()
    (legacy_root / "0001_old.md").write_text("---\ntitle: Old\n---\nOld body.\n")
    legacy_pb = tmp_path / "home" / "_playbooks" / "les" / "_lessons"
    legacy_pb.mkdir()
    (legacy_pb / "0002_old.md").write_text("---\ntitle: Older\n---\nOlder body.\n")
    vault_lessons = tmp_path / "vault" / "lessons"
    vault_lessons.mkdir(parents=True)
    (vault_lessons / "0003_vault.md").write_text("---\ntitle: Vault\n---\nVault body.\n")
    ctx = ctx.model_copy(update={"lessons": Lesson.load_dir(vault_lessons)})

    out = compose(pb, context=ctx)
    for path in (legacy_root, legacy_pb, vault_lessons):
        assert (
            f"**Note — tell the user:** legacy lessons detected ({path}) — playbooks no"
            " longer read them; migrate to _lessons/ with targets: frontmatter." in out
        )
    assert "**STOP" not in out
    assert "Old body." not in out
    assert "## Lessons" not in out
    assert "legacy lessons detected" not in compose(
        pb, context=ctx, include_lessons=False
    )


def test_no_notices_without_legacy_or_untargeted(tmp_path: Path) -> None:
    pb, ctx = _build_lessons(tmp_path, lessons={"0001_alpha.md": _LESSON_A})
    assert "**Note" not in compose(pb, context=ctx)


def test_name_clash_notice_blocks(tmp_path: Path) -> None:
    _build_lessons(tmp_path, lessons={"0001_alpha.md": _LESSON_A}, name="dup")
    vault_pb = tmp_path / "vault" / "_playbooks" / "dup"
    (vault_pb / "s1").mkdir(parents=True)
    (vault_pb / "playbook.md").write_text(
        "---\nname: dup\ntitle: Dup\ngraph:\n  s1: []\n---\nPreamble.\n"
    )
    (vault_pb / "s1" / "prompt.md").write_text("---\nsummary: s1\n---\nStep body.\n")
    pbs = Playbook.load_all(
        vault=tmp_path / "vault",
        home_dir=tmp_path / "home",
        plugin_root=tmp_path / "nocore",
    )
    out = compose(next(p for p in pbs if p.name == "dup"))
    assert (
        "**STOP — tell the user:** playbook 'dup' is defined in more than one root"
        " (global, local) — playbook names must be unique; rename one." in out
    )
    assert "## Lessons" not in out
    _assert_blocking(out)
    assert "Preamble." in out


def _plant_lessons_vault(tmp_path: Path, *, with_lessons: bool = True) -> Path:
    """A bare vault carrying one playbook, optionally with a playbook-targeted and a
    step-targeted lesson in the vault `_lessons/` root."""
    vault = tmp_path / ("vault" if with_lessons else "bare-vault")
    pb_dir = vault / "_playbooks" / "les"
    (pb_dir / "s1").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: les\ntitle: Les\ngraph:\n  s1: []\n---\nPreamble.\n"
    )
    (pb_dir / "s1" / "prompt.md").write_text("---\nsummary: s1\n---\nStep body.\n")
    if with_lessons:
        (vault / "_lessons").mkdir()
        (vault / "_lessons" / "0001_alpha.md").write_text(_LESSON_A)
        (vault / "_lessons" / "0002_step.md").write_text(_LESSON_STEP)
    return vault


def test_cli_no_lessons_flag(tmp_path: Path) -> None:
    vault = _plant_lessons_vault(tmp_path)
    bare = _plant_lessons_vault(tmp_path, with_lessons=False)
    base = [str(BOOPING_BIN), "render-playbook", "les", "--project", str(vault)]
    with_lessons = subprocess.run(base, cwd=tmp_path, capture_output=True, text=True)
    without = subprocess.run(
        [*base, "--no-lessons"], cwd=tmp_path, capture_output=True, text=True
    )
    bare_out = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "les", "--project", str(bare)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert with_lessons.returncode == 0
    assert "## Lessons" in with_lessons.stdout
    assert without.returncode == 0
    assert without.stdout == bare_out.stdout

    step = [*base, "--step", "s1"]
    step_out = subprocess.run(step, cwd=tmp_path, capture_output=True, text=True)
    step_bare = subprocess.run(
        [*step, "--no-lessons"], cwd=tmp_path, capture_output=True, text=True
    )
    assert "## Lessons" in step_out.stdout
    assert "Step-scoped body." in step_out.stdout
    assert "Alpha body." not in step_out.stdout
    assert step_bare.stdout == "Step body.\n"


def test_cli_help_lists_no_lessons(tmp_path: Path) -> None:
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--no-lessons" in result.stdout


def test_cli_unknown_step_still_exits_1_with_lessons(tmp_path: Path) -> None:
    vault = _plant_lessons_vault(tmp_path)
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "les",
            "--step", "nope", "--project", str(vault),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "step not found" in result.stderr


# --- --set config overrides -------------------------------------------------


def test_set_override_parses_dotted_key_into_nested_mapping() -> None:
    assert parse_set_overrides(["a.b.c=x"]) == {"a": {"b": {"c": "x"}}}


def test_set_override_parses_flat_key_and_keeps_value_a_string() -> None:
    assert parse_set_overrides(["threshold=3"]) == {"threshold": "3"}


def test_set_override_parses_value_containing_equals() -> None:
    assert parse_set_overrides(["a.b=x=y"]) == {"a": {"b": "x=y"}}


def test_set_override_repeated_pairs_later_wins() -> None:
    parsed = parse_set_overrides(["a.b=1", "a.c=2", "a.b=3"])
    assert parsed == {"a": {"b": "3", "c": "2"}}


def test_set_override_malformed_pair_raises() -> None:
    with pytest.raises(ValueError, match="nope"):
        parse_set_overrides(["nope"])


def test_set_override_wins_over_core_value(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "jinja-composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "jinja-composed",
            "--project", str(vault),
            "--set", "sprint.default_threshold_sp=7",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Preamble threshold: 7" in result.stdout


def test_set_override_repeated_later_wins_on_cli(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "jinja-composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "jinja-composed",
            "--project", str(vault),
            "--set", "sprint.default_threshold_sp=7",
            "--set", "sprint.default_threshold_sp=9",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Preamble threshold: 9" in result.stdout


def test_set_override_applies_to_step_surface(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "jinja-composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "jinja-composed",
            "--step", "first", "--project", str(vault),
            "--set", "sprint.default_threshold_sp=7",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Wave-one body, threshold 7." in result.stdout


def test_set_override_malformed_pair_exits_1(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "jinja-composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "jinja-composed",
            "--project", str(vault), "--set", "nope",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "nope" in result.stderr


def test_set_override_absent_leaves_config_unchanged(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "jinja-composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "jinja-composed",
            "--project", str(vault),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Preamble threshold: 35" in result.stdout


def test_set_override_documented_in_help(tmp_path: Path) -> None:
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--set" in result.stdout
    assert "KEY=VALUE" in result.stdout


# --- pinnable now() ---------------------------------------------------------


def test_pinned_now_reaches_playbook_bodies() -> None:
    ctx = _ctx().model_copy(
        update={"config": {**_ctx().config, "now": "19700101-00-00"}}
    )
    env = build_env(context=ctx)
    assert env.from_string('{{ now() }}|{{ now("%H:%M") }}').render() == (
        "19700101-00-00|19700101-00-00"
    )


def test_unpinned_now_in_playbook_bodies_is_time_shaped() -> None:
    env = build_env(context=_ctx())
    assert re.fullmatch(r"\d{8}-\d{2}-\d{2}", env.from_string("{{ now() }}").render())
