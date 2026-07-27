from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter

_MODEL_TIERS = {"opus", "sonnet", "haiku", "fable"}


def _warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr)


def resolve_agent(value: str | None) -> dict[str, str]:
    """Resolve a step's collapsed `agent` grammar into a rendering mode.

    * ``None`` → inline execution.
    * ``<model>:<effort>`` (model tier before the first colon) → model sub-agent.
    * any other non-null string → named sub-agent (colons in the name are kept).
    """
    if value is None:
        return {"mode": "inline"}
    left, sep, right = value.partition(":")
    if sep and left in _MODEL_TIERS:
        return {"mode": "model", "model": left, "effort": right}
    return {"mode": "named", "name": value}


class Step(BaseModel):
    name: str
    title: str | None = None
    summary: str = ""
    agent: str | None = None
    review_gate: str | None = None
    body: str = ""
    path: Path


class GraphProblem(BaseModel):
    kind: Literal["cycle", "unknown_dep"]
    cycle: list[str] = []  # kind=cycle: the cycle path, e.g. ["a", "b", "a"]
    dep: str = ""  # kind=unknown_dep: the missing key
    dependent: str = ""  # kind=unknown_dep: the step that listed it


class WaveResolution(BaseModel):
    waves: list[list[str]] = []  # empty when any problem present
    problems: list[GraphProblem] = []


def resolve_waves(graph: dict[str, list[str]]) -> WaveResolution:
    """Resolve a dependency graph into ordered waves.

    Wave level = 1 + max(level of deps); steps with no deps land in wave 1.
    Within a wave, steps keep graph key insertion order. Problems (unknown deps,
    cycles) are collected, never raised; any problem present → ``waves == []``.
    """
    problems: list[GraphProblem] = []

    for step, deps in graph.items():
        for dep in deps:
            if dep not in graph:
                problems.append(
                    GraphProblem(kind="unknown_dep", dep=dep, dependent=step)
                )

    # Detect cycles via DFS; one problem per distinct cycle found.
    WHITE, GREY, BLACK = 0, 1, 2
    color: dict[str, int] = {node: WHITE for node in graph}
    seen_cycles: set[tuple[str, ...]] = set()

    def visit(node: str, stack: list[str]) -> None:
        color[node] = GREY
        stack.append(node)
        for dep in graph.get(node, []):
            if dep not in graph:
                continue
            if color[dep] == GREY:
                idx = stack.index(dep)
                cyc = stack[idx:] + [dep]
                key = tuple(cyc)
                if key not in seen_cycles:
                    seen_cycles.add(key)
                    problems.append(GraphProblem(kind="cycle", cycle=cyc))
            elif color[dep] == WHITE:
                visit(dep, stack)
        stack.pop()
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            visit(node, [])

    if problems:
        return WaveResolution(waves=[], problems=problems)

    # No problems: compute levels via memoized longest-path.
    level: dict[str, int] = {}

    def compute(node: str) -> int:
        if node in level:
            return level[node]
        deps = graph[node]
        level[node] = 1 if not deps else 1 + max(compute(dep) for dep in deps)
        return level[node]

    for node in graph:
        compute(node)

    max_level = max(level.values(), default=0)
    waves: list[list[str]] = [[] for _ in range(max_level)]
    for node in graph:  # graph insertion order preserved within each wave
        waves[level[node] - 1].append(node)

    return WaveResolution(waves=waves, problems=[])


class Playbook(BaseModel):
    name: str
    title: str
    summary: str = ""
    trigger: str = ""
    requires_project: bool = False
    scope: Literal["global", "local"]
    path: Path
    body: str = ""
    steps: list[Step] = []
    graph: dict[str, list[str]] = {}

    @classmethod
    def load_all(cls, vault: Path | None, home_dir: Path) -> list[Playbook]:
        """Discover playbooks from the global root (`home_dir/_playbooks`) and, when a
        vault is attached, the local root (`vault/_playbooks`). Local shadows global on
        name collision. `_`-prefixed entries (e.g. `_lib`) are skipped. Missing roots
        yield nothing; missing/partial frontmatter degrades with a warning, not a crash.
        """
        result: list[Playbook] = []
        by_name: dict[str, int] = {}

        for scope, root in (
            ("global", home_dir / "_playbooks"),
            ("local", vault / "_playbooks" if vault is not None else None),
        ):
            if root is None or not root.is_dir():
                continue
            for pb_dir in sorted(root.iterdir()):
                if not pb_dir.is_dir() or pb_dir.name.startswith("_"):
                    continue
                pb = _load_one(pb_dir, scope)  # type: ignore[arg-type]
                if pb is None:
                    continue
                if pb.name in by_name:
                    result[by_name[pb.name]] = pb
                else:
                    by_name[pb.name] = len(result)
                    result.append(pb)

        return result


def _load_one(pb_dir: Path, scope: Literal["global", "local"]) -> Playbook | None:
    manifest = pb_dir / "playbook.md"
    if not manifest.is_file():
        _warn(f"playbook {pb_dir.name}: no playbook.md, skipping")
        return None

    fm, body = parse_frontmatter(manifest)
    name = str(fm.get("name", pb_dir.name))
    title = str(fm.get("title", name))
    summary = str(fm.get("summary", ""))
    trigger = str(fm.get("trigger", ""))
    requires_project = bool(fm.get("requires_project", False))

    raw_graph: dict[Any, Any] = fm.get("graph") or {}
    graph: dict[str, list[str]] = {}
    for step, deps in raw_graph.items():
        dep_list: list[Any] = deps or []
        graph[str(step)] = [str(d) for d in dep_list]

    steps: list[Step] = []
    for step_path in sorted((pb_dir / "steps").glob("*.md")):
        if step_path.name.startswith("_"):
            continue
        steps.append(_load_step(step_path))

    return Playbook(
        name=name,
        title=title,
        summary=summary,
        trigger=trigger,
        requires_project=requires_project,
        scope=scope,
        path=manifest,
        body=body,
        steps=steps,
        graph=graph,
    )


def _load_step(step_path: Path) -> Step:
    fm, body = parse_frontmatter(step_path)
    return Step(
        name=str(fm.get("name", step_path.stem)),
        title=_opt_str(fm.get("title")),
        summary=str(fm.get("summary", "")),
        agent=_opt_str(fm.get("agent")),
        review_gate=_opt_str(fm.get("review_gate")),
        body=body,
        path=step_path,
    )


def _opt_str(val: Any) -> str | None:
    return str(val) if val is not None else None
