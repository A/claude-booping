---
title: Booperiser CLI foundation — vault resolution, config merge, Jinja render
type: feature
status: cancelled
plan_status: cancelled
sp: 31
split_from: null
created: 2026-08-04 18:27
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Booperiser CLI foundation — project/vault resolution, three-tier config
  merge, Jinja render with an sh filter executing config values as shell commands"
commit: null
sessions:
- 19353202-bcd7-486e-98b9-9125e36b8dad
metrics_active_minutes: 50
metrics_models:
- claude-opus-5
metrics_tokens_input: 301
metrics_tokens_output: 216584
metrics_tokens_cache_creation: 1442456
metrics_tokens_cache_read: 24511939
---

# Booperiser CLI foundation — vault resolution, config merge, Jinja render

## Context

Every runtime surface of the plugin goes through one CLI today, `bin/booping` (uv project at `booping-python/`): plan transitions, sprints rendering, frontmatter mutation, vault commits, build-time file rendering, scaffolding, debug dumps, and playbooks. `Context.assemble()` loads plans, retros, plan templates, review templates, skills, agents, extra instructions, lessons, playbooks and config on every invocation, so rendering anything pays for the entire vault model — including a `validate_skills()` pass unrelated to the render at hand.

This plan lays the foundation of `booperiser`, a second CLI that will eventually replace `booping` for playbooks. It ships the three capabilities everything else sits on and nothing more: project/vault resolution, core → global → project config merge with the merged mapping proxied raw into Jinja, and Jinja rendering — behind the `render` command.

Playbook rendering is deliberately **not** in this plan. It arrives next, piloted against one playbook rather than all seven, and it needs every piece built here before it can start.

After this plan: `bin/booperiser render src/templates/docs/plan_lifecycle_overview.md.j2` produces output byte-identical to `bin/booping render` of the same template, resolving the attached project's vault, merging all three config tiers, and executing config values as shell commands through the `sh` filter. `booping` is untouched — no file of its source, none of its subcommands, none of its templates.

## Decisions

- **`render` and `render-playbook` stay separate commands**: they are different operations sharing only an output medium. A template render takes a path, picks one loader root, renders one file. A playbook render resolves a *name* across three discovery roots with precedence and clash detection, computes a document shape before any text exists (graph parsing, wave levelling, cycle detection, twelve kinds of graph problem), emits that shape through booperiser's own chrome templates with the playbook's files as input data, sub-renders N bodies each under its own loader chain, reports graph problems in-band at exit 0 rather than as errors, and splices in lessons at harness level. Overloading one target to mean either is the `git checkout` mistake — the branch-or-path ambiguity git eventually had to split into `switch` and `restore`. What the two commands genuinely share is three flags and one context-assembly call, which an argparse parent parser and a shared function cover without merging the commands.
- **This plan ships `render` only**: `render-playbook` arrives with the playbook engine, in the follow-up plan. `render` therefore takes a filesystem path — no polymorphic target, no reserved-name form, no disambiguation heuristic.
- **Sibling uv projects, no workspace**: `booperiser-python/` sits beside `booping-python/` with its own lockfile and virtualenv, invoked through a `bin/booperiser` wrapper. A `[tool.uv.workspace]` would force a single shared lockfile, a single shared venv, and one `requires-python` intersection across both members — uv's own docs state workspaces are "not suited for cases in which members have conflicting requirements, or desire a separate virtual environment for each member", which is exactly the independence this replacement needs.
- **No code imported from `booping-python`**: booperiser is a clean-slate parallel implementation. Importing booping's `context` package would reintroduce the coupling the new CLI exists to escape, and would make booping's refactors booperiser's breakage.
- **PyYAML, not ruamel.yaml**: booperiser parses the same config and frontmatter files booping parses. PyYAML follows YAML 1.1; ruamel.yaml defaults to YAML 1.2, where bare `yes`/`no`/`on`/`off` stop being booleans, `0755` stops being octal, and `12:34:56` stops being sexagesimal. Round-trip preservation — ruamel's actual strength — is worthless here because booperiser only reads.
- **argparse, not click/typer/cyclopts**: one subcommand does not justify a dependency. argparse's only friction under basedpyright strict is the known typeshed looseness of `Namespace` and `parse_args()`, worked around with explicit annotations; click and typer carry an open, unresolved strict-mode typing gap on their decorators.
- **Hand-rolled deep merge**: mergedeep has had no release since 2021; deepmerge 2.1.0 is maintained but would need configuring around a single custom rule (the `agents` shallow-merge exception). Roughly twenty lines of recursive merge expresses that rule more clearly than a strategy list does.
- **Raw merged dict as `config`, no typed model**: the merged mapping is injected into Jinja unchanged. No dataclasses, no pydantic, no validation layer. Templates read `config.foo.bar`, which Jinja resolves as `getattr` then `__getitem__`, so ordinary keys work through dot access.
- **Reserved-name guard on config keys**: because Jinja tries `getattr` first, a config key literally named `items`, `keys`, `values`, `get`, `copy`, `update`, `pop`, `setdefault`, `clear` or `popitem` would resolve to the bound dict method and silently render a method repr instead of the data. The config loader rejects such keys at load time with a named error rather than letting the template lie.
- **A `sh` filter replaces the hardcoded `now()` global — and replaces a macro registry too**: `{{ config.macros.now | sh }}` executes whatever the expression evaluates to as a shell command and yields its stripped stdout. Filter arguments become positional shell arguments, so the format string lives in the command (`date +"${1:-%Y%m%d-%H-%M}"`) and never in Python: `{{ config.macros.now | sh("%H:%M") }}`. Because the filter operates on any expression rather than on registered names, there is no registration pass, no per-name globals, and no collision between a macro name and a template variable — config is plain data and `sh` is the only executor.
- **Macros are namespaced by wherever they sit in config**: `config.macros.*` is the core convention, but a playbook may keep its own commands anywhere in the merged tree — `{{ config.playbooks.setup.macros.branch | sh }}` works with no change to the filter. This is why the filter beats a registry: namespacing costs nothing because the executor never learns names.
- **`{{ !expr }}` prefix syntax is rejected**: Jinja has no prefix `!` operator, and adding one means rewriting the expression parser. A `filter_stream` extension could rewrite the tokens, but it breaks every Jinja-aware editor and linter, and `!` is YAML's tag sigil — actively confusing in files carrying YAML frontmatter. The filter form is idiomatic and costs one function.
- **`sh` results cached per command and argument tuple, per process**: one `date` subprocess per render regardless of how many bodies invoke it, and no chance of two calls in one render straddling a minute boundary and disagreeing.
- **Booperiser provides no `now()` global**: `playbooks/groom/playbook.md:16` is the only `now()` call in any playbook, and under `LenientUndefined` it would render empty rather than fail loudly. `setup` — the pilot — does not call it, so nothing breaks here; that body is edited to the filter form before booperiser ever renders groom, and booping keeps its own `now()` meanwhile.
- **`LenientUndefined` semantics retained**: playbook bodies rely on missing config keys degrading to empty rather than raising, and byte-identical output against booping is the acceptance bar. A strict `Undefined` would break both.
- **Booperiser reads its global config tier from `booperiser/config.yaml`, not `booping/config.yaml`**: the two CLIs never contend for one machine-level file during the transition. The cost is duplicating `home_dir` there while both are installed.
- **The context carries only what a render needs**: `project`, `config`, and — once the playbook engine lands — `playbooks`, `targeted_lessons`, `plans`, `plan_templates`. This plan builds the first two. Never loaded: retros, review templates, skills, agents, extra instructions, the legacy untargeted `lessons/` directory, and skill validation.
- **Nothing is removed from `src/templates/`**: the legacy skills keep running on booping and keep every partial they reference. That tree is deleted later in one piece, together with booping.
- **The playbook engine pilots against `setup`**: 2 steps, no `states:`, no subgraph, no core-partial dependencies, a 132-line report. `groom` carries states and the one live `_lessons.j2` dependency; `playbook-authoring` carries 12 steps, a subgraph and states. Piloting on `setup` proves discovery, manifest parsing, waves, `jinja: true` bodies and `inline_steps` without dragging in state machines, subgraphs or the partial-inlining migration. That is the next plan, not this one.

## Architecture

`bin/booperiser` is a four-line shell wrapper resolving the plugin root from its own location and exec'ing `uv run --project "$PLUGIN_ROOT/booperiser-python" booperiser "$@"`, mirroring `bin/booping`. The Python side rediscovers the plugin root independently by walking up for a directory containing both `src/` and `bin/booperiser`, so library-level calls in tests never depend on the wrapper.

Module tree under `booperiser-python/src/booperiser/`:

| Module | Responsibility |
|---|---|
| `cli.py` | argparse parser, the `render` subcommand's argument surface, exit-code mapping |
| `project.py` | `.booping` marker walk, vault resolution ladder, `is_local_vault`, repo HEAD |
| `config.py` | tier loading, deep merge, `--set` parsing, reserved-key guard |
| `shell.py` | the `sh` filter — shell execution of any expression value, with caching |
| `rendering.py` | environment construction, `LenientUndefined`, globals and filter injection |
| `tools.py` | `tools.render` with cycle detection and depth limiting |
| `context.py` | the frozen context dataclass and its assembly |
| `commands/render.py` | target resolution, output routing, error reporting |

Input sources: the plugin's `src/config.yaml` (core tier), `${XDG_CONFIG_HOME:-~/.config}/booperiser/config.yaml` (global tier), `{vault}/config.yaml` (project tier), and the `.booping` marker. Output sinks: stdout, or a file via `--output`. Side effects: shell subprocesses spawned by the `sh` filter, and nothing else — booperiser never writes vault state, never mutates frontmatter, never touches git.

`render` takes a filesystem path. The follow-up plan adds `render-playbook {name}` as a sibling subcommand: the shared flags (`--output`, `--set`) are declared once on an argparse parent parser and the shared context assembly is one function, so adding the second command duplicates neither.

## Milestones

### M1: Project skeleton and vault resolution — 8 SP | pending

**Goal**: `bin/booperiser` runs and resolves the attached project's vault correctly from anywhere in the repo tree.

**Verify**: `bin/booperiser --help` exits 0 listing the `render` subcommand, and `cd booperiser-python && uv run pytest tests/project_test.py` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Scaffold the uv project — pyproject with hatchling and explicit wheel packages, jinja2 and pyyaml deps, dev group, ruff and basedpyright config, argparse skeleton with `render` stubbed | `booperiser-python/pyproject.toml`, `booperiser-python/src/booperiser/cli.py`, `booperiser-python/src/booperiser/__init__.py` | 3 | pending |
| 1.2 | Implement marker walk and vault resolution — `.booping` discovery upward, `vault_path:` absolute / `~` / repo-relative, `home_dir` fallback, `is_local_vault`, repo HEAD | `booperiser-python/src/booperiser/project.py` | 3 | pending |
| 1.3 | Wrapper script, justfile recipes, and test harness with HOME and XDG isolation | `bin/booperiser`, `justfile`, `booperiser-python/tests/conftest.py`, `booperiser-python/tests/project_test.py` | 2 | pending |

#### Task 1.1 DoD

- [ ] `[tool.hatch.build.targets.wheel] packages = ["src/booperiser"]` is declared explicitly — hatchling does not auto-discover a src layout and would otherwise ship a wheel with no package and a broken console script.
- [ ] `[project.scripts] booperiser = "booperiser.cli:main"` is declared.
- [ ] `requires-python = ">=3.12"`; dependencies are jinja2 (`>=3.1.6`) and pyyaml (`>=6.0.3`) only; dev group carries pytest, ruff, basedpyright. No pydantic, no ruamel.yaml, no deep-merge library, no CLI framework.
- [ ] The lockfile resolves under uv 0.12.1 or later and lives at `booperiser-python/uv.lock`, separate from booping's.
- [ ] ruff `line-length = 100` with `select = ["E","F","I","UP"]`; basedpyright `typeCheckingMode = "strict"` over `src` and `tests`.
- [ ] No `[tool.uv.workspace]` is added anywhere in the repo.
- [ ] `booperiser --help` exits 0 and lists `render`.

#### Task 1.2 DoD

- [ ] Resolution walks upward from the start directory to the filesystem root and returns `None` when no `.booping` marker exists.
- [ ] Marker `vault_path:` wins over `home_dir`; absolute paths are used as-is, `~` is expanded, relative paths resolve against the repo directory.
- [ ] With no `vault_path:`, the vault is `{home_dir}/{project_name}` with `home_dir` read from the core plus global merge, never from a hardcoded default.
- [ ] `project_name` defaults to the marker directory's name when the marker declares none.
- [ ] `is_local_vault` is true exactly when the resolved vault lies inside the repo working tree.
- [ ] Repo HEAD resolution returns `None` rather than raising when git is absent or the directory is not a repository.
- [ ] There is one code path reading `home_dir` — booping's split between `load_cwd_configured` and `Context.assemble` reading it twice is not reproduced.

#### Task 1.3 DoD

- [ ] `bin/booperiser` resolves the plugin root from its own location and execs `uv run --project` against `booperiser-python`.
- [ ] `just booperiser-lint`, `just booperiser-typecheck`, `just booperiser-test` all exit 0.
- [ ] An autouse fixture repoints `HOME` and `XDG_CONFIG_HOME` at per-test temporary directories, so no test can read the developer's real config.
- [ ] Tests cover every resolution branch named in task 1.2's DoD.

---

### M2: Config merge, `--set` overrides, and the `sh` filter — 9 SP | pending

**Goal**: the three config tiers merge deterministically, `--set` layers on top, and any config value can be executed as a shell command through the `sh` filter.

**Verify**: `cd booperiser-python && uv run pytest tests/config_test.py tests/shell_test.py` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Tier loading and deep merge — core, global, project; dict recursion, list and scalar replacement, `agents` shallow-merge exception, XDG path resolved at call time | `booperiser-python/src/booperiser/config.py` | 3 | pending |
| 2.2 | `--set` dotted-key parsing layered as the final tier, plus the reserved-key guard | `booperiser-python/src/booperiser/config.py` | 2 | pending |
| 2.3 | The `sh` filter — shell execution of any expression value, positional argument passing, per-process caching | `booperiser-python/src/booperiser/shell.py`, `src/config.yaml` | 4 | pending |

#### Task 2.1 DoD

- [ ] Tier order is core, then global, then project; later tiers win and absent keys fall through.
- [ ] Mappings recurse; lists and scalars are replaced wholesale, never concatenated.
- [ ] A key listed in the shallow-merge set (`agents`) has its direct children overwritten without further recursion.
- [ ] `${XDG_CONFIG_HOME:-~/.config}/booperiser/config.yaml` is resolved at call time, not import time, so tests can repoint it.
- [ ] A missing global or project file is skipped silently; a missing core file is a named error, not a traceback.
- [ ] `home_dir` resolves from the core plus global partial merge only, so setting it in the project tier is a documented no-op.
- [ ] The merged result matches `bin/booping config-get` for `plan.statuses`, `sprint`, `git` and `tasks` on this repo.

#### Task 2.2 DoD

- [ ] `--set a.b.c=value` builds a nested mapping and deep-merges as the final tier, after project.
- [ ] The flag is repeatable and later pairs win.
- [ ] Values remain strings with no type coercion.
- [ ] A pair without `=` writes a message to stderr and exits 1.
- [ ] A config key colliding with a dict method name (`items`, `keys`, `values`, `get`, `copy`, `update`, `pop`, `setdefault`, `clear`, `popitem`) at any depth is rejected at load time, naming the dotted path and the reason.
- [ ] The guard runs against the merged result, so a key introduced by any tier or by `--set` is caught.

#### Task 2.3 DoD

- [ ] `{{ expr | sh }}` runs the string `expr` evaluates to through the shell and returns stdout stripped of trailing whitespace.
- [ ] The filter operates on any expression, not on registered names — `{{ config.macros.now | sh }}` and `{{ config.playbooks.setup.macros.branch | sh }}` both work with no registration step and no code change.
- [ ] Filter arguments are passed as positional shell parameters, so `date +"${1:-%Y%m%d-%H-%M}"` honours both `{{ config.macros.now | sh }}` and `{{ config.macros.now | sh("%H:%M") }}`.
- [ ] Results are cached per command string and argument tuple for the process lifetime; a second identical call spawns no second subprocess.
- [ ] A non-zero exit writes the command, its exit code and its stderr to stderr, then exits 2.
- [ ] Applying `sh` to a value that is not a string — an undefined, a mapping, a list — is a named error naming the expression, not a stringified command.
- [ ] `--set macros.now='echo 19700101-00-00'` pins the value with no pinning-specific code path involved.
- [ ] `src/config.yaml` gains a `macros` block declaring `now` as `date +"${1:-%Y%m%d-%H-%M}"`, and booping ignores the new key.
- [ ] No `now()` global is registered; the only shell path into a template is the filter.

---

### M3: Jinja engine and the `render` command — 10 SP | pending

**Goal**: `bin/booperiser render {template}` renders any template with context, config, tools and macros in scope.

**Verify**: `bin/booperiser render src/templates/docs/plan_lifecycle_overview.md.j2 | diff - <(bin/booping render src/templates/docs/plan_lifecycle_overview.md.j2)` produces no output.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Environment construction — `LenientUndefined`, plugin-root discovery, globals injection, trailing-newline preservation | `booperiser-python/src/booperiser/rendering.py`, `booperiser-python/src/booperiser/context.py` | 4 | pending |
| 3.2 | `tools.render` with cycle detection and depth limit, sharing one environment across nested calls | `booperiser-python/src/booperiser/tools.py` | 3 | pending |
| 3.3 | The `render` command — target resolution, `--output`, `--set`, exit codes | `booperiser-python/src/booperiser/commands/render.py`, `booperiser-python/src/booperiser/cli.py` | 3 | pending |

#### Task 3.1 DoD

- [ ] Missing attributes, subscripts, calls, iteration, and `.get` / `.items` / `.values` / `.keys` on undefined values all degrade silently rather than raising.
- [ ] Plugin-root discovery walks up for a directory holding both `src/` and `bin/booperiser`, bounded in depth, and raises a named error when not found.
- [ ] Every render receives the `context`, `config` and `tools` globals and the `sh` filter.
- [ ] `keep_trailing_newline` is enabled, matching booping's output byte-for-byte.
- [ ] `config` reaches the template as the raw merged dict, not a wrapper.
- [ ] The context dataclass is frozen and carries `project` and `config` only; adding a field is a deliberate edit, not a side effect of a loader.

#### Task 3.2 DoD

- [ ] `tools.render('{path}')` resolves relative to the plugin root and renders through the same environment instance as its caller.
- [ ] A template rendering itself, directly or transitively, raises a named cycle error listing the stack.
- [ ] Nesting beyond ten levels raises a named depth error.
- [ ] Keyword arguments passed to `tools.render` reach the target template.

#### Task 3.3 DoD

- [ ] The target is a filesystem path; a missing file writes a stderr message naming it and exits 1.
- [ ] `--output` and `--set` are declared on an argparse parent parser, so the follow-up plan's `render-playbook` inherits them without redeclaring either.
- [ ] Context assembly is one function the command calls, not logic inlined into the command body.
- [ ] A path under `src/templates/` renders with that directory as loader root so `{% include "_partials/x.j2" %}` resolves.
- [ ] A path elsewhere under the plugin root renders with the plugin root as loader root.
- [ ] A path outside the plugin root renders from its own source text.
- [ ] `--output {path}` writes to that file; `--output -` and the default write to stdout.
- [ ] Exit codes: 0 success, 1 user error, 2 internal error.
- [ ] Diagnostics go to stderr; rendered output goes only to stdout.

---

### M4: Parity verification and documentation — 4 SP | pending

**Goal**: booperiser's render is provably equivalent to booping's on templates within scope, and the CLI is documented.

**Verify**: `just booperiser-parity` exits 0.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Parity harness — a recipe and a test diffing booperiser's render against booping's for every in-scope template | `justfile`, `booperiser-python/tests/parity_test.py` | 2 | pending |
| 4.2 | Documentation — CLI section, layout entry, config schema entry for `macros`, and the scope boundary | `CLAUDE.md` | 2 | pending |

#### Task 4.1 DoD

- [ ] The harness renders each in-scope template with both CLIs and diffs the results.
- [ ] In-scope templates are those whose bodies read only `config`, `context.project` and shell-executed config values — at minimum `src/templates/docs/plan_lifecycle_overview.md.j2`.
- [ ] Templates depending on context fields booperiser does not yet load are listed explicitly in the harness as skipped, each with the field naming why — no silent omission.
- [ ] Booping is invoked with `--set now=...` and booperiser with `--set macros.now='echo ...'`, so both sides are pinned and the diff is stable across runs.
- [ ] The recipe exits non-zero on the first mismatch and names the template.
- [ ] A pytest case runs the same comparison, so parity breaks fail the test suite and not only the recipe.

#### Task 4.2 DoD

- [ ] `CLAUDE.md`'s `## CLI` section documents `bin/booperiser render` with its full flag surface, alongside the existing `bin/booping` entries.
- [ ] The `## Layout` section gains a `booperiser-python/` entry stating the scope boundary — playbooks only, no code shared with booping, own lockfile and virtualenv, no uv workspace.
- [ ] The `## Config schema` section documents the `sh` filter — shell execution of any config value, positional argument passing, per-process caching, free namespacing, and the `--set macros.now='echo ...'` pinning idiom — plus the `macros` block as the core convention rather than a special key.
- [ ] It is recorded that booperiser registers no `now()` global and that `groom/playbook.md` must move to the filter form before booperiser renders it.
- [ ] No claim is made that booperiser renders playbooks.

---

## I/O contract

**Arguments and flags**

- `booperiser render {template-path} [--output {path}] [--set {key}={value}]` — render one template with full context. `--set` deep-merges a dotted key into `config` as the final tier, repeatable, later pairs win, values stay strings.

`render-playbook {name}` is the sibling command the follow-up plan adds; `--output` and `--set` are declared on a shared parent parser so it inherits them unchanged.

**stdin**: not read.

**stdout**: the rendered template, and nothing else. `--output {path}` redirects it to a file; `--output -` is explicit stdout.

**stderr**: diagnostics only — missing template, malformed `--set`, reserved config key, `sh` applied to a non-string, shell command failure. Never duplicated on stdout.

**Exit codes**: `0` success; `1` user error — missing template, malformed `--set`, reserved config key collision, `sh` on a non-string value; `2` internal error — shell command failure, unreadable core config, filesystem failure mid-write.

## Final Verification

- [ ] `booperiser --help` and `booperiser render --help` reflect the documented surface.
- [ ] Happy path verified: `just booperiser-parity` exits 0.
- [ ] Failure paths verified: missing template, malformed `--set`, reserved config key, `sh` on a non-string value, failing shell command — each with its documented exit code and a stderr message.
- [ ] `just booperiser-lint`, `just booperiser-typecheck`, `just booperiser-test` all exit 0.
- [ ] `just lint`, `just typecheck`, `just test` still exit 0 for booping.
- [ ] `just build` and `just playbook-reports` still exit 0 and leave the tree clean — this plan touches neither.
- [ ] `git diff -- booping-python/ skills/ agents/ playbooks/` is empty; the only booping-side change is the additive `macros` block in `src/config.yaml`.

## Out of scope

- The `render-playbook` command and everything behind it: discovery, manifest parsing, graph and wave resolution, subgraphs, state machines, notices, lesson injection, composed output, `--step`. That is the next plan, piloted on `setup`.
- Editing `playbooks/groom/playbook.md`'s `now("%Y%m%d-%H-%M")` call into the filter form. It only matters once booperiser renders groom, which this plan does not do.
- Every booping subcommand other than rendering: `playbook-state`, `playbook-transition`, `transition`, `render-sprints`, `frontmatter-update`, `vault-commit`, `scaffold`, `build`, `config-get`, `debug-context`, `debug-template`.
- Retiring, deprecating or modifying `booping`. It keeps every subcommand and stays the reference implementation.
- Migrating skills or agents to booperiser. Every skill keeps running on booping unchanged.
- Removing anything from `src/templates/`. No partial is deleted, moved or edited; the tree is removed later in one piece, together with booping.
- Inlining the three core partials that playbook bodies still pull. That belongs to the playbook-engine plan, and the `setup` pilot needs none of them.
- Plans, retros, plan templates, review templates, skills, agents, extra instructions and lessons in booperiser's context. The playbook engine adds `plans` and `plan_templates` when playbook bodies need them.
- Windows and macOS-native config paths. XDG resolution is the POSIX form; platformdirs is not adopted.
- Any `[tool.uv.workspace]` adoption.

## CLAUDE.md impact

All updates land in task 4.2. The `## CLI` section gains `bin/booperiser render` with its flag surface, noting `render-playbook` as the planned sibling command. The `## Layout` section gains a `booperiser-python/` entry naming the scope boundary — playbooks only, no code shared with booping, own lockfile and virtualenv, no uv workspace — and stating that playbook rendering is not implemented yet. The `## Config schema` section gains the `sh` filter: shell execution of any config value, positional arguments, per-process caching, namespacing anywhere in the merged tree, the `macros` block as convention rather than special key, and the pinning idiom. It also records that booperiser registers no `now()` global. Nothing in the existing booping documentation is invalidated: no partial moves, no playbook body changes, no skill changes, and `src/config.yaml` gains one additive `macros` block that booping ignores.
