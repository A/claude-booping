from __future__ import annotations

from pathlib import Path

import pytest

from booping.context.playbook import Playbook, resolve_agent, resolve_waves
from tests.helpers import get_fixture_path


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
