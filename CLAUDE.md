# booping plugin — project guide

Claude Code plugin that grooms and executes plans across user projects. Plans live under `~/Claude/{project}/` (the per-project vault); skills, agents, templates, and config live in this repo.

## Status (April 2026)

Migrating to a template-driven skill pipeline. State of play:

- **Template pipeline is live**: `src/config.yaml` + `src/templates/` → `skills/*/SKILL.md` and `agents/*.md` via `bin/booping-build`.
- **`/groom` and `/develop`** are fully template-driven; their `skills/*/SKILL.md` are generated artifacts.
- **Other skills** (`chat`, `retro`, `learn`, `install`, `help`) still author their `SKILL.md` by hand and reference `docs/partial_*.md`. They are due for migration but work as-is in the meantime.
- **Agents**: all three (`booping-researcher`, `booping-developer-middle`, `booping-developer-senior`) are template-driven. The two developer tiers share `_partials/_developer_body.j2` — only frontmatter (`model`, `effort`, `reasoning`, `color`) diverges. Each agent injects project-local extensions via `!`bin/booping-extra-instructions agent_booping-<name>.md`` at the bottom of its body.
- **CLIs**: `booping-plans` (read-only), `booping-create-project`, `booping-validate-plan` — unchanged. New: `booping-build`, `booping-project-name`.

## Layout

- `src/config.yaml` — single source of truth for structured data the pipeline renders into skills (plan statuses + transitions, task types, per-skill description / effort / agents / etc.).
- `src/templates/skills/<name>.md.j2` — skill templates. One file per skill; renders to `skills/<name>/SKILL.md`.
- `src/templates/agents/<name>.md.j2` — agent templates. Render to `agents/<name>.md`. The two developer tiers share `_partials/_developer_body.j2`.
- `src/templates/docs/<name>.md.j2` — doc templates (frontmatter template, etc.). Render to `docs/<name>.md`.
- `src/templates/plan_templates/<name>.md.j2` — core plan templates (backend, frontend, claude-skill, cli). Each has YAML frontmatter (`name`, `description`) + two top-level sections: `# Plan Body` and `# Quality Checklist`. Render to `docs/plan_templates/<name>.md`. User projects may add their own templates under `~/Claude/{project}/plan_templates/*.md` (hand-authored `.md`, same frontmatter shape + two sections).
- `src/templates/_partials/_*.j2` — reusable fragments. Underscore prefix marks them as inputs, not outputs. Include via `{% include %}` (data-only partials) or import + macro call (parameterized partials, e.g. `_plan_transitions.j2`, `_plan_frontmatter.j2`, `_plan_template.j2`).
- `src/docs/*.md` — reference docs lazy-loaded by skills via `[label](src/docs/...)` links. No `partial_` prefix. Hand-authored.
- `skills/<name>/SKILL.md` — **generated output** for template-driven skills; **authored** directly for the not-yet-migrated ones. Never edit a generated `SKILL.md` by hand.
- `docs/plan_templates/*.md`, `docs/template_plan_frontmatter.md` — **generated output** from `src/templates/`; never hand-edit.
- `docs/partial_*.md`, other `docs/template_*.md` — legacy partials/templates still referenced by unmigrated skills.
- `agents/<name>.md` — **generated output** from `src/templates/agents/`; never hand-edit.
- `bin/` — standalone uv inline scripts:
  - `booping-build` — render skill, agent, doc, and plan templates from `src/templates/` → `skills/*/SKILL.md`, `agents/*.md`, `docs/*.md`, `docs/plan_templates/*.md`; `--watch` for dev loop.
  - `booping-project-name` — reads `.booping` in cwd; prints a fenced YAML block (`name:`, `directory:`) when initialized, or a paragraph pointing at `src/docs/how_to_initialize_project.md` when not. Designed to be inlined via `!`bin/booping-project-name`` at skill-load time.
  - `booping-sprint-threshold` — prints the SP total above which /groom should suggest splitting a plan. Not a velocity (no cadence); a heuristic ceiling. Today echoes `sprint.default_threshold_sp` from config. Inlined via `!`bin/booping-sprint-threshold``.
  - `booping-extra-instructions <filename>` — reads `~/Claude/{project}/_booping/<filename>` and prints a framed "User-specific instructions" block wrapping the body; prints nothing if the project isn't initialized or the file is missing. Inlined per-skill via `!`bin/booping-extra-instructions skill_<name>.md`` and per-agent via `!`bin/booping-extra-instructions agent_booping-<name>.md`` so project overrides travel with the skill or agent without a separate read step.
  - `booping-lessons` — enumerates `~/Claude/{project}/lessons/*.md`, prints a "Lessons" block with an index and each lesson's full body plus a conflict-handling rule. Prints "No lessons accumulated yet" when the directory is empty; prints nothing if the project isn't initialized. Inlined via `!`bin/booping-lessons`` so the active rule set is live at skill load.
  - `booping-plan-templates` — enumerates core plan templates from `docs/plan_templates/*.md` plus project-local templates from `~/Claude/{project}/plan_templates/*.md`; prints a grouped list with each template's name, description, and path. Inlined via `!`bin/booping-plan-templates`` so available templates are discoverable at skill load.
  - `booping-plans`, `booping-validate-plan`, `booping-create-project` — as before.

## Config vs skill — ownership boundary

Config is the **contract between skills** and, looking forward, the **user-facing customisation surface**. A per-project user override of `src/config.yaml` is the intended path for tuning the plan lifecycle, sprint scale, task types, and agent wiring. Rendering stays build-time for now (`booping-build` compiles plugin config → `skills/*/SKILL.md`); a per-project rebuild is the intended rollout for user overrides. Dynamic runtime compilation via inline `!`commands`` so config isn't baked is a future iteration — out of scope for now.

What the **config owns**:

- Where a plan can go (statuses, transitions, owner).
- Boundaries of each move (`gates` — verifiable preconditions; `when` — human-readable trigger).
- Artifacts produced in a state.
- Side effects on exit (`on_exit` — frontmatter mutations, commits, etc.).
- Structured surfaces that other skills / CLIs also consume: task types, sprint scale, agent capabilities.

What the **skill owns**:

- Verbs and heuristics — *how* to produce the artifacts and clear the gates for the states it owns.
- User interaction — what to ask, when, how to present, how to handle approval vs change requests vs cancellation.
- Judgment calls the contract can't pre-specify.
- Invariants the skill enforces across all its states ("Hard rules").

What goes in **docs/**: long-form craft (quality checklists, cross-validation rules, split guidance) that's reusable or too long to inline. Lazy-loaded from the skill body.

The skill body must not restate the flow the transitions table already carries. If a fact is in config, the skill body does not also describe it in prose.

## Principles

- **Minimum useful context**: show only information the skill needs to perform its job. Never bake in stale, speculative, or unrelated data.
- **Less prose, less drift**: every extra sentence in a skill or partial adds tension between what's written and what the model does. Cut motivation, restated context, "you are the skill / you are responsible to" preambles, and any explanation the schema or a referenced doc already carries. The schema is the source of truth; prose decays.
- **Pre-execute with `!`commands``**: inject dynamic content (project name, vault path) into the skill body at load time via inline shell. Saves a round-trip tool call per fact.
- **Lazy-load with `[doc](path)` references**: link to docs the skill reads only when the situation demands it. Keeps the baseline skill body small.
- **Hard-wire with j2 partials**: use `{% include %}` (or a macro) for content that *must* be present every invocation. Reserve partials for mandatory data that would otherwise force an unnecessary tool call.
- **Schema over prose**: structured data lives in `src/config.yaml`. If a format or value is there, the skill body must not also describe it in prose — render from config.

## Skill design

- **Wide-domain**: skills must work across stacks (Django, Rust, Hugo, etc.). Project-specific concerns live in `~/Claude/{project}/_booping/skill_<name>.md`, `lessons/`, and the project's own `CLAUDE.md` — never in the skill here.
- **Phases over flat sections**: Preflight → High-level workflow → Phase 0..N.
- **Preflight becomes thinner** in template-driven skills: items that were "Read partial X" now appear either as inlined partial content, as `!`command`` blocks, or as lazy `[detailed guidance](src/docs/…)` links. Preflight is for the things that still require the model to act (e.g. read vault lessons, read `_booping/skill_<name>.md`).
- **Research delegation**: delegate heavy reads / summarization work to `booping-researcher` to protect the skill's context. The agent is for *aggregating many sources into a summary*, not for single-file spot checks — those stay in the skill.
- **Agent wiring**: skills own all reads/writes against `~/Claude/{project}/`. Agents touch only code in the attached repo and never scan the vault. Briefings carry the request, related files, and DoD — no lesson paths. Lesson context reaches agents via two baked-in channels: DoD + Verify pasted from the plan (folded in by `/groom`) and the shared extension at `~/Claude/{project}/_booping/agent_booping-<name>.md`, injected at agent load time via `!`bin/booping-extra-instructions agent_booping-<name>.md`` (owned by `/learn`).
- **Per-project quality checks**: `/develop` runs the project's own lint / typecheck / test tooling once at Phase 4 (Final Verification), alongside plan-authored `Verify` commands. Command discovery order: repo `CLAUDE.md` → `_booping/skill_develop.md` → inspection of `package.json`, `pyproject.toml`, `Justfile`, etc.

## Config schema (`src/config.yaml`)

Top-level keys currently in use:

- `skills.<name>.effort` — frontmatter `effort` value.
- `skills.<name>.agents.<agent-name>.good_for` / `.bad_for` — delegation guidance rendered by `_available_agents.j2`. Currently used by `/groom` and `/develop`.
- `git.branches` — list of `{branch, when}` entries. `branch` is the literal prefix string (slash and format up to user, e.g. `feat/`); `when` is a list of short matches (plan `type` names like `feature`, or freeform descriptors). Rendered via `_git_guide.j2` macro; consumed by `/develop` for branch selection.
- `plan.statuses.<key>` — `desc`, `owner` (skill), `terminal` (bool), optional `artifacts` (list of strings describing what the state produces), `transitions` (list of `{to, skill, when, gates?, on_exit?}`). Filtered per-skill by `_plan_transitions.j2` (macro shows only statuses a skill owns or has transitions out of, and only rows where `skill == <current>`). `gates` is a list of verifiable preconditions rendered into the `Gates` column; `on_exit` is a list of short instruction strings (frontmatter mutations, side effects) rendered verbatim into the `On exit` column (e.g. `"set \`planned: yyyymmdd hh:mm\`"`).
- `tasks` — list of `{type, description, doc_uri}`. Rendered by `_task_classification.j2` as bullets with a lazy-load link to `doc_uri` (relative from repo root).
- `sprint` — `scale` (list of `{sp, meaning}`), `default_threshold_sp` (SP total past which /groom should propose splitting — not a velocity), `redecompose_threshold` (tasks ≥ this SP must be re-decomposed), `group_threshold` (tasks ≤ this SP should be grouped into one agent briefing). Rendered by `_sprint_planning.j2`; `redecompose_threshold` / `group_threshold` are skipped when falsy. Threshold is inlined at skill-load time via `!`bin/booping-sprint-threshold``.

## Plan lifecycle

- Statuses + transitions live in `src/config.yaml` (`plan.statuses`). The rendered skill body shows only that skill's slice. Terminal states: `done`, `fail`, `cancelled`.
- Status transitions are **manual frontmatter edits**, not CLI mutations. The skill applies them when a trigger in its rendered transitions table matches an internal action.
- Current flow: `backlog → in-spec → awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro → awaiting-learning → done`, with `cancelled` / `fail` terminal branches and in-groom loopbacks (`awaiting-plan-review → in-spec`, `in-spec → backlog`).
  - `backlog` is for parked plans only (split stubs, user-filed ideas not yet in grooming). Active groom runs write directly to `in-spec`.
  - `in-spec` is where `/groom` does its work. `awaiting-plan-review` is the explicit user-approval gate. `ready-for-dev` is the queue `/develop` claims from. No backlog-shortcut into `/develop`.
- Each transition carries `when` (trigger), optional `gates` (verifiable preconditions), and optional `on_exit` (frontmatter mutations / side effects). Each status carries optional `artifacts` (what the state produces).
- After a transition, verify with `booping-plans --status <new-status>`.
- `sprints.md` is a snapshot regenerated by `/chat` on orient via `booping-plans --format=md`; never hand-edit.

## Project vault layout (`~/Claude/{project}/`)

- `plans/{YYYYMMDD}-{kebab-title}.md` — plan files; frontmatter per `docs/template_plan_frontmatter.md`. Sibling stubs set `split_from: plans/...` to point at the primary plan they were split from.
- `plan_templates/*.md` — project-local plan templates. Each has frontmatter (`name`, `description`) + two top-level sections (`# Plan Body`, `# Quality Checklist`). Picked up by `booping-plan-templates` alongside core templates; can override a core template by sharing its `name`, or add entirely new ones.
- `lessons/` — accumulated lessons; loaded by skills' Preflight.
- `_booping/skill_<name>.md` — project-local extensions to wide-domain skills.
- `CLAUDE.md` — project conventions; loaded by skills.

## CLI

- `bin/booping-build` — render skills from `src/`. `--watch` re-renders on change (via `watchfiles`).
- `bin/booping-project-name` — emit project context (YAML block or uninitialized notice) for inlining into skills via `!`…``.
- `bin/booping-plans` — list plans, filter by status, sort by any frontmatter field. Tab-separated output.
- `bin/booping-validate-plan <plan-path>` — Gemini cross-validation. Handles its own API-key check; never inspect `GEMINI_API_KEY` from agent context.
- `just build`, `just watch` — shortcuts for the renderer.
- No tests. (User-set policy.)

## Editing conventions

- For template-driven skills: edit `src/templates/` and `src/config.yaml`; never edit the generated `skills/<name>/SKILL.md` directly. Run `just build` (or keep `just watch` running) to regenerate.
- Prefer extracting to a partial over inlining when prose grows past a paragraph or two.
- Prefer moving structured data into `src/config.yaml` over prose in partials.
- No comments that restate code. Only WHY for non-obvious bits.
- No tests in `bin/`.
- Conventional commits with scope: `feat(booping): ...`, `fix(install): ...`, etc.
- The plugin code itself stays stack-agnostic — no Python/Django/JS specifics inside skills.

## Migrating an old skill to the template pipeline

Use `src/templates/skills/groom.md.j2` as the reference.

1. Copy `skills/<name>/SKILL.md` → `src/templates/skills/<name>.md.j2`.
2. Move structured values (`effort`, `description`, per-skill agents, task-type / status / transition surfaces touching this skill) into `src/config.yaml`.
3. Replace the project-resolution Preflight bullet with `{% include "_partials/_project_context.j2" %}`.
4. Replace the plan-transitions Preflight bullet with `{{ plan_transitions.render("<skill>") }}` (import the macro with `with context`).
5. Replace the task-classification Preflight bullet with `{{ task_classification.render() }}`.
6. Replace agent-delegation Preflight bullets with `{{ available_agents.render("<skill>") }}`.
7. For any remaining partial read that fits the "small detail the skill loads on demand" shape, move it to `src/docs/<name>.md` and swap the Preflight bullet for a lazy `[detailed guidance](src/docs/<name>.md)` link.
8. Rebuild, sanity-check the rendered `skills/<name>/SKILL.md`, then delete the now-unreferenced `docs/partial_*.md` predecessors.

When the last old skill is migrated, `docs/partial_*.md` and `docs/template_*.md` can be retired wholesale.
