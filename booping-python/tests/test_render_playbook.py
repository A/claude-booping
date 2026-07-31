from __future__ import annotations

import os
import subprocess
from pathlib import Path

from booping.commands.render_playbook import compose, compose_step
from booping.context import Context
from booping.context.playbook import Playbook
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


def test_wave_one_fetch_command_no_after() -> None:
    gather = _section(_composed(), "## Gather")
    assert "Run `booping render-playbook composed --step gather` for content." in gather
    assert "Gather the raw model-agent inputs and return a bulleted list." not in gather
    assert "- After:" not in gather


def test_later_wave_fetch_command_and_after_and_parallel() -> None:
    out = _composed()
    draft = _section(out, "## Draft")
    assert "Run `booping render-playbook composed --step draft` for content." in draft
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
        "**STOP — tell the user:** step 'one' runs inline (agent: null) but shares a"
        " wave with other steps; inline steps cannot run in parallel."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_orphan_note_non_blocking() -> None:
    out = _render("orphan")
    assert (
        "**Note — tell the user:** step 'extra' exists on disk but is not wired"
        " into the graph; it will not run." in out
    )
    # Non-blocking: the graph + wired step section still render.
    assert "## Execution graph" in out
    assert "## A" in out
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


def _build(
    tmp_path: Path,
    graph_yaml: str,
    steps: dict[str, str],
    name: str = "sg",
) -> Playbook:
    """A playbook planted in a tmp local root: `graph_yaml` verbatim under `graph:`,
    one step dir per `steps` entry (name → `agent:` frontmatter value)."""
    pb_dir = tmp_path / "_playbooks" / name
    pb_dir.mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        f"---\nname: {name}\ntitle: SG\ngraph:\n{graph_yaml}---\nPreamble.\n"
    )
    for step_name, agent in steps.items():
        (pb_dir / step_name).mkdir()
        (pb_dir / step_name / "prompt.md").write_text(
            f"---\nsummary: {step_name} summary\nagent: {agent}\n---\n{step_name} body\n"
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
    assert "## Execution graph" in out


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
            f"**STOP — tell the user:** step '{name}' runs inline (agent: null) but"
            " shares a wave with other steps; inline steps cannot run in parallel."
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


def _mermaid(out: str) -> str:
    body = out.split("```mermaid\n", 1)[1]
    return body.split("```", 1)[0]


def test_mermaid_cluster(tmp_path: Path) -> None:
    out = _sg_out(tmp_path)
    assert out.count("```mermaid") == 1
    chart = _mermaid(out)
    assert chart.count("  subgraph ") == 1
    assert chart.count("\n  end\n") == 1
    assert '  subgraph pipeline["pipeline (repeat)"]\n' in chart
    # Inner edges sit inside the cluster; outer edges point at the cluster id.
    cluster = chart.split('  subgraph pipeline["pipeline (repeat)"]\n', 1)[1]
    cluster = cluster.split("  end\n", 1)[0]
    assert cluster == "    spec --> fixtures\n    spec --> tests\n"
    assert "  manifest --> pipeline\n" in chart
    assert "  pipeline --> publish\n" in chart


def test_mermaid_cluster_title_without_repeat(tmp_path: Path) -> None:
    graph = "  a: []\n  group:\n    dependencies: [a]\n    graph:\n      b: []\n"
    chart = _mermaid(compose(_build(tmp_path, graph, {"a": "null", "b": "null"})))
    assert '  subgraph group["group"]\n' in chart
    # A lone inner step with no deps still shows up as a bare node in the cluster.
    assert "    b\n" in chart


def test_wave_list_nests_inner_waves(tmp_path: Path) -> None:
    graph = _section(_sg_out(tmp_path), "## Execution graph")
    assert (
        "1. `manifest`\n"
        "2. `pipeline` *(subgraph)*\n"
        "    1. `spec`\n"
        "    2. `fixtures` ∥ `tests`\n"
        "3. `publish`\n" in graph
    )


def test_subgraph_section_order(tmp_path: Path) -> None:
    out = _sg_out(tmp_path)
    order = [
        out.index("## Manifest"),
        out.index("## Subgraph: pipeline"),
        out.index("## Spec"),
        out.index("## Fixtures"),
        out.index("## Tests"),
        out.index("## Publish"),
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


def test_inner_step_part_of_bullet_and_fetch_form(tmp_path: Path) -> None:
    pb = _sg(tmp_path)
    out = compose(pb)
    spec = _section(out, "## Spec")
    assert spec.index("- Part of: pipeline (repeated)") < spec.index("- Summary:")
    assert "Run `booping render-playbook sg --step spec` for content." in spec
    assert "spec body" not in spec
    fixtures = _section(out, "## Fixtures")
    assert "- Part of: pipeline (repeated)" in fixtures
    assert "- After: spec" in fixtures
    assert "- Parallel with: tests" in fixtures


def test_inner_step_part_of_without_repeat_has_no_suffix(tmp_path: Path) -> None:
    graph = "  a: []\n  group:\n    dependencies: [a]\n    graph:\n      b: []\n"
    b = _section(
        compose(_build(tmp_path, graph, {"a": "null", "b": "null"})), "## B"
    )
    assert "- Part of: group\n" in b


def test_outer_steps_have_no_part_of_bullet(tmp_path: Path) -> None:
    out = _sg_out(tmp_path)
    assert "- Part of:" not in _section(out, "## Manifest")
    assert "- Part of:" not in _section(out, "## Publish")


def test_step_flag_on_inner_step_returns_bare_body(tmp_path: Path) -> None:
    pb = _sg(tmp_path)
    out = compose_step(pb, "fixtures")
    assert out == "fixtures body\n"
    assert "Part of:" not in out
    assert "## Fixtures" not in out


# --- declared inputs / outputs ----------------------------------------------


def _io(tmp_path: Path, extra_frontmatter: str) -> str:
    """The `## One` section of a single-step playbook whose step carries
    `extra_frontmatter` (declared inputs/outputs) on top of the usual keys."""
    pb_dir = tmp_path / "_playbooks" / "io"
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: io\ntitle: IO\ngraph:\n  one: []\n---\nPreamble.\n"
    )
    (pb_dir / "one" / "prompt.md").write_text(
        f"---\nsummary: one summary\nagent: null\n{extra_frontmatter}---\none body\n"
    )
    pbs = Playbook.load_all(
        vault=tmp_path, home_dir=tmp_path / "nohome", plugin_root=tmp_path / "nocore"
    )
    return _section(compose(next(p for p in pbs if p.name == "io")), "## One")


def test_inputs_bullets_with_and_without_from(tmp_path: Path) -> None:
    section = _io(
        tmp_path,
        "inputs:\n  - what: the brief\n    from: intake\n  - a bare input\n",
    )
    assert "- Inputs:\n  - the brief (from intake)\n  - a bare input\n" in section


def test_outputs_bullets(tmp_path: Path) -> None:
    section = _io(tmp_path, "outputs:\n  - a draft\n  - a summary line\n")
    assert "- Outputs:\n  - a draft\n  - a summary line\n" in section
    assert "- Inputs:" not in section


def test_no_labels_when_nothing_declared(tmp_path: Path) -> None:
    section = _io(tmp_path, "")
    assert "- Inputs:" not in section
    assert "- Outputs:" not in section


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
    assert out.index("## Execution graph") < out.index("## State") < out.index("## Intake")


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
    assert (
        "| `intaking` | `developing-steps` | intake step complete |"
        " request + scope captured in the artifact | `frontmatter-update intaken=@now` |"
        in state
    )
    assert "| `done` | *(terminal)* | — | — | — |" in state


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
    for step_name, agent in steps.items():
        (pb_dir / step_name).mkdir()
        (pb_dir / step_name / "prompt.md").write_text(
            f"---\nsummary: {step_name} summary\nagent: {agent}\n---\n{step_name} body\n"
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
    assert "## Execution graph" in out
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
    first = _section(compose(_load("jinja-composed"), context=_ctx()), "## First")
    assert "Run `booping render-playbook jinja-composed --step first` for content." in first
    assert "Wave-one body" not in first


def test_jinja_later_wave_step_shows_step_command() -> None:
    second = _section(compose(_load("jinja-composed"), context=_ctx()), "## Second")
    assert "Run `booping render-playbook jinja-composed --step second` for content." in second
    assert "Read [Second]" not in second


def test_fetch_line_shape_is_uniform_across_jinja_modes() -> None:
    ctx = _ctx()
    plain = _section(compose(_load("composed"), context=ctx), "## Draft")
    jinja = _section(compose(_load("jinja-composed"), context=ctx), "## Second")
    assert "Run `booping render-playbook composed --step draft` for content." in plain
    assert (
        "Run `booping render-playbook jinja-composed --step second` for content." in jinja
    )


def test_no_read_link_form_anywhere() -> None:
    ctx = _ctx()
    outs = (
        compose(_load("composed"), context=ctx),
        compose(_load("jinja-composed"), context=ctx),
    )
    for out in outs:
        assert "for content." in out
        assert "] for content." not in out


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
    assert "## Execution graph" in out
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
    assert "## Draft" not in out
    assert "Review gate:" not in out
    assert "Parallel with:" not in out


def test_step_body_only_jinja_rendered() -> None:
    ctx = _ctx()
    out = compose_step(_load("jinja-composed"), "first", ctx)
    assert out.startswith(f"Wave-one body, threshold {_threshold(ctx)}.")
    assert "## Project Context" in out
    assert "## First" not in out
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
        '---\nsummary: only\nagent: sonnet:medium\n---\n{% include "_lib/shared.md" %}\n'
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
    assert "## Execution graph" in text
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
    assert "## Execution graph" in result.stdout
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
    assert "## Draft" not in result.stdout
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
    assert "## Execution graph" in result.stdout


# --- lessons ----------------------------------------------------------------


def _build_lessons(
    tmp_path: Path,
    *,
    root_lessons: dict[str, str] | None = None,
    pb_lessons: dict[str, str] | None = None,
    jinja: bool = False,
    name: str = "les",
) -> Playbook:
    """A one-step playbook in a tmp global root, carrying the given `_lessons/` files
    (mapping filename → full file text) at root and playbook level."""
    root = tmp_path / "home" / "_playbooks"
    pb_dir = root / name
    (pb_dir / "s1").mkdir(parents=True)
    fm_jinja = "jinja: true\n" if jinja else ""
    (pb_dir / "playbook.md").write_text(
        f"---\nname: {name}\ntitle: Les\n{fm_jinja}graph:\n  s1: []\n---\nPreamble.\n"
    )
    (pb_dir / "s1" / "prompt.md").write_text("---\nsummary: s1\n---\nStep body.\n")
    for level, files in (("", root_lessons), (name, pb_lessons)):
        if not files:
            continue
        lessons_dir = (root / level / "_lessons") if level else (root / "_lessons")
        lessons_dir.mkdir(parents=True, exist_ok=True)
        for filename, text in files.items():
            (lessons_dir / filename).write_text(text)
    pbs = Playbook.load_all(
        vault=None, home_dir=tmp_path / "home", plugin_root=tmp_path / "nocore"
    )
    return next(p for p in pbs if p.name == name)


_LESSON_A = "---\ntitle: Alpha rule\n---\nAlpha body.\n"
_LESSON_B = "---\ntitle: Beta rule\n---\nBeta body.\n"
_LESSON_STEP = "---\ntitle: Step rule\nstep: s1\n---\nStep-scoped body.\n"


def test_lessons_section_locked_format(tmp_path: Path) -> None:
    pb = _build_lessons(
        tmp_path,
        root_lessons={"0001_alpha.md": _LESSON_A},
        pb_lessons={"0002_beta.md": _LESSON_B},
    )
    assert _section(compose(pb), "## Lessons") == (
        "## Lessons\n"
        "\n"
        "The following 2 lesson(s) apply to this playbook. Never silently violate one;"
        " conflict → stop and flag.\n"
        "\n"
        "### 0001_alpha — Alpha rule\n"
        "*(scope: global)*\n"
        "\n"
        "Alpha body.\n"
        "\n"
        "### 0002_beta — Beta rule\n"
        "*(scope: playbook)*\n"
        "\n"
        "Beta body.\n"
    )


def test_step_targeted_lessons_absent_from_composed(tmp_path: Path) -> None:
    pb = _build_lessons(tmp_path, pb_lessons={"0002_step.md": _LESSON_STEP})
    out = compose(pb)
    assert "## Lessons" not in out
    assert "Step-scoped body." not in out


def test_no_lessons_no_section(tmp_path: Path) -> None:
    assert "## Lessons" not in compose(_build_lessons(tmp_path))


def test_lessons_section_between_preamble_and_graph(tmp_path: Path) -> None:
    pb = _build_lessons(tmp_path, pb_lessons={"0001_alpha.md": _LESSON_A})
    out = compose(pb)
    order = [out.index("Preamble."), out.index("## Lessons"), out.index("## Execution graph")]
    assert order == sorted(order)


def test_lesson_body_is_not_jinja_rendered(tmp_path: Path) -> None:
    pb = _build_lessons(
        tmp_path,
        pb_lessons={"0001_alpha.md": "---\ntitle: Raw\n---\nToken {{ leftover }} kept.\n"},
        jinja=True,
    )
    assert "Token {{ leftover }} kept." in compose(pb, context=_ctx())


def test_step_lessons_locked_format(tmp_path: Path) -> None:
    pb = _build_lessons(
        tmp_path, pb_lessons={"0001_alpha.md": _LESSON_A, "0002_step.md": _LESSON_STEP}
    )
    assert compose_step(pb, "s1") == (
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
    pb = _build_lessons(
        tmp_path,
        pb_lessons={"0002_step.md": "---\ntitle: Step rule\nstep: s1\n---\n{{ raw }} kept.\n"},
        jinja=True,
    )
    out = compose_step(pb, "s1", _ctx())
    assert out.startswith("Step body.\n\n## Lessons\n")
    assert "{{ raw }} kept." in out


def test_step_without_targeted_lessons_unchanged(tmp_path: Path) -> None:
    pb = _build_lessons(tmp_path, pb_lessons={"0001_alpha.md": _LESSON_A})
    assert compose_step(pb, "s1") == "Step body.\n"


def test_no_lessons_flag_suppresses_both_surfaces(tmp_path: Path) -> None:
    pb = _build_lessons(
        tmp_path, pb_lessons={"0001_alpha.md": _LESSON_A, "0002_step.md": _LESSON_STEP}
    )
    assert "## Lessons" not in compose(pb, include_lessons=False)
    assert compose_step(pb, "s1", include_lessons=False) == "Step body.\n"


def test_orphan_lesson_note_non_blocking(tmp_path: Path) -> None:
    pb = _build_lessons(
        tmp_path,
        pb_lessons={"0003_ghost.md": "---\ntitle: Ghost\nstep: nope\n---\nGhost body.\n"},
    )
    out = compose(pb)
    assert (
        "**Note — tell the user:** lesson '0003_ghost.md' targets unknown step 'nope'"
        " in playbook 'les'; it is ignored." in out
    )
    assert "**STOP" not in out
    assert "## Execution graph" in out
    assert "## Lessons" not in out


def test_name_clash_notice_blocks(tmp_path: Path) -> None:
    _build_lessons(tmp_path, pb_lessons={"0001_alpha.md": _LESSON_A}, name="dup")
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


def _plant_lessons_vault(tmp_path: Path) -> Path:
    """A bare vault carrying one playbook with a playbook-scoped and a step-scoped lesson."""
    vault = tmp_path / "vault"
    pb_dir = vault / "_playbooks" / "les"
    (pb_dir / "s1").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: les\ntitle: Les\ngraph:\n  s1: []\n---\nPreamble.\n"
    )
    (pb_dir / "s1" / "prompt.md").write_text("---\nsummary: s1\n---\nStep body.\n")
    (pb_dir / "_lessons").mkdir()
    (pb_dir / "_lessons" / "0001_alpha.md").write_text(_LESSON_A)
    (pb_dir / "_lessons" / "0002_step.md").write_text(_LESSON_STEP)
    return vault


def test_cli_no_lessons_flag(tmp_path: Path) -> None:
    vault = _plant_lessons_vault(tmp_path)
    base = [str(BOOPING_BIN), "render-playbook", "les", "--project", str(vault)]
    with_lessons = subprocess.run(base, cwd=tmp_path, capture_output=True, text=True)
    without = subprocess.run(
        [*base, "--no-lessons"], cwd=tmp_path, capture_output=True, text=True
    )
    assert with_lessons.returncode == 0
    assert "## Lessons" in with_lessons.stdout
    assert without.returncode == 0
    assert "## Lessons" not in without.stdout

    step = [*base, "--step", "s1"]
    step_out = subprocess.run(step, cwd=tmp_path, capture_output=True, text=True)
    step_bare = subprocess.run(
        [*step, "--no-lessons"], cwd=tmp_path, capture_output=True, text=True
    )
    assert "## Lessons" in step_out.stdout
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
