from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, cast

from jinja2 import Environment, FileSystemLoader

from booping import logger
from booping.context import Context
from booping.context.playbook import Playbook, resolve_agent, resolve_waves
from booping.rendering import LenientUndefined, build_source_env, get_plugin_root

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
    " {name}/prompt.md does not exist. Do not execute this playbook."
)
_INLINE_PARALLEL = (
    "**STOP — tell the user:** step '{name}' runs inline (agent: null) but shares a"
    " wave with other steps; inline steps cannot run in parallel."
    " Do not execute this playbook."
)
_ORPHAN = (
    "**Note — tell the user:** step '{name}' exists on disk but is not wired into"
    " the graph; it will not run."
)
_NO_CONTEXT = (
    "**STOP — tell the user:** playbook '{name}' sets jinja: true but was rendered"
    " without project context. Do not execute this playbook."
)
_JINJA_ERROR = (
    "**STOP — tell the user:** Jinja rendering of {where} failed: {error}."
    " Do not execute this playbook."
)


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "render-playbook", help="Render a playbook's composed procedure to stdout"
    )
    p.add_argument("name", help="Playbook name to render")
    p.add_argument(
        "--step",
        type=str,
        default=None,
        metavar="NAME",
        help="Print only this step's body (no surrounding sections)",
    )
    p.add_argument(
        "--project",
        type=str,
        default=None,
        metavar="PATH",
        help="Resolve context against this vault instead of the attached project",
    )
    p.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="PATH",
        help="Output path (default: stdout); use - for stdout",
    )
    p.set_defaults(func=_run)


def build_env(
    plugin_root: Path | None = None, context: Context | None = None
) -> Environment:
    """The env compose() renders its partials — and, for jinja playbooks, its
    preamble and step bodies — through. Loader root is `src/templates/` either way,
    so `{% include "_partials/…" %}` resolves from sources living anywhere on disk.
    """
    root = plugin_root if plugin_root is not None else get_plugin_root()
    if context is not None:
        env = build_source_env(context=context, config=context.config, plugin_root=root)
    else:
        env = Environment(
            loader=FileSystemLoader(str(root / "src" / "templates")),
            undefined=LenientUndefined,
            keep_trailing_newline=True,
        )
    globals_: dict[str, Any] = cast("dict[str, Any]", env.globals)
    globals_["resolve_agent"] = resolve_agent
    return env


def render_source(env: Environment, source: str) -> tuple[str, str | None]:
    """Render an ad-hoc source; return (rendered, None) or ("", error message)."""
    try:
        return env.from_string(source).render(), None
    except Exception as exc:  # any Jinja failure becomes an in-band notice
        return "", f"{type(exc).__name__}: {exc}"


def compose(
    pb: Playbook, plugin_root: Path | None = None, context: Context | None = None
) -> str:
    """Render a playbook to the locked output contract:
    notices → body preamble → ``## Execution graph`` → step sections in wave order.
    The ``graph:`` frontmatter drives sequencing. The preamble and embedded step
    bodies pass through verbatim unless the playbook sets ``jinja: true``, in which
    case they are rendered through the full context env (which `context` must
    supply). Any blocking notice omits both the execution graph and the step
    sections; non-blocking orphan notes render in either case.
    """
    env = build_env(plugin_root=plugin_root, context=context if pb.jinja else None)

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

    # Missing step dirs (graph key order).
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

    # Orphan step dirs (steps order) — non-blocking, emitted in both cases.
    for step in pb.steps:
        if step.name not in pb.graph:
            notices.append(_ORPHAN.format(name=step.name))

    preamble = pb.body
    bodies = {name: step.body for name, step in steps_by_name.items()}

    if pb.jinja:
        if context is None:
            notices.append(_NO_CONTEXT.format(name=pb.name))
            blocking = True
        else:
            preamble, err = render_source(env, pb.body)
            if err is not None:
                notices.append(_JINJA_ERROR.format(where="the preamble", error=err))
                blocking = True
            # Only wave-1 bodies are embedded; later waves are fetched via --step.
            for name in waves[0] if waves and not blocking else []:
                rendered, err = render_source(env, steps_by_name[name].body)
                if err is not None:
                    notices.append(
                        _JINJA_ERROR.format(where=f"step '{name}'", error=err)
                    )
                    blocking = True
                    break
                bodies[name] = rendered

    sections: list[str] = []
    if notices:
        sections.append("\n".join(notices))
    if preamble.strip():
        sections.append(preamble.strip())

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
                        body=bodies[name],
                        deps=pb.graph[name],
                        siblings=siblings,
                        embed=wave_idx == 0,
                        playbook=pb.name,
                        jinja=pb.jinja,
                    ).strip()
                )

    return "\n\n".join(sections) + "\n"


def compose_step(pb: Playbook, step_name: str, context: Context | None = None) -> str:
    """The step body alone — no headings, instruction bullets, or gate chrome.
    Jinja-rendered when the playbook opts in; verbatim otherwise.
    """
    step = next(s for s in pb.steps if s.name == step_name)
    if not pb.jinja:
        return step.body
    if context is None:
        return _NO_CONTEXT.format(name=pb.name) + "\n"
    rendered, err = render_source(build_env(context=context), step.body)
    if err is not None:
        return _JINJA_ERROR.format(where=f"step '{step_name}'", error=err) + "\n"
    return rendered


def _run(args: argparse.Namespace) -> None:
    project_str: str | None = args.project
    vault_override = (
        Path(project_str).expanduser().resolve() if project_str is not None else None
    )
    ctx = Context.assemble(vault_override=vault_override)

    pb = next((p for p in ctx.playbooks if p.name == args.name), None)
    if pb is None:
        known = ", ".join(sorted(p.name for p in ctx.playbooks)) or "(none)"
        print(
            f"error: playbook not found: {args.name} (known: {known})",
            file=sys.stderr,
        )
        sys.exit(1)

    if pb.requires_project and ctx.project is None and vault_override is None:
        print(
            f"error: playbook '{args.name}' requires a booping project; none attached here",
            file=sys.stderr,
        )
        sys.exit(1)

    step_name: str | None = args.step
    if step_name is not None and not any(s.name == step_name for s in pb.steps):
        known = ", ".join(s.name for s in pb.steps) or "(none)"
        print(
            f"error: step not found in playbook '{args.name}': {step_name} (known: {known})",
            file=sys.stderr,
        )
        sys.exit(1)

    output_str: str | None = args.output
    message = args.name
    if step_name is not None:
        message = f"{message} --step {step_name}"
    if output_str is not None and output_str != "-":
        message = f"{message} → {output_str}"
    log_vault = vault_override
    if log_vault is None and ctx.project is not None:
        log_vault = ctx.project.directory
    logger.log(
        vault=log_vault,
        subcommand="render-playbook",
        message=message,
    )

    if step_name is not None:
        result = compose_step(pb, step_name, ctx)
    else:
        result = compose(pb, context=ctx)

    if output_str is None or output_str == "-":
        sys.stdout.write(result)
    else:
        output_path = Path(output_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result)
