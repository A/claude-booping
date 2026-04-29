from __future__ import annotations

from pathlib import Path

from booping.context.project import Project
from booping.context.plan import Plan
from booping.context.lesson import Lesson, Retro
from booping.context.plan_template import PlanTemplate
from booping.context.config import load_config
from booping.context.extra_instructions import load_extra_instructions
from booping.context.skill import Skill, Agent


class Context:
    """Holds all runtime data for template rendering."""

    def __init__(
        self,
        project: Project | None,
        plans: list[Plan],
        lessons: list[Lesson],
        retros: list[Retro],
        plan_templates: list[PlanTemplate],
        skills: dict[str, Skill],
        agents: dict[str, Agent],
        config: dict,
        extra_instructions: dict[str, str],
        assembled_plugin_root: Path,
    ):
        self.project = project
        self.plans = plans
        self.lessons = lessons
        self.retros = retros
        self.plan_templates = plan_templates
        self.skills = skills
        self.agents = agents
        self.config = config
        self.extra_instructions = extra_instructions
        self._assembled_plugin_root = assembled_plugin_root

    @classmethod
    def assemble(cls, plugin_root: Path | None = None, vault: Path | None = None) -> Context:
        """Load all context data from plugin root and vault."""
        if plugin_root is None:
            # __file__ is src/booping/context/__init__.py
            # .parent = src/booping/context/ ; .parent.parent = src/booping/ ; .parent.parent.parent = src/
            # .parent.parent.parent.parent = booping-python/ ; .parent.parent.parent.parent.parent = repo root
            plugin_root = Path(__file__).parent.parent.parent.parent.parent
        if vault is None:
            vault = _find_vault()

        config = load_config(plugin_root, [vault / "config.yaml"] if vault else [])

        project = None
        plans: list[Plan] = []
        lessons: list[Lesson] = []
        retros: list[Retro] = []
        plan_templates: list[PlanTemplate] = []
        extra_instructions: dict[str, str] = {}

        if vault:
            project = Project.load_cwd(vault)
            plans = Plan.load_all(vault)
            lessons = Lesson.load_all(vault)
            retros = Retro.load_all(vault)
            plan_templates = PlanTemplate.load_all(plugin_root, vault)
            extra_instructions = load_extra_instructions(vault)

        skills = Skill.load_all(plugin_root)
        agents = Agent.load_all(plugin_root)

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
            assembled_plugin_root=plugin_root,
        )


def _find_vault() -> Path | None:
    """Walk upward from cwd looking for .booping file."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".booping").exists():
            return parent
    return None