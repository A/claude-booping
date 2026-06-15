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
def full_config() -> dict[str, Any]:
    """Load the real plugin config (src/config.yaml) with no overrides."""
    plugin_root = Path(__file__).resolve().parents[3]
    return config_mod.load(plugin_root, [])


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
    def test_own_edges_returned(self, full_config: dict[str, Any]) -> None:
        edges = resolve_edges("backlog", full_config)
        tos = {e.to for e in edges}
        # Own edges: backlog → in-spec, backlog → cancelled
        assert "in-spec" in tos
        assert "cancelled" in tos

    def test_inherits_planning_edges(self, full_config: dict[str, Any]) -> None:
        edges = resolve_edges("backlog", full_config)
        tos = {e.to for e in edges}
        # Inherited from planning: backlog also gets → in-progress
        assert "in-progress" in tos

    def test_substate_wins_on_collision(self, full_config: dict[str, Any]) -> None:
        # backlog has its own → cancelled edge; planning also has → cancelled.
        # The substate edge should win, so there's only one cancelled edge.
        edges = resolve_edges("backlog", full_config)
        cancelled_edges = [e for e in edges if e.to == "cancelled"]
        assert len(cancelled_edges) == 1
        # The substate edge carries the specific "when"
        assert "before grooming" in cancelled_edges[0].when

    def test_in_spec_gets_inherited_in_progress(self, full_config: dict[str, Any]) -> None:
        edges = resolve_edges("in-spec", full_config)
        tos = {e.to for e in edges}
        assert "in-progress" in tos

    def test_in_progress_own_edges(self, full_config: dict[str, Any]) -> None:
        edges = resolve_edges("in-progress", full_config)
        tos = {e.to for e in edges}
        assert "awaiting-retro" in tos
        assert "fail" in tos

    def test_terminal_status_no_edges(self, full_config: dict[str, Any]) -> None:
        edges = resolve_edges("done", full_config)
        assert edges == []

    def test_ready_for_dev_gets_inherited_cancelled(self, full_config: dict[str, Any]) -> None:
        edges = resolve_edges("ready-for-dev", full_config)
        tos = {e.to for e in edges}
        # Own: → in-progress.  Inherited from planning: → cancelled.
        assert "in-progress" in tos
        assert "cancelled" in tos

    def test_awaiting_plan_review_edges(self, full_config: dict[str, Any]) -> None:
        edges = resolve_edges("awaiting-plan-review", full_config)
        tos = {e.to for e in edges}
        # Own: → ready-for-dev, → in-spec, → cancelled
        assert "ready-for-dev" in tos
        assert "in-spec" in tos
        assert "cancelled" in tos
        # Inherited from planning: → in-progress (no collision)
        assert "in-progress" in tos


# ---------------------------------------------------------------------------
# resolve_hooks
# ---------------------------------------------------------------------------

class TestResolveHooks:
    def test_same_superstate_no_boundary_hooks(self, full_config: dict[str, Any]) -> None:
        # in-spec → awaiting-plan-review: both in planning, no boundary crossed
        hooks = resolve_hooks("in-spec", "awaiting-plan-review", full_config)
        assert hooks[0] == "frontmatter-update status=awaiting-plan-review"
        # Edge hooks: planned + commit
        assert "frontmatter-update planned=@now" in hooks
        assert "frontmatter-update commit=@head" in hooks
        # No boundary hooks (same superstate)
        assert "frontmatter-update completed=@now" not in hooks
        assert "frontmatter-update started=@now" not in hooks
        # Post hooks
        assert "render-sprints" in hooks
        assert "vault-commit" in hooks

    def test_planning_to_terminal_boundary(self, full_config: dict[str, Any]) -> None:
        # backlog → cancelled: crosses planning → terminal
        hooks = resolve_hooks("backlog", "cancelled", full_config)
        assert hooks[0] == "frontmatter-update status=cancelled"
        # terminal on_entry fires
        assert "frontmatter-update completed=@now" in hooks
        # Post hooks
        assert "render-sprints" in hooks

    def test_planning_to_executing_boundary(self, full_config: dict[str, Any]) -> None:
        # ready-for-dev → in-progress: crosses planning → executing
        hooks = resolve_hooks("ready-for-dev", "in-progress", full_config)
        assert hooks[0] == "frontmatter-update status=in-progress"
        # executing on_entry fires (started + commit)
        assert "frontmatter-update started=@now" in hooks
        assert "frontmatter-update commit=@head" in hooks
        # Post hooks
        assert "render-sprints" in hooks

    def test_executing_to_closing_boundary(self, full_config: dict[str, Any]) -> None:
        # in-progress → awaiting-retro: crosses executing → closing
        hooks = resolve_hooks("in-progress", "awaiting-retro", full_config)
        assert hooks[0] == "frontmatter-update status=awaiting-retro"
        # closing on_entry fires (completed)
        assert "frontmatter-update completed=@now" in hooks
        # Edge hook: suggest /retro
        assert "suggest /retro" in hooks

    def test_executing_to_terminal_boundary(self, full_config: dict[str, Any]) -> None:
        # in-progress → fail: crosses executing → terminal
        hooks = resolve_hooks("in-progress", "fail", full_config)
        assert hooks[0] == "frontmatter-update status=fail"
        # terminal on_entry fires (completed)
        assert "frontmatter-update completed=@now" in hooks

    def test_closing_to_terminal_boundary(self, full_config: dict[str, Any]) -> None:
        # awaiting-learning → done: crosses closing → terminal
        hooks = resolve_hooks("awaiting-learning", "done", full_config)
        assert hooks[0] == "frontmatter-update status=done"
        # terminal on_entry fires (completed)
        assert "frontmatter-update completed=@now" in hooks

    def test_closing_internal_no_boundary(self, full_config: dict[str, Any]) -> None:
        # awaiting-retro → awaiting-learning: both in closing
        hooks = resolve_hooks("awaiting-retro", "awaiting-learning", full_config)
        assert hooks[0] == "frontmatter-update status=awaiting-learning"
        # Edge hooks
        assert "frontmatter-update retro=retrospectives/YYYYMMDD-{kebab-title}.md" in hooks
        assert "frontmatter-update goal=success|partial|fail" in hooks
        # No boundary hooks (same superstate)
        assert "frontmatter-update completed=@now" not in hooks

    def test_awaiting_retro_to_done(self, full_config: dict[str, Any]) -> None:
        # awaiting-retro → done: crosses closing → terminal
        hooks = resolve_hooks("awaiting-retro", "done", full_config)
        assert hooks[0] == "frontmatter-update status=done"
        # Edge hook: goal=skipped
        assert "frontmatter-update goal=skipped" in hooks
        # terminal on_entry fires
        assert "frontmatter-update completed=@now" in hooks

    def test_invalid_transition_raises(self, full_config: dict[str, Any]) -> None:
        with pytest.raises(InvalidTransitionError):
            resolve_hooks("done", "in-progress", full_config)

    def test_invalid_same_status_transition(self, full_config: dict[str, Any]) -> None:
        with pytest.raises(InvalidTransitionError):
            resolve_hooks("in-spec", "in-spec", full_config)


# ---------------------------------------------------------------------------
# Hook ordering
# ---------------------------------------------------------------------------

class TestHookOrdering:
    def test_order_status_set_first(self, full_config: dict[str, Any]) -> None:
        hooks = resolve_hooks("in-spec", "awaiting-plan-review", full_config)
        assert hooks[0] == "frontmatter-update status=awaiting-plan-review"

    def test_order_on_exit_before_edge_hooks(self, full_config: dict[str, Any]) -> None:
        # in-progress → awaiting-retro: exits executing, enters closing
        hooks = resolve_hooks("in-progress", "awaiting-retro", full_config)
        # executing on_exit is empty, but the ordering still holds:
        # edge hooks come before on_entry
        suggest_idx = hooks.index("suggest /retro")
        completed_idx = hooks.index("frontmatter-update completed=@now")
        assert suggest_idx < completed_idx

    def test_order_on_entry_after_edge_hooks(self, full_config: dict[str, Any]) -> None:
        # awaiting-retro → done: edge hook (goal=skipped) before terminal on_entry
        hooks = resolve_hooks("awaiting-retro", "done", full_config)
        goal_idx = hooks.index("frontmatter-update goal=skipped")
        completed_idx = hooks.index("frontmatter-update completed=@now")
        assert goal_idx < completed_idx

    def test_order_post_hooks_last(self, full_config: dict[str, Any]) -> None:
        hooks = resolve_hooks("in-spec", "awaiting-plan-review", full_config)
        render_idx = hooks.index("render-sprints")
        vault_idx = hooks.index("vault-commit")
        # All other hooks come before post hooks
        assert render_idx == len(hooks) - 2
        assert vault_idx == len(hooks) - 1

    def test_full_order_crossing_boundary(self, full_config: dict[str, Any]) -> None:
        # ready-for-dev → in-progress: planning → executing
        hooks = resolve_hooks("ready-for-dev", "in-progress", full_config)
        expected = [
            "frontmatter-update status=in-progress",
            # planning on_exit (empty)
            # edge hooks (empty — moved to boundary)
            "frontmatter-update started=@now",
            "frontmatter-update commit=@head",
            "render-sprints",
            "vault-commit",
        ]
        assert hooks == expected


# ---------------------------------------------------------------------------
# Equivalence table verification
# ---------------------------------------------------------------------------

class TestEquivalence:
    def test_every_old_mutation_appears_in_new_wiring(
        self, full_config: dict[str, Any], equivalence_table: list[dict[str, Any]]
    ) -> None:
        """Every pre-change on_exit mutation appears exactly once in the new wiring."""
        for entry in equivalence_table:
            from_s: str = str(entry["from"])
            to_s: str = str(entry["to"])
            new_hook: str = str(entry["new_hook"])
            new_location: str = str(entry["new_location"])

            if new_location == "edge_hooks":
                hooks = resolve_hooks(from_s, to_s, full_config)
                assert new_hook in hooks, (
                    f"Edge hook {new_hook!r} missing for {from_s} → {to_s}. "
                    f"Got: {hooks}"
                )
            elif new_location == "superstate_on_entry":
                target: str = str(entry["new_target"])
                superstates: dict[str, Any] = full_config.get("plan", {}).get("superstates", {})
                on_entry: list[Any] = superstates.get(target, {}).get("on_entry", [])
                on_entry_strs = [str(h) for h in on_entry]
                assert new_hook in on_entry_strs, (
                    f"Superstate on_entry {new_hook!r} missing for {target!r}. "
                    f"Got: {on_entry_strs}"
                )

    def test_no_duplicate_mutations(self, equivalence_table: list[dict[str, Any]]) -> None:
        """Each (from, to, old) triple is unique in the equivalence table."""
        seen: set[tuple[str, str, str]] = set()
        for entry in equivalence_table:
            key = (str(entry["from"]), str(entry["to"]), str(entry["old"]))
            assert key not in seen, f"Duplicate entry: {key}"
            seen.add(key)


# ---------------------------------------------------------------------------
# Deep-merge safety
# ---------------------------------------------------------------------------

class TestDeepMergeSafety:
    def test_superstates_merge_over_empty_override(self, full_config: dict[str, Any]) -> None:
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
        assert "planning" in ss
        assert "executing" in ss
        assert "closing" in ss
        assert "terminal" in ss

        # Hooks should survive the merge
        post: list[Any] = merged.get("plan", {}).get("hooks", {}).get("post", [])
        assert "render-sprints" in post
        assert "vault-commit" in post

    def test_original_statuses_preserved_after_merge(self, full_config: dict[str, Any]) -> None:
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