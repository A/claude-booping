"""State-machine resolver — superstate-aware edge + hook resolution.

Operates on a *machine dict* carrying ``statuses``, ``superstates``, and
``hooks`` — the shape of ``config["plan"]`` and of a playbook manifest's
``states:`` entry alike.  Produces valid edges and ordered hook lists for any
status transition, without executing them (that is the dispatcher's job).
"""
from __future__ import annotations

from typing import Any


class InvalidTransitionError(Exception):
    """Raised when ``resolve_hooks`` is called with a ``to`` status that is
    not reachable from ``from_status`` via any own or inherited edge."""


# ---------------------------------------------------------------------------
# Edge representation
# ---------------------------------------------------------------------------

class Edge:
    """A single transition edge with metadata."""

    __slots__ = ("to", "skill", "when", "gates", "hooks")

    def __init__(
        self,
        to: str,
        skill: str,
        when: str = "",
        gates: list[str] | None = None,
        hooks: list[str] | None = None,
    ) -> None:
        self.to = to
        self.skill = skill
        self.when = when
        self.gates = gates or []
        self.hooks = hooks or []

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Edge(to={self.to!r}, skill={self.skill!r}, "
            f"when={self.when!r}, gates={self.gates!r}, hooks={self.hooks!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        return (
            self.to == other.to
            and self.skill == other.skill
            and self.when == other.when
            and self.gates == other.gates
            and self.hooks == other.hooks
        )

    def __hash__(self) -> int:
        return hash((self.to, self.skill, self.when, tuple(self.gates), tuple(self.hooks)))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_transition(t: dict[str, Any]) -> Edge:
    """Parse a raw transition dict from config into an Edge. `skill` is plan-only —
    playbook state machines have no owning skill, so it defaults to empty."""
    return Edge(
        to=str(t["to"]),
        skill=str(t.get("skill", "")),
        when=str(t.get("when", "")),
        gates=[str(g) for g in t.get("gates", [])],
        hooks=[str(h) for h in t.get("hooks", [])],
    )


def _superstate_for(status: str, superstates: dict[str, Any]) -> str | None:
    """Return the superstate name that contains *status*, or None."""
    for name, ss in superstates.items():
        if status in ss.get("states", []):
            return name
    return None


def _superstate_hooks(key: str, superstate_name: str, superstates: dict[str, Any]) -> list[str]:
    """Return the ``key`` (``on_exit`` / ``on_entry``) hooks list for a superstate."""
    ss = superstates.get(superstate_name, {})
    return [str(h) for h in ss.get(key, [])]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_edges(status: str, machine: dict[str, Any]) -> list[Edge]:
    """Return all valid edges from *status*: own transitions ∪ inherited
    superstate transitions, with substate edges winning on ``to`` collision.
    """
    statuses = machine.get("statuses", {})
    superstates = machine.get("superstates", {})

    # Own edges
    status_data = statuses.get(status, {})
    own_edges: list[Edge] = [_parse_transition(t) for t in status_data.get("transitions", [])]
    own_tos: set[str] = {e.to for e in own_edges}

    # Inherited edges from superstate
    ss_name = _superstate_for(status, superstates)
    inherited_edges: list[Edge] = []
    if ss_name is not None:
        ss_data = superstates[ss_name]
        for t in ss_data.get("transitions", []):
            edge = _parse_transition(t)
            if edge.to not in own_tos:
                inherited_edges.append(edge)

    return own_edges + inherited_edges


def resolve_hooks(from_status: str, to_status: str, machine: dict[str, Any]) -> list[str]:
    """Return the ordered hook list for transitioning *from_status* → *to_status*.

    Order:
    1. ``frontmatter-update status=<to>``  (status-set, prepended for dispatcher)
    2. on_exit boundary hooks — inner→outer, only if boundary crossed
    3. matched edge hooks
    4. on_entry boundary hooks — outer→inner, only if boundary crossed
    5. ``hooks.post``

    Raises :class:`InvalidTransitionError` when *to_status* is not reachable.
    """
    superstates = machine.get("superstates", {})

    # 1. Find the matched edge
    edges = resolve_edges(from_status, machine)
    matched: Edge | None = None
    for e in edges:
        if e.to == to_status:
            matched = e
            break
    if matched is None:
        raise InvalidTransitionError(
            f"No valid transition from {from_status!r} to {to_status!r}"
        )

    result: list[str] = []

    # 1. Status-set (prepended for the dispatcher)
    result.append(f"frontmatter-update status={to_status}")

    # 2. on_exit boundary hooks (inner → outer, only if boundary crossed)
    from_ss = _superstate_for(from_status, superstates)
    to_ss = _superstate_for(to_status, superstates)
    if from_ss is not None and from_ss != to_ss:
        # Exiting from_ss — add on_exit hooks
        result.extend(_superstate_hooks("on_exit", from_ss, superstates))

    # 3. Edge hooks
    result.extend(matched.hooks)

    # 4. on_entry boundary hooks (outer → inner, only if boundary crossed)
    if to_ss is not None and from_ss != to_ss:
        result.extend(_superstate_hooks("on_entry", to_ss, superstates))

    # 5. post hooks (always run)
    post_hooks = machine.get("hooks", {}).get("post", [])
    result.extend(str(h) for h in post_hooks)

    return result