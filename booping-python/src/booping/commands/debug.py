from __future__ import annotations


import yaml

from pathlib import Path

from booping.context import Context
from booping.tools import Tools
from booping.rendering import render
from jinja2 import StrictUndefined


def add_parser(subparsers) -> None:
    p = subparsers.add_parser("debug-context", help="Dump assembled Context as YAML")
    p.add_argument("--full", action="store_true", help="Include full bodies")
    p.set_defaults(func=_run_debug_context)

    p2 = subparsers.add_parser("debug-template", help="Render template with full context")
    p2.add_argument("path", help="Template path")
    p2.set_defaults(func=_run_debug_template)


def _run_debug_context(args) -> None:
    ctx = Context.assemble()

    data = {
        "project": {
            "name": ctx.project.name if ctx.project else None,
            "directory": str(ctx.project.directory) if ctx.project else None,
        } if ctx.project else None,
        "plans": [
            {"title": p.title, "status": p.status, "sp": p.sp, "type": p.type}
            for p in ctx.plans
        ],
        "lessons": [
            {"id": lesson.id, "title": lesson.title}
            for lesson in ctx.lessons
        ],
        "retros": [
            {"plan": r.plan, "goal": r.goal, "created": str(r.created) if r.created else None}
            for r in ctx.retros
        ],
        "plan_templates": [
            {"name": t.name, "description": t.description, "source": t.source}
            for t in ctx.plan_templates
        ],
        "skills": {name: {"description": s.description, "debug_enabled": s.debug_enabled} for name, s in ctx.skills.items()},
        "agents": {name: {"description": a.description} for name, a in ctx.agents.items()},
        "config": {
            "sprint": ctx.config.get("sprint", {}),
        },
        "extra_instructions_keys": list(ctx.extra_instructions.keys()),
    }

    if args.full:
        data["lessons"] = [{"id": lesson.id, "title": lesson.title, "body": lesson.body} for lesson in ctx.lessons]
        data["retros"] = [{"plan": r.plan, "goal": r.goal, "body": r.body} for r in ctx.retros]

    print(yaml.dump(data, default_flow_style=False, sort_keys=False))


def _run_debug_template(args) -> None:
    # __file__ is src/booping/commands/debug.py
    # .parent.parent.parent.parent.parent = repo root
    plugin_root = Path(__file__).parent.parent.parent.parent.parent
    ctx = Context.assemble()
    tools_ns = Tools(plugin_root=plugin_root, context=ctx, config=ctx.config)

    result = render(
        template_path=args.path,
        context=ctx,
        config=ctx.config,
        tools=tools_ns,
        kwargs={},
        plugin_root=plugin_root,
        undefined=StrictUndefined,
    )
    print(result)
    print("\n## Debug context")
    print(f"  plans: {len(ctx.plans)}")
    print(f"  lessons: {len(ctx.lessons)}")
    print(f"  project: {ctx.project.name if ctx.project else 'none'}")