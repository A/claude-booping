from __future__ import annotations

from pathlib import Path

import pytest

from booping.context.playbook import Playbook, resolve_agent, resolve_waves
from tests.helpers import get_fixture_path


def _home() -> Path:
    return get_fixture_path("playbooks-home")


def _vault() -> Path:
    return get_fixture_path("playbooks-vault")


def test_global_only_discovery() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home())
    names = {pb.name for pb in pbs}
    # alpha, shared, partial discovered; _lib and nomanifest excluded.
    assert names == {"alpha", "shared", "partial"}
    assert all(pb.scope == "global" for pb in pbs)


def test_underscore_dirs_excluded() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home())
    assert "_lib" not in {pb.name for pb in pbs}


def test_fields_and_step_ordering() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert alpha.title == "Alpha Playbook"
    assert alpha.summary == "A global-only playbook for testing."
    assert alpha.trigger == "when the user says alpha"
    assert "Alpha playbook overview body" in alpha.body
    # Steps are discovered by sorted glob of steps/*.md; `_`-prefixed skipped.
    assert [s.name for s in alpha.steps] == ["draft", "gather"]


def test_step_review_gate_and_agent_null_vs_set() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    draft, gather = alpha.steps
    assert gather.agent == "sonnet:medium"
    assert gather.review_gate is None
    assert draft.agent is None
    assert draft.review_gate == "confirm the draft before continuing"
    assert "Draft the artifact" in draft.body


def test_requires_project_defaults_false_and_parses_true() -> None:
    pbs = Playbook.load_all(vault=_vault(), home_dir=_home())
    by_name = {pb.name: pb for pb in pbs}
    # Not set in alpha's frontmatter → default False; explicit true in beta.
    assert by_name["alpha"].requires_project is False
    assert by_name["beta"].requires_project is True


def test_underscore_prefixed_step_skipped() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert "ignored" not in {s.name for s in alpha.steps}


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
    pbs = Playbook.load_all(vault=_vault(), home_dir=_home())
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
    pbs = Playbook.load_all(vault=None, home_dir=_home())
    partial = next(pb for pb in pbs if pb.name == "partial")
    # Missing title falls back to name; missing summary/trigger default to "".
    assert partial.title == "partial"
    assert partial.summary == ""
    assert partial.trigger == ""
    # Missing step file (`missing`) is dropped; present step (no frontmatter) survives.
    assert [s.name for s in partial.steps] == ["present"]
    assert "Body-only step" in partial.steps[0].body


def test_missing_roots_empty() -> None:
    assert Playbook.load_all(vault=None, home_dir=Path("/nonexistent/home")) == []
    assert (
        Playbook.load_all(vault=Path("/nonexistent/vault"), home_dir=Path("/nonexistent/home"))
        == []
    )


def test_global_root_follows_non_default_home_dir(tmp_path: Path) -> None:
    # A non-default home_dir with its own _playbooks root is honoured.
    root = tmp_path / "custom-home"
    pb_dir = root / "_playbooks" / "gamma" / "steps"
    pb_dir.mkdir(parents=True)
    (root / "_playbooks" / "gamma" / "playbook.md").write_text(
        "---\nname: gamma\ntitle: Gamma\nsteps:\n  - s1\n---\nbody\n"
    )
    (pb_dir / "s1.md").write_text("---\nname: s1\n---\nstep body\n")
    pbs = Playbook.load_all(vault=None, home_dir=root)
    assert [pb.name for pb in pbs] == ["gamma"]
    assert pbs[0].scope == "global"


def test_no_manifest_dir_warns(capsys: pytest.CaptureFixture[str]) -> None:
    Playbook.load_all(vault=None, home_dir=_home())
    err = capsys.readouterr().err
    assert "nomanifest" in err


def test_graph_loads_verbatim_insertion_order() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home())
    alpha = next(pb for pb in pbs if pb.name == "alpha")
    assert alpha.graph == {"gather": [], "draft": ["gather"]}
    assert list(alpha.graph.keys()) == ["gather", "draft"]


def test_graph_missing_defaults_empty() -> None:
    pbs = Playbook.load_all(vault=None, home_dir=_home())
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
