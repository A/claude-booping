from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context import config as config_mod
from booping.context import lifecycle as lifecycle
from booping.context.agent import Agent
from booping.context.lesson import Lesson
from booping.context.plan_template import PlanTemplate
from booping.context.playbook import Playbook
from booping.context.project import Project
from booping.context.review_template import ReviewTemplate
from booping.context.skill import Skill
from booping.rendering import get_plugin_root


class Context(BaseModel):
    project: Project | None = None
    # The vault every loader read from — the project's directory, or the explicit
    # override a pinned render passed. Queries resolve their glob roots against it.
    vault: Path | None = None
    lessons: list[Lesson] = []
    targeted_lessons: list[Lesson] = []
    plan_templates: list[PlanTemplate] = []
    review_templates: list[ReviewTemplate] = []
    skills: dict[str, Skill] = {}
    agents: dict[str, Agent] = {}
    playbooks: list[Playbook] = []
    config: dict[str, Any] = {}
    # Machine level: a global config tier exists. Distinct from `config["home_dir"]`,
    # which always resolves (core default) and so cannot answer *whether* booping is set up.
    booping_initialized: bool = False

    @classmethod
    def assemble(
        cls,
        start: Path | None = None,
        plugin_root: Path | None = None,
        vault_override: Path | None = None,
    ) -> Context:
        """Assemble full context.

        vault_override: point loaders at an explicit vault instead of the
        ~/Claude/<project>/ directory that Project.directory resolves to. Used by tests
        (fixture vaults) and by `render-playbook --project`.
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

        # An explicit vault pins the config tiers as well as discovery: the global tier is
        # machine-local, and a pinned render must be reproducible on another machine.
        tiers = [] if vault_override is not None else [global_path]

        if vault is not None:
            cfg = config_mod.load(root, [*tiers, vault / "config.yaml"])
            lessons = Lesson.load_all(vault)
            plan_templates = PlanTemplate.load_all(root, vault)
            review_templates = ReviewTemplate.load_all(root, vault)
        else:
            cfg = config_mod.load(root, tiers)
            lessons = []
            plan_templates = PlanTemplate.load_all(root, Path("/dev/null"))
            review_templates = ReviewTemplate.load_all(root, Path("/dev/null"))

        skills = Skill.load_all(root)
        agents = Agent.load_all(root)
        # An explicit vault pins discovery to core + that vault: the global roots are
        # machine-local, and a pinned render must be reproducible on another machine.
        pinned_home_dir = None if vault_override is not None else home_dir
        playbooks = Playbook.load_all(vault, pinned_home_dir, root)
        targeted_lessons = Lesson.load_targeted(pinned_home_dir, vault)

        return cls(
            project=project,
            vault=vault,
            lessons=lessons,
            targeted_lessons=targeted_lessons,
            plan_templates=plan_templates,
            review_templates=review_templates,
            skills=skills,
            agents=agents,
            playbooks=playbooks,
            config=cfg,
            booping_initialized=global_path.is_file(),
        )
