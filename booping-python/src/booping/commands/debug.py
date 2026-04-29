from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.ext import LoopControlExtension

from booping.context import Context
from booping.context.config import Config as ConfigLoader
from booping.rendering import find_plugin_root, render
from booping.tools import Tools

if TYPE_CHECKING:
    import argparse


def _format_plans_compact(plans: list) -> list[str]:
    lines = []
    for p in plans:
        sp_str = f", {p.sp} SP" if p.sp is not None else ""
        lines.append(f"{p.title} ({p.status}{sp_str})")
    return lines


def _format_lessons_compact(lessons: list) -> list[str]:
    return [f"{lesson.id} -- {lesson.title}" for lesson in lessons]


def _format_retros_compact(retros: list) -> list[str]:
    lines = []
    for r in retros:
        created_str = f", {r.created}" if r.created else ""
        goal_str = r.goal or ""
        plan_str = r.plan or ""
        if created_str:
            lines.append(
                f"{plan_str} -- {goal_str} ({created_str})"
            )
        else:
            lines.append(f"{plan_str} -- {goal_str}")
    return lines


def _format_skills_compact(skills: dict) -> list[str]:
    return [f"{name} -- {s.description}" for name, s in skills.items()]


def _format_agents_compact(agents: dict) -> list[str]:
    return [f"{name} -- {a.description}" for name, a in agents.items()]


def _format_extra_instructions_compact(extra_instructions: dict) -> list[str]:
    return list(extra_instructions.keys())


def _format_plan_templates_compact(templates: list) -> list[str]:
    return [f"{t.name} -- {t.description} ({t.source})" for t in templates]


def handle(args: argparse.Namespace) -> int:
    full = getattr(args, "full", False)
    plugin_root = find_plugin_root(str(Path.cwd()))
    ctx = Context.assemble(plugin_root)

    output: dict = {}

    output["project"] = (
        ctx.project.model_dump(mode="json") if ctx.project else None
    )

    if full:
        output["plans"] = [p.model_dump(mode="json") for p in ctx.plans]
    else:
        output["plans"] = _format_plans_compact(ctx.plans)

    if full:
        output["lessons"] = [
            lesson.model_dump(mode="json") for lesson in ctx.lessons
        ]
    else:
        output["lessons"] = _format_lessons_compact(ctx.lessons)

    if full:
        output["retros"] = [r.model_dump(mode="json") for r in ctx.retros]
    else:
        output["retros"] = _format_retros_compact(ctx.retros)

    if full:
        output["skills"] = {
            name: s.model_dump(mode="json")
            for name, s in ctx.skills.items()
        }
    else:
        output["skills"] = _format_skills_compact(ctx.skills)

    if full:
        output["agents"] = {
            name: a.model_dump(mode="json")
            for name, a in ctx.agents.items()
        }
    else:
        output["agents"] = _format_agents_compact(ctx.agents)

    if full:
        output["extra_instructions"] = ctx.extra_instructions
    else:
        output["extra_instructions"] = _format_extra_instructions_compact(
            ctx.extra_instructions
        )

    output["config"] = ctx.config

    if full:
        output["plan_templates"] = [
            t.model_dump(mode="json") for t in ctx.plan_templates
        ]
    else:
        output["plan_templates"] = _format_plan_templates_compact(
            ctx.plan_templates
        )

    print(yaml.dump(output, default_flow_style=False))
    return 0


def _collect_overridden_keys(
    merged: Any, core: Any, prefix: str = ""
) -> list[str]:
    if not isinstance(core, dict) or not isinstance(merged, dict):
        if merged != core:
            return [prefix] if prefix else []
        return []
    keys: list[str] = []
    for key in merged:
        full_key = f"{prefix}.{key}" if prefix else key
        if key not in core:
            keys.append(full_key)
        else:
            keys.extend(
                _collect_overridden_keys(merged[key], core[key], full_key)
            )
    return keys


def handle_debug_template(args: argparse.Namespace) -> int:
    template_path = args.path
    vault = Path(args.vault) if args.vault else None

    plugin_root = find_plugin_root(template_path)
    templates_dir = plugin_root / "src" / "templates"

    ctx = Context.assemble(plugin_root, vault)

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
        extensions=[LoopControlExtension],
    )

    template_rel = Path(template_path).resolve().relative_to(templates_dir)
    tpl = env.get_template(str(template_rel))

    context = ctx.model_dump(mode="python")
    tools = Tools(
        render_fn=render,
        plugin_root=str(plugin_root),
        vault=str(vault) if vault else None,
    )
    render_globals: dict[str, Any] = {
        "context": context,
        "config": ctx.config,
        "tools": tools,
        "kwargs": {},
    }

    try:
        rendered = tpl.render(**render_globals)
    except Exception as exc:
        print(
            f"Error rendering {template_path}: {exc}",
            file=sys.stderr,
        )
        return 1

    print(rendered)

    core_config = ConfigLoader.load(plugin_root, override_paths=[])
    overridden = _collect_overridden_keys(ctx.config, core_config)

    project_line = (
        f"{ctx.project.name} ({ctx.project.directory})"
        if ctx.project
        else "not initialized"
    )

    print()
    print("## Debug context")
    print(f"- Project: {project_line}")
    print(f"- Plans: {len(ctx.plans)}")
    print(f"- Lessons: {len(ctx.lessons)}")
    print(f"- Retros: {len(ctx.retros)}")
    print(f"- Plan templates: {len(ctx.plan_templates)}")
    print(f"- Skills: {len(ctx.skills)}")
    print(f"- Agents: {len(ctx.agents)}")
    if overridden:
        print(f"- Config keys overridden: {', '.join(overridden)}")
    else:
        print("- Config keys overridden: (none)")

    return 0