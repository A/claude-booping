from __future__ import annotations

from pathlib import Path

import pytest

from booping.context.playbook import (
    Playbook,
    Step,
    StepInput,
    resolve_agent,
    resolve_waves,
)
from tests.helpers import get_fixture_path


def _load_graph(tmp_path: Path, graph_yaml: str) -> Playbook:
    """Load a single playbook whose `graph:` frontmatter block is `graph_yaml`."""
    pb_dir = tmp_path / "_playbooks" / "sub"
    pb_dir.mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        f"---\nname: sub\ntitle: Sub\ngraph:\n{graph_yaml}---\nbody\n"
    )
    pbs = Playbook.load_all(vault=None, home_dir=tmp_path, plugin_root=_no_core())
    return pbs[0]


def _load_manifest(tmp_path: Path, manifest_yaml: str, playbook_md: str) -> Playbook:
    """Load a single playbook from an explicit playbook.md + playbook.yaml pair."""
    pb_dir = tmp_path / "_playbooks" / "man"
    pb_dir.mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(playbook_md)
    (pb_dir / "playbook.yaml").write_text(manifest_yaml)
    pbs = Playbook.load_all(vault=None, home_dir=tmp_path, plugin_root=_no_core())
    return pbs[0]


def _manifests() -> Path:
    return get_fixture_path("playbooks-yaml-manifest")


def _home() -> Path:
    return get_fixture_path("playbooks-home")


def _vault() -> Path:
    return get_fixture_path("playbooks-vault")


def _core() -> Path:
    return get_fixture_path("playbooks-core")


def _no_core() -> Path:
    return Path("/nonexistent/plugin-root")


def test_global_only_discovery() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    names = {pb.name for pb in pbs}
    # alpha, shared, partial discovered; _lib and nomanifest excluded.
    assert names == {"alpha", "shared", "partial"}
    assert all(pb.scope == "global" for pb in pbs)


def test_underscore_dirs_excluded() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    assert "_lib" not in {pb.name for pb in pbs}


def test_fields_and_step_ordering() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert alpha.title == "Alpha Playbook"
    assert alpha.summary == "A global-only playbook for testing."
    assert alpha.trigger == "when the user says alpha"
    assert "Alpha playbook overview body" in alpha.body
    # Steps are the sorted non-`_` subdirs holding a prompt.md; step name = dir name.
    assert [s.name for s in alpha.steps] == ["draft", "gather"]
    assert all(s.path.name == "prompt.md" for s in alpha.steps)


def test_step_review_gate_and_agent_null_vs_set() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    draft, gather = alpha.steps
    assert gather.agent == "sonnet:medium"
    assert gather.review_gate is None
    assert draft.agent is None
    assert draft.review_gate == "confirm the draft before continuing"
    assert "Draft the artifact" in draft.body


def test_requires_project_defaults_false_and_parses_true() -> None:
    pbs = Playbook.load_all(vault=_vault(), home_dir=_home(), plugin_root=_no_core())
    by_name = {pb.name: pb for pb in pbs}
    # Not set in alpha's frontmatter → default False; explicit true in beta.
    assert by_name["alpha"].requires_project is False
    assert by_name["beta"].requires_project is True


def test_underscore_prefixed_step_dir_skipped(
    capsys: pytest.CaptureFixture[str],
) -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert "_ignored" not in {s.name for s in alpha.steps}
    assert "ignored" not in {s.name for s in alpha.steps}
    assert "_ignored" not in capsys.readouterr().err


def test_dir_without_prompt_warns_and_skips(
    capsys: pytest.CaptureFixture[str],
) -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert "notes" not in {s.name for s in alpha.steps}
    assert "notes/ has no prompt.md" in capsys.readouterr().err


def test_prompt_variants_ignored() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    gather = next(s for s in alpha.steps if s.name == "gather")
    # `gather/prompt.haiku-4-5.md` sits next to prompt.md and must be invisible.
    assert [s.name for s in alpha.steps].count("gather") == 1
    assert "Variant body" not in gather.body
    assert "Gather the raw inputs" in gather.body


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, {"mode": "inline"}),
        ("sonnet:medium", {"mode": "model", "model": "sonnet", "effort": "medium"}),
        ("opus:high", {"mode": "model", "model": "opus", "effort": "high"}),
        ("booping-researcher", {"mode": "named", "name": "booping-researcher"}),
        (
            "booping:booping-researcher",
            {"mode": "named", "name": "booping:booping-researcher"},
        ),
    ],
)
def test_resolve_agent(value: str | None, expected: dict[str, str]) -> None:
    assert resolve_agent(value) == expected


def test_local_shadows_global() -> None:
    pbs = Playbook.load_all(vault=_vault(), home_dir=_home(), plugin_root=_no_core())
    by_name = {pb.name: pb for pb in pbs}
    # shared exists in both roots — local wins, global absent.
    shared = by_name["shared"]
    assert shared.scope == "local"
    assert shared.title == "Local Shared"
    assert [pb for pb in pbs if pb.name == "shared"] == [shared]
    # local-only and global-only both present.
    assert by_name["beta"].scope == "local"
    assert by_name["alpha"].scope == "global"


def test_tolerant_partial_frontmatter() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    partial = next(pb for pb in pbs if pb.name == "partial")
    # Missing title falls back to name; missing summary/trigger default to "".
    assert partial.title == "partial"
    assert partial.summary == ""
    assert partial.trigger == ""
    # Missing step file (`missing`) is dropped; present step (no frontmatter) survives.
    assert [s.name for s in partial.steps] == ["present"]
    assert "Body-only step" in partial.steps[0].body


def test_missing_roots_empty() -> None:
    assert (
        Playbook.load_all(
            vault=None, home_dir=Path("/nonexistent/home"), plugin_root=_no_core()
        )
        == []
    )
    assert (
        Playbook.load_all(
            vault=Path("/nonexistent/vault"),
            home_dir=Path("/nonexistent/home"),
            plugin_root=_no_core(),
        )
        == []
    )


def test_missing_core_root_degrades_silently(
    capsys: pytest.CaptureFixture[str],
) -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    assert {pb.name for pb in pbs} == {"alpha", "shared", "partial"}
    assert "plugin-root" not in capsys.readouterr().err


def test_core_discovery() -> None:
    pbs = Playbook.load_all(
        vault=None, home_dir=Path("/nonexistent/home"), plugin_root=_core()
    )
    assert {pb.name for pb in pbs} == {"alpha", "shared", "core-only"}
    assert all(pb.scope == "core" for pb in pbs)
    core_only = next(pb for pb in pbs if pb.name == "core-only")
    assert core_only.title == "Core Only"
    assert [s.name for s in core_only.steps] == ["only"]


def test_global_shadows_core() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_core())
    by_name = {pb.name: pb for pb in pbs}
    assert by_name["alpha"].scope == "global"
    assert by_name["alpha"].title == "Alpha Playbook"
    assert by_name["shared"].scope == "global"
    assert by_name["core-only"].scope == "core"
    assert [pb for pb in pbs if pb.name == "alpha"] == [by_name["alpha"]]


def test_local_shadows_global_shadows_core() -> None:
    pbs = Playbook.load_all(vault=_vault(), home_dir=_home(), plugin_root=_core())
    by_name = {pb.name: pb for pb in pbs}
    # shared exists in all three roots — local wins.
    assert by_name["shared"].scope == "local"
    assert by_name["shared"].title == "Local Shared"
    assert [pb for pb in pbs if pb.name == "shared"] == [by_name["shared"]]
    # alpha in core + global — global wins; core-only survives untouched.
    assert by_name["alpha"].scope == "global"
    assert by_name["core-only"].scope == "core"
    assert by_name["beta"].scope == "local"


def test_global_root_follows_non_default_home_dir(tmp_path: Path) -> None:
    # A non-default home_dir with its own _playbooks root is honoured.
    root = tmp_path / "custom-home"
    step_dir = root / "_playbooks" / "gamma" / "s1"
    step_dir.mkdir(parents=True)
    (root / "_playbooks" / "gamma" / "playbook.md").write_text(
        "---\nname: gamma\ntitle: Gamma\ngraph:\n  s1: []\n---\nbody\n"
    )
    (step_dir / "prompt.md").write_text("---\nsummary: s1\n---\nstep body\n")
    pbs = Playbook.load_all(vault=None, home_dir=root, plugin_root=_no_core())
    assert [pb.name for pb in pbs] == ["gamma"]
    assert pbs[0].scope == "global"


def test_no_manifest_dir_skipped_silently(capsys: pytest.CaptureFixture[str]) -> None:
    Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    err = capsys.readouterr().err
    assert "nomanifest" not in err


def test_graph_loads_verbatim_insertion_order() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert alpha.graph == {"gather": [], "draft": ["gather"]}
    assert list(alpha.graph.keys()) == ["gather", "draft"]


def test_graph_missing_defaults_empty() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    partial = next(pb for pb in pbs if pb.name == "partial")
    assert partial.graph == {}


def test_resolve_waves_diamond() -> None:
    graph = {"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]}
    res = resolve_waves(graph)
    assert res.problems == []
    assert res.waves == [["a"], ["b", "c"], ["d"]]


def test_resolve_waves_cross_wave_edge() -> None:
    # dep from wave 1 (a) consumed in wave 3 (d).
    graph = {"a": [], "b": ["a"], "c": ["b"], "d": ["a", "c"]}
    res = resolve_waves(graph)
    assert res.problems == []
    assert res.waves == [["a"], ["b"], ["c"], ["d"]]


def test_resolve_waves_linear_chain() -> None:
    graph = {"a": [], "b": ["a"], "c": ["b"]}
    res = resolve_waves(graph)
    assert res.problems == []
    assert res.waves == [["a"], ["b"], ["c"]]


def test_resolve_waves_cycle() -> None:
    graph = {"a": ["b"], "b": ["a"]}
    res = resolve_waves(graph)
    assert res.waves == []
    assert len(res.problems) == 1
    prob = res.problems[0]
    assert prob.kind == "cycle"
    assert prob.cycle[0] == prob.cycle[-1]
    assert set(prob.cycle) == {"a", "b"}


def test_resolve_waves_unknown_dep() -> None:
    graph = {"a": [], "b": ["a", "missing"]}
    res = resolve_waves(graph)
    assert res.waves == []
    assert len(res.problems) == 1
    prob = res.problems[0]
    assert prob.kind == "unknown_dep"
    assert prob.dep == "missing"
    assert prob.dependent == "b"


def test_resolve_waves_empty_graph() -> None:
    res = resolve_waves({})
    assert res.waves == []
    assert res.problems == []


def test_resolve_waves_deterministic() -> None:
    graph = {"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]}
    assert resolve_waves(graph).waves == resolve_waves(graph).waves


_SUBGRAPH_YAML = """\
  intake: []
  loop:
    dependencies: [intake]
    repeat: until the reviewer is satisfied
    graph:
      draft: []
      review: [draft]
  publish: [loop]
"""


def test_subgraph_node_parsed(tmp_path: Path) -> None:
    pb = _load_graph(tmp_path, _SUBGRAPH_YAML)
    assert pb.graph_problems == []
    # Outer graph keeps a flat shape; the subgraph key maps to its `dependencies`.
    assert pb.graph == {"intake": [], "loop": ["intake"], "publish": ["loop"]}
    assert list(pb.subgraphs) == ["loop"]
    loop = pb.subgraphs["loop"]
    assert loop.name == "loop"
    assert loop.dependencies == ["intake"]
    assert loop.repeat == "until the reviewer is satisfied"
    assert loop.graph == {"draft": [], "review": ["draft"]}


def test_subgraph_without_repeat_is_none(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  a: []\n  group:\n    dependencies: [a]\n    graph:\n      b: []\n",
    )
    assert pb.graph_problems == []
    assert pb.subgraphs["group"].repeat is None


@pytest.mark.parametrize(
    ("graph_yaml", "detail_match"),
    [
        ("  g:\n    graph:\n      b: []\n", "dependencies"),
        ("  g:\n    dependencies: []\n", "graph"),
        (
            "  g:\n    dependencies: []\n    graph:\n      b: []\n    bogus: 1\n",
            "bogus",
        ),
        ("  g:\n    dependencies: nope\n    graph:\n      b: []\n", "dependencies"),
        ("  g:\n    dependencies: []\n    graph: nope\n", "graph"),
        ("  g:\n    dependencies: []\n    graph: {}\n", "graph"),
    ],
)
def test_bad_subgraph_node(tmp_path: Path, graph_yaml: str, detail_match: str) -> None:
    pb = _load_graph(tmp_path, graph_yaml)
    assert [p.kind for p in pb.graph_problems] == ["bad_node"]
    prob = pb.graph_problems[0]
    assert prob.node == "g"
    assert detail_match in prob.detail
    # The malformed node is dropped from both maps.
    assert pb.graph == {}
    assert pb.subgraphs == {}


def test_nested_subgraph_reported(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  outer:\n"
        "    dependencies: []\n"
        "    graph:\n"
        "      inner:\n"
        "        dependencies: []\n"
        "        graph:\n"
        "          deep: []\n",
    )
    assert [p.kind for p in pb.graph_problems] == ["nested_subgraph"]
    prob = pb.graph_problems[0]
    assert prob.node == "inner"
    assert prob.scope == "outer"
    assert pb.subgraphs["outer"].graph == {}


def test_duplicate_step_outer_and_inner(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  draft: []\n  loop:\n    dependencies: []\n    graph:\n      draft: []\n",
    )
    assert [p.kind for p in pb.graph_problems] == ["duplicate_step"]
    assert pb.graph_problems[0].node == "draft"
    assert pb.graph_problems[0].scope == "loop"


def test_duplicate_step_across_two_inner_graphs(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  one:\n    dependencies: []\n    graph:\n      shared: []\n"
        "  two:\n    dependencies: []\n    graph:\n      shared: []\n",
    )
    assert [p.kind for p in pb.graph_problems] == ["duplicate_step"]
    assert pb.graph_problems[0].node == "shared"
    assert pb.graph_problems[0].scope == "two"


def test_inner_step_colliding_with_subgraph_key(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  loop:\n    dependencies: []\n    graph:\n      loop: []\n",
    )
    assert [p.kind for p in pb.graph_problems] == ["duplicate_step"]
    assert pb.graph_problems[0].node == "loop"


def test_scalar_node_value_is_bad_node(tmp_path: Path) -> None:
    pb = _load_graph(tmp_path, "  a: nope\n")
    assert [p.kind for p in pb.graph_problems] == ["bad_node"]
    assert pb.graph == {}


def test_flat_graph_has_no_subgraphs_or_problems() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert alpha.subgraphs == {}
    assert alpha.graph_problems == []


def test_resolve_scopes_outer_and_inner_waves(tmp_path: Path) -> None:
    pb = _load_graph(tmp_path, _SUBGRAPH_YAML)
    scopes = pb.resolve_scopes()
    assert set(scopes) == {"", "loop"}
    # The subgraph node is placed by its `dependencies`, exactly like a plain step.
    assert scopes[""].waves == [["intake"], ["loop"], ["publish"]]
    assert scopes[""].problems == []
    assert scopes["loop"].waves == [["draft"], ["review"]]
    assert scopes["loop"].problems == []


def test_resolve_scopes_inner_problem_carries_scope(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  a: []\n"
        "  loop:\n    dependencies: [a]\n    graph:\n      b: [nope]\n      c: [b]\n",
    )
    inner = pb.resolve_scopes()["loop"]
    assert inner.waves == []
    assert [(p.kind, p.dep, p.dependent, p.scope) for p in inner.problems] == [
        ("unknown_dep", "nope", "b", "loop")
    ]


def test_inner_dep_on_outer_step_is_unknown(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  a: []\n  loop:\n    dependencies: [a]\n    graph:\n      b: [a]\n",
    )
    inner = pb.resolve_scopes()["loop"]
    assert [(p.kind, p.dep, p.scope) for p in inner.problems] == [
        ("unknown_dep", "a", "loop")
    ]


def test_subgraph_dependency_on_inner_step_is_unknown(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  a: []\n  loop:\n    dependencies: [b]\n    graph:\n      b: []\n",
    )
    outer = pb.resolve_scopes()[""]
    assert [(p.kind, p.dep, p.dependent, p.scope) for p in outer.problems] == [
        ("unknown_dep", "b", "loop", "")
    ]


def test_inner_cycle_carries_scope(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  loop:\n    dependencies: []\n    graph:\n      b: [c]\n      c: [b]\n",
    )
    probs = pb.resolve_scopes()["loop"].problems
    assert [p.kind for p in probs] == ["cycle"]
    assert probs[0].scope == "loop"


def test_executable_step_names(tmp_path: Path) -> None:
    pb = _load_graph(tmp_path, _SUBGRAPH_YAML)
    assert pb.executable_step_names == ["intake", "draft", "review", "publish"]


def test_executable_step_names_flat_graph() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert alpha.executable_step_names == ["gather", "draft"]


_NO_GRAPH_MD = "---\nname: man\ntitle: Man\n---\nbody\n"
_FM_GRAPH_MD = "---\nname: man\ntitle: Man\ngraph:\n  a: []\n---\nbody\n"


def _manifest_playbooks() -> dict[str, Playbook]:
    pbs = Playbook.load_all(vault=None, home_dir=_manifests(), plugin_root=_no_core())
    return {pb.name: pb for pb in pbs}


def test_playbook_yaml_graph_matches_frontmatter_twin() -> None:
    by_name = _manifest_playbooks()
    yaml_twin, fm_twin = by_name["yaml-twin"], by_name["fm-twin"]
    assert yaml_twin.graph_problems == [] and fm_twin.graph_problems == []
    assert yaml_twin.graph == fm_twin.graph
    assert yaml_twin.subgraphs == fm_twin.subgraphs
    assert yaml_twin.executable_step_names == fm_twin.executable_step_names
    assert yaml_twin.resolve_scopes()[""].waves == fm_twin.resolve_scopes()[""].waves
    assert yaml_twin.resolve_scopes()[""].waves == [["intake"], ["build"], ["check"]]


def test_graph_in_both_files_is_stop(tmp_path: Path) -> None:
    pb = _load_manifest(tmp_path, "graph:\n  b: []\n", _FM_GRAPH_MD)
    assert [p.kind for p in pb.graph_problems] == ["graph_in_both"]
    # The manifest's graph wins, so the rest of the load stays coherent.
    assert pb.graph == {"b": []}


def test_unparseable_manifest_is_stop(tmp_path: Path) -> None:
    pb = _load_manifest(tmp_path, "graph: [oops\n", _NO_GRAPH_MD)
    assert [p.kind for p in pb.graph_problems] == ["bad_manifest"]
    assert pb.graph_problems[0].detail


def test_non_mapping_manifest_is_stop(tmp_path: Path) -> None:
    pb = _load_manifest(tmp_path, "- just\n- a list\n", _NO_GRAPH_MD)
    assert [p.kind for p in pb.graph_problems] == ["bad_manifest"]


def test_manifest_absent_keeps_frontmatter_graph() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home(), plugin_root=_no_core())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert alpha.graph == {"gather": [], "draft": ["gather"]}
    assert alpha.graph_problems == []
    assert alpha.states == {}
    assert alpha.state_refs == {}


def test_manifest_without_states_is_valid() -> None:
    yaml_twin = _manifest_playbooks()["yaml-twin"]
    assert yaml_twin.states == {}
    assert yaml_twin.state_refs == {}
    assert yaml_twin.graph_problems == []


def test_states_parsed_with_refs() -> None:
    pb = _manifest_playbooks()["stateful"]
    assert pb.graph_problems == []
    assert set(pb.states) == {"main", "step"}
    main = pb.states["main"]
    assert main.artifact == "index.md"
    assert main.initial == "intaking"
    assert list(main.statuses) == ["intaking", "developing-steps", "done"]
    assert pb.states["step"].artifact == "steps/{instance}/index.md"
    assert pb.state_refs == {"": "main", "step-pipeline": "step"}
    assert pb.subgraphs["step-pipeline"].state == "step"


def test_states_raw_preserved_for_resolver() -> None:
    pb = _manifest_playbooks()["stateful"]
    raw = pb.states["main"].raw
    assert raw["artifact"] == "index.md"
    assert raw["initial"] == "intaking"
    transition = raw["statuses"]["intaking"]["transitions"][0]
    assert transition == {
        "to": "developing-steps",
        "when": "intake step complete",
        "gates": ["request + scope captured in the artifact"],
        "hooks": ["frontmatter-update intaken=@now"],
    }
    assert raw["statuses"]["done"] == {"terminal": True}


def test_unknown_state_ref(tmp_path: Path) -> None:
    pb = _load_manifest(
        tmp_path,
        "state: nope\ngraph:\n  a: []\n"
        "states:\n  main:\n    artifact: index.md\n    initial: s\n"
        "    statuses:\n      s: {terminal: true}\n",
        _NO_GRAPH_MD,
    )
    kinds = [(p.kind, p.node, p.scope) for p in pb.graph_problems]
    assert ("unknown_state", "nope", "") in kinds
    assert ("orphan_state", "main", "") in kinds


def test_unknown_state_ref_from_subgraph(tmp_path: Path) -> None:
    pb = _load_manifest(
        tmp_path,
        "graph:\n  loop:\n    dependencies: []\n    state: nope\n"
        "    graph:\n      b: []\n",
        _NO_GRAPH_MD,
    )
    assert [(p.kind, p.node, p.scope) for p in pb.graph_problems] == [
        ("unknown_state", "nope", "loop")
    ]


def test_orphan_state_only(tmp_path: Path) -> None:
    pb = _load_manifest(
        tmp_path,
        "graph:\n  a: []\n"
        "states:\n  unused:\n    artifact: index.md\n    initial: s\n"
        "    statuses:\n      s: {terminal: true}\n",
        _NO_GRAPH_MD,
    )
    assert [(p.kind, p.node) for p in pb.graph_problems] == [("orphan_state", "unused")]


@pytest.mark.parametrize(
    ("entry", "detail_match"),
    [
        ("    initial: s\n    statuses:\n      s: {}\n", "artifact"),
        ("    artifact: index.md\n    statuses:\n      s: {}\n", "initial"),
        (
            "    artifact: index.md\n    initial: nope\n    statuses:\n      s: {}\n",
            "initial",
        ),
        ("    artifact: index.md\n    initial: s\n", "initial"),
        ("", "mapping"),
    ],
)
def test_bad_state_entry(tmp_path: Path, entry: str, detail_match: str) -> None:
    pb = _load_manifest(
        tmp_path,
        f"state: main\ngraph:\n  a: []\nstates:\n  main:\n{entry}",
        _NO_GRAPH_MD,
    )
    assert [p.kind for p in pb.graph_problems] == ["bad_state"]
    prob = pb.graph_problems[0]
    assert prob.node == "main"
    assert detail_match in prob.detail
    assert pb.states == {}


def test_instance_artifact_rejected_outside_subgraph(tmp_path: Path) -> None:
    pb = _load_manifest(
        tmp_path,
        "state: main\ngraph:\n  a: []\n"
        "states:\n  main:\n    artifact: steps/{instance}/index.md\n    initial: s\n"
        "    statuses:\n      s: {terminal: true}\n",
        _NO_GRAPH_MD,
    )
    assert [p.kind for p in pb.graph_problems] == ["bad_state"]
    assert "{instance}" in pb.graph_problems[0].detail


def test_instance_artifact_allowed_for_subgraph_state() -> None:
    pb = _manifest_playbooks()["stateful"]
    assert pb.graph_problems == []
    assert "{instance}" in pb.states["step"].artifact


def _load_step_fm(tmp_path: Path, step_fm: str) -> Step:
    """Load a single-step playbook whose step frontmatter body is `step_fm`."""
    pb_dir = tmp_path / "_playbooks" / "io"
    (pb_dir / "one").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text("---\nname: io\ntitle: IO\n---\nbody\n")
    (pb_dir / "one" / "prompt.md").write_text(f"---\nsummary: s\n{step_fm}---\ndo it\n")
    pbs = Playbook.load_all(vault=None, home_dir=tmp_path, plugin_root=_no_core())
    return pbs[0].steps[0]


def test_step_io_absent_keys_default_empty(tmp_path: Path) -> None:
    step = _load_step_fm(tmp_path, "")
    assert step.inputs == []
    assert step.outputs == []


def test_step_inputs_mapping_with_from(tmp_path: Path) -> None:
    step = _load_step_fm(
        tmp_path, "inputs:\n  - what: the brief\n    from: intake\noutputs:\n  - a draft\n"
    )
    assert step.inputs == [StepInput(what="the brief", from_="intake")]
    assert step.outputs == ["a draft"]


def test_step_inputs_mapping_without_from(tmp_path: Path) -> None:
    step = _load_step_fm(tmp_path, "inputs:\n  - what: the brief\n")
    assert step.inputs == [StepInput(what="the brief", from_=None)]


def test_step_inputs_string_shorthand(tmp_path: Path) -> None:
    step = _load_step_fm(tmp_path, "inputs:\n  - the brief\n")
    assert step.inputs == [StepInput(what="the brief", from_=None)]


@pytest.mark.parametrize(
    "entry",
    ["  - from: intake\n", "  - 3\n", "  - - nested\n"],
)
def test_step_malformed_input_entry_skipped(
    tmp_path: Path, entry: str, capsys: pytest.CaptureFixture[str]
) -> None:
    step = _load_step_fm(tmp_path, f"inputs:\n{entry}  - the brief\n")
    assert step.inputs == [StepInput(what="the brief")]
    assert "one/prompt.md has malformed inputs entry, skipping" in capsys.readouterr().err


def test_step_malformed_output_entry_skipped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    step = _load_step_fm(tmp_path, "outputs:\n  - what: nope\n  - a draft\n")
    assert step.outputs == ["a draft"]
    err = capsys.readouterr().err
    assert "one/prompt.md has malformed outputs entry, skipping" in err


@pytest.mark.parametrize("key", ["inputs", "outputs"])
def test_step_non_list_io_warns_and_empties(
    tmp_path: Path, key: str, capsys: pytest.CaptureFixture[str]
) -> None:
    step = _load_step_fm(tmp_path, f"{key}: just a string\n")
    assert getattr(step, key) == []
    assert f"one/prompt.md has non-list {key}, ignoring" in capsys.readouterr().err


def test_subgraph_state_must_be_string(tmp_path: Path) -> None:
    pb = _load_graph(
        tmp_path,
        "  loop:\n    dependencies: []\n    state: 3\n    graph:\n      b: []\n",
    )
    assert [p.kind for p in pb.graph_problems] == ["bad_node"]
    assert "state" in pb.graph_problems[0].detail
