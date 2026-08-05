from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from booping.context import config as config_mod
from booping.context.lifecycle import (
    InvalidTransitionError,
    resolve_edges,
    resolve_hooks,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def machine() -> dict[str, Any]:
    """The plan state machine from the real plugin config, with no overrides."""
    plugin_root = Path(__file__).resolve().parents[3]
    cfg: dict[str, Any] = config_mod.load(plugin_root, [])
    return cfg.get("plan", {})


@pytest.fixture()
def equivalence_table() -> list[dict[str, Any]]:
    """Load the on_exit → hooks equivalence fixture."""
    path = Path(__file__).resolve().parents[1] / "__fixtures__" / "on_exit_equivalence.yaml"
    data: Any = yaml.safe_load(path.read_text())
    return data["entries"]


# ---------------------------------------------------------------------------
# resolve_edges
# ---------------------------------------------------------------------------

class TestResolveEdges:
    def test_own_edges_returned(self, machine: dict[str, Any]) -> None:
        edges = resolve_edges("backlog", machine)
        tos = {e.to for e in edges}
        # Own edge: backlog → in-spec
        assert "in-spec" in tos

    def test_inherits_specification_cancelled(self, machine: dict[str, Any]) -> None:
        edges = resolve_edges("backlog", machine)
        tos = {e.to for e in edges}
        # Inherited from the specification superstate: → cancelled
        assert "cancelled" in tos

    def test_substate_wins_on_collision(self, machine: dict[str, Any]) -> None:
        # awaiting-learning has its own gated → done edge; the review superstate
        # also offers → done (the skip path). The substate edge wins on the `to`
        # collision, so there's only one done edge and it carries the gated "when".
        edges = resolve_edges("awaiting-learning", machine)
        done_edges = [e for e in edges if e.to == "done"]
        assert len(done_edges) == 1
        assert "accepted learnings" in done_edges[0].when

    def test_spec_states_do_not_reach_in_progress(self, machine: dict[str, Any]) -> None:
        # in-progress lives only on ready-for-dev now; specification-phase states
        # must not inherit a shortcut into execution.
        for status in ("backlog", "in-spec", "awaiting-plan-review"):
            tos = {e.to for e in resolve_edges(status, machine)}
            assert "in-progress" not in tos

    def test_in_progress_own_edges(self, machine: dict[str, Any]) -> None:
        edges = resolve_edges("in-progress", machine)
        tos = {e.to for e in edges}
        # Own: → awaiting-retro.  Inherited from executing: → fail.
        assert "awaiting-retro" in tos
        assert "fail" in tos

    def test_terminal_status_no_edges(self, machine: dict[str, Any]) -> None:
        edges = resolve_edges("done", machine)
        assert edges == []

    def test_ready_for_dev_gets_inherited_cancelled(self, machine: dict[str, Any]) -> None:
        edges = resolve_edges("ready-for-dev", machine)
        tos = {e.to for e in edges}
        # Own: → in-progress.  Inherited from planned: → cancelled.
        assert "in-progress" in tos
        assert "cancelled" in tos

    def test_awaiting_plan_review_edges(self, machine: dict[str, Any]) -> None:
        edges = resolve_edges("awaiting-plan-review", machine)
        tos = {e.to for e in edges}
        # Own: → ready-for-dev, → in-spec
        assert "ready-for-dev" in tos
        assert "in-spec" in tos
        # Inherited from planned: → cancelled
        assert "cancelled" in tos
        # No shortcut into execution
        assert "in-progress" not in tos


# ---------------------------------------------------------------------------
# resolve_hooks
# ---------------------------------------------------------------------------

class TestResolveHooks:
    def test_same_superstate_no_boundary_hooks(self, machine: dict[str, Any]) -> None:
        # in-spec → awaiting-plan-review: both in planning, no boundary crossed
        hooks = resolve_hooks("in-spec", "awaiting-plan-review", machine)
        assert hooks[0] == "frontmatter-update status=awaiting-plan-review"
        # Edge hooks: planned + commit
        assert "frontmatter-update planned=@now" in hooks
        assert "frontmatter-update commit=@head" in hooks
        # No boundary hooks (same superstate)
        assert "frontmatter-update completed=@now" not in hooks
        assert "frontmatter-update started=@now" not in hooks
        # Post hooks
        assert "vault-commit" in hooks

    def test_planning_to_terminal_boundary(self, machine: dict[str, Any]) -> None:
        # backlog → cancelled: crosses specification → terminal
        hooks = resolve_hooks("backlog", "cancelled", machine)
        assert hooks[0] == "frontmatter-update status=cancelled"
        # terminal on_entry fires
        assert "frontmatter-update completed=@now" in hooks
        # Post hooks
        assert "vault-commit" in hooks

    def test_planning_to_executing_boundary(self, machine: dict[str, Any]) -> None:
        # ready-for-dev → in-progress: crosses planned → executing
        hooks = resolve_hooks("ready-for-dev", "in-progress", machine)
        assert hooks[0] == "frontmatter-update status=in-progress"
        # executing on_entry fires (started + commit)
        assert "frontmatter-update started=@now" in hooks
        assert "frontmatter-update commit=@head" in hooks
        # Post hooks
        assert "vault-commit" in hooks

    def test_executing_to_review_boundary(self, machine: dict[str, Any]) -> None:
        # in-progress → awaiting-retro: crosses executing → review
        hooks = resolve_hooks("in-progress", "awaiting-retro", machine)
        assert hooks[0] == "frontmatter-update status=awaiting-retro"
        # closing on_entry fires (completed)
        assert "frontmatter-update completed=@now" in hooks
        # Edge hook: suggest /playbook retro
        assert "suggest /playbook retro" in hooks

    def test_executing_to_terminal_boundary(self, machine: dict[str, Any]) -> None:
        # in-progress → fail: crosses executing → terminal
        hooks = resolve_hooks("in-progress", "fail", machine)
        assert hooks[0] == "frontmatter-update status=fail"
        # terminal on_entry fires (completed)
        assert "frontmatter-update completed=@now" in hooks

    def test_closing_to_terminal_boundary(self, machine: dict[str, Any]) -> None:
        # awaiting-learning → done: crosses review → terminal
        hooks = resolve_hooks("awaiting-learning", "done", machine)
        assert hooks[0] == "frontmatter-update status=done"
        # terminal on_entry fires (completed)
        assert "frontmatter-update completed=@now" in hooks

    def test_closing_internal_no_boundary(self, machine: dict[str, Any]) -> None:
        # awaiting-retro → awaiting-learning: both in review
        hooks = resolve_hooks("awaiting-retro", "awaiting-learning", machine)
        assert hooks[0] == "frontmatter-update status=awaiting-learning"
        # Edge hooks
        assert "frontmatter-update retro=retrospectives/YYYYMMDD-{kebab-title}.md" in hooks
        assert "frontmatter-update goal=success|partial|fail" in hooks
        # No boundary hooks (same superstate)
        assert "frontmatter-update completed=@now" not in hooks

    def test_awaiting_retro_to_done(self, machine: dict[str, Any]) -> None:
        # awaiting-retro → done: crosses closing → terminal
        hooks = resolve_hooks("awaiting-retro", "done", machine)
        assert hooks[0] == "frontmatter-update status=done"
        # Edge hook: goal=skipped
        assert "frontmatter-update goal=skipped" in hooks
        # terminal on_entry fires
        assert "frontmatter-update completed=@now" in hooks

    def test_invalid_transition_raises(self, machine: dict[str, Any]) -> None:
        with pytest.raises(InvalidTransitionError):
            resolve_hooks("done", "in-progress", machine)

    def test_invalid_same_status_transition(self, machine: dict[str, Any]) -> None:
        with pytest.raises(InvalidTransitionError):
            resolve_hooks("in-spec", "in-spec", machine)


# ---------------------------------------------------------------------------
# Machine-dict genericity — any dict of the shape resolves, not just plan config
# ---------------------------------------------------------------------------

class TestArbitraryMachine:
    def test_resolves_a_non_plan_machine(self) -> None:
        custom: dict[str, Any] = {
            "statuses": {
                "draft": {
                    "transitions": [
                        {"to": "shipped", "skill": "x", "hooks": ["frontmatter-update ship=@now"]}
                    ]
                },
                "shipped": {},
            },
            "superstates": {
                "open": {"states": ["draft"], "on_exit": ["frontmatter-update closed=@now"]},
            },
            "hooks": {"post": ["vault-commit"]},
        }

        assert [e.to for e in resolve_edges("draft", custom)] == ["shipped"]
        assert resolve_hooks("draft", "shipped", custom) == [
            "frontmatter-update status=shipped",
            "frontmatter-update closed=@now",
            "frontmatter-update ship=@now",
            "vault-commit",
        ]


# ---------------------------------------------------------------------------
# Hook ordering
# ---------------------------------------------------------------------------

class TestHookOrdering:
    def test_order_status_set_first(self, machine: dict[str, Any]) -> None:
        hooks = resolve_hooks("in-spec", "awaiting-plan-review", machine)
        assert hooks[0] == "frontmatter-update status=awaiting-plan-review"

    def test_order_on_exit_before_edge_hooks(self, machine: dict[str, Any]) -> None:
        # in-progress → awaiting-retro: exits executing, enters closing
        hooks = resolve_hooks("in-progress", "awaiting-retro", machine)
        # executing on_exit is empty, but the ordering still holds:
        # edge hooks come before on_entry
        suggest_idx = hooks.index("suggest /playbook retro")
        completed_idx = hooks.index("frontmatter-update completed=@now")
        assert suggest_idx < completed_idx

    def test_order_on_entry_after_edge_hooks(self, machine: dict[str, Any]) -> None:
        # awaiting-retro → done: edge hook (goal=skipped) before terminal on_entry
        hooks = resolve_hooks("awaiting-retro", "done", machine)
        goal_idx = hooks.index("frontmatter-update goal=skipped")
        completed_idx = hooks.index("frontmatter-update completed=@now")
        assert goal_idx < completed_idx

    def test_order_post_hooks_last(self, machine: dict[str, Any]) -> None:
        hooks = resolve_hooks("in-spec", "awaiting-plan-review", machine)
        vault_idx = hooks.index("vault-commit")
        # All other hooks come before post hooks
        assert vault_idx == len(hooks) - 1

    def test_full_order_crossing_boundary(self, machine: dict[str, Any]) -> None:
        # ready-for-dev → in-progress: planned → executing
        hooks = resolve_hooks("ready-for-dev", "in-progress", machine)
        expected = [
            "frontmatter-update status=in-progress",
            # planned on_exit (empty)
            # edge hooks (empty — moved to boundary)
            "frontmatter-update started=@now",
            "frontmatter-update commit=@head",
            "vault-commit",
        ]
        assert hooks == expected


# ---------------------------------------------------------------------------
# Equivalence table verification
# ---------------------------------------------------------------------------

class TestEquivalence:
    def test_every_old_mutation_appears_in_new_wiring(
        self, machine: dict[str, Any], equivalence_table: list[dict[str, Any]]
    ) -> None:
        """Every pre-change on_exit mutation appears exactly once in the new wiring."""
        for entry in equivalence_table:
            from_s: str = str(entry["from"])
            to_s: str = str(entry["to"])
            new_hook: str = str(entry["new_hook"])
            new_location: str = str(entry["new_location"])

            if new_location == "edge_hooks":
                hooks = resolve_hooks(from_s, to_s, machine)
                assert new_hook in hooks, (
                    f"Edge hook {new_hook!r} missing for {from_s} → {to_s}. "
                    f"Got: {hooks}"
                )
            elif new_location == "superstate_on_entry":
                target: str = str(entry["new_target"])
                superstates: dict[str, Any] = machine.get("superstates", {})
                on_entry: list[Any] = superstates.get(target, {}).get("on_entry", [])
                on_entry_strs = [str(h) for h in on_entry]
                assert new_hook in on_entry_strs, (
                    f"Superstate on_entry {new_hook!r} missing for {target!r}. "
                    f"Got: {on_entry_strs}"
                )

    def test_no_duplicate_mutations(self, equivalence_table: list[dict[str, Any]]) -> None:
        """Each (from, to, new_hook) mutation is listed once. Keying on the
        emitted hook (not the `old` provenance) — multiple new mutations may
        share one `old` source (e.g. inherited planning edges)."""
        seen: set[tuple[str, str, str]] = set()
        for entry in equivalence_table:
            key = (str(entry["from"]), str(entry["to"]), str(entry["new_hook"]))
            assert key not in seen, f"Duplicate entry: {key}"
            seen.add(key)

    def test_mutation_set_matches_fixture_exactly(
        self, machine: dict[str, Any], equivalence_table: list[dict[str, Any]]
    ) -> None:
        """For every valid edge, the frontmatter mutations resolve_hooks emits
        equal EXACTLY the set documented in the fixture — none missing, none
        undocumented. The mechanical status=<to> set is excluded (it is implied
        by every edge, not a tracked mutation). This is the "no extras"
        direction: a stray mutation wired in without a fixture row fails here.
        """
        # Documented frontmatter mutations per edge, keyed (from, to).
        documented: dict[tuple[str, str], set[str]] = {}
        for entry in equivalence_table:
            new_hook = str(entry["new_hook"])
            if not new_hook.startswith("frontmatter-update "):
                # non-frontmatter rows (e.g. `suggest /playbook retro`)
                # aren't tracked here
                continue
            key = (str(entry["from"]), str(entry["to"]))
            documented.setdefault(key, set()).add(new_hook)

        statuses: dict[str, Any] = machine.get("statuses", {})
        for from_s in statuses:
            for edge in resolve_edges(from_s, machine):
                key = (from_s, edge.to)
                hooks = resolve_hooks(from_s, edge.to, machine)
                actual = {
                    h
                    for h in hooks
                    if h.startswith("frontmatter-update ")
                    and not h.startswith("frontmatter-update status=")
                }
                expected = documented.get(key, set())
                assert actual == expected, (
                    f"Mutation set mismatch for {from_s} → {edge.to}.\n"
                    f"  resolve_hooks emits: {sorted(actual)}\n"
                    f"  fixture documents : {sorted(expected)}\n"
                    f"  undocumented extras: {sorted(actual - expected)}\n"
                    f"  documented missing : {sorted(expected - actual)}"
                )


# ---------------------------------------------------------------------------
# Deep-merge safety
# ---------------------------------------------------------------------------

class TestDeepMergeSafety:
    def test_superstates_merge_over_empty_override(self) -> None:
        """plan.superstates + plan.hooks deep-merge cleanly over an empty
        project override (no contract regression)."""
        plugin_root = Path(__file__).resolve().parents[3]
        # Simulate an empty project override
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
            yaml.dump({"plan": {"statuses": {}}}, f)
            override_path = Path(f.name)

        merged = config_mod.load(plugin_root, [override_path])
        override_path.unlink()

        # Superstates should survive the merge
        ss: dict[str, Any] = merged.get("plan", {}).get("superstates", {})
        assert "specification" in ss
        assert "planned" in ss
        assert "executing" in ss
        assert "review" in ss
        assert "terminal" in ss

        # Hooks should survive the merge
        post: list[Any] = merged.get("plan", {}).get("hooks", {}).get("post", [])
        assert "vault-commit" in post

    def test_original_statuses_preserved_after_merge(self) -> None:
        """Existing plan.statuses content is not lost after adding superstates."""
        plugin_root = Path(__file__).resolve().parents[3]
        cfg = config_mod.load(plugin_root, [])
        statuses: dict[str, Any] = cfg.get("plan", {}).get("statuses", {})
        assert "backlog" in statuses
        assert "in-spec" in statuses
        assert "in-progress" in statuses
        # Check a transition still has its gates
        in_spec: dict[str, Any] = statuses["in-spec"]
        apr_trans: list[dict[str, Any]] = [
            t for t in in_spec["transitions"] if t["to"] == "awaiting-plan-review"
        ]
        assert len(apr_trans) == 1
        assert len(apr_trans[0]["gates"]) == 2