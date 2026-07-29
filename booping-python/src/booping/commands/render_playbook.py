from __future__ import annotations

import argparse
import posixpath
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from jinja2 import BaseLoader, ChoiceLoader, DictLoader, Environment, FileSystemLoader

from booping import logger
from booping.context import Context
from booping.context.playbook import GraphProblem, Playbook, Step, resolve_agent
from booping.rendering import LenientUndefined, build_source_env, get_plugin_root

_NO_GRAPH = (
    "**STOP — tell the user:** playbook '{name}' has no graph: in its frontmatter."
    " Do not execute this playbook."
)
_UNKNOWN_DEP = (
    "**STOP — tell the user:** '{dep}' is listed as a dependency of '{name}' but is"
    " not a step in the graph. Do not execute this playbook."
)
_UNKNOWN_DEP_INNER = (
    "**STOP — tell the user:** in subgraph '{scope}': '{dep}' is listed as a dependency"
    " of '{name}' but is not a step in that subgraph. Do not execute this playbook."
)
_CYCLE = (
    "**STOP — tell the user:** the graph has a cycle: {path}."
    " Do not execute this playbook."
)
_CYCLE_INNER = (
    "**STOP — tell the user:** in subgraph '{scope}': the graph has a cycle: {path}."
    " Do not execute this playbook."
)
_BAD_NODE = (
    "**STOP — tell the user:** graph node '{name}' is malformed: {detail}."
    " Do not execute this playbook."
)
_BAD_NODE_INNER = (
    "**STOP — tell the user:** in subgraph '{scope}': graph node '{name}' is malformed:"
    " {detail}. Do not execute this playbook."
)
_NESTED_SUBGRAPH = (
    "**STOP — tell the user:** node '{name}' inside subgraph '{scope}' is itself a"
    " subgraph; only one level of nesting is supported."
    " Do not execute this playbook."
)
_DUPLICATE_STEP = (
    "**STOP — tell the user:** step '{name}' appears in more than one scope (subgraph"
    " '{scope}'); step names must be unique across the playbook."
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


class PlaybookEnvironment(Environment):
    """Resolves `./x` and `../x` against the including template's own directory.
    Bare names keep hitting the search chain unchanged; a name escaping above the
    loader root is left alone and degrades to a normal TemplateNotFound.
    """

    def join_path(self, template: str, parent: str) -> str:
        if not template.startswith(("./", "../")):
            return template
        joined = posixpath.normpath(
            posixpath.join(posixpath.dirname(parent), template)
        )
        return template if joined.startswith("..") else joined


def build_env(
    plugin_root: Path | None = None,
    context: Context | None = None,
    *,
    search_dirs: Sequence[Path] = (),
    source: tuple[str, str] | None = None,
) -> Environment:
    """The env compose() renders its partials and preamble — and compose_step its
    step bodies — through. `search_dirs` are prepended (most specific
    first) to the always-last `src/templates/` root, so `{% include "_partials/…" %}`
    resolves from sources living anywhere on disk. `source` is an in-memory body
    served under a name, so Jinja hands a real `parent` to `join_path`.
    """
    root = plugin_root if plugin_root is not None else get_plugin_root()
    loaders: list[BaseLoader] = []
    if source is not None:
        loaders.append(DictLoader({source[0]: source[1]}))
    loaders.extend(FileSystemLoader(str(d)) for d in search_dirs if d.is_dir())
    loaders.append(FileSystemLoader(str(root / "src" / "templates")))
    loader = ChoiceLoader(loaders)

    if context is not None:
        env = build_source_env(
            context=context,
            config=context.config,
            plugin_root=root,
            loader=loader,
            env_class=PlaybookEnvironment,
        )
    else:
        env = PlaybookEnvironment(
            loader=loader,
            undefined=LenientUndefined,
            keep_trailing_newline=True,
        )
    globals_: dict[str, Any] = cast("dict[str, Any]", env.globals)
    globals_["resolve_agent"] = resolve_agent
    return env


def render_body(
    pb: Playbook,
    body: str,
    step: Step | None,
    context: Context,
    plugin_root: Path | None = None,
) -> tuple[str, str | None]:
    """Render a playbook body (preamble when `step` is None, else a step prompt)
    against the chain: own dir → playbook dir → playbook roots → `src/templates/`.
    Returns (rendered, None) or ("", error message).
    """
    path = pb.path if step is None else step.path
    search_dirs: list[Path] = []
    if step is not None:
        search_dirs.append(step.path.parent)
    search_dirs.append(pb.path.parent)
    search_dirs.extend(pb.search_roots)

    # The body is served under its own basename so `./x` / `../x` inside it resolve
    # against its own directory — the first entry of the chain.
    name = path.name
    env = build_env(
        plugin_root=plugin_root,
        context=context,
        search_dirs=search_dirs,
        source=(name, body),
    )
    try:
        return env.get_template(name).render(), None
    except Exception as exc:  # any Jinja failure becomes an in-band notice
        return "", f"{type(exc).__name__}: {exc}"


def _shape_notice(prob: GraphProblem) -> str:
    if prob.kind == "nested_subgraph":
        return _NESTED_SUBGRAPH.format(name=prob.node, scope=prob.scope)
    if prob.kind == "duplicate_step":
        return _DUPLICATE_STEP.format(name=prob.node, scope=prob.scope)
    template = _BAD_NODE_INNER if prob.scope else _BAD_NODE
    return template.format(name=prob.node, detail=prob.detail, scope=prob.scope)


def _resolver_notice(prob: GraphProblem) -> str:
    if prob.kind == "cycle":
        path = " → ".join(prob.cycle)
        if prob.scope:
            return _CYCLE_INNER.format(path=path, scope=prob.scope)
        return _CYCLE.format(path=path)
    if prob.scope:
        return _UNKNOWN_DEP_INNER.format(
            dep=prob.dep, name=prob.dependent, scope=prob.scope
        )
    return _UNKNOWN_DEP.format(dep=prob.dep, name=prob.dependent)


def compose(
    pb: Playbook, plugin_root: Path | None = None, context: Context | None = None
) -> str:
    """Render a playbook to the locked output contract:
    notices → body preamble → ``## Execution graph`` → step sections in wave order.
    The ``graph:`` frontmatter drives sequencing. No step body is ever embedded —
    every step section is fetch-form. The preamble passes through verbatim unless
    the playbook sets ``jinja: true``, in which case it is rendered through the full
    context env (which `context` must supply). Any blocking notice omits both the
    execution graph and the step sections; non-blocking orphan notes render in
    either case.
    """
    env = build_env(plugin_root=plugin_root, context=context if pb.jinja else None)

    steps_by_name = {s.name: s for s in pb.steps}
    step_names = set(steps_by_name)

    scopes = pb.resolve_scopes()
    waves = scopes[""].waves
    inner_waves = {name: scopes[name].waves for name in pb.subgraphs}

    notices: list[str] = []
    blocking = False

    if not pb.graph:
        notices.append(_NO_GRAPH.format(name=pb.name))
        blocking = True

    # Shape problems collected by the loader, then resolver problems per scope
    # (outer first, subgraphs in graph order).
    for prob in pb.graph_problems:
        notices.append(_shape_notice(prob))
        blocking = True

    for scope in ["", *pb.subgraphs]:
        for prob in scopes[scope].problems:
            notices.append(_resolver_notice(prob))
            blocking = True

    # Missing step dirs: every executable name (outer plain steps + inner steps) must
    # map to a step dir; subgraph keys are grouping nodes and map to nothing.
    for key in pb.executable_step_names:
        if key not in step_names:
            notices.append(_MISSING.format(name=key))
            blocking = True

    # Inline steps sharing a parallel wave, per scope (outer waves, then inner waves).
    for scope_waves in [waves, *inner_waves.values()]:
        for wave in scope_waves:
            if len(wave) > 1:
                for name in wave:
                    step = steps_by_name.get(name)
                    if step is not None and step.agent is None:
                        notices.append(_INLINE_PARALLEL.format(name=name))
                        blocking = True

    # Orphan step dirs (steps order) — non-blocking, emitted in both cases.
    wired = set(pb.executable_step_names) | set(pb.graph)
    for step in pb.steps:
        if step.name not in wired:
            notices.append(_ORPHAN.format(name=step.name))

    preamble = pb.body

    if pb.jinja:
        if context is None:
            notices.append(_NO_CONTEXT.format(name=pb.name))
            blocking = True
        else:
            preamble, err = render_body(pb, pb.body, None, context, plugin_root)
            if err is not None:
                notices.append(_JINJA_ERROR.format(where="the preamble", error=err))
                blocking = True

    sections: list[str] = []
    if notices:
        sections.append("\n".join(notices))
    if preamble.strip():
        sections.append(preamble.strip())

    if not blocking:
        sections.append(
            env.get_template("_partials/_playbook_graph.j2")
            .render(
                graph=pb.graph,
                waves=waves,
                subgraphs=pb.subgraphs,
                inner_waves=inner_waves,
            )
            .strip()
        )
        step_tmpl = env.get_template("_partials/_playbook_step.j2")

        def render_step(
            name: str, deps: list[str], wave: list[str], part_of: str | None
        ) -> str:
            sub = pb.subgraphs.get(part_of) if part_of is not None else None
            return step_tmpl.render(
                step=steps_by_name[name],
                deps=deps,
                siblings=[n for n in wave if n != name],
                playbook=pb.name,
                jinja=pb.jinja,
                part_of=part_of,
                repeated=sub is not None and sub.repeat is not None,
            ).strip()

        for wave in waves:
            for name in wave:
                sub = pb.subgraphs.get(name)
                if sub is None:
                    sections.append(render_step(name, pb.graph[name], wave, None))
                    continue
                sections.append(
                    step_tmpl.render(
                        subgraph=sub,
                        waves=inner_waves[name],
                    ).strip()
                )
                for inner_wave in inner_waves[name]:
                    for inner in inner_wave:
                        sections.append(
                            render_step(inner, sub.graph[inner], inner_wave, name)
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
    rendered, err = render_body(pb, step.body, step, context)
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
