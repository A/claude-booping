# booping plugin — project guide

Claude Code plugin that grooms and executes plans across user projects. Plans live under `~/Claude/{project}/` (the per-project vault); skills, agents, templates, and config live in this repo.

## Status

_Last updated: 2026-04-29._

Runtime template rendering is live. Current state:

- **Runtime rendering**: skills (`/chat`, `/groom`, `/develop`, `/retro`, `/learn`) and agents (`booping-researcher`, `booping-developer-middle`, `booping-developer-senior`) are hand-authored thin shells containing frontmatter plus `!`booping render src/templates/…``. Context (config, lessons, extra instructions, agents, plan templates, project name, sprint threshold) is assembled at load time by the `booping render` subcommand, which deep-merges project-level config at `~/Claude/{project}/config.yaml` over core config at `src/config.yaml`.
- **Agents**: the two developer tiers share `_partials/_developer_body.j2` — only frontmatter (`model`, `effort`, `reasoning`, `color`) diverges. Extra instructions are rendered inline via `{{ tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='agent_booping-<name>') }}`.
- **CLI**: `booping` (unified CLI with `render`, `plans`, `debug-context`, `debug-template` subcommands), `booping-create-project`, `booping-external-llm-call`.

## Layout

- `src/config.yaml` — single source of truth for structured data the pipeline renders into skills (plan statuses + transitions, task types, per-skill description / effort / agents / etc.).
- `src/templates/skills/<name>.md.j2` — skill templates. One file per skill; renders to `skills/<name>/SKILL.md`.
- `src/templates/agents/<name>.md.j2` — agent templates. Render to `agents/<name>.md`. The two developer tiers share `_partials/_developer_body.j2`.
- `src/templates/docs/<name>.md.j2` — doc templates (frontmatter template, etc.). Render to `docs/<name>.md`.
- `src/templates/plan_templates/<name>.md.j2` — core plan templates (backend, frontend, claude-skill, cli). Each has YAML frontmatter (`name`, `description`) + two top-level sections: `# Plan Body` and `# Quality Checklist`. Render to `docs/plan_templates/<name>.md`. User projects may add their own templates under `~/Claude/{project}/plan_templates/*.md` (hand-authored `.md`, same frontmatter shape + two sections).
- `src/templates/_partials/_*.j2` — reusable fragments. Underscore prefix marks them as inputs, not outputs. Include via `{% include %}` (data-only partials) or import + macro call (parameterized partials, e.g. `_plan_transitions.j2`, `_plan_frontmatter.j2`, `_plan_template.j2`).
- `src/docs/*.md` — reference docs lazy-loaded by skills via `[label](src/docs/...)` links. Hand-authored. Cross-validation gates reference `src/docs/cross_validation.md` (consumed by `/groom`'s `in-spec → awaiting-plan-review` transition).
- `skills/<name>/SKILL.md` — hand-authored thin shell: frontmatter (`effort`) plus `!`booping render src/templates/skills/<name>.md.j2``. The template body is rendered at skill-load time; only the frontmatter is hand-maintained.
- `docs/` — generated output only: `docs/plan_templates/*.md`, `docs/template_plan_frontmatter.md`, `docs/plan_lifecycle_overview.md` (lazy-loaded by `/chat` for the full lifecycle reference), and the `docs/images/` directory. Generated via `just build-docs`; never hand-edit.
- `agents/<name>.md` — hand-authored thin shell: frontmatter (`model`, `effort`, `reasoning`, `color`) plus `!`booping render src/templates/agents/<name>.md.j2``. Rendered at agent-load time; only the frontmatter is hand-maintained.
- `booping-python/` — Python package backing the `booping` CLI:
  - `src/booping/cli.py` — Click CLI entry point (`render`, `plans`, `debug-context`, `debug-template` subcommands).
  - `src/booping/rendering.py` — Jinja2 template rendering engine; assembles context and renders templates.
  - `src/booping/context/` — context-assembling modules (`config.py`, `project.py`, `lesson.py`, `extra_instructions.py`, `agent.py`, `skill.py`, `plan.py`, `plan_template.py`, `retro.py`). Each gathers one slice of runtime context (core config deep-merged with project config, vault data, etc.).
  - `src/booping/tools.py` — Jinja2 global functions (`render`, `debug`) available in templates.
  - `tests/` — pytest suite with snapshot tests.
- `bin/` — standalone scripts:
  - `booping` — unified CLI wrapper (`uv run --project booping-python booping "$@"`).
  - `booping-create-project` — scaffolds `~/Claude/{project-name}/`.
  - `booping-external-llm-call` — renders a Jinja2 prompt template under `bin/llm-call-templates/` and sends it to Gemini.
  - `llm-call-templates/` — Jinja2 prompt templates for `booping-external-llm-call`.

## Information ownership

Every piece of information lives in exactly one of these owners. When you can't decide where something belongs, walk this list top-down.

### `src/config.yaml`

The contract between skills and, looking forward, the user-facing customisation surface. Project-level config at `~/Claude/{project}/config.yaml` deep-merges over core config at runtime — so users can tune the plan lifecycle, sprint scale, task types, and agent wiring without forking the plugin.

- Where a plan can go (statuses, transitions, owner).
- Boundaries of each move (`gates` — verifiable preconditions; `when` — human-readable trigger).
- Artifacts produced in a state.
- Side effects on exit (`on_exit` — frontmatter mutations, commits, etc.).
- Structured surfaces that other skills / CLIs also consume: task types, sprint scale, agent capabilities, branch conventions.

### Skill (`src/templates/skills/<name>.md.j2`)

Instructions, goal, rules, and judgement specific to one skill — the verbs and heuristics for clearing the gates that config defines.

- Verbs and heuristics — *how* to produce the artifacts and clear the gates for the states this skill owns.
- User interaction — what to ask, when, how to present, how to handle approval vs change requests vs cancellation.
- Judgment calls the contract can't pre-specify.
- Invariants the skill enforces across all its states ("Hard rules").

### Shared template fragments (`src/templates/_partials/`, `src/docs/`)

Content shared across skills/agents, or extracted from a single skill body to keep it lean.

- Cross-cutting guides included into multiple skills (git guide, plan transitions, available agents, project context).
- Process fragments extracted from a single skill into its own partial (sprint planning, plan-frontmatter shape, task classification).
- Bodies shared across sibling agents (`_developer_body.j2` for the two developer tiers).
- Lazy-loaded craft docs (`src/docs/*.md`) that a skill links into via `[label](src/docs/...)` when the situation demands it.

### Project vault (`~/Claude/{project}/`)

Out of framework scope — authored per-project, loaded by skills at runtime.

- Per-skill / per-agent extensions (`_booping/skill_<name>.md`, `_booping/agent_<name>.md`).
- Accumulated lessons (`lessons/`).
- Project-local plan templates (`plan_templates/*.md`).

The attached repo's own `CLAUDE.md` is also loaded by skills (it sits in the repo, not the vault) — same role as the above: project conventions the framework reads but doesn't author.

## Principles

- **Minimum useful context**: show only information the skill needs to perform its job. Never bake in stale, speculative, or unrelated data.
- **Less prose, less drift**: every extra sentence in a skill or partial adds tension between what's written and what the model does. Cut motivation, restated context, "you are the skill / you are responsible to" preambles, and any explanation the schema or a referenced doc already carries. The schema is the source of truth; prose decays.
- **Schema over prose**: structured data lives in `src/config.yaml`. If a format or value is there, the skill body must not also describe it in prose — render from config.

## Information hierarchy

When you write a skill, walk these questions top-down for every piece of information you're tempted to inline. Each step moves the cost out of the skill body and into a cheaper mechanism.

1. **Does the skill need this for its main route?** Load it eagerly: inline a CLI fact via `!`command``, or include a static fragment as a partial.
   - Example: project name + path loaded at skill load via `{{ tools.render('src/templates/_partials/_project_context.j2') }}`.
   - Example: the git guide included via the `_git_guide.j2` partial.

2. **Does the skill need this only on a specific route, or only when a condition holds?** Lazy-load with a `[label](src/docs/...)` link; the model fetches it when the situation demands it.
   - Example: `/groom` links to per-task-type guidance; only the active type's guide (one of `feature`, `bug`, `refactoring`) is loaded per plan.

3. **Does the skill need the whole, or only one slice?** Split into a partial.
   - Example: `/develop` only needs the plan frontmatter shape; it does not pull in the full plan-template body.

4. **Is this information already available to the skill?** Remove the duplicate.
   - Example: plan transitions are rendered into each skill via `_plan_transitions.j2`. Skills must not restate the flow in their own prose.

5. **Is the value dynamic?** Reference the source, never the literal.
   - Example: the status `/learn` queries to find plans to absorb is named in `src/config.yaml`; the skill renders from there rather than spelling the status name in prose.

## Skill design

- **Wide-domain**: skills must work across stacks (Django, Rust, Hugo, etc.). Project-specific concerns live in `~/Claude/{project}/_booping/skill_<name>.md`, `lessons/`, and the project's own `CLAUDE.md` — never in the skill here.
- **Phases over flat sections**: Preflight → High-level workflow → Phase 0..N.
- **Preflight becomes thinner** in template-driven skills: items that were "Read partial X" now appear either as inlined partial content, as `!`command`` blocks, or as lazy `[detailed guidance](src/docs/…)` links. Preflight is for the things that still require the model to act (e.g. read vault lessons, read `_booping/skill_<name>.md`).
- **Research delegation**: delegate heavy reads / summarization work to `booping-researcher` to protect the skill's context. The agent is for *aggregating many sources into a summary*, not for single-file spot checks — those stay in the skill.
- **Agent wiring**: skills own all reads/writes against `~/Claude/{project}/`. Agents touch only code in the attached repo and never scan the vault. Briefings carry the request, related files, and DoD — no lesson paths. Lesson context reaches agents via two baked-in channels: DoD + Verify pasted from the plan (folded in by `/groom`) and the shared extension at `~/Claude/{project}/_booping/agent_booping-<name>.md`, rendered inline via `{{ tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='agent_booping-<name>') }}` (owned by `/learn`).
- **Per-project quality checks**: `/develop` runs the project's own lint / typecheck / test tooling once at Phase 4 (Final Verification), alongside plan-authored `Verify` commands. Command discovery order: repo `CLAUDE.md` → `_booping/skill_develop.md` → inspection of `package.json`, `pyproject.toml`, `Justfile`, etc.

## Config schema (`src/config.yaml`)

Top-level keys currently in use:

- `skills.<name>.effort` — frontmatter `effort` value.
- `skills.<name>.agents.<agent-name>.good_for` / `.bad_for` — delegation guidance rendered by `_available_agents.j2`. Currently used by `/groom` and `/develop`.
- `git.branches` — list of `{branch, when}` entries. `branch` is the literal prefix string (slash and format up to user, e.g. `feat/`); `when` is a list of short matches (plan `type` names like `feature`, or freeform descriptors). Rendered via `_git_guide.j2` macro; consumed by `/develop` for branch selection.
- `plan.statuses.<key>` — `desc`, `owner` (skill), `terminal` (bool), optional `artifacts` (list of strings describing what the state produces), `transitions` (list of `{to, skill, when, gates?, on_exit?}`). Filtered per-skill by `_plan_transitions.j2` (macro shows only statuses a skill owns or has transitions out of, and only rows where `skill == <current>`). `gates` is a list of verifiable preconditions rendered into the `Gates` column; `on_exit` is a list of short instruction strings (frontmatter mutations, side effects) rendered verbatim into the `On exit` column (e.g. `"set \`planned: yyyymmdd hh:mm\`"`).
- `tasks` — list of `{type, description, doc_uri}`. Rendered by `_task_classification.j2` as bullets with a lazy-load link to `doc_uri` (relative from repo root).
- `sprint` — `scale` (list of `{sp, meaning}`), `default_threshold_sp` (SP total past which /groom should propose splitting — not a velocity), `redecompose_threshold` (tasks ≥ this SP must be re-decomposed), `group_threshold` (tasks ≤ this SP should be grouped into one agent briefing). Rendered by `_sprint_planning.j2`; `redecompose_threshold` / `group_threshold` are skipped when falsy.

## Plan lifecycle

- Statuses + transitions live in `src/config.yaml` (`plan.statuses`). The rendered skill body shows only that skill's slice. Terminal states: `done`, `fail`, `cancelled`.
- Status transitions are **manual frontmatter edits**, not CLI mutations. The skill applies them when a trigger in its rendered transitions table matches an internal action.
- Current flow: `backlog → in-spec → awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro → awaiting-learning → done`, with `cancelled` / `fail` terminal branches and in-groom loopbacks (`awaiting-plan-review → in-spec`, `in-spec → backlog`).
  - `backlog` is for parked plans only (split stubs, user-filed ideas not yet in grooming). Active groom runs write directly to `in-spec`.
  - `in-spec` is where `/groom` does its work. `awaiting-plan-review` is the explicit user-approval gate. `ready-for-dev` is the queue `/develop` claims from. No backlog-shortcut into `/develop`.
- Each transition carries `when` (trigger), optional `gates` (verifiable preconditions), and optional `on_exit` (frontmatter mutations / side effects). Each status carries optional `artifacts` (what the state produces).
- After a transition, verify with `booping plans --status <new-status>`.
- `sprints.md` is a snapshot derived from plan frontmatter via `booping plans --format=md`. `/chat` refreshes it on orient; nothing else regenerates it today, so it can drift between plan transitions. A planned PostToolUse + SessionStart/End hook bundle (queued as a follow-up plan) will refresh it automatically on every plan write. Never hand-edit it.

## Project vault layout (`~/Claude/{project}/`)

- The vault is **Obsidian-ready**: markdown files + YAML frontmatter that Obsidian renders as Properties. No proprietary database. Open `~/Claude/{project}/` in Obsidian for graph view + backlinks across plans, retros, and lessons.
- `plans/{YYYYMMDD}-{kebab-title}.md` — plan files; frontmatter per `docs/template_plan_frontmatter.md`. Sibling stubs set `split_from: plans/...` to point at the primary plan they were split from.
- `plan_templates/*.md` — project-local plan templates. Each has frontmatter (`name`, `description`) + two top-level sections (`# Plan Body`, `# Quality Checklist`). Picked up by the `plan_template` context module alongside core templates; can override a core template by sharing its `name`, or add entirely new ones.
- `lessons/` — accumulated lessons; loaded by skills' Preflight.
- `notes/` — user notes (plan-review comments, code-review threads, ideas for next sprints). Not consumed by skills or agents — purely for the user's own reference.
- `_booping/skill_<name>.md` — project-local extensions to wide-domain skills.

(Project conventions live in the attached repo's own `CLAUDE.md`, not in the vault.)

## CLI

- `booping render <template>` — render a Jinja2 template from `src/templates/` against the assembled context (core config deep-merged with project config, lessons, extra instructions, agents, etc.). Called from skill/agent thin shells via `!`booping render src/templates/…``.
- `booping plans` — list plans, filter by status, sort by any frontmatter field. Tab-separated output.
- `booping debug-context` — dump the assembled context (merged config, project info, etc.) for inspection.
- `booping debug-template <template>` — render a template with debug output showing context variables.
- `booping-create-project` — scaffold `~/Claude/{project-name}/`.
- `booping-external-llm-call --prompt=<name> --context.<key>=<path>... [-- <free-text>]` — render a Jinja2 prompt template from `bin/llm-call-templates/<name>.md.j2` against caller-supplied context (file or directory paths read into `{{ <key> }}`; trailing free-text becomes `{{ message }}`) and send it to Gemini. Handles its own API-key check; never inspect `GEMINI_API_KEY` from agent context. Current templates: `validate-plan` (cross-validates a plan against project lessons).
- `just build-docs` — render doc and plan templates from `src/templates/docs/` and `src/templates/plan_templates/` into `docs/`.

## Editing conventions

- For template-driven skills: edit `src/templates/` and `src/config.yaml`; never edit the thin shell `skills/<name>/SKILL.md` directly (only the frontmatter `effort` is hand-maintained). Templates are rendered at skill-load time via `!`booping render``, not by a build step. Use `just build-docs` for static docs/plan-templates only.
- Prefer extracting to a partial over inlining when prose grows past a paragraph or two.
- Prefer moving structured data into `src/config.yaml` over prose in partials.
- No comments that restate code. Only WHY for non-obvious bits.
- No tests in `bin/`.
- Conventional commits with scope: `feat(booping): ...`, `fix(install): ...`, etc.
- The plugin code itself stays stack-agnostic — no Python/Django/JS specifics inside skills.
- README.md's Statuses section is hand-maintained narrative — revisit it whenever `src/config.yaml` `plan.statuses` changes (status name, description, terminal flag, or addition/removal).

## Adding a new template-driven skill

Use `src/templates/skills/groom.md.j2` as the reference.

1. Decide what goes in config vs prose: structured values (`effort`, `description`, per-skill agents, task-type / status / transition surfaces) belong in `src/config.yaml`; verbs, heuristics, and judgment calls go in the template.
2. Author the template at `src/templates/skills/<name>.md.j2`. Standard wiring in the template body:
   - `{% include "_partials/_project_context.j2" %}` — loads project name/path at skill load.
   - `{{ available_agents.render("<name>") }}` (import macro with `with context`) — renders agent delegation table from config.
   - `{{ plan_transitions.render("<name>") }}` (import macro with `with context`) — renders the transitions slice for this skill.
   - `{{ tools.render('src/templates/_partials/_lessons.j2') }}` — inlines live lessons at skill load.
   - `{{ tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='skill_<name>') }}` — inlines project-local skill extension at skill load.
3. Add the skill's `effort` and `agents` block to `src/config.yaml` under `skills.<name>`.
4. For any detail only some routes need, write it as `src/docs/<name>.md` and lazy-link from the skill body with `[label](src/docs/<name>.md)` rather than inlining.
5. Hand-author `skills/<name>/SKILL.md` with frontmatter (`effort`) plus `!`booping render src/templates/skills/<name>.md.j2``.
