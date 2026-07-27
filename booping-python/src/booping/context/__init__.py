from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context import config as config_mod
from booping.context import extra_instructions as ei_mod
from booping.context import lifecycle as lifecycle
from booping.context.agent import Agent
from booping.context.lesson import Lesson
from booping.context.plan import Plan
from booping.context.plan_template import PlanTemplate
from booping.context.playbook import Playbook
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
    playbooks: list[Playbook] = []
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
        global_path = config_mod.global_config_path()

        # Resolve the vault before the project tier can be merged: the vault-home base
        # (`home_dir`) lives in config, so load_cwd_configured loads core + global first,
        # reads `home_dir` from that partial merge, then resolves the vault. The `.booping`
        # `vault_path:` marker still wins over `home_dir` inside Project.load_cwd.
        project = Project.load_cwd_configured(
            start=start, plugin_root=root, global_path=global_path
        )

        # Same core+global merge Project.load_cwd_configured reads `home_dir` from —
        # the global-playbooks root hangs off it, resolved (with `~` expansion) before
        # the project tier, so a project-tier `home_dir` stays inert here too.
        base_cfg = config_mod.load(root, [global_path])
        home_dir = Path(str(base_cfg.get("home_dir", "~/Claude"))).expanduser()

        if vault_override is not None:
            vault: Path | None = vault_override
        elif project is not None:
            vault = project.directory
        else:
            vault = None

        if vault is not None:
            override_paths = [global_path, vault / "config.yaml"]
            cfg = config_mod.load(root, override_paths)
            config_mod.validate_skills(cfg)
            plans = Plan.load_all(vault)
            lessons = Lesson.load_all(vault)
            retros = Retro.load_all(vault)
            plan_templates = PlanTemplate.load_all(root, vault)
            review_templates = ReviewTemplate.load_all(root, vault)
            extra_instructions = ei_mod.load(vault)
        else:
            cfg = config_mod.load(root, [global_path])
            config_mod.validate_skills(cfg)
            plans = []
            lessons = []
            retros = []
            plan_templates = PlanTemplate.load_all(root, Path("/dev/null"))
            review_templates = ReviewTemplate.load_all(root, Path("/dev/null"))
            extra_instructions = {}

        skills = Skill.load_all(root)
        agents = Agent.load_all(root)
        playbooks = Playbook.load_all(vault, home_dir, root)

        return cls(
            project=project,
            plans=plans,
            lessons=lessons,
            retros=retros,
            plan_templates=plan_templates,
            review_templates=review_templates,
            skills=skills,
            agents=agents,
            playbooks=playbooks,
            config=cfg,
            extra_instructions=extra_instructions,
        )
