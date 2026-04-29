# booping plugin — project guide

Claude Code plugin that grooms and executes plans across user projects. Plans live under `~/Claude/{project}/` (the per-project vault); skills, agents, templates, and config live in this repo.

## Status

_Last updated: 2026-04-29._

Runtime template-rendering pipeline is live. Current state:

- **Runtime rendering**: skills and agents are thin shells (frontmatter + one `!`booping render <template-path>`` line). Templates are rendered at skill-load time by `bin/booping` (Python uv project at `booping-python/`). No build step required for skill/agent changes.
- **Project config override**: `~/Claude/{project}/config.yaml` deep-merges over `src/config.yaml` at render time. Project keys win; missing keys fall through to core; lists replace wholesale.
- **Single CLI**: `bin/booping` with subcommands `render`, `render-sprints`, `debug-context`, `debug-template`. All standalone `bin/booping-*` helper scripts (11 scripts that previously injected dynamic content) have been removed; their functionality is now part of the Python CLI or handled by Jinja2 context loading.
- **Static docs**: `docs/` and `docs/plan_templates/` are still pre-rendered. Rebuild with `just build-docs` when their `.md.j2` sources change.

## Layout

- `booping-python/` — uv Python project containing the `booping` CLI (subcommands `render`, `render-sprints`, `debug-context`, `debug-template`). Source under `booping-python/src/booping/`; tests under `booping-python/tests/`.
- `bin/booping` — shell wrapper: resolves plugin root from its own location and exec's `uv run --project booping-python booping "$@"`.
- `bin/booping-create-project` — standalone uv inline script; scaffolds `~/Claude/{project}/` vault directories + `.booping` marker. Out of scope for the runtime pipeline.
- `bin/booping-external-llm-call` — standalone uv inline script; renders a Jinja2 prompt template from `bin/llm-call-templates/` and sends it to Gemini. Out of scope for the runtime pipeline.
- `src/config.yaml` — single source of truth for structured data rendered into skills (plan statuses + transitions, task types, per-skill agents / status / etc.). Loaded at render time by `Context.assemble()`.
- `src/templates/skills/<name>.md.j2` — skill templates. Rendered at skill-load time via `!`booping render ...`` in the thin shell.
- `src/templates/agents/<name>.md.j2` — agent templates. Same shape. The two developer tiers share `_partials/_developer_body.j2`.
- `src/templates/docs/<name>.md.j2` — doc templates. Pre-rendered to `docs/<name>.md` via `just build-docs`.
- `src/templates/plan_templates/<name>.md.j2` — core plan templates (backend, frontend, claude-skill, cli). Pre-rendered to `docs/plan_templates/<name>.md` via `just build-docs`. User projects may add their own under `~/Claude/{project}/plan_templates/*.md` (hand-authored `.md`, same frontmatter + two-section shape).
- `src/templates/_partials/_*.j2` — reusable fragments. Include via `{% include %}` (data-only) or import + macro (parameterized, e.g. `_plan_transitions.j2`). Parameterized partials receive call-site arguments via the `kwargs` namespace.
- `src/docs/*.md` — reference docs lazy-loaded by skills via `[label](src/docs/...)` links. Hand-authored.
- `skills/<name>/SKILL.md` — **hand-authored thin shell**: frontmatter + a single `!`booping render src/templates/skills/<name>.md.j2`` line. Never generated; edit frontmatter in place.
- `agents/<name>.md` — **hand-authored thin shell**: same shape + `!`booping render src/templates/agents/<name>.md.j2``.
- `docs/` — **pre-rendered static output**: `docs/plan_templates/*.md`, `docs/template_plan_frontmatter.md`, `docs/plan_lifecycle_overview.md`, `docs/images/`. Rebuild with `just build-docs` when `.md.j2` sources change. Never hand-edit.
- `~/Claude/{project}/config.yaml` — optional per-project config override; deep-merges over `src/config.yaml` at render time.

## Information ownership

Every piece of information lives in exactly one of these owners. When you can't decide where something belongs, walk this list top-down.

### `src/config.yaml`

Loaded at skill-load time by `Context.assemble()` — no build step. Per-project overrides live at `~/Claude/{project}/config.yaml` and deep-merge over `src/config.yaml` (project keys win; missing keys fall through; lists replace wholesale). The architecture leaves room for a future global config (e.g. `~/Claude/config.yaml`) by accepting an ordered override-paths list in `Config.load()` — adding a global tier is a one-line change when needed.

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
   - Example: project name + path rendered into skill body via `{% include "_partials/_project_context.j2" %}`.
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
- **Agent wiring**: skills own all reads/writes against `~/Claude/{project}/`. Agents touch only code in the attached repo and never scan the vault. Briefings carry the request, related files, and DoD — no lesson paths. Lesson context reaches agents via two baked-in channels: DoD + Verify pasted from the plan (folded in by `/groom`) and the shared extension at `~/Claude/{project}/_booping/agent_booping-<name>.md`, injected at agent load time via `tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='agent_booping-<name>')` in the agent template (owned by `/learn`).
- **Per-project quality checks**: `/develop` runs the project's own lint / typecheck / test tooling once at Phase 4 (Final Verification), alongside plan-authored `Verify` commands. Command discovery order: repo `CLAUDE.md` → `_booping/skill_develop.md` → inspection of `package.json`, `pyproject.toml`, `Justfile`, etc.

## Config schema (`src/config.yaml`)

Top-level keys currently in use:

- `skills.<name>.agents.<agent-name>.good_for` / `.bad_for` — delegation guidance rendered by `_available_agents.j2`. Currently used by `/groom` and `/develop`.
- `skills.<name>.status` — the plan status this skill owns (e.g. `learn → awaiting-learning`, `retro → awaiting-retro`). Rendered into skill bodies that gate on a single status.
- `git.branches` — list of `{branch, when}` entries. `branch` is the literal prefix string (slash and format up to user, e.g. `feat/`); `when` is a list of short matches (plan `type` names like `feature`, or freeform descriptors). Rendered via `_git_guide.j2` macro; consumed by `/develop` for branch selection.
- `plan.statuses.<key>` — `desc`, `owner` (skill), `terminal` (bool), optional `artifacts` (list of strings describing what the state produces), `transitions` (list of `{to, skill, when, gates?, on_exit?}`). Filtered per-skill by `_plan_transitions.j2` (macro shows only statuses a skill owns or has transitions out of, and only rows where `skill == <current>`). `gates` is a list of verifiable preconditions rendered into the `Gates` column; `on_exit` is a list of short instruction strings (frontmatter mutations, side effects) rendered verbatim into the `On exit` column (e.g. `"set \`planned: yyyymmdd hh:mm\`"`).
- `tasks` — list of `{type, description, doc_uri}`. Rendered by `_task_classification.j2` as bullets with a lazy-load link to `doc_uri` (relative from repo root).
- `sprint` — `scale` (list of `{sp, meaning}`), `default_threshold_sp` (SP total past which /groom should propose splitting — not a velocity), `redecompose_threshold` (tasks ≥ this SP must be re-decomposed), `group_threshold` (tasks ≤ this SP should be grouped into one agent briefing). Rendered by `_sprint_planning.j2`; `redecompose_threshold` / `group_threshold` are skipped when falsy. Threshold is rendered inline at skill-load time from `config.sprint.default_threshold_sp`.

## Plan lifecycle

- Statuses + transitions live in `src/config.yaml` (`plan.statuses`). The rendered skill body shows only that skill's slice. Terminal states: `done`, `fail`, `cancelled`.
- Status transitions are **manual frontmatter edits**, not CLI mutations. The skill applies them when a trigger in its rendered transitions table matches an internal action.
- Current flow: `backlog → in-spec → awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro → awaiting-learning → done`, with `cancelled` / `fail` terminal branches and in-groom loopbacks (`awaiting-plan-review → in-spec`, `in-spec → backlog`).
  - `backlog` is for parked plans only (split stubs, user-filed ideas not yet in grooming). Active groom runs write directly to `in-spec`.
  - `in-spec` is where `/groom` does its work. `awaiting-plan-review` is the explicit user-approval gate. `ready-for-dev` is the queue `/develop` claims from. No backlog-shortcut into `/develop`.
- Each transition carries `when` (trigger), optional `gates` (verifiable preconditions), and optional `on_exit` (frontmatter mutations / side effects). Each status carries optional `artifacts` (what the state produces).
- After a transition, verify by re-reading the plan frontmatter to confirm `status:` matches the new state.
- `sprints.md` is a snapshot rendered from `context.plans` via `booping render-sprints` (template `src/templates/sprints.md.j2`). `/chat` refreshes it on orient; nothing else regenerates it today, so it can drift between plan transitions. A planned PostToolUse + SessionStart/End hook bundle (queued as a follow-up plan) will refresh it automatically on every plan write. Never hand-edit it.

## Project vault layout (`~/Claude/{project}/`)

- The vault is **Obsidian-ready**: markdown files + YAML frontmatter that Obsidian renders as Properties. No proprietary database. Open `~/Claude/{project}/` in Obsidian for graph view + backlinks across plans, retros, and lessons.
- `plans/{YYYYMMDD}-{kebab-title}.md` — plan files; frontmatter per `docs/template_plan_frontmatter.md`. Sibling stubs set `split_from: plans/...` to point at the primary plan they were split from.
- `plan_templates/*.md` — project-local plan templates. Each has frontmatter (`name`, `description`) + two top-level sections (`# Plan Body`, `# Quality Checklist`). Discovered alongside core templates by `PlanTemplate.load_all()`; can override a core template by sharing its `name`, or add entirely new ones.
- `lessons/` — accumulated lessons; loaded by skills' Preflight.
- `notes/` — user notes (plan-review comments, code-review threads, ideas for next sprints). Not consumed by skills or agents — purely for the user's own reference.
- `_booping/skill_<name>.md` — project-local extensions to wide-domain skills.

(Project conventions live in the attached repo's own `CLAUDE.md`, not in the vault.)

## CLI

- `bin/booping render <template-path> [--output <path>]` — render a Jinja2 template with full project context to stdout (or to a file with `--output`). Used at skill-load time via `!`booping render ...`` and for static doc regeneration.
- `bin/booping render-sprints [--output <path>]` — render `<vault>/sprints.md` from `src/templates/sprints.md.j2`. Default output is the resolved vault's `sprints.md`; `--output PATH` overrides; `--output -` writes to stdout.
- `bin/booping debug-context` — dump the assembled `Context` as YAML for troubleshooting.
- `bin/booping debug-template <template-path>` — render a template and append a debug context footer.
- `bin/booping-create-project <project-name>` — scaffold `~/Claude/{project}/` vault directories + `.booping` marker.
- `bin/booping-external-llm-call --prompt=<name> --context.<key>=<path>... [-- <free-text>]` — render a Jinja2 prompt template from `bin/llm-call-templates/<name>.md.j2` and send it to Gemini. Handles its own API-key check. Current templates: `validate-plan`.
- `just build-docs` — pre-render `src/templates/docs/*.md.j2` and `src/templates/plan_templates/*.md.j2` to their static output paths under `docs/`.
- `just lint`, `just typecheck`, `just test` — run ruff, basedpyright, pytest against `booping-python/`.

## Editing conventions

- Edits to `src/templates/skills/*.md.j2`, `src/templates/agents/*.md.j2`, and `src/templates/_partials/*.j2` are **live** — rendered at skill-load time, no rebuild needed. Edits to `src/templates/docs/*.md.j2` or `src/templates/plan_templates/*.md.j2` require `just build-docs` to regenerate the static outputs under `docs/`.
- `skills/<name>/SKILL.md` and `agents/<name>.md` are **hand-authored thin shells** — edit frontmatter in place when it needs changing (e.g. adding a new allowed-tool). Never replace the body.
- Prefer extracting to a partial over inlining when prose grows past a paragraph or two.
- Prefer moving structured data into `src/config.yaml` over prose in partials.
- No comments that restate code. Only WHY for non-obvious bits.
- Conventional commits with scope: `feat(booping): ...`, `fix(install): ...`, etc.
- The plugin code itself stays stack-agnostic — no Python/Django/JS specifics inside skills.
- README.md's Statuses section is hand-maintained narrative — revisit it whenever `src/config.yaml` `plan.statuses` changes (status name, description, terminal flag, or addition/removal).

## Adding a new template-driven skill

Use `src/templates/skills/chat.md.j2` as the reference.

1. Decide what goes in config vs prose: structured values (per-skill agents, owned status, task-type / status / transition surfaces) belong in `src/config.yaml`; verbs, heuristics, and judgment calls go in the template.
2. Author the template at `src/templates/skills/<name>.md.j2`. No frontmatter — the thin shell carries it. Standard wiring:
   - `{% include "_partials/_project_context.j2" %}` — loads project name/path at render time.
   - `{{ available_agents.render("<name>") }}` (import macro with `with context`) — renders agent delegation table from config.
   - `{{ plan_transitions.render("<name>") }}` (import macro with `with context`) — renders the transitions slice for this skill.
   - `{{ tools.render('src/templates/_partials/_lessons.j2') }}` — inlines live lessons.
   - `{{ tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='skill_<name>') }}` — inlines project-local skill extension.
3. Add the skill's `agents` block (and any `status` it owns) to `src/config.yaml` under `skills.<name>`. Skills with no structured surface still get an empty entry (`<name>: {}`) so `_available_agents.j2` can resolve them.
4. For any detail only some routes need, write it as `src/docs/<name>.md` and lazy-link from the skill body with `[label](src/docs/<name>.md)` rather than inlining.
5. **Hand-author** `skills/<name>/SKILL.md` as a thin shell: copy frontmatter shape from a sibling skill (e.g. `skills/chat/SKILL.md`); set `allowed-tools` (include `Bash(booping:*)` plus any non-booping shell calls the skill needs); set the body to `!`booping render src/templates/skills/<name>.md.j2``. No build step.
6. Sanity-check by running `bin/booping render src/templates/skills/<name>.md.j2` and inspecting the output.
