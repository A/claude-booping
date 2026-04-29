from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context.agent import Agent
from booping.context.config import Config
from booping.context.extra_instructions import ExtraInstructions
from booping.context.lesson import Lesson
from booping.context.plan import Plan
from booping.context.plan_template import PlanTemplate
from booping.context.project import Project
from booping.context.retro import Retro
from booping.context.skill import Skill


class Context(BaseModel):
    project: Project | None = None
    plans: list[Plan] = []
    lessons: list[Lesson] = []
    retros: list[Retro] = []
    plan_templates: list[PlanTemplate] = []
    skills: dict[str, Skill] = {}
    agents: dict[str, Agent] = {}
    config: dict[str, Any] = {}
    extra_instructions: dict[str, str] = {}

    @classmethod
    def assemble(cls, plugin_root: Path, vault: Path | None = None) -> "Context":
        project: Project | None = None
        if vault is not None:
            booping_file = vault / ".booping"
            if booping_file.is_file():
                import yaml

                data = yaml.safe_load(booping_file.read_text()) or {}
                project = Project(
                    name=data.get("project_name", vault.name),
                    directory=vault,
                )

        plans = Plan.load_all(vault) if vault else []
        lessons = Lesson.load_all(vault) if vault else []
        retros = Retro.load_all(vault) if vault else []
        plan_templates = PlanTemplate.load_all(plugin_root, vault)
        skills = Skill.load_all(plugin_root)
        agents = Agent.load_all(plugin_root)

        override_paths = [vault / "config.yaml"] if vault else []
        config = Config.load(plugin_root, override_paths)

        extra_instructions = ExtraInstructions.load(vault)

        return cls(
            project=project,
            plans=plans,
            lessons=lessons,
            retros=retros,
            plan_templates=plan_templates,
            skills=skills,
            agents=agents,
            config=config,
            extra_instructions=extra_instructions,
        )