---
title: Skill runtime template rendering with project config overrides
type: refactoring
status: done
sp: 35
split_from: null
created: 2026-04-29 00:00
planned: 20260429 14:34
started: 20260429 14:53
completed: null
retro: null
goal: null
summary: "Ship the booping CLI: runtime skill/agent rendering with project config.yaml overrides, replacing single-purpose scripts"
---

# Skill runtime template rendering with project config overrides

## Context

Today every skill body is pre-rendered by `bin/booping-build` from `src/templates/skills/<name>.md.j2` + `src/config.yaml` into `skills/<name>/SKILL.md`. The rendered file is what Claude Code loads. Per-project dynamic content (project name, lessons, extra instructions, plan templates, sprint threshold) is injected at skill-load time via individual `!`booping-*`` commands embedded in the rendered body. This means:

- Config changes require rebuilding the plugin (`just build`).
- A project cannot override any config value.
- Each piece of dynamic content needs its own dedicated `bin/booping-*` script.

After this lands:

- A single `bin/booping` tool (Python uv project) renders skill and agent bodies at skill-load time. Each generated `SKILL.md` and `agents/<name>.md` is a thin shell: frontmatter + one `!`booping render <template-path>`` line.
- Project-level config at `~/Claude/{project}/config.yaml` deep-merges over `src/config.yaml` (project keys win). A proof-of-concept demo overrides `sprint.default_threshold_sp` and verifies the rendered `/groom` reflects it.
- All `bin/booping-*` scripts that today exist solely to inject content into skill bodies (extra-instructions, lessons, project-name, plan-templates, sprint-threshold, agents, skills, commands, workflow) are deleted. `booping-plans` is subsumed into `booping plans`. `booping-build` is dropped; its docs/plan-templates rendering responsibility moves to `booping render <path> --output <path>` invoked manually when those static artifacts change.
- `bin/booping-create-project` and `bin/booping-external-llm-call` stay as-is (out of scope).

## Decisions

- **Tool surface — single `booping` CLI**: subcommands `render`, `plans`, `debug-context`, `debug-template`. Why: one tool surface replaces ~10 single-purpose scripts, keeps the user-facing footprint small, and makes future additions (e.g. `booping config show`) a subcommand rather than another script.
- **Render takes a template path, not a name**: `booping render src/templates/skills/groom.md.j2`. Why: explicit, generic across artifact types (skills, agents, anything else), and avoids hidden naming conventions.
- **Eager context, single source per field**: `Context.assemble()` loads everything (project, plans, lessons, retros, plan_templates, config) up front. Each context field is one Pydantic model + one classmethod loader, co-located in one module under `booping-python/src/booping/context/<field>.py`. Why: the user prefers 1 place per field; templates filter at render time; reads are cheap (≤3s budget).
- **Templates receive four namespaces — `context`, `config`, `tools`, `kwargs`** — and `context` is identical for every render: `context` is the loaded data; `config` is a flat reference into `context.config` for ergonomics; `tools` is a namespace with callable helpers — `tools.render(template_path, **kwargs)` renders another template with the same `context`/`config`/`tools` globals plus a fresh `kwargs` namespace containing the call-site kwargs (`{{ kwargs.foo }}` inside the partial, never bare `{{ foo }}`). Per-template variation happens at the call site, never by mutating `context` based on what's being rendered.
- **Project config at `~/Claude/{project}/config.yaml`**: NOT inside `_booping/`. Deep-merged with core: missing keys fall through to core; present keys override; lists are replaced wholesale (not concatenated). Why: simpler mental model than per-key list semantics; project-level configurability is the demo, lists can be addressed later.
- **Architecture leaves room for global config**: `Config.load()` accepts an ordered list of override sources (`[core, global?, project?]`). Today only project → core is wired; adding global later is a one-line change. Why: user mentioned global config (e.g. custom vault dir) as a planned next step; design now accommodates without locking it in.
- **Skill/agent files become hand-authored thin shells**: `skills/<name>/SKILL.md` and `agents/<name>.md` get frontmatter (static — `name`, `description`, `allowed-tools`, `effort`) + a body of just `!`booping render src/templates/<type>/<name>.md.j2``. Why: dropping `booping-build`'s skill/agent rendering means no generator runs on these files — they exist on disk and stay in sync by being trivial.
- **Frontmatter stays static / hand-authored**: even though `effort` lives in `src/config.yaml` today, the SKILL.md frontmatter copies it manually. Why: Claude Code reads frontmatter before `!` expansion, so it must be on disk; rare edits (effort changes once per skill, ever) don't justify a build step.
- **`docs/` and `docs/plan_templates/` stay statically rendered**: these have no `!` commands and are lazy-loaded via filesystem reads (Claude can't trigger `!` expansion on a file it Reads). They keep their `.md.j2` templates and are rebuilt with `booping render <template> --output <path>` invoked manually (or via a thin `just build-docs` recipe). Why: runtime rendering doesn't apply to lazy-loaded files; keeping them static is the natural fit.
- **`allowed-tools` keeps existing entries**: per-skill allowed-tools still includes git, project test commands, etc. The booping-specific entries collapse to a single `Bash(booping:*)`. Why: skills still execute non-booping shell calls during their flow.
- **Tests use fixture directories, not the live filesystem**: pytest with `tests/__fixtures__/<scenario>/` directories (mirroring the [obsidian-blog](~/Dev/@A/obsidian-blog/tests/) pattern). Each fixture is a complete fake vault or plugin-root tree. Tests resolve a fixture path via a helper, point loaders at it, assert behavior. Pure data tests (Pydantic model construction, parsing) skip the filesystem entirely. No mocking of `open()` / `pathlib`. `pytest-snapshot` for asserting rendered template output. Why: the user pointed to obsidian-blog as the reference pattern; isolated fixture trees are easy to inspect and debug, and avoid reading the user's actual `~/Claude/claude-booping/` vault during tests.

## Architecture

### Layout after migration

```
booping-python/                       # NEW: uv Python project
  pyproject.toml
  uv.lock
  src/booping/
    __init__.py
    cli.py                            # argparse subcommands
    rendering.py                      # Jinja2 environment, render(template_path, context)
    tools.py                          # `tools` namespace passed to templates
    context/
      __init__.py                     # Context model + assemble()
      project.py                      # Project model + load_cwd()
      plan.py                         # Plan model + load_all(vault)
      lesson.py
      retro.py
      plan_template.py                # core + project merge
      config.py                       # core + project merge (extensible to global)
      extra_instructions.py           # _booping/skill_*.md and _booping/agent_*.md content
    commands/
      render.py                       # `booping render <path>`
      plans.py                        # `booping plans [filters]` (subsumes bin/booping-plans)
      debug.py                        # `booping debug-context`, `booping debug-template <path>`
  tests/
    __fixtures__/
      vault-empty/                    # uninitialized: no .booping
      vault-minimal/                  # .booping + empty plans/lessons/etc.
      vault-full/                     # populated: plans, lessons, retros, plan_templates, _booping/
      vault-with-config-override/     # has config.yaml overriding sprint.default_threshold_sp
      plugin-root-minimal/            # stand-in for the plugin root: src/config.yaml + sample templates
    helpers.py                        # get_fixture_path(name) helper
    context/
      project_test.py                 # tests for context/project.py loader
      plan_test.py
      lesson_test.py
      retro_test.py
      plan_template_test.py
      config_test.py                  # config merge / override behaviour
      extra_instructions_test.py
      assemble_test.py                # Context.assemble() smoke test against vault-full
    rendering_test.py                 # render() with snapshot fixtures
    commands/
      render_test.py
      debug_test.py

bin/booping                           # NEW: shell wrapper, exec uv run from booping-python/
bin/booping-create-project            # UNCHANGED (out of scope)
bin/booping-external-llm-call         # UNCHANGED (out of scope)
# DELETED: booping-build, booping-extra-instructions, booping-lessons, booping-plans,
# booping-project-name, booping-plan-templates, booping-sprint-threshold,
# booping-agents, booping-skills, booping-commands, booping-workflow, booping-debug-mode

skills/<name>/SKILL.md                # HAND-AUTHORED THIN SHELL: frontmatter + !`booping render ...`
agents/<name>.md                      # HAND-AUTHORED THIN SHELL: frontmatter + !`booping render ...`
docs/...                              # UNCHANGED (still pre-rendered; templates remain in src/templates/docs/)

src/templates/skills/<name>.md.j2     # CHANGED: drops !`booping-*` commands; uses {{ context.x }} etc.
src/templates/agents/<name>.md.j2     # CHANGED: same
src/templates/_partials/*.j2          # CHANGED where they reference !`booping-*`
src/config.yaml                       # UNCHANGED schema (project override deep-merges)

~/Claude/{project}/config.yaml        # NEW (optional): project override of any config key
```

### Render pipeline (skill-load time)

1. Claude Code reads `skills/<name>/SKILL.md`, parses frontmatter.
2. Claude Code finds `!`booping render src/templates/skills/<name>.md.j2`` in the body.
3. `executeShellCommandsInPrompt` invokes the wrapper at `bin/booping`.
4. Wrapper exec's `uv run --project booping-python booping render <path>`.
5. CLI calls `Context.assemble()` — reads `.booping`, vault files, both configs, deep-merges.
6. CLI loads the Jinja2 template with `context`, `config`, `tools` globals.
7. Rendered body is printed to stdout, replaces the `!` line. Claude Code never sees the `!`.

### Project root discovery

`Project.load_cwd()` walks **upward** from `Path.cwd()` looking for a `.booping` file (stops at the filesystem root). Reasoning: Claude Code may invoke skills with cwd inside a subdirectory of the repo, not at the repo root — the previous `bin/booping-project-name` only checked `Path.cwd()` directly, which would silently fail. The walk-up is the same idiom git uses to find `.git`.

### Project config merge

`Config.load(plugin_root: Path, override_paths: list[Path]) -> dict`:

1. Read `<plugin_root>/src/config.yaml` (always present).
2. For each path in `override_paths` (in order), if it exists, read and deep-merge it on top.
3. Return merged dict.

Default call site: `override_paths=[vault / "config.yaml"]` (project only). Future: prepend a global path (e.g. `Path.home() / "Claude" / "config.yaml"`) — no signature change.

Deep-merge semantics: dict keys recursively merge; non-dict values (scalars, lists) replace wholesale.

### `tools.render` cycle and depth protection

The renderer threads a per-call render stack through Jinja2's globals. `tools.render(path)` pushes `path` before rendering and pops on exit. Two guards:

1. **Cycle**: if `path` is already on the stack, raise `RenderCycleError(f"cycle detected: {path} → ... → {path}")` showing the chain.
2. **Depth**: if the stack length exceeds the configured maximum (default 10), raise `RenderDepthExceededError`.

Both errors propagate out as ordinary Python exceptions, surfacing in Claude Code's shell output for the `!` command — Claude sees the error text instead of an empty/hung body.

### Tools namespace and globals

Every render exposes four top-level namespaces:

- `context` — assembled data (project, plans, lessons, retros, plan_templates, skills, agents, config, extra_instructions). Identical shape for every render.
- `config` — alias of `context.config` for ergonomic access from templates.
- `tools` — callable helpers. `tools.render(template_path, **kwargs)` renders another template with the same `context`/`config`/`tools` globals plus a `kwargs` namespace containing the call-site kwargs.
- `kwargs` — dict-like access to the kwargs the current template was rendered with. The top-level render call seeds `kwargs = {}`; nested `tools.render(path, foo='bar')` rebinds `kwargs` to `{'foo': 'bar'}` for the duration of that nested render.

This is the mechanism for parameterised partials: e.g. `_partials/_extra_instructions.j2` reads `kwargs.extra_instruction_key` to fetch `context.extra_instructions[<key>]` and emit the framed user-instructions block. Used by every skill (each picks its own key) and by both developer agents (which share `agent_booping-developer`).

Why kwargs as a dedicated namespace instead of bare locals: **clear separation between data (`context`/`config`), capabilities (`tools`), and per-call parameters (`kwargs`)**. A template reader sees `{{ kwargs.foo }}` and immediately knows it's parameterised at the call site — bare `{{ foo }}` would conflate with locals defined by `{% set %}` inside the template. And **`context` should stay identical for every render** — per-template auto-resolution would make the context shape vary by which template is being rendered, which is surprising and harder to test.

## Execution mode — milestone-by-milestone, one session each

`/develop` runs **one milestone per session** and then stops. After each milestone:

1. Complete every task in the milestone, flip its DoD checkboxes, run the milestone's `Verify` step, confirm it's green.
2. Commit the milestone's changes (one commit per milestone, scope `feat(booping):` / `refactor(booping):` per `git.commit_message` config).
3. **Stop.** Do not start the next milestone in the same session — print a short status (which milestone closed, which is next) and exit.
4. The user reviews, may edit the plan or the diff, then starts a fresh session for the next milestone.

The plan stays in `in-progress` across milestones; `started` is set when M1 begins; `completed` is set only when M8 closes (per the standard transitions table).

If `/develop` is invoked again on this plan in a new session, it resumes from the first milestone whose status is `pending`. It does not re-run completed milestones.

## Milestones

### M1: booping-python uv project + render stub + test scaffold — 6 SP | done

**Goal**: a `booping render <template-path>` command that renders a Jinja2 template with empty context to stdout, invokable as `booping` from PATH. `pytest` runs against fixture-based tests with a green smoke test.

**Verify**: `bin/booping render src/templates/skills/chat.md.j2 2>&1 | head -20` runs without error (output may be malformed since templates still expect context — that's M2's job). `cd booping-python && uv run pytest` is green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Scaffold uv project: `pyproject.toml`, ruff + basedpyright config, Justfile entries (`just lint`, `just typecheck`, `just test`), `src/booping/__init__.py`. Pin Python ≥3.12. Runtime deps: `jinja2`, `pyyaml`, `pydantic`. Dev deps: `pytest`, `pytest-snapshot`, `ruff`, `basedpyright`. | `booping-python/pyproject.toml`, `booping-python/uv.lock`, `Justfile` | 2 | done |
| 1.2 | Wrapper at `bin/booping`: bash script that resolves plugin root from its own location and exec's `uv run --project "$PLUGIN_ROOT/booping-python" booping "$@"`. Make executable. Verified at draft time: `.claude-plugin/plugin.json` does not reference any bin paths today, so no plugin.json edit is required from this task. (M6.1 re-verifies on cleanup.) | `bin/booping` | 1 | done |
| 1.3 | CLI: argparse with subcommands `render`, `plans`, `debug-context`, `debug-template`. Implement `render <path>` stub: read template, render with `context = {}`, `config = {}`, `tools = {}` and lenient undefined (so M2 can land progressively). Print to stdout. | `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/render.py`, `booping-python/src/booping/rendering.py` | 2 | done |
| 1.4 | Test infrastructure: `tests/helpers.py` with `get_fixture_path(name)`. Fixture skeletons for `vault-empty/`, `vault-minimal/`, `vault-full/`, `vault-with-config-override/`, `plugin-root-minimal/` — populate with realistic but minimal content (one or two plans, one lesson, one retro, etc.). One smoke test verifying the `render` stub renders an arbitrary Jinja2 template against the `plugin-root-minimal/` fixture. | `booping-python/tests/__init__.py`, `booping-python/tests/helpers.py`, `booping-python/tests/__fixtures__/...`, `booping-python/tests/rendering_test.py` (smoke only) | 1 | done |

#### Task 1.1 DoD

- [x] `cd booping-python && uv sync` succeeds.
- [x] `cd booping-python && uv run ruff check .` passes.
- [x] `cd booping-python && uv run basedpyright` passes.
- [x] `cd booping-python && uv run pytest` runs (zero collected tests is acceptable until T1.4).
- [x] `just lint`, `just typecheck`, `just test` recipes route to the above.

#### Task 1.2 DoD

- [x] `bin/booping --help` works from any cwd inside the repo.
- [x] `bin/booping --help` works when invoked as `booping --help` (PATH resolution intact in `~/.claude/plugins/cache/booping-local/booping/<version>/bin/`).
- [x] No reference to deleted bin paths in `.claude-plugin/plugin.json`.

#### Task 1.3 DoD

- [x] `booping render <any-jinja2-template> ` prints the template body (with `{{ }}` blocks left as-is or noop'd via undefined-default).
- [x] `booping render --help` lists `<path>` argument.
- [x] Other subcommand stubs (`plans`, `debug-context`, `debug-template`) print "not implemented" and exit non-zero.

#### Task 1.4 DoD

- [x] `tests/__fixtures__/` contains: `vault-empty/`, `vault-minimal/` (with `.booping`), `vault-full/` (with at least 2 plans, 1 lesson, 1 retro, 1 plan_template, 1 `_booping/skill_groom.md` extra), `vault-with-config-override/` (with `config.yaml` overriding `sprint.default_threshold_sp`), `plugin-root-minimal/` (with `src/config.yaml` and at least one `.j2` template).
- [x] `tests/helpers.py` exposes `get_fixture_path(name)` resolving relative to `tests/__fixtures__/`.
- [x] `cd booping-python && uv run pytest` collects and passes the smoke test (renders a fixture template via the `render` command).
- [x] No test reads from `~/Claude/` or any path outside `booping-python/tests/__fixtures__/`.

---

### M2: Context loaders + project config merge — 8 SP | done

**Goal**: `Context.assemble()` returns a fully-loaded Context with project, plans, lessons, retros, plan_templates, skills, agents, config, and extra_instructions populated. Project config at `~/Claude/{project}/config.yaml` deep-merges over `src/config.yaml`. All loaders covered by fixture-based tests.

**Verify**: `cd booping-python && uv run pytest` is green with all loader tests passing (no real-filesystem reads outside `tests/__fixtures__/`). Smoke check from inside `/home/anton/Claude/claude-booping/`: `booping debug-context` prints YAML with all fields populated. Add a test override file at `/home/anton/Claude/claude-booping/config.yaml` with `sprint: { default_threshold_sp: 50 }`; re-run `booping debug-context` and confirm the merged value is `50`. Delete the override file.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `Project` model with fields `name: str`, `directory: Path` (vault root). `Project.load_cwd()`: walk **upward** from `Path.cwd()` looking for a `.booping` file (stop at filesystem root); on hit, parse YAML, read `project_name`, return `Project(name=..., directory=Path.home() / "Claude" / name)`. On miss, return `None` (callers short-circuit). Wire into `Context`. | `booping-python/src/booping/context/project.py`, `booping-python/src/booping/context/__init__.py` | 1 | done |
| 2.2 | `Plan` model with fields: `path: Path`, `title: str`, `type: Literal['feature', 'bug', 'refactoring']`, `status: str`, `sp: int \| None`, `split_from: str \| None`, `created: date \| None`, `planned: str \| None`, `started: str \| None`, `completed: str \| None`, `retro: str \| None`, `goal: str \| None`, `business_goal: str = ""`, `body: str = ""`. `Plan.load_all(vault: Path)` reads `vault/plans/*.md`, parses YAML frontmatter, returns list. Empty list when `vault/plans/` missing. | `booping-python/src/booping/context/plan.py` | 1 | done |
| 2.3 | `Lesson` model with fields: `id: str` (filename stem), `path: Path`, `title: str` (frontmatter `title` → fallback to id), `body: str`, `frontmatter: dict[str, Any]`. `Retro` model with fields: `path: Path`, `plan: str \| None`, `goal: str \| None`, `created: date \| None`, `body: str`, `frontmatter: dict[str, Any]`. Both loaders enumerate `vault/lessons/*.md` / `vault/retrospectives/*.md`, parse frontmatter + body, sorted by filename. | `booping-python/src/booping/context/lesson.py`, `booping-python/src/booping/context/retro.py` | 1 | done |
| 2.4 | `PlanTemplate` model with fields: `name: str`, `description: str`, `path: Path`, `body: str`, `source: Literal['core', 'project']`. `PlanTemplate.load_all(plugin_root, vault)`: read `<plugin_root>/docs/plan_templates/*.md` (source=`core`), then `<vault>/plan_templates/*.md` if present (source=`project`); for each, parse frontmatter (`name` falls back to filename stem; `description` defaults to `""`). When project and core share a `name`, the project entry replaces the core entry in the returned list. | `booping-python/src/booping/context/plan_template.py` | 1 | done |
| 2.5 | `Config.load(plugin_root: Path, override_paths: list[Path]) -> dict` — read `<plugin_root>/src/config.yaml`, then deep-merge each `override_paths` entry that exists onto it in order. Deep-merge helper: nested dicts recurse; lists/scalars replace. The plan-default call site uses `override_paths=[vault / "config.yaml"]`; future global config inserts a global path before the project path with no signature change. Implement `debug-context` subcommand to dump merged Context as YAML for verification. | `booping-python/src/booping/context/config.py`, `booping-python/src/booping/commands/debug.py` | 2 | done |
| 2.6 | `ExtraInstructions` loader — eager-load every `<vault>/_booping/skill_*.md` and `<vault>/_booping/agent_*.md` into `context.extra_instructions: dict[str, str]` keyed by filename stem (e.g. `'skill_groom'`, `'agent_booping-developer'`). `context` is identical for every render — no auto-resolution. Templates select their key explicitly. `Tools` namespace with `tools.render(template_path: str, **kwargs: Any) -> str` — renders another template with the SAME `context`/`config`/`tools` globals, **plus a `kwargs` global containing all keyword arguments as a dict-like object** (templates read e.g. `{{ kwargs.extra_instruction_key }}`). The four top-level namespaces are `context`, `config`, `tools`, `kwargs` — clean separation, kwargs never leak into the local namespace. The top-level render call (the skill/agent SKILL.md) gets `kwargs = {}`. **Cycle detection**: the renderer keeps a per-call stack of currently-rendering template paths; `tools.render` raises a clear error if it would push a path already on the stack, and a separate max-depth check (default 10) raises on runaway nesting. | `booping-python/src/booping/context/extra_instructions.py`, `booping-python/src/booping/tools.py`, `booping-python/src/booping/rendering.py` | 1 | done |
| 2.7 | `Skill` and `Agent` metadata models with fields: `name: str`, `description: str`, `path: Path`, plus optional `effort: str \| None`, `model: str \| None`, `allowed_tools: list[str]`, `user_invocable: bool` (Skill only), `color: str \| None` (Agent only). `Skill` also has `debug_enabled: bool` (true when `<plugin_root>/skills/<name>/.debug_enabled` exists — replaces `bin/booping-debug-mode`). Loaders enumerate `<plugin_root>/skills/*/SKILL.md` and `<plugin_root>/agents/*.md`, parse frontmatter only (no body needed for `/help` rendering — they're listings, not embeddings). `Context.skills` (a dict keyed by name for ergonomic access like `context.skills.learn`) and `Context.agents` exposed. | `booping-python/src/booping/context/skill.py`, `booping-python/src/booping/context/agent.py` | 1 | done |

#### Task 2.1 DoD

- [x] `Context.assemble().project.name` and `.directory` match what `bin/booping-project-name` prints today when run from the booping repo root.
- [x] When invoked from a subdirectory (e.g. `src/templates/`), `Project.load_cwd()` walks up and still finds `.booping` at the repo root.
- [x] When `.booping` is missing anywhere up to filesystem root, `Project.load_cwd()` returns `None` and downstream loaders short-circuit to empty/default values.
- [x] `tests/context/project_test.py`: covers (a) load from fixture root, (b) load when cwd is a fixture subdirectory (walk-up), (c) absent `.booping` returns `None` — passes.

#### Task 2.2 DoD

- [x] `len(Context.assemble().plans)` matches `wc -l < <(bin/booping-plans)` for the booping vault.
- [x] Each `Plan` exposes the frontmatter fields used by current skills (`title`, `type`, `status`, `sp`, `created`, `planned`, `started`, `completed`, `retro`, `goal`, `business_goal`).
- [x] `tests/context/plan_test.py`: loads plans from `vault-full/`, asserts count and field values for one well-known fixture plan — passes.

#### Task 2.3 DoD

- [x] `Lesson` exposes `id`, `title`, `body`, plus any frontmatter the current `bin/booping-lessons` parses.
- [x] `Retro` exposes the fields current retro flows reference (path, plan, goal, etc.).
- [x] `tests/context/lesson_test.py` and `tests/context/retro_test.py`: each loads from `vault-full/` and asserts at least count + one full-field assertion — pass.

#### Task 2.4 DoD

- [x] Core-only mode: list matches `bin/booping-plan-templates` output (4 core templates).
- [x] Project-template override: dropping `~/Claude/claude-booping/plan_templates/claude-skill.md` (with same `name: claude-skill`) replaces the core entry in the loaded list.
- [x] `tests/context/plan_template_test.py`: tests core-only against `plugin-root-minimal/` and override behavior using a fixture vault that ships a `plan_templates/<name>.md` colliding with a core name — passes.

#### Task 2.5 DoD

- [x] `booping debug-context | grep default_threshold_sp` prints `35` (core) when no project config exists.
- [x] Adding `~/Claude/claude-booping/config.yaml` with `sprint: { default_threshold_sp: 50 }` causes the same command to print `50`.
- [x] Removing the override file restores `35`.
- [x] Deep-merge handles nested overrides (e.g. overriding only `sprint.default_threshold_sp` leaves `sprint.scale` from core intact).
- [x] `Config.load`'s signature accepts an ordered override-paths list (verified by reading the function signature; not exercised end-to-end).
- [x] `tests/context/config_test.py`: covers (a) core-only load against `plugin-root-minimal/`, (b) project override against `vault-with-config-override/` with deep-merge assertion (overridden key changed, sibling keys untouched), (c) list replacement semantics (a list at the override level replaces wholesale), (d) ordered override-paths list signature — passes.

#### Task 2.6 DoD

- [x] `context.extra_instructions` is a dict containing every `_booping/skill_*.md` and `_booping/agent_*.md` file in the vault, keyed by stem; absent vault directories yield an empty dict.
- [x] `context` returned from `Context.assemble()` is shape-identical regardless of which template will be rendered (no auto-resolution).
- [x] A template using `{{ tools.render('src/templates/_partials/_project_context.j2') }}` produces the same output as `{% include "_partials/_project_context.j2" %}` (verified by side-by-side render).
- [x] `tools.render(path, foo='bar')` makes `{{ kwargs.foo }}` (not bare `{{ foo }}`) available inside the rendered template; bare `{{ foo }}` is undefined.
- [x] The top-level render call seeds `kwargs = {}` (empty namespace); a top-level template that reads `{{ kwargs.x }}` for an unset key gets the configured undefined behavior, not a crash on `kwargs` itself.
- [x] Self-reference: a template that calls `{{ tools.render('<itself>') }}` raises a clear cycle-detection error (not infinite recursion).
- [x] Mutual reference: A→B→A cycle across two templates raises the same error.
- [x] Max-depth guard: when nesting exceeds the depth limit (default 10) without forming a cycle, raises a depth-limit error.
- [x] `tests/context/extra_instructions_test.py`: loads from `vault-full/`, asserts the dict shape (keys present, values are file bodies) and that an absent file yields no key — passes.
- [x] `tests/rendering_test.py`: covers (a) `tools.render(template_path)` producing identical output to `{% include %}` for an idempotent partial, (b) `tools.render(path, foo='bar')` makes `kwargs.foo` available and bare `foo` undefined, (c) self-reference raises cycle error, (d) mutual reference raises cycle error, (e) depth limit raises — passes.
- [x] `tests/context/assemble_test.py`: end-to-end smoke test asserting `Context.assemble()` populates every field non-empty against `vault-full/` + `plugin-root-minimal/` — passes.

#### Task 2.7 DoD

- [x] `len(Context.assemble().skills)` equals the number of `<plugin_root>/skills/*/SKILL.md` files; `len(.agents)` equals `<plugin_root>/agents/*.md` count.
- [x] Each `Skill`/`Agent` exposes `name`, `description`, `path`, plus the listed optional fields when present in frontmatter.
- [x] `Skill.debug_enabled` is `True` when a sibling `.debug_enabled` file exists in the skill directory, `False` otherwise.
- [x] `tests/context/skill_test.py` and `tests/context/agent_test.py`: each loads from `plugin-root-minimal/` and asserts count + one full-field assertion against a fixture entry. `skill_test.py` also covers `debug_enabled` by including a fixture skill with `.debug_enabled` and one without — pass.

---

### M3: Migrate skill templates and partials — 8 SP | done

**Goal**: every `src/templates/skills/<name>.md.j2` and every `src/templates/_partials/*.j2` uses `{{ context.x }}` / `{{ config.x }}` / `{{ tools.x() }}` for what was previously injected by `!`booping-*`` commands. No `!` commands remain inside templates or partials. `booping render src/templates/skills/<name>.md.j2` produces a body equivalent to today's rendered SKILL.md (modulo cosmetics).

**Verify**: for each skill, run `booping render src/templates/skills/<name>.md.j2 > /tmp/<name>.new.md` and compare to today's `skills/<name>/SKILL.md` (after stripping today's frontmatter). Diff should be small and explainable (e.g. whitespace, no functional drift).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Refactor partials that reference `!`booping-*`` commands: `_project_context.j2`, `_sprint_planning.j2`, `_shared_instructions.j2`, `_plan_template.j2`. Replace `!` lines with Jinja2 expressions over `context`/`config`. Author a new `_extra_instructions.j2` partial that reads `kwargs.extra_instruction_key` and emits the framed "User-specific instructions" block (matching the format `bin/booping-extra-instructions` produced) when `context.extra_instructions[kwargs.extra_instruction_key]` exists and is non-empty; emits nothing otherwise. Author a new `_lessons.j2` partial that renders the framed "Lessons" block from `context.lessons` (matching the format `bin/booping-lessons` produced) — every skill needs the same block, so extract once. Audit other partials (`_plan_lesson_check.j2`, `_learn_targets.j2`, `_session_log_extraction.j2`, `_retrospective_template.j2`) for any other `!` usage. | `src/templates/_partials/_project_context.j2`, `src/templates/_partials/_sprint_planning.j2`, `src/templates/_partials/_shared_instructions.j2`, `src/templates/_partials/_plan_template.j2`, `src/templates/_partials/_extra_instructions.j2` (new), `src/templates/_partials/_lessons.j2` (new) | 2 | done |
| 3.2 | Migrate `chat.md.j2` (smallest body, exercises lessons + project context). Establishes the per-skill pattern: where `!`booping-lessons`` lived, render `_lessons.j2`; where `!`booping-extra-instructions skill_chat.md`` lived, render `_extra_instructions.j2` with `extra_instruction_key='skill_chat'`; where `!`booping-project-name`` lived, render `_project_context.j2`. | `src/templates/skills/chat.md.j2` | 1 | done |
| 3.3 | Migrate `groom.md.j2` (largest body, most `!` commands: project, lessons, extras, plan-templates, sprint-threshold). | `src/templates/skills/groom.md.j2` | 2 | done |
| 3.4 | Migrate `develop.md.j2`. | `src/templates/skills/develop.md.j2` | 1 | done |
| 3.5 | Migrate `retro.md.j2` and `learn.md.j2`. Replace `!`booping-plans --status {{ config.skills.<skill>.status }}`` with a Jinja2 loop over `context.plans` filtered by `plan.status == config.skills.<skill>.status` (each template formats the matched plans into its existing block — diff vs current rendered output verifies parity). Replace `!`booping-debug-mode learn`` with `{% if context.skills.learn.debug_enabled %}Debug mode enabled. You can update this skill at <template path>{% endif %}` (the message body matches what `bin/booping-debug-mode` prints today). | `src/templates/skills/retro.md.j2`, `src/templates/skills/learn.md.j2` | 1 | done |
| 3.6 | Migrate `help.md.j2` and `install.md.j2`. These rely on `!`booping-skills``, `!`booping-agents``, `!`booping-commands``, `!`booping-workflow`` — replace with Jinja2 loops over `context.skills`, `context.agents` (loaded by T2.7), and over `config.plan.statuses` for the workflow chain. The `!`booping-commands`` "First time in a repo: /install" line becomes `{% if context.project is none %}…{% endif %}`. Also update the descriptive prose at lines 65–67 of `help.md.j2` (which currently explains the loading mechanism using `!`booping-lessons``, `!`booping-extra-instructions skill_<name>.md``, `!`booping-extra-instructions agent_booping-<name>.md`` literals) to describe the new mechanism — the runtime context loader — without referring to the deleted bin scripts. | `src/templates/skills/help.md.j2`, `src/templates/skills/install.md.j2` | 1 | done |

#### Task 3.1 DoD

- [x] `grep -rn '!\`booping-' src/templates/_partials/` returns no matches.
- [x] Each refactored partial renders identically (or with explainable trivial diff) to its previous `!`-driven output, verified per-partial in a scratch template.
- [x] `_extra_instructions.j2` invoked with `tools.render(..., extra_instruction_key='skill_groom')` against `vault-full/` produces the same framed block that `bin/booping-extra-instructions skill_groom.md` emits today.
- [x] `_extra_instructions.j2` emits nothing when the key is absent or the body is empty.
- [x] `_lessons.j2` rendered against `vault-full/` produces the same block `bin/booping-lessons` emits today.

#### Task 3.2 DoD

- [x] `grep -n '!\`' src/templates/skills/chat.md.j2` returns no matches.
- [x] `booping render src/templates/skills/chat.md.j2` output matches `skills/chat/SKILL.md` body section (post-frontmatter) modulo trivial whitespace.

#### Task 3.3 DoD

- [x] `grep -n '!\`' src/templates/skills/groom.md.j2` returns no matches.
- [x] Rendered body diff vs current `skills/groom/SKILL.md` (post-frontmatter) is trivial.
- [x] Sprint-threshold in rendered body picks up project override when `~/Claude/claude-booping/config.yaml` sets `sprint.default_threshold_sp`.

#### Task 3.4 DoD

- [x] `grep -n '!\`' src/templates/skills/develop.md.j2` returns no matches.
- [x] Rendered body diff trivial.

#### Task 3.5 DoD

- [x] No `!` commands remain in either template.
- [x] `retro` and `learn` rendered bodies show the same status-filtered plan list as today (verified by diff against current `skills/retro/SKILL.md` and `skills/learn/SKILL.md`).
- [x] When `<plugin_root>/skills/learn/.debug_enabled` is present, learn's rendered body contains the debug-mode notice; absent, the section is omitted (verified by toggling the marker file).
- [x] Rendered body diffs trivial.

#### Task 3.6 DoD

- [x] No `!` commands remain in either template.
- [x] `help`'s skills/agents/commands/workflow tables render correctly from `context.skills`, `context.agents`, `config.plan.statuses`.
- [x] "First time in a repo: /install" line appears only when `context.project is None`.
- [x] `help.md.j2` lines 65–67 prose no longer mentions `booping-lessons` or `booping-extra-instructions` literals; describes the runtime context-loader mechanism instead.
- [x] `grep -nE 'booping-(lessons|extra-instructions|debug-mode|plans|sprint-threshold|plan-templates|project-name|skills|agents|commands|workflow|build)' src/templates/skills/help.md.j2` returns no hits.
- [x] Rendered body diffs trivial.

#### M3 cross-cutting DoD (applies to every task above)

- [x] **Four-check IA pass** (lesson 0004) applied to each refactored template/partial **before saving**: scoping (does this skill need this block?), duplication (does it appear elsewhere — extract to partial?), configurability (is this user-tunable — partial it?), hierarchy (does the detail level match the file?). Recorded by reviewing the diff against the four checks; trivial files may note "passed" without per-bullet annotation.

---

### M4: Migrate agent templates — 3 SP | done

**Goal**: every `src/templates/agents/<name>.md.j2` uses context/config/tools instead of `!` commands.

**Verify**: for each agent, run `booping render src/templates/agents/<name>.md.j2 > /tmp/<name>.new.md` and compare to today's `agents/<name>.md` body. Diff trivial.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Refactor the shared `_developer_body.j2` partial and the `booping-developer-middle.md.j2`, `booping-developer-senior.md.j2` agent templates. Replace `!`booping-extra-instructions agent_booping-developer.md`` with `tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='agent_booping-developer')` — both developer tiers share the same extras key (preserving today's convention). Render each and diff vs current `agents/booping-developer-{middle,senior}.md` to confirm no behavior drift. | `src/templates/_partials/_developer_body.j2`, `src/templates/agents/booping-developer-middle.md.j2`, `src/templates/agents/booping-developer-senior.md.j2` | 2 | done |
| 4.2 | Migrate `booping-researcher.md.j2`. Replace `!`booping-extra-instructions agent_booping-researcher.md`` with `tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='agent_booping-researcher')`. Render and diff vs current `agents/booping-researcher.md`. | `src/templates/agents/booping-researcher.md.j2` | 1 | done |

#### Task 4.1 DoD

- [x] `grep -rn '!\`' src/templates/agents/booping-developer-*.md.j2 src/templates/_partials/_developer_body.j2` returns no matches.
- [x] Rendered body diffs vs current `agents/booping-developer-middle.md` and `booping-developer-senior.md` trivial.

#### Task 4.2 DoD

- [x] `grep -n '!\`' src/templates/agents/booping-researcher.md.j2` returns no matches.
- [x] Rendered body diff trivial.

#### M4 cross-cutting DoD (applies to every task above)

- [x] **Four-check IA pass** (lesson 0004) applied to each refactored agent template/partial before saving: scoping, duplication, configurability, hierarchy.

---

### M5: Replace generated artifacts with thin shells — 4 SP | done

**Goal**: `skills/<name>/SKILL.md` and `agents/<name>.md` are hand-authored thin shells (frontmatter + one `!`booping render <template-path>`` line). Static docs/plan-templates rendering moves off `booping-build`.

**Verify**: in Claude Code, invoke `/groom`, `/chat`, `/develop`, `/retro`, `/learn`, `/help`, `/install` — each loads, the body renders correctly with project context (lessons, project name, etc.). Invoke a skill that delegates to an agent and confirm the agent's body renders.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Rewrite each `skills/<name>/SKILL.md` (7 files) by hand: copy current frontmatter; replace body with single line `!`booping render src/templates/skills/<name>.md.j2``. Update `allowed-tools` — drop `Bash(booping-extra-instructions:*)`, `Bash(booping-lessons:*)`, etc.; keep git, project-test, and any non-booping entries; add `Bash(booping:*)`. | `skills/{chat,develop,groom,help,install,learn,retro}/SKILL.md` | 2 | done |
| 5.2 | Rewrite each `agents/<name>.md` (3 files) by hand: same shape — frontmatter + `!`booping render src/templates/agents/<name>.md.j2``. Update allowed-tools similarly. | `agents/{booping-developer-middle,booping-developer-senior,booping-researcher}.md` | 1 | done |
| 5.3 | **Locked: Option B — drop `bin/booping-build` entirely**. Add `--output <path>` flag to `booping render` (writes rendered output to the given file instead of stdout). Add a `just build-docs` recipe that loops over `src/templates/docs/*.md.j2` and `src/templates/plan_templates/*.md.j2`, calling `booping render <template> --output <derived-path>` for each (output paths follow the existing `docs/<name>.md` and `docs/plan_templates/<name>.md` mapping). Verify the regenerated files match current on-disk content (modulo trivial whitespace). | `Justfile`, `booping-python/src/booping/commands/render.py` (no longer touches `bin/booping-build`; that file is deleted in M6.1) | 1 | done |

#### Task 5.1 DoD

- [x] Each `SKILL.md` body is exactly: a single `!`booping render src/templates/skills/<name>.md.j2`` line (plus optional surrounding whitespace).
- [x] Each `SKILL.md` frontmatter retains `name`, `description`, `user-invocable` (where present), `allowed-tools`, `effort`, `model` (where present).
- [x] `allowed-tools` no longer references `booping-extra-instructions`, `booping-lessons`, `booping-project-name`, `booping-plan-templates`, `booping-sprint-threshold`, `booping-agents`, `booping-skills`, `booping-commands`, `booping-workflow`, `booping-debug-mode`, `booping-build`, `booping-plans`. Includes `Bash(booping:*)`.
- [x] Each skill loads cleanly in Claude Code (smoke test: `/<skill> help me with X` triggers, body renders, no shell errors visible).

#### Task 5.2 DoD

- [x] Each `agents/<name>.md` body is the single `!` render line.
- [x] An invocation that delegates to `booping-developer-middle` (or any agent) renders the agent body successfully.

#### Task 5.3 DoD

- [x] `booping render <path> --output <path>` writes rendered output to disk.
- [x] `just build-docs` regenerates `docs/plan_lifecycle_overview.md`, `docs/template_plan_frontmatter.md`, and `docs/plan_templates/*.md` from `src/templates/docs/*.md.j2` and `src/templates/plan_templates/*.md.j2`.
- [x] Re-running `just build-docs` after a clean repo produces no diff against the committed docs (modulo trivial whitespace).
- [x] `bin/booping-build` deletion deferred to M6.1 (single removal pass).

---

### M6: Cleanup — remove redundant scripts and update CLAUDE.md/README — 3 SP | done

**Goal**: every `bin/booping-*` script that's been subsumed by `bin/booping` subcommands or by context loading is deleted. CLAUDE.md and README reflect the new layout. No stale references anywhere in the repo.

**Verify**: `git grep 'booping-extra-instructions\|booping-lessons\|booping-project-name\|booping-plan-templates\|booping-sprint-threshold\|booping-agents\|booping-skills\|booping-commands\|booping-workflow\|booping-debug-mode\|booping-build\|booping-plans'` returns no hits in `bin/`, `src/`, `skills/`, `agents/`, `docs/`, `CLAUDE.md`, `README.md`. Hits in `plans/` and historical `retrospectives/` are acceptable (immutable plan history).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Delete redundant bin scripts: `booping-extra-instructions`, `booping-lessons`, `booping-project-name`, `booping-plan-templates`, `booping-sprint-threshold`, `booping-agents`, `booping-skills`, `booping-commands`, `booping-workflow`, `booping-debug-mode`, `booping-plans` (subsumed by `booping plans`), `booping-build` (replaced by `just build-docs`). Re-verify `.claude-plugin/plugin.json` references no deleted bin paths (clean at draft time per M1.2; this is the cleanup checkpoint). | `bin/booping-*`, `.claude-plugin/plugin.json` | 1 | done |
| 6.2 | Update `CLAUDE.md`: rewrite the `## Layout` section (booping-python/, deleted scripts, hand-authored thin shells); rewrite the `## CLI` section (subcommands of `booping`); update `## Information ownership` (config now also at `~/Claude/{project}/config.yaml`); update `## Adding a new template-driven skill` (steps now include hand-authoring SKILL.md, no booping-build). | `CLAUDE.md` | 1 | done |
| 6.3 | Update `README.md` (Statuses section unchanged; CLI section, Layout/Status section refresh as needed). Audit `src/docs/*.md` for stale `booping-*` references and update. Remove any references to the `Status` block that mention build-time rendering of skills. | `README.md`, `src/docs/*.md` | 1 | done |

#### Task 6.1 DoD

- [x] `ls bin/` shows only `booping`, `booping-create-project`, `booping-external-llm-call`, and the `llm-call-templates/` directory.
- [x] No skill/agent/template/doc references the deleted scripts (verified via `git grep` excluding `plans/` and `retrospectives/`).
- [x] `git grep -F 'booping-' .claude-plugin/plugin.json` returns no hits (re-verification — file unchanged from draft baseline).

#### Task 6.2 DoD

- [x] `CLAUDE.md` `## Layout`, `## CLI`, `## Information ownership`, `## Adding a new template-driven skill` sections updated.
- [x] No mention of "rendering stays build-time for now" or similar (the line at line 46 of current CLAUDE.md).
- [x] New section or line clarifying project-level config at `~/Claude/{project}/config.yaml`.

#### Task 6.3 DoD

- [x] `git grep 'booping-extra-instructions\|booping-lessons\|booping-project-name\|booping-plan-templates\|booping-sprint-threshold\|booping-agents\|booping-skills\|booping-commands\|booping-workflow\|booping-debug-mode' README.md src/docs/` returns no hits.
- [x] Status section of `README.md` reflects post-migration state.

---

### M7: Debug subcommands — 2 SP | pending

**Goal**: `booping debug-context` prints the assembled Context as YAML; `booping debug-template <path>` renders a template with full context and prints to stdout (essentially `booping render <path>` with verbose context dump). Both useful for troubleshooting per-project rendering during development.

**Verify**: `booping debug-context` from inside `/home/anton/Claude/claude-booping/` prints non-empty YAML with all sections. `booping debug-template src/templates/skills/groom.md.j2` prints the rendered body plus a trailing context summary block.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Implement `booping debug-context` (already stubbed in M2; finalize formatting — print Context as readable YAML, sorted keys, lessons/plans summarized to title-only by default with a `--full` flag for full bodies). | `booping-python/src/booping/commands/debug.py` | 1 | pending |
| 7.2 | Implement `booping debug-template <path>`: render the template, print the body, then a `## Debug context` footer summarizing what was loaded (counts: N plans, N lessons, project name/dir, config keys overridden). | `booping-python/src/booping/commands/debug.py` | 1 | pending |

#### Task 7.1 DoD

- [ ] `booping debug-context --help` documents `--full`.
- [ ] Default output is compact (one line per plan/lesson, no full bodies).
- [ ] `--full` includes bodies.

#### Task 7.2 DoD

- [ ] `booping debug-template src/templates/skills/groom.md.j2` exits 0, prints non-empty rendered body and a debug footer.
- [ ] When the template references an undefined variable, the error includes the template path and variable name (Jinja2 StrictUndefined for debug-template; lenient for plain `render` to avoid breaking skill loads).

---

### M8: Final render review — 1 SP | pending

**Goal**: user reviews rendered skill and agent bodies side-by-side with the pre-migration versions (commit before M3 vs current). Any IA issues exposed by the migration are recorded as follow-up items (separate plan), not handled in this sprint.

**Verify**: explicit user sign-off captured in this plan.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Render each skill and agent; produce a side-by-side diff vs the pre-M3 baseline. Walk the user through any non-trivial differences. Capture sign-off. If new follow-up plans are needed, file them as `backlog` stubs in `~/Claude/claude-booping/plans/`. | `~/Claude/claude-booping/plans/*` (any new stubs) | 1 | pending |

#### Task 8.1 DoD

- [ ] Each rendered skill/agent reviewed by user.
- [ ] Sign-off recorded.
- [ ] Follow-up stubs (if any) created with `status: backlog`.

---

## Final Verification

- [ ] All seven skills load in Claude Code with rendered bodies that match (modulo trivial whitespace) the pre-migration outputs unless an intentional improvement is documented.
- [ ] All three agents load in Claude Code with rendered bodies similarly verified.
- [ ] Project config override demo: setting `~/Claude/claude-booping/config.yaml` with `sprint: { default_threshold_sp: 50 }` causes `/groom`'s rendered body to show `Split threshold: 50 SP`. Removing the file restores `35 SP`.
- [ ] No `!`booping-<anything>`` commands remain inside any template or partial under `src/templates/`.
- [ ] No deleted bin script is referenced in `bin/`, `src/`, `skills/`, `agents/`, `docs/`, `CLAUDE.md`, or `README.md`.
- [ ] `cd booping-python && uv run ruff check . && uv run basedpyright && uv run pytest` all pass.
- [ ] No test reads from `~/Claude/` or any path outside `booping-python/tests/__fixtures__/`.
- [ ] `just build-docs` (or whichever surviving recipe) regenerates static docs cleanly.
- [ ] User sign-off on rendered output (M8) captured.

## Out of scope

- `bin/booping-create-project` and `bin/booping-external-llm-call` — kept as-is.
- Migrating `docs/*` and `docs/plan_templates/*` to runtime rendering — they stay statically rendered (lazy-loaded via Read; runtime rendering doesn't apply).
- Global config (e.g. `~/Claude/config.yaml`) — architecture leaves room for it (`Config.load` accepts an ordered override list) but no implementation lands.
- Per-project schema overrides (statuses, transitions, task types, agents) — only verifying `sprint.default_threshold_sp` in this plan; full schema overrides covered by the deep-merge mechanism but not exercised end-to-end.
- Rewriting skill content (prose, phases, craft) — this is a pure infrastructure refactor; skill semantics are unchanged.
- Caching the assembled Context — perf is acceptable un-cached at current vault size.
- Hooks to auto-regenerate `sprints.md` on plan write — separate planned follow-up (already noted in CLAUDE.md).

## CLAUDE.md impact

Sections to update (covered in M6.2):

- `## Status` (current state paragraph at top)
- `## Layout` (booping-python/, hand-authored skills/agents, deleted bin scripts)
- `## CLI` (booping subcommands replace several scripts)
- `## Information ownership` (project config at `~/Claude/{project}/config.yaml`)
- `## Adding a new template-driven skill` (steps now include hand-authoring SKILL.md)
- `## Editing conventions` (no longer "edit src/templates/, run just build" — runtime rendering means edits are live; explain when `just build-docs` is still needed)

## Risk register

- **Skill load latency on the agentic hot path** (Gemini blind spot, accepted): every skill invocation re-runs `uv run` + full `Context.assemble()` (cold-start Python + read all plans/lessons/retros from disk). For Claude Code conversational turns this adds latency on every skill switch. Accepted by user (≤3s budget). Mitigations available if it bites: (a) cache assembled Context per-session via a sidecar process or filesystem mtime check, (b) replace `uv run` with a stable Python interpreter and explicit module load, (c) use `__pycache__` and lazy imports to shorten cold start. **None of these are in scope; the plan ships un-cached and we measure first.** M7's `debug-template` includes a timing line so drift is observable.
- **Hand-authored frontmatter drift**: SKILL.md frontmatter copies `effort` from config manually. If someone edits `src/config.yaml` `skills.<name>.effort` and forgets to update SKILL.md frontmatter, the two diverge silently. Mitigation: low frequency of effort changes; future iteration could add a lint or generator if it bites.
- **`!` command failure leaves skill body empty/garbled**: if `bin/booping render` errors out at skill load, Claude sees the shell error formatting per `executeShellCommandsInPrompt`. Mitigation: M2 wires lenient undefined defaults for the runtime path; M7 debug commands give visibility; tested via M5 smoke tests. Cycle/depth errors raise clearly (T2.6) rather than hanging.
- **`uv run` cold-start latency**: first invocation may pay sync cost. Mitigation: `uv` caches dependencies; subsequent runs in a session are warm. If needed, we can pre-bake a `pyz` or use a faster invocation path — defer until measured.
- **Vault not discoverable from cwd**: addressed in T2.1 by walking up from `Path.cwd()` for `.booping`. Residual risk: invocation from a sibling tree (e.g. cwd is a parent of multiple booping repos) walks up past the intended project. Acceptable — same failure mode as `git`.
