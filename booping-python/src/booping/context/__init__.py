from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context import config as config_mod
from booping.context import extra_instructions as ei_mod
from booping.context.agent import Agent
from booping.context.lesson import Lesson
from booping.context.plan import Plan
from booping.context.plan_template import PlanTemplate
from booping.context.project import Project
from booping.context.retro import Retro
from booping.context.review_template import ReviewTemplate
from booping.context.skill import Skill
from booping.rendering import get_plugin_root


class Context(BaseModel):
    project: Project | None = None
    plans: list[Plan] = []
    lessons: list[Lesson] = []
    retros: list[Retro] = []
    plan_templates: list[PlanTemplate] = []
    review_templates: list[ReviewTemplate] = []
    skills: dict[str, Skill] = {}
    agents: dict[str, Agent] = {}
    config: dict[str, Any] = {}
    extra_instructions: dict[str, str] = {}

    @classmethod
    def assemble(
        cls,
        start: Path | None = None,
        plugin_root: Path | None = None,
        vault_override: Path | None = None,
    ) -> Context:
        """Assemble full context.

        vault_override: used in tests to point loaders at a fixture vault instead of
        the real ~/Claude/<project>/ directory that Project.directory resolves to.
        """
        root = plugin_root if plugin_root is not None else get_plugin_root()
        project = Project.load_cwd(start=start)

        if vault_override is not None:
            vault: Path | None = vault_override
        elif project is not None:
            vault = project.directory
        else:
            vault = None

        if vault is not None:
            override_paths = [vault / "config.yaml"]
            cfg = config_mod.load(root, override_paths)
            plans = Plan.load_all(vault)
            lessons = Lesson.load_all(vault)
            retros = Retro.load_all(vault)
            plan_templates = PlanTemplate.load_all(root, vault)
            review_templates = ReviewTemplate.load_all(root, vault)
            extra_instructions = ei_mod.load(vault)
        else:
            cfg = config_mod.load(root, [])
            plans = []
            lessons = []
            retros = []
            plan_templates = PlanTemplate.load_all(root, Path("/dev/null"))
            review_templates = ReviewTemplate.load_all(root, Path("/dev/null"))
            extra_instructions = {}

        skills = Skill.load_all(root)
        agents = Agent.load_all(root)

        return cls(
            project=project,
            plans=plans,
            lessons=lessons,
            retros=retros,
            plan_templates=plan_templates,
            review_templates=review_templates,
            skills=skills,
            agents=agents,
            config=cfg,
            extra_instructions=extra_instructions,
        )
