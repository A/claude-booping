from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal, cast

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


class SubgraphNode(BaseModel):
    name: str
    dependencies: list[str] = []
    repeat: str | None = None
    graph: dict[str, list[str]] = {}


class GraphProblem(BaseModel):
    kind: Literal[
        "cycle", "unknown_dep", "bad_node", "nested_subgraph", "duplicate_step"
    ]
    cycle: list[str] = []  # kind=cycle: the cycle path, e.g. ["a", "b", "a"]
    dep: str = ""  # kind=unknown_dep: the missing key
    dependent: str = ""  # kind=unknown_dep: the step that listed it
    node: str = ""  # kind=bad_node/nested_subgraph/duplicate_step: the offending key
    detail: str = ""  # kind=bad_node: what is wrong with it
    scope: str = ""  # subgraph name the problem was found in; "" = outer graph


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
    jinja: bool = False
    scope: Literal["core", "global", "local"]
    path: Path
    body: str = ""
    steps: list[Step] = []
    # Outer scope only: plain step → deps, subgraph node → its `dependencies`.
    graph: dict[str, list[str]] = {}
    subgraphs: dict[str, SubgraphNode] = {}
    # Shape/scope problems collected while parsing `graph:` frontmatter.
    graph_problems: list[GraphProblem] = []
    # Discovery roots that exist on disk, most specific first (local, global, core).
    search_roots: list[Path] = []

    @property
    def executable_step_names(self) -> list[str]:
        """Every name that must map to a step dir: outer plain steps plus all inner
        steps. Subgraph keys are grouping nodes and are excluded."""
        names: list[str] = []
        for key in self.graph:
            sub = self.subgraphs.get(key)
            if sub is None:
                names.append(key)
            else:
                names.extend(sub.graph)
        return names

    def resolve_scopes(self) -> dict[str, WaveResolution]:
        """Wave resolution per scope: key ``""`` is the outer graph, any other key is a
        subgraph name holding its inner graph's resolution. Inner problems carry
        ``scope`` set to the subgraph name."""
        scopes: dict[str, WaveResolution] = {"": resolve_waves(self.graph)}
        for name, sub in self.subgraphs.items():
            res = resolve_waves(sub.graph)
            scopes[name] = WaveResolution(
                waves=res.waves,
                problems=[p.model_copy(update={"scope": name}) for p in res.problems],
            )
        return scopes

    @classmethod
    def load_all(
        cls, vault: Path | None, home_dir: Path, plugin_root: Path
    ) -> list[Playbook]:
        """Discover playbooks from the core root (`plugin_root/playbooks`), the global root
        (`home_dir/_playbooks`) and, when a vault is attached, the local root
        (`vault/_playbooks`). Roots are scanned core → global → local and a later-scanned
        playbook replaces an earlier one of the same name, so precedence is
        core < global < local. `_`-prefixed entries (e.g. `_lib`) are skipped. Missing roots
        yield nothing; missing/partial frontmatter degrades with a warning, not a crash.
        """
        result: list[Playbook] = []
        by_name: dict[str, int] = {}

        roots: list[tuple[str, Path | None]] = [
            ("core", plugin_root / "playbooks"),
            ("global", home_dir / "_playbooks"),
            ("local", vault / "_playbooks" if vault is not None else None),
        ]
        # Most specific first, so a root-relative include resolves local > global > core.
        search_roots = [r for _, r in reversed(roots) if r is not None and r.is_dir()]

        for scope, root in roots:
            if root is None or not root.is_dir():
                continue
            for pb_dir in sorted(root.iterdir()):
                if not pb_dir.is_dir() or pb_dir.name.startswith("_"):
                    continue
                pb = _load_one(pb_dir, scope, search_roots)  # type: ignore[arg-type]
                if pb is None:
                    continue
                if pb.name in by_name:
                    result[by_name[pb.name]] = pb
                else:
                    by_name[pb.name] = len(result)
                    result.append(pb)

        return result


def _load_one(
    pb_dir: Path,
    scope: Literal["core", "global", "local"],
    search_roots: list[Path] | None = None,
) -> Playbook | None:
    manifest = pb_dir / "playbook.md"
    if not manifest.is_file():
        return None

    fm, body = parse_frontmatter(manifest)
    name = str(fm.get("name", pb_dir.name))
    title = str(fm.get("title", name))
    summary = str(fm.get("summary", ""))
    trigger = str(fm.get("trigger", ""))
    requires_project = bool(fm.get("requires_project", False))
    jinja = bool(fm.get("jinja", False))

    graph, subgraphs, graph_problems = _parse_graph(fm.get("graph") or {})

    steps: list[Step] = []
    for step_dir in sorted(pb_dir.iterdir()):
        if not step_dir.is_dir() or step_dir.name.startswith("_"):
            continue
        prompt = step_dir / "prompt.md"
        if not prompt.is_file():
            _warn(f"playbook {pb_dir.name}: {step_dir.name}/ has no prompt.md, skipping")
            continue
        steps.append(_load_step(step_dir.name, prompt))

    return Playbook(
        name=name,
        title=title,
        summary=summary,
        trigger=trigger,
        requires_project=requires_project,
        jinja=jinja,
        scope=scope,
        path=manifest,
        body=body,
        steps=steps,
        graph=graph,
        subgraphs=subgraphs,
        graph_problems=graph_problems,
        search_roots=search_roots or [],
    )


_SUBGRAPH_KEYS = {"dependencies", "graph", "repeat"}


def _parse_graph(
    raw_graph: dict[Any, Any],
) -> tuple[dict[str, list[str]], dict[str, SubgraphNode], list[GraphProblem]]:
    """Parse the `graph:` mapping into the outer graph, its subgraph nodes and any
    shape/scope problems. A list value is a plain step's deps; a mapping value is a
    subgraph node. Malformed nodes are dropped and reported, never raised."""
    graph: dict[str, list[str]] = {}
    subgraphs: dict[str, SubgraphNode] = {}
    problems: list[GraphProblem] = []
    for raw_key, value in raw_graph.items():
        key = str(raw_key)
        if isinstance(value, dict):
            node = _parse_subgraph(key, value, problems)  # type: ignore[arg-type]
            if node is None:
                continue
            graph[key] = node.dependencies
            subgraphs[key] = node
        elif value is None or isinstance(value, list):
            graph[key] = _str_list(value)
        else:
            problems.append(
                GraphProblem(kind="bad_node", node=key, detail="deps must be a list")
            )

    seen = set(graph)
    for name, node in subgraphs.items():
        for inner in node.graph:
            if inner in seen:
                problems.append(
                    GraphProblem(kind="duplicate_step", node=inner, scope=name)
                )
            seen.add(inner)

    return graph, subgraphs, problems


def _parse_subgraph(
    key: str, value: dict[Any, Any], problems: list[GraphProblem]
) -> SubgraphNode | None:
    def bad(detail: str) -> None:
        problems.append(GraphProblem(kind="bad_node", node=key, detail=detail))

    extra = sorted(str(k) for k in value if str(k) not in _SUBGRAPH_KEYS)
    if extra:
        bad(f"unknown key(s): {', '.join(extra)}")
        return None
    if "dependencies" not in value:
        bad("missing `dependencies`")
        return None
    if "graph" not in value:
        bad("missing `graph`")
        return None

    deps = value["dependencies"]
    if deps is None:
        deps = []
    if not isinstance(deps, list):
        bad("`dependencies` must be a list")
        return None

    inner_raw = value["graph"]
    if not isinstance(inner_raw, dict) or not inner_raw:
        bad("`graph` must be a non-empty mapping")
        return None

    repeat = value.get("repeat")
    if repeat is not None and not isinstance(repeat, str):
        bad("`repeat` must be a string")
        return None

    inner: dict[str, list[str]] = {}
    for raw_inner_key, inner_value in cast("dict[Any, Any]", inner_raw).items():
        inner_key = str(raw_inner_key)
        if isinstance(inner_value, dict):
            problems.append(
                GraphProblem(kind="nested_subgraph", node=inner_key, scope=key)
            )
            continue
        if inner_value is not None and not isinstance(inner_value, list):
            problems.append(
                GraphProblem(
                    kind="bad_node",
                    node=inner_key,
                    scope=key,
                    detail="deps must be a list",
                )
            )
            continue
        inner[inner_key] = _str_list(inner_value)

    return SubgraphNode(
        name=key,
        dependencies=_str_list(deps),
        repeat=repeat,
        graph=inner,
    )


def _str_list(value: Any) -> list[str]:
    items: list[Any] = cast("list[Any]", value) if value else []
    return [str(item) for item in items]


def _load_step(dir_name: str, step_path: Path) -> Step:
    fm, body = parse_frontmatter(step_path)
    return Step(
        name=dir_name,
        title=_opt_str(fm.get("title")),
        summary=str(fm.get("summary", "")),
        agent=_opt_str(fm.get("agent")),
        review_gate=_opt_str(fm.get("review_gate")),
        body=body,
        path=step_path,
    )


def _opt_str(val: Any) -> str | None:
    return str(val) if val is not None else None
