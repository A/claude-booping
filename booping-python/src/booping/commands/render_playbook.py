from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, cast

from jinja2 import Environment, FileSystemLoader

from booping import logger
from booping.context import Context
from booping.context.playbook import Playbook, resolve_agent, resolve_waves
from booping.rendering import LenientUndefined, get_plugin_root

_NO_GRAPH = (
    "**STOP — tell the user:** playbook '{name}' has no graph: in its frontmatter."
    " Do not execute this playbook."
)
_UNKNOWN_DEP = (
    "**STOP — tell the user:** '{dep}' is listed as a dependency of '{name}' but is"
    " not a step in the graph. Do not execute this playbook."
)
_CYCLE = (
    "**STOP — tell the user:** the graph has a cycle: {path}."
    " Do not execute this playbook."
)
_MISSING = (
    "**STOP — tell the user:** step '{name}' is referenced in the graph but"
    " steps/{name}.md does not exist. Do not execute this playbook."
)
_INLINE_PARALLEL = (
    "**STOP — tell the user:** step '{name}' runs inline (agent: null) but shares a"
    " wave with other steps; inline steps cannot run in parallel."
    " Do not execute this playbook."
)
_ORPHAN = (
    "**Note — tell the user:** step '{name}' exists in steps/ but is not wired into"
    " the graph; it will not run."
)


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "render-playbook", help="Render a playbook's composed procedure to stdout"
    )
    p.add_argument("name", help="Playbook name to render")
    p.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="PATH",
        help="Output path (default: stdout); use - for stdout",
    )
    p.set_defaults(func=_run)


def compose(pb: Playbook, plugin_root: Path | None = None) -> str:
    """Render a playbook to the locked output contract:
    notices → body preamble (verbatim) → ``## Execution graph`` → step sections in
    wave order. The ``graph:`` frontmatter drives sequencing; the body is inserted
    verbatim (no Jinja evaluation). Any blocking notice omits both the execution
    graph and the step sections; non-blocking orphan notes render in either case.
    """
    root = plugin_root if plugin_root is not None else get_plugin_root()
    templates_dir = root / "src" / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=LenientUndefined,
        keep_trailing_newline=True,
    )
    globals_: dict[str, Any] = cast("dict[str, Any]", env.globals)
    globals_["resolve_agent"] = resolve_agent

    steps_by_name = {s.name: s for s in pb.steps}
    step_names = set(steps_by_name)
    graph_keys = list(pb.graph.keys())

    resolution = resolve_waves(pb.graph)
    waves = resolution.waves

    notices: list[str] = []
    blocking = False

    if not pb.graph:
        notices.append(_NO_GRAPH.format(name=pb.name))
        blocking = True

    # Resolver problems: unknown_dep entries precede cycle entries (resolve_waves
    # collects them in that order); render each in problem order.
    for prob in resolution.problems:
        if prob.kind == "unknown_dep":
            notices.append(_UNKNOWN_DEP.format(dep=prob.dep, name=prob.dependent))
            blocking = True
        elif prob.kind == "cycle":
            notices.append(_CYCLE.format(path=" → ".join(prob.cycle)))
            blocking = True

    # Missing step files (graph key order).
    for key in graph_keys:
        if key not in step_names:
            notices.append(_MISSING.format(name=key))
            blocking = True

    # Inline steps sharing a parallel wave (wave order).
    for wave in waves:
        if len(wave) > 1:
            for name in wave:
                step = steps_by_name.get(name)
                if step is not None and step.agent is None:
                    notices.append(_INLINE_PARALLEL.format(name=name))
                    blocking = True

    # Orphan step files (steps order) — non-blocking, emitted in both cases.
    for step in pb.steps:
        if step.name not in pb.graph:
            notices.append(_ORPHAN.format(name=step.name))

    sections: list[str] = []
    if notices:
        sections.append("\n".join(notices))
    if pb.body.strip():
        sections.append(pb.body.strip())

    if not blocking:
        sections.append(
            env.get_template("_partials/_playbook_graph.j2")
            .render(graph=pb.graph, waves=waves)
            .strip()
        )
        step_tmpl = env.get_template("_partials/_playbook_step.j2")
        for wave_idx, wave in enumerate(waves):
            for name in wave:
                step = steps_by_name[name]
                siblings = [n for n in wave if n != name]
                sections.append(
                    step_tmpl.render(
                        step=step,
                        deps=pb.graph[name],
                        siblings=siblings,
                        embed=wave_idx == 0,
                    ).strip()
                )

    return "\n\n".join(sections) + "\n"


def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble()

    pb = next((p for p in ctx.playbooks if p.name == args.name), None)
    if pb is None:
        known = ", ".join(sorted(p.name for p in ctx.playbooks)) or "(none)"
        print(
            f"error: playbook not found: {args.name} (known: {known})",
            file=sys.stderr,
        )
        sys.exit(1)

    if pb.requires_project and ctx.project is None:
        print(
            f"error: playbook '{args.name}' requires a booping project; none attached here",
            file=sys.stderr,
        )
        sys.exit(1)

    output_str: str | None = args.output
    message = args.name
    if output_str is not None and output_str != "-":
        message = f"{message} → {output_str}"
    logger.log(
        vault=ctx.project.directory if ctx.project is not None else None,
        subcommand="render-playbook",
        message=message,
    )

    result = compose(pb)

    if output_str is None or output_str == "-":
        sys.stdout.write(result)
    else:
        output_path = Path(output_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result)
