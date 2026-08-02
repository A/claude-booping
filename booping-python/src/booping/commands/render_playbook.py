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
from booping.context.lesson import Lesson
from booping.context.lifecycle import resolve_edges
from booping.context.playbook import GraphProblem, Playbook, Step, resolve_detached
from booping.rendering import (
    LenientUndefined,
    build_source_env,
    get_plugin_root,
    make_now,
)
from booping.utils import deep_merge

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
    "**STOP — tell the user:** step '{name}' is not detached but shares a wave with"
    " other steps; a step sharing a wave must be `detached:`."
    " Do not execute this playbook."
)
_LEGACY_AGENT_KEY = (
    "**STOP — tell the user:** step '{name}' declares `agent:` in its frontmatter;"
    " that key was renamed to `detached:`. Do not execute this playbook."
)
_ORPHAN = (
    "**Note — tell the user:** step '{name}' exists on disk but is not wired into"
    " the graph; it will not run."
)
_GRAPH_IN_BOTH = (
    "**STOP — tell the user:** playbook '{playbook}' declares graph: in both"
    " playbook.yaml and playbook.md frontmatter; keep exactly one."
    " Do not execute this playbook."
)
_BAD_MANIFEST = (
    "**STOP — tell the user:** playbook.yaml of playbook '{playbook}' is malformed:"
    " {detail}. Do not execute this playbook."
)
_BAD_STATE = (
    "**STOP — tell the user:** states entry '{name}' is malformed: {detail}."
    " Do not execute this playbook."
)
_UNKNOWN_STATE = (
    "**STOP — tell the user:** the outer graph references state '{name}' but"
    " playbook.yaml declares no such states entry. Do not execute this playbook."
)
_UNKNOWN_STATE_INNER = (
    "**STOP — tell the user:** subgraph '{scope}' references state '{name}' but"
    " playbook.yaml declares no such states entry. Do not execute this playbook."
)
_ORPHAN_STATE = (
    "**Note — tell the user:** states entry '{name}' is declared but no graph scope"
    " references it; it will never be used."
)
_NO_CONTEXT = (
    "**STOP — tell the user:** playbook '{name}' sets jinja: true but was rendered"
    " without project context. Do not execute this playbook."
)
_JINJA_ERROR = (
    "**STOP — tell the user:** Jinja rendering of {where} failed: {error}."
    " Do not execute this playbook."
)
_NAME_CLASH = (
    "**STOP — tell the user:** playbook '{name}' is defined in more than one root"
    " ({scopes}) — playbook names must be unique; rename one."
)
_ORPHAN_LESSON = (
    "**Note — tell the user:** lesson '{file}' targets unknown step '{step}' in"
    " playbook '{name}'; it is ignored."
)
_NON_BLOCKING = {"orphan_state", "orphan_lesson"}


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
    p.add_argument(
        "--set",
        action="append",
        dest="set_overrides",
        default=None,
        metavar="KEY=VALUE",
        help=(
            "Override a config value for this render (dotted key, e.g."
            " sprint.default_threshold_sp=3); repeatable, later pairs win, and the"
            " value wins over every config tier"
        ),
    )
    p.add_argument(
        "--no-lessons",
        action="store_true",
        help="Suppress the Lessons section on both the composed and --step surfaces",
    )
    p.add_argument(
        "--inline-steps",
        action="store_true",
        help=(
            "Embed each non-detached step's body in its composed section instead of"
            " the fetch command (detached steps keep fetch-form); implied by"
            " `inline_steps: true` in the playbook's manifest frontmatter"
        ),
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
    globals_["resolve_detached"] = resolve_detached
    globals_["now"] = make_now(context.config if context is not None else None)
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


def _render_step_fields(
    pb: Playbook,
    step: Step,
    context: Context,
    plugin_root: Path | None = None,
) -> tuple[Step, str | None]:
    """Render the frontmatter fields a `jinja: true` playbook may template —
    `summary` and `detached` — through the step's own loader chain. A `detached`
    that renders empty (the config key it names is absent) degrades to
    runner-performed. Returns (step, None) or (step, error message).
    """
    fields = {"summary": step.summary, "detached": step.detached}
    if not any(v and "{" in v for v in fields.values()):
        return step, None

    search_dirs = [step.path.parent, pb.path.parent, *pb.search_roots]
    env = build_env(
        plugin_root=plugin_root, context=context, search_dirs=search_dirs
    )
    rendered: dict[str, Any] = {}
    for key, value in fields.items():
        if not value:
            continue
        try:
            rendered[key] = env.from_string(value).render().strip()
        except Exception as exc:
            return step, f"{type(exc).__name__}: {exc}"
    if "detached" in rendered and not rendered["detached"]:
        rendered["detached"] = None
    return step.model_copy(update=rendered), None


def parse_set_overrides(pairs: Sequence[str]) -> dict[str, Any]:
    """`a.b=c` → `{"a": {"b": "c"}}`, accumulated later-wins across pairs. Values stay
    strings. Raises ValueError carrying the offending pair when it has no `=`.
    """
    overrides: dict[str, Any] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise ValueError(pair)
        nested: dict[str, Any] = {}
        cursor = nested
        parts = key.split(".")
        for part in parts[:-1]:
            child: dict[str, Any] = {}
            cursor[part] = child
            cursor = child
        cursor[parts[-1]] = value
        overrides = deep_merge(overrides, nested)
    return overrides


def _shape_notice(prob: GraphProblem, playbook: str) -> str:
    if prob.kind == "nested_subgraph":
        return _NESTED_SUBGRAPH.format(name=prob.node, scope=prob.scope)
    if prob.kind == "duplicate_step":
        return _DUPLICATE_STEP.format(name=prob.node, scope=prob.scope)
    if prob.kind == "graph_in_both":
        return _GRAPH_IN_BOTH.format(playbook=playbook)
    if prob.kind == "bad_manifest":
        return _BAD_MANIFEST.format(playbook=playbook, detail=prob.detail)
    if prob.kind == "bad_state":
        return _BAD_STATE.format(name=prob.node, detail=prob.detail)
    if prob.kind == "unknown_state":
        template = _UNKNOWN_STATE_INNER if prob.scope else _UNKNOWN_STATE
        return template.format(name=prob.node, scope=prob.scope)
    if prob.kind == "orphan_state":
        return _ORPHAN_STATE.format(name=prob.node)
    if prob.kind == "orphan_lesson":
        return _ORPHAN_LESSON.format(file=prob.detail, step=prob.node, name=playbook)
    if prob.kind == "legacy_agent_key":
        return _LEGACY_AGENT_KEY.format(name=prob.node)
    if prob.kind == "name_clash":
        return _NAME_CLASH.format(name=playbook, scopes=prob.detail)
    template = _BAD_NODE_INNER if prob.scope else _BAD_NODE
    return template.format(name=prob.node, detail=prob.detail, scope=prob.scope)


def _state_entries(pb: Playbook) -> list[dict[str, Any]]:
    """Everything the ``## State`` section renders, per ``states:`` entry: which graph
    scopes reference it, whether its artifact is per-instance, and one row per status
    carrying that status's resolved outgoing edges. Outer entry first."""
    outer_ref = pb.state_refs.get("")
    order = [outer_ref] if outer_ref in pb.states else []
    order.extend(name for name in pb.states if name not in order)

    entries: list[dict[str, Any]] = []
    for name in order:
        machine = pb.states[name]
        rows: list[dict[str, Any]] = []
        for status, raw in machine.statuses.items():
            data = cast("dict[str, Any]", raw) if isinstance(raw, dict) else {}
            rows.append(
                {
                    "status": status,
                    "terminal": bool(data.get("terminal", False)),
                    "edges": [
                        {
                            "to": e.to,
                            "when": e.when,
                            "gates": e.gates,
                            "hooks": e.hooks,
                        }
                        for e in resolve_edges(status, machine.raw)
                    ],
                }
            )
        entries.append(
            {
                "name": name,
                "artifact": machine.artifact,
                "initial": machine.initial,
                "scopes": [
                    "outer graph" if scope == "" else f"subgraph `{scope}`"
                    for scope, ref in pb.state_refs.items()
                    if ref == name
                ],
                "per_instance": "{instance}" in machine.artifact,
                "is_outer": name == outer_ref,
                "rows": rows,
            }
        )
    return entries


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


def _render_lessons(
    lessons: list[Lesson], env: Environment, *, step_mode: bool = False
) -> str:
    """The `## Lessons` section for either surface; empty string when nothing applies."""
    if not lessons:
        return ""
    return (
        env.get_template("_partials/_playbook_lessons.j2")
        .render(lessons=lessons, step_mode=step_mode)
        .strip()
    )


def compose(
    pb: Playbook,
    plugin_root: Path | None = None,
    context: Context | None = None,
    *,
    include_lessons: bool = True,
    inline_steps: bool = False,
) -> str:
    """Render a playbook to the locked output contract:
    notices → body preamble → ``## Playbook Steps`` → step sections in wave order.
    The ``graph:`` frontmatter drives sequencing. By default no step body is
    embedded — every step section is fetch-form. With ``inline_steps`` (the
    parameter, or ``inline_steps: true`` in the playbook's manifest frontmatter)
    each non-detached step's body (plus its step-scoped lessons) replaces the
    fetch command; detached steps keep fetch-form so their agents fetch their own
    body. The preamble passes through verbatim unless
    the playbook sets ``jinja: true``, in which case it is rendered through the full
    context env (which `context` must supply). Any blocking notice omits both the
    execution graph and the step sections; non-blocking orphan notes render in
    either case.
    """
    env = build_env(plugin_root=plugin_root, context=context if pb.jinja else None)
    inline_steps = inline_steps or pb.inline_steps

    steps = list(pb.steps)
    field_errors: list[str] = []
    if pb.jinja and context is not None:
        resolved: list[Step] = []
        for step in steps:
            step, err = _render_step_fields(pb, step, context, plugin_root)
            if err is not None:
                field_errors.append(
                    _JINJA_ERROR.format(
                        where=f"step '{step.name}' frontmatter", error=err
                    )
                )
            resolved.append(step)
        steps = resolved

    steps_by_name = {s.name: s for s in steps}
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
        notices.append(_shape_notice(prob, pb.name))
        if prob.kind not in _NON_BLOCKING:
            blocking = True

    if field_errors:
        notices.extend(field_errors)
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
                    if step is not None and step.detached is None:
                        notices.append(_INLINE_PARALLEL.format(name=name))
                        blocking = True

    # Orphan step dirs (steps order) — non-blocking, emitted in both cases.
    wired = set(pb.executable_step_names) | set(pb.graph)
    for step in steps:
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
        if include_lessons:
            playbook_lessons = [lesson for lesson in pb.lessons if lesson.step is None]
            section = _render_lessons(playbook_lessons, env)
            if section:
                sections.append(section)
        sections.append(
            env.get_template("_partials/_playbook_graph.j2")
            .render(
                graph=pb.graph,
                waves=waves,
                subgraphs=pb.subgraphs,
                inner_waves=inner_waves,
                steps=steps_by_name,
                playbook=pb.name,
                states=_state_entries(pb),
            )
            .strip()
        )
        step_tmpl = env.get_template("_partials/_playbook_step.j2")

        def inline_body(step: Step) -> str:
            if not pb.jinja:
                body = step.body
            else:
                # context is present here: jinja without context is blocking above.
                assert context is not None
                rendered, err = render_body(pb, step.body, step, context, plugin_root)
                if err is not None:
                    return _JINJA_ERROR.format(
                        where=f"step '{step.name}'", error=err
                    )
                body = rendered
            lessons = (
                [lesson for lesson in pb.lessons if lesson.step == step.name]
                if include_lessons
                else []
            )
            section = _render_lessons(lessons, env, step_mode=True)
            if section:
                body = body.rstrip("\n") + "\n\n" + section
            return body.strip()

        def render_step(name: str, deps: list[str], part_of: str | None) -> str:
            sub = pb.subgraphs.get(part_of) if part_of is not None else None
            step = steps_by_name[name]
            body = (
                inline_body(step)
                if inline_steps and step.detached is None
                else None
            )
            return step_tmpl.render(
                step=step,
                deps=deps,
                playbook=pb.name,
                part_of=part_of,
                repeated=sub is not None and sub.repeat is not None,
                body=body,
            ).strip()

        for wave in waves:
            for name in wave:
                sub = pb.subgraphs.get(name)
                if sub is None:
                    sections.append(render_step(name, pb.graph[name], None))
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
                            render_step(inner, sub.graph[inner], name)
                        )

    return "\n\n".join(sections) + "\n"


def compose_step(
    pb: Playbook,
    step_name: str,
    context: Context | None = None,
    *,
    include_lessons: bool = True,
) -> str:
    """The step body alone — no headings, instruction bullets, or gate chrome —
    followed by the lessons targeting this step. Jinja-rendered when the playbook
    opts in; verbatim otherwise (lesson bodies are never Jinja-rendered).
    """
    step = next(s for s in pb.steps if s.name == step_name)
    if not pb.jinja:
        body = step.body
    elif context is None:
        return _NO_CONTEXT.format(name=pb.name) + "\n"
    else:
        rendered, err = render_body(pb, step.body, step, context)
        if err is not None:
            return _JINJA_ERROR.format(where=f"step '{step_name}'", error=err) + "\n"
        body = rendered

    lessons = [lesson for lesson in pb.lessons if lesson.step == step_name]
    if not include_lessons or not lessons:
        return body
    section = _render_lessons(lessons, build_env(), step_mode=True)
    return body.rstrip("\n") + "\n\n" + section + "\n"


def _run(args: argparse.Namespace) -> None:
    set_pairs: list[str] = args.set_overrides or []
    try:
        overrides = parse_set_overrides(set_pairs)
    except ValueError as exc:
        print(
            f"error: malformed --set pair (expected KEY=VALUE): {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    project_str: str | None = args.project
    vault_override = (
        Path(project_str).expanduser().resolve() if project_str is not None else None
    )
    ctx = Context.assemble(vault_override=vault_override)
    if overrides:
        ctx = ctx.model_copy(
            update={
                "config": deep_merge(
                    ctx.config, overrides, shallow_merge_keys=["agents"]
                )
            }
        )

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

    include_lessons = not args.no_lessons
    if step_name is not None:
        result = compose_step(pb, step_name, ctx, include_lessons=include_lessons)
    else:
        result = compose(
            pb,
            context=ctx,
            include_lessons=include_lessons,
            inline_steps=args.inline_steps,
        )

    if output_str is None or output_str == "-":
        sys.stdout.write(result)
    else:
        output_path = Path(output_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result)
