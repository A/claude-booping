from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal, cast

import yaml
from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter
from booping.context.lesson import Lesson

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


class StepInput(BaseModel):
    what: str
    from_: str | None = None


class Step(BaseModel):
    name: str
    title: str | None = None
    summary: str = ""
    agent: str | None = None
    review_gate: str | None = None
    inputs: list[StepInput] = []
    outputs: list[str] = []
    body: str = ""
    path: Path


class SubgraphNode(BaseModel):
    name: str
    dependencies: list[str] = []
    repeat: str | None = None
    state: str | None = None
    graph: dict[str, list[str]] = {}


class StateMachine(BaseModel):
    """One `states:` entry of a playbook.yaml manifest. Shape mirrors `config["plan"]`
    so the generalized lifecycle resolver consumes `raw` unchanged."""

    name: str
    artifact: str
    initial: str
    statuses: dict[str, Any] = {}
    raw: dict[str, Any] = {}


class GraphProblem(BaseModel):
    kind: Literal[
        "cycle",
        "unknown_dep",
        "bad_node",
        "nested_subgraph",
        "duplicate_step",
        "graph_in_both",
        "bad_manifest",
        "bad_state",
        "unknown_state",
        "orphan_state",
        "orphan_lesson",
        "name_clash",
    ]
    cycle: list[str] = []  # kind=cycle: the cycle path, e.g. ["a", "b", "a"]
    dep: str = ""  # kind=unknown_dep: the missing key
    dependent: str = ""  # kind=unknown_dep: the step that listed it
    node: str = ""  # kind=bad_node/nested_subgraph/duplicate_step: the offending key
    # kind=bad_state/unknown_state/orphan_state: the states entry name
    # kind=orphan_lesson: the unknown step the lesson points at
    detail: str = ""  # kind=bad_node/bad_manifest/bad_state: what is wrong with it
    # kind=orphan_lesson: the lesson filename; kind=name_clash: the clashing scopes
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
    # playbook.yaml `states:` entries, and the `state:` ref per scope
    # ("" = outer scope, any other key = subgraph name).
    states: dict[str, StateMachine] = {}
    state_refs: dict[str, str] = {}
    # Shape/scope problems collected while parsing the manifest.
    graph_problems: list[GraphProblem] = []
    # Discovery roots that exist on disk, most specific first (local, global, core).
    search_roots: list[Path] = []
    # Root-level then playbook-level lessons, most general scope first.
    lessons: list[Lesson] = []
    # Scopes declaring this name when 2+ roots carry a playbook.md for it.
    clash_scopes: list[str] = []

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
        scopes_by_name: dict[str, list[str]] = {}

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
                scopes_by_name.setdefault(pb.name, []).append(scope)
                if pb.name in by_name:
                    result[by_name[pb.name]] = pb
                else:
                    by_name[pb.name] = len(result)
                    result.append(pb)

        existing = [(scope, root) for scope, root in roots if root and root.is_dir()]
        root_lessons = _merge_lessons(
            [(_ROOT_LESSON_SCOPES[scope], root / "_lessons") for scope, root in existing]
        )
        for pb in result:
            _attach_lessons(pb, root_lessons, [root for _, root in existing])
            clash = scopes_by_name[pb.name]
            if len(clash) > 1:
                pb.clash_scopes = clash
                pb.graph_problems.append(
                    GraphProblem(kind="name_clash", node=pb.name, detail=", ".join(clash))
                )

        return result


_ROOT_LESSON_SCOPES = {"core": "core", "global": "global", "local": "project"}


def _merge_lessons(dirs: list[tuple[str, Path]]) -> list[Lesson]:
    """Load each `(scope, dir)` pair, ordered least → most specific. A filename carried by
    several dirs keeps only its most specific copy; output keeps the given dir order."""
    loaded = [Lesson.load_dir(path, scope=scope) for scope, path in dirs]
    winner: dict[str, int] = {}
    for index, lessons in enumerate(loaded):
        for lesson in lessons:
            winner[lesson.path.name] = index
    merged: list[Lesson] = []
    for index, lessons in enumerate(loaded):
        merged.extend(
            lesson for lesson in lessons if winner[lesson.path.name] == index
        )
    return merged


def _attach_lessons(pb: Playbook, root_lessons: list[Lesson], roots: list[Path]) -> None:
    """Root-level lessons plus this playbook's own `_lessons/` unioned across every root
    (a name may carry lessons in a root that has no playbook.md for it). A lesson whose
    `step:` names an unknown step is dropped and reported."""
    own = sorted(
        _merge_lessons([("playbook", root / pb.name / "_lessons") for root in roots]),
        key=lambda lesson: lesson.path.name,
    )
    known = {step.name for step in pb.steps}
    kept: list[Lesson] = []
    for lesson in root_lessons + own:
        if lesson.step is not None and lesson.step not in known:
            pb.graph_problems.append(
                GraphProblem(
                    kind="orphan_lesson", node=lesson.step, detail=lesson.path.name
                )
            )
            continue
        kept.append(lesson)
    pb.lessons = kept


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

    manifest_yaml, manifest_problems = _load_manifest_yaml(pb_dir / "playbook.yaml")

    graph_problems: list[GraphProblem] = list(manifest_problems)
    if "graph" in manifest_yaml and fm.get("graph") is not None:
        graph_problems.append(GraphProblem(kind="graph_in_both"))
    raw_graph: Any = (
        manifest_yaml["graph"] if "graph" in manifest_yaml else fm.get("graph")
    )

    graph, subgraphs, parse_problems = _parse_graph(
        cast("dict[Any, Any]", raw_graph) if isinstance(raw_graph, dict) else {}
    )
    graph_problems.extend(parse_problems)

    states, state_refs = _parse_states(
        manifest_yaml.get("states"),
        manifest_yaml.get("state"),
        subgraphs,
        graph_problems,
    )

    steps: list[Step] = []
    for step_dir in sorted(pb_dir.iterdir()):
        if not step_dir.is_dir() or step_dir.name.startswith("_"):
            continue
        prompt = step_dir / "prompt.md"
        if not prompt.is_file():
            _warn(f"playbook {pb_dir.name}: {step_dir.name}/ has no prompt.md, skipping")
            continue
        steps.append(_load_step(step_dir.name, prompt, pb_dir.name))

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
        states=states,
        state_refs=state_refs,
        graph_problems=graph_problems,
        search_roots=search_roots or [],
    )


_SUBGRAPH_KEYS = {"dependencies", "graph", "repeat", "state"}


def _load_manifest_yaml(path: Path) -> tuple[dict[str, Any], list[GraphProblem]]:
    """Load the optional `playbook.yaml` manifest. Absent → empty mapping, no problems;
    unparseable or non-mapping content → empty mapping plus a `bad_manifest` problem."""
    if not path.is_file():
        return {}, []
    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        return {}, [GraphProblem(kind="bad_manifest", detail=str(exc))]
    if raw is None:
        return {}, []
    if not isinstance(raw, dict):
        return {}, [GraphProblem(kind="bad_manifest", detail="not a YAML mapping")]
    return {str(k): v for k, v in cast("dict[Any, Any]", raw).items()}, []


def _parse_states(
    raw_states: Any,
    outer_ref: Any,
    subgraphs: dict[str, SubgraphNode],
    problems: list[GraphProblem],
) -> tuple[dict[str, StateMachine], dict[str, str]]:
    """Parse the manifest's `states:` entries and the `state:` refs pointing at them
    (outer scope + one per subgraph). Malformed entries are dropped and reported."""
    refs: dict[str, str] = {}
    if outer_ref is not None:
        refs[""] = str(outer_ref)
    for name, sub in subgraphs.items():
        if sub.state is not None:
            refs[name] = sub.state
    instance_refs = {ref for scope, ref in refs.items() if scope}

    entries: dict[Any, Any] = (
        cast("dict[Any, Any]", raw_states) if isinstance(raw_states, dict) else {}
    )
    states: dict[str, StateMachine] = {}
    for raw_name, value in entries.items():
        name = str(raw_name)

        def bad(detail: str, name: str = name) -> None:
            problems.append(GraphProblem(kind="bad_state", node=name, detail=detail))

        if not isinstance(value, dict):
            bad("must be a mapping")
            continue
        entry = cast("dict[Any, Any]", value)
        artifact = str(entry.get("artifact") or "")
        initial = str(entry.get("initial") or "")
        statuses = entry.get("statuses")
        if not artifact:
            bad("missing `artifact`")
            continue
        if not isinstance(statuses, dict) or initial not in statuses:
            bad(f"`initial` '{initial}' is not in `statuses`")
            continue
        if "{instance}" in artifact and name not in instance_refs:
            bad("`{instance}` in `artifact` requires a subgraph to reference this state")
            continue
        states[name] = StateMachine(
            name=name,
            artifact=artifact,
            initial=initial,
            statuses={str(k): v for k, v in cast("dict[Any, Any]", statuses).items()},
            raw={str(k): v for k, v in entry.items()},
        )

    declared = {str(k) for k in entries}
    for scope, ref in refs.items():
        if ref not in declared:
            problems.append(GraphProblem(kind="unknown_state", node=ref, scope=scope))
    for name in states:
        if name not in refs.values():
            problems.append(GraphProblem(kind="orphan_state", node=name))

    return states, refs


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

    state = value.get("state")
    if state is not None and not isinstance(state, str):
        bad("`state` must be a string")
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
        state=state,
        graph=inner,
    )


def _str_list(value: Any) -> list[str]:
    items: list[Any] = cast("list[Any]", value) if value else []
    return [str(item) for item in items]


def _load_step(dir_name: str, step_path: Path, pb_name: str) -> Step:
    fm, body = parse_frontmatter(step_path)
    return Step(
        name=dir_name,
        title=_opt_str(fm.get("title")),
        summary=str(fm.get("summary", "")),
        agent=_opt_str(fm.get("agent")),
        review_gate=_opt_str(fm.get("review_gate")),
        inputs=_parse_inputs(fm.get("inputs"), pb_name, dir_name),
        outputs=_parse_outputs(fm.get("outputs"), pb_name, dir_name),
        body=body,
        path=step_path,
    )


def _entries(value: Any, key: str, pb_name: str, dir_name: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        _warn(f"playbook {pb_name}: {dir_name}/prompt.md has non-list {key}, ignoring")
        return []
    return cast("list[Any]", value)


def _parse_inputs(value: Any, pb_name: str, dir_name: str) -> list[StepInput]:
    inputs: list[StepInput] = []
    for entry in _entries(value, "inputs", pb_name, dir_name):
        if isinstance(entry, str):
            inputs.append(StepInput(what=entry))
            continue
        what = (
            cast("dict[Any, Any]", entry).get("what") if isinstance(entry, dict) else None
        )
        if not isinstance(what, str) or not what:
            _warn(
                f"playbook {pb_name}: {dir_name}/prompt.md has malformed inputs entry, "
                "skipping"
            )
            continue
        source = cast("dict[Any, Any]", entry).get("from")
        inputs.append(StepInput(what=what, from_=_opt_str(source)))
    return inputs


def _parse_outputs(value: Any, pb_name: str, dir_name: str) -> list[str]:
    outputs: list[str] = []
    for entry in _entries(value, "outputs", pb_name, dir_name):
        if not isinstance(entry, str) or not entry:
            _warn(
                f"playbook {pb_name}: {dir_name}/prompt.md has malformed outputs entry, "
                "skipping"
            )
            continue
        outputs.append(entry)
    return outputs


def _opt_str(val: Any) -> str | None:
    return str(val) if val is not None else None
