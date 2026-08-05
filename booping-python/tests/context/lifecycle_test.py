from __future__ import annotations

from typing import Any

import pytest

from booping.context.lifecycle import (
    InvalidTransitionError,
    resolve_edges,
    resolve_hooks,
)


@pytest.fixture()
def machine() -> dict[str, Any]:
    """A machine dict of the shape a playbook manifest's `states:` entry carries."""
    return {
        "statuses": {
            "draft": {
                "transitions": [
                    {
                        "to": "shipped",
                        "hooks": ["frontmatter-update ship=stamped"],
                    },
                    {"to": "abandoned"},
                ]
            },
            "shipped": {
                "transitions": [{"to": "abandoned", "when": "own edge wins"}]
            },
            "abandoned": {"terminal": True},
        },
        "superstates": {
            "open": {
                "states": ["draft", "shipped"],
                "transitions": [{"to": "abandoned", "when": "inherited"}],
                "on_exit": ["frontmatter-update closed=stamped"],
            },
            "terminal": {
                "states": ["abandoned"],
                "on_entry": ["frontmatter-update completed=stamped"],
            },
        },
        "hooks": {"post": ["script commit"]},
    }


class TestResolveEdges:
    def test_own_and_inherited_edges(self, machine: dict[str, Any]) -> None:
        assert {e.to for e in resolve_edges("draft", machine)} == {
            "shipped",
            "abandoned",
        }

    def test_substate_wins_on_collision(self, machine: dict[str, Any]) -> None:
        edges = [e for e in resolve_edges("shipped", machine) if e.to == "abandoned"]
        assert len(edges) == 1
        assert edges[0].when == "own edge wins"

    def test_terminal_status_no_edges(self, machine: dict[str, Any]) -> None:
        assert resolve_edges("abandoned", machine) == []


class TestResolveHooks:
    def test_full_order_crossing_boundary(self, machine: dict[str, Any]) -> None:
        assert resolve_hooks("draft", "abandoned", machine) == [
            "frontmatter-update status=abandoned",
            "frontmatter-update closed=stamped",
            "frontmatter-update completed=stamped",
            "script commit",
        ]

    def test_no_boundary_hooks_within_superstate(self, machine: dict[str, Any]) -> None:
        assert resolve_hooks("draft", "shipped", machine) == [
            "frontmatter-update status=shipped",
            "frontmatter-update ship=stamped",
            "script commit",
        ]

    def test_invalid_transition_raises(self, machine: dict[str, Any]) -> None:
        with pytest.raises(InvalidTransitionError):
            resolve_hooks("abandoned", "draft", machine)

    def test_invalid_same_status_transition(self, machine: dict[str, Any]) -> None:
        with pytest.raises(InvalidTransitionError):
            resolve_hooks("draft", "draft", machine)
