---
status: done
title: Frontmatter query — a query surface replacing context.plans and 
  render-sprints
type: feature
plan_status: ready-for-dev
sp: 32
split_from: null
created: 2026-08-05 12:35
planned: null
started: 20260805 06:27
completed: null
retro: null
goal: null
summary: "Generic frontmatter query (CLI + Jinja) addressed by dotted config path,
  replacing context.plans, the Plan model and every sprints.md renderer"
commit: ab5fb376ff348dffd45aef634eefa36d0f8bdb7a
reviewed_at: 20260805 06:26
sessions:
- 4f9347cd-ac7f-4d3f-9b44-ef4e280bd7ed
- a269e5e5-f1ac-4c6c-860b-e3d79d6ccac2
metrics_active_minutes: 169
metrics_models:
- claude-opus-5
metrics_tokens_input: 1634
metrics_tokens_output: 419560
metrics_tokens_cache_creation: 3452665
metrics_tokens_cache_read: 79755924
---

# Frontmatter query — a query surface replacing context.plans and render-sprints

## Context

Listing markdown files by frontmatter is implemented five times in this repo. `Context.assemble()` eagerly loads and parses every plan in the vault on every render (`booping-python/src/booping/context/__init__.py:81`), producing typed `Plan` objects that five template sites filter with `selectattr`. `commands/render_sprints.py` renders one fixed table from that same data, and `commands/transition.py:140-169` renders it a second time inline as a `plan.hooks.post` dispatch. The three playbook hook scripts each hand-roll frontmatter parsing plus markdown-table emission in standalone stdlib Python, because they are contractually forbidden from importing or shelling into `booping`. Those three copies have already drifted: `playbooks/retro/_scripts/close-working-set` and its `learn` twin prefer `index.md` over `plan.md` on a directory carrying both, while `playbooks/groom/_scripts/_plan_status.py` and `Plan.load_all` prefer `plan.md`; the Jinja template escapes 3 of 9 columns while all three scripts escape 9 of 9.

A playbook author who wants a listing the core did not anticipate has no surface at all. `context.plans` is fixed in shape, scope and type, and nothing exposes any other directory of markdown.

After this plan: one loader serves every case through three faces — `booping query` for scripts and debugging, a `query` filter for template bodies, and query specs declared in config under whatever dotted path their consumer owns. `sprints.md` stops being rendered by anything: `vault.scaffold` seeds it once with an Obsidian Bases fence and Obsidian evaluates it live. `context.plans`, the `Plan` model, `render_sprints.py`, `sprints.md.j2`, the inline renderer in `transition.py`, and the `render_sprints()` function in all three hook scripts are deleted. A `macro()` global replaces the `now()` global with config-declared argv lists.

This is one step of a stated direction: core becomes a glue layer that serves user-authored and core playbooks through the same generic surfaces, owning no domain model of its own.

## Decisions

- **Queries are addressed by dotted config path** — `booping query --config develop.developable_plans`, `{{ 'develop.developable_plans' | query }}`. The value at the addressed path *is* the spec, with no wrapper key, matching what `booping config-get {dotted.key}` and `booping scaffold {dotted.path} {dest}` already do. A query therefore lives beside its consumer rather than in a central registry, and rides the core to global to project merge like any other config value.
- **Resolution reuses `scaffold`'s implementation, not `config-get`'s** — `context/scaffold.py:181-207` raises a `ScaffoldError` naming the first non-resolving segment and separately enforces value shape; `commands/config_get.py:26-35` returns a bare sentinel with no shape check. A query spec must be a mapping with a usable `glob`, so the shape-checking resolver is the one worth generalising. The dotted-path walk moves to a shared helper both callers use.
- **The query returns rows, never markdown** — table emission is a separate output mode (`--output table`) and a separate filter (`| as_table`). A caller that gets a pre-rendered table cannot narrow a preset before rendering, which would push every "the queue minus the one I already picked" case straight back to raw globbing.
- **Rows are attribute-accessible objects, not raw dicts** — Jinja resolves `foo.bar` as `getattr` before `__getitem__` (verified against the pinned Jinja 3.1.6 source), so a plain dict with a `status` key is fine but a dict with an `items`, `keys`, `values` or `get` key silently renders a bound-method repr. Frontmatter keys are author-controlled, so plain dicts arm that trap for every playbook author. Each row is wrapped in a small object exposing its keys as attributes, recursively for nested mappings. This is the seam a later config-declared per-file-type schema (pydantic models) slots into without changing any call site.
- **Plan-shape precedence becomes user-owned config, not engine logic** — `plans.glob` is an ordered list (`['plans/*/index.md', 'plans/*/plan.md', 'plans/*.md']`); the first glob to claim a slug wins and later claims on the same slug are skipped. `Plan.load_all`'s bespoke `plan.md`-over-`index.md` rule and directory-shadows-flat rule are expressed as list order instead of hidden precedence. A vault with legacy flat plans edits one key.
- **Slug identity is the match's directory name when the file is an index of a directory, else its stem** — needed for de-duplication across globs. This preserves the one piece of `Plan.load_all` semantics the ordered list cannot express on its own.
- **Malformed frontmatter is skipped with a stderr warning, never fatal** — inherited from `Plan.load_all:72-81` deliberately. A single unparseable file must not break a render of an unrelated body.
- **Results are explicitly sorted before any user sort applies** — `Path.glob` documents no ordering ("The paths are returned in no particular order"), so byte-reproducible playbook reports require a deterministic base order (by slug) regardless of filesystem.
- **`--where` uses a fixed operator vocabulary, not an expression language** — `k=v`, `k!=v`, `k:in=a,b`. Hugo's `where` settled on a fixed token set (`eq` / `ne` / `in` / `gt` / `lt`) and Jekyll on equality alone; Dataview is the outlier with full boolean expressions, and it needs a parser and a grammar to document. The vocabulary can grow later; it cannot shrink.
- **`--where` gets its own parser** — `utils.parse_set_overrides` splits on the first `=` and builds nesting, with no operator concept. `--where` is `action="append"` collecting raw `K=V` strings that a dedicated parser turns into filter triples.
- **`sprints.md` becomes an Obsidian Bases fence, seeded once by `vault.scaffold`** — a ```base block embedded in the note, carrying `filters:` and a `views:` table with `order:` and `sort:`, per the reference at `~/Dev/@A/notes/journal/VAULT_STATE.md`. Nothing writes the file again. It is a purely human-facing artifact: no skill, playbook body or command parses its content today. Obsidian evaluates the view live, so it is never stale, and the three hook scripts lose their renderers entirely rather than gaining a shared one. **Bases over Dataview**: Bases is a core plugin, so a fresh vault renders the view with nothing installed, and the fence stays plain markdown rather than becoming a separate Obsidian-specific `.base` file. Accepted cost: outside Obsidian the file is an inert code block (the machine-facing need is what `booping query` exists for), and vault git history stops carrying a materialised snapshot of plan state per commit.
- **The hook scripts stay self-contained** — each states verbatim in its docstring that nothing shells back into `booping` and nothing outside the standard library is imported, which is what lets a vault run without a `.booping` marker. They lose `render_sprints()` and `discover_plans()` outright; no shared library is introduced and no script gains a `booping` dependency.
- **`macro()` takes argv lists, never shell strings** — `subprocess.run(argv, capture_output=True, text=True, check=True)` with `shell=False` (the default) performs no shell interpretation, so a template-supplied argument cannot inject. The superseded booperiser plan's `sh` filter executed shell strings with `$1` positional substitution; that mechanism is deliberately not carried over.
- **`macro()` replaces the `now()` global** — `config.macros.now: ["date", "+%Y%m%d-%H-%M"]`. One call site exists in the whole tree (`playbooks/groom/playbook.md:16`).
- **Macro results are cached per argv tuple, per process** — one `date` subprocess per render however many bodies ask, and no two calls in one render straddling a minute boundary. `functools` documentation explicitly warns against caching impure calls, so this is a stated assumption: a macro is expected to be idempotent within one render, and a macro that is not must not be declared.
- **Report reproducibility moves from `--set now=` to `--stub-macro`** — `--stub-macro {dotted.path}={literal}` (repeatable) makes a macro return the literal without executing. `just playbook-reports` uses `--stub-macro macros.now=19700101-00-00`. This generalises past time to any macro a body calls.
- **The dead sprints hook is removed here, not deferred** — with nothing rendering `sprints.md`, `transition.py:140-169`, its dispatch at `transition.py:255-257`, and the `render-sprints` entry in `src/config.yaml` `plan.hooks.post` all render a file no writer produces. This touches the plan state machine's config but does not depend on the separate sprint that removes it.
- **`DIR_PLAN_NAMES` moves to `utils.py`** — `commands/vault_commit.py:9` imports the constant (not the `Plan` class) to decide directory-vs-file addressing in commit messages, and still needs it after `plan.py` is deleted.
- **Macros stay core-tier and global-tier only for now** — a project-tier config can arrive with a `git clone` of a repo carrying a local vault, and macro execution happens during rendering, inside the already-approved `Bash(booping:*)` allowance, with no second permission decision. Project-tier macros are ignored with a stderr warning until an explicit opt-in exists.
- **No reserved-key guard on `config` itself** — `rendering.py:140` injects the merged config raw, so a config key named `items` has the same collision hazard rows do. It is pre-existing, hand-authored config is a controlled surface, and fixing it means changing `foo.bar` semantics for every existing body. Recorded as a known risk, not addressed.

## Architecture

One loader, three faces, no duplicated traversal.

```
                      booping-python/src/booping/query.py
                      +----------------------------------+
   config spec ------>| resolve_spec  (dotted path)      |
   ad-hoc flags ----->| run(spec) -> list[Row]           |<-- context/_yaml.py
                      |   glob -> dedupe by slug -> parse|    (parse_frontmatter)
                      |   -> filter -> sort -> project   |
                      +------+--------------------+------+
                             |                    |
                 commands/query.py            rendering.py
                 (table|json|yaml|paths)      (query filter, as_table filter,
                                               macro global)
```

**New module** `booping-python/src/booping/query.py` — spec resolution, glob and slug de-duplication, frontmatter reading via the existing authoritative `context/_yaml.py:54` `parse_frontmatter`, filtering, sorting, column projection, and the `Row` wrapper type. Pure logic: no argparse, no Jinja, no I/O beyond reading the matched files.

**New module** `booping-python/src/booping/macros.py` — argv resolution from a dotted config path, `subprocess.run` execution, per-process cache keyed by the argv tuple, and stub injection.

**New command** `booping-python/src/booping/commands/query.py` — argparse surface, output formatting, exit-code mapping. A thin shell over `query.py`.

**Shared helper** — the dotted-path walk currently duplicated in `context/scaffold.py:181-207` and `commands/config_get.py:26-35` moves into one function both call, plus `query.py`.

**Deleted**: `booping-python/src/booping/context/plan.py`, `booping-python/src/booping/commands/render_sprints.py`, `src/templates/sprints.md.j2`, `Context.plans`, `rendering.py`'s `make_now` and `now` global, `transition.py`'s `_dispatch_render_sprints`, and `render_sprints()` / `discover_plans()` in all three hook scripts.

**Input sources**: markdown files matched by a spec's `glob`, resolved relative to the vault; the merged config for spec and macro lookup. **Output sinks**: stdout (`table`, `json`, `yaml`, `paths`), or a template body via the filter. **Side effects**: macro subprocesses only — `query` itself never writes.

## Milestones

### M1: Query engine and shared dotted-path resolution — 5 SP | done

**Goal**: `query.run()` turns a spec into ordered, filtered rows against a fixture vault, and one dotted-path resolver serves scaffold, config-get and query.

**Verify**: `cd booping-python && uv run pytest tests/query_test.py tests/context/scaffold_test.py tests/commands/config_get_test.py -q` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Extract the dotted-path walk from `scaffold.resolve` into a shared `resolve_path(config, dotted)` raising a path-carrying error; repoint `scaffold.py` and `config_get.py` at it, preserving each command's existing stderr text and exit codes | `booping-python/src/booping/context/scaffold.py`, `booping-python/src/booping/commands/config_get.py`, `booping-python/src/booping/utils.py`, `booping-python/tests/context/scaffold_test.py`, `booping-python/tests/commands/config_get_test.py` | 2 | done |
| 1.2 | `query.py`: spec model (`glob`, `where`, `sort`, `columns`), ordered-glob discovery with slug de-duplication, frontmatter read via `parse_frontmatter`, malformed-file skip with stderr warning, deterministic base sort by slug | `booping-python/src/booping/query.py`, `booping-python/tests/query_test.py` | 3 | done |

#### Task 1.1 DoD

- [x] `resolve_path(config, "a.b.c")` returns the value; a missing segment raises an error naming that segment and the walked prefix.
- [x] `booping config-get nope.key` still prints `error: key not found: nope.key` to stderr and exits 1.
- [x] `booping scaffold nope.tree /tmp/x` still exits 1 with its existing wrong-shape message.
- [x] No behaviour change in either command's stdout.

#### Task 1.2 DoD

- [x] A spec with `glob: ['plans/*/index.md', 'plans/*.md']` over a fixture vault returns one row per slug, the earlier glob winning on collision.
- [x] A slug is the parent directory name for a directory match and the file stem for a flat match.
- [x] A file with unparseable frontmatter is skipped, a warning naming it goes to stderr, and the remaining rows are returned.
- [x] Rows come back sorted by slug when no `sort` is given, on a fixture whose filesystem order differs.

---

### M2: Filtering, sorting, projection and the Row wrapper — 4 SP | done

**Goal**: specs filter and sort rows, and a row exposes its frontmatter keys as attributes without dict-method collisions.

**Verify**: `cd booping-python && uv run pytest tests/query_test.py -q` passes, including a row whose frontmatter carries an `items` key.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `where` evaluation for `=`, `!=`, `in`; `sort` by field with `-` prefix for descending, missing values ordered last; `columns` projection preserving declared order | `booping-python/src/booping/query.py`, `booping-python/tests/query_test.py` | 2 | done |
| 2.2 | `Row` wrapper: attribute access over frontmatter keys, recursive for nested mappings, `path` and `slug` always present, underlying mapping reachable for serialization | `booping-python/src/booping/query.py`, `booping-python/tests/query_test.py` | 2 | done |

#### Task 2.1 DoD

- [x] `where: {status: ready-for-dev}` returns only matching rows.
- [x] `k!=v` and `k:in=[a, b]` each filter as specified, and a row missing the key is excluded by all three operators.
- [x] `sort: -created` orders descending with rows lacking `created` last.
- [x] `columns: [status, title]` yields rows carrying exactly those keys plus `path` and `slug`.

#### Task 2.2 DoD

- [x] `row.status` returns the frontmatter value.
- [x] A row whose frontmatter has an `items` key returns that value from `row.items`, not a bound method.
- [x] A nested mapping is itself attribute-accessible one level down.
- [x] `row.absent` renders empty under `LenientUndefined` rather than raising.

---

### M3: `booping query` command — 5 SP | done

**Goal**: the command runs both addressing forms and emits all four output formats with a documented exit-code contract.

**Verify**: `bin/booping query --glob 'plans/*/index.md' --where status=ready-for-dev --output json | jq -e 'type == "array"'` exits 0, and `cd booping-python && uv run pytest tests/commands/query_test.py -q` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | argparse surface: `--config`, `--glob` (repeatable), `--where` (repeatable, `action="append"`), `--sort`, `--columns`, `--output`, `--project`; the `--where` parser for the three operators; mutual-exclusion and exit-1 errors | `booping-python/src/booping/commands/query.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/commands/query_test.py` | 3 | done |
| 3.2 | Output writers: `table` (GFM, `\|` escaping per cell, newlines collapsed to spaces), `json`, `yaml`, `paths` | `booping-python/src/booping/commands/query.py`, `booping-python/tests/commands/query_test.py` | 2 | done |

#### Task 3.1 DoD

- [x] `booping query --config a.b.c` resolves the spec and runs it.
- [x] `booping query --glob 'x/*.md' --where status=done --sort -created` runs without a config entry.
- [x] `--where` given twice applies both filters.
- [x] A malformed `--where` pair, an unknown `--config` path, and a value at that path that is not a mapping each print a distinct stderr message and exit 1.
- [x] `booping query --help` lists every flag above.

#### Task 3.2 DoD

- [x] `--output table` emits a GFM table whose cells escape `|` as `\|` and contain no raw newline.
- [x] `--output json` emits an array of objects parseable by `jq`.
- [x] `--output yaml` round-trips through `yaml.safe_load`.
- [x] `--output paths` emits one vault-relative path per line and nothing else.
- [x] Diagnostics go to stderr on every format; stdout carries only the payload.

---

### M4: Jinja surface — `query` and `as_table` filters — 4 SP | done

**Goal**: template bodies query without `context.plans`, and inline arguments narrow a config-declared spec.

**Verify**: `bin/booping render-playbook retro --project playbooks/_fixtures/vault` renders its candidate table from the query surface, and `cd booping-python && uv run pytest tests/templates/query_filter_test.py -q` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Register a `@pass_context` `query` filter and an `as_table` filter in `_build_env` and `build_source_env`; inline kwargs deep-merge over the resolved spec | `booping-python/src/booping/rendering.py`, `booping-python/tests/templates/query_filter_test.py` | 2 | done |
| 4.2 | Declare the core query specs in config (`plans.glob` default plus the specs the five consumer sites need) and document the spec schema | `src/config.yaml`, `booping-python/tests/context/config_test.py` | 2 | done |

#### Task 4.1 DoD

- [x] `{{ 'plans.all' | query }}` returns rows inside a skill body, a playbook body and a scaffold seed string.
- [x] `{{ 'plans.all' | query(where={'status': 'done'}) }}` narrows the declared spec without mutating it for later calls in the same render.
- [x] `{{ rows | as_table(columns=['status','title']) }}` emits a GFM table identical to the command's `--output table` for the same rows.
- [x] A filter call naming an unresolvable path raises a render error naming the path, not a silent empty result.

#### Task 4.2 DoD

- [x] `plans.glob` is an ordered list and a query spec omitting `glob` falls back to it.
- [x] Each of the five consumer sites has a named spec resolvable by dotted path.
- [x] `booping config-get plans.glob` prints the list.

---

### M5: Cut over the five consumers and delete the plan model — 5 SP | done

**Goal**: nothing reads `context.plans`; the `Plan` model and its module are gone.

**Verify**: `rg 'context\.plans|from booping\.context\.plan' --glob '!_reports' -n` returns nothing, and `just test && just playbook-reports && git diff --exit-code -- playbooks/*/_reports/` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Rewrite the five template sites onto the query filter | `src/templates/skills/code-review.md.j2`, `playbooks/code-review/scope/opus-5.md`, `playbooks/retro/playbook.md`, `playbooks/learn/playbook.md`, `playbooks/groom/intake/fable-5.md` | 2 | done |
| 5.2 | Delete `context/plan.py`, `Context.plans` and its assembly; move `DIR_PLAN_NAMES` to `utils.py` and repoint `vault_commit.py`; delete `tests/context/plan_test.py`, fix `assemble_test.py` | `booping-python/src/booping/context/plan.py`, `booping-python/src/booping/context/__init__.py`, `booping-python/src/booping/utils.py`, `booping-python/src/booping/commands/vault_commit.py`, `booping-python/tests/context/plan_test.py`, `booping-python/tests/context/assemble_test.py` | 3 | done |

#### Task 5.1 DoD

- [x] The fixture vault used for verification carries at least one plan at each status the five specs filter on (`awaiting-retro`, `awaiting-learning`, `ready-for-dev`, `awaiting-plan-review`, `in-progress`), and every plan in it carries every key the five sites render (`status`, `sp`, `title`, `summary`, `created`, `completed`, `commit`), including at least one plan with a null `sp` and a null `created`.
- [x] Each rewritten body renders the same columns it rendered before, verified against that fixture by diffing its render against the pre-change render.
- [x] `just playbook-reports` leaves `playbooks/*/_reports/` byte-identical to the committed copies, or the diff is reviewed and committed deliberately.
- [x] No body references `context.plans`.

#### Task 5.2 DoD

- [x] `booping-python/src/booping/context/plan.py` no longer exists.
- [x] `Context` has no `plans` attribute and `Context.assemble` does not load plans on either branch.
- [x] `booping vault-commit awaiting-retro {plan}` still writes a commit message addressing a directory plan by slug.
- [x] `just test`, `just lint` and `just typecheck` pass.

---

### M6: `macro()` replaces `now()` — 4 SP | done

**Goal**: config-declared argv macros run from templates, `now()` is gone, and playbook reports stay byte-reproducible.

**Verify**: `just playbook-reports && git diff --exit-code -- playbooks/*/_reports/` passes, run twice at different wall-clock minutes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | `macros.py`: dotted-path argv resolution, `subprocess.run` with `shell=False`, per-argv-tuple process cache, `CalledProcessError` and `FileNotFoundError` mapped to distinct render errors, project-tier macros ignored with a stderr warning | `booping-python/src/booping/macros.py`, `booping-python/tests/macros_test.py` | 2 | done |
| 6.2 | Register the `macro` global in both envs; add `--stub-macro` to `render`, `render-playbook` and `scaffold`; delete `make_now` and the `now` global; migrate `playbooks/groom/playbook.md`; point `just playbook-reports` at `--stub-macro` | `booping-python/src/booping/rendering.py`, `booping-python/src/booping/commands/render.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/commands/scaffold.py`, `src/config.yaml`, `playbooks/groom/playbook.md`, `Justfile` | 2 | done |

#### Task 6.1 DoD

- [x] `macro('macros.now')` returns the subprocess stdout, stripped.
- [x] Two calls to the same macro in one render spawn one subprocess.
- [x] A macro whose command exits non-zero fails the render with a message naming the macro path and the exit code.
- [x] A macro naming a missing executable fails with a distinct message.
- [x] A macro declared only in the project tier is ignored and warned about on stderr.

#### Task 6.2 DoD

- [x] `{{ macro('macros.now') }}` renders a timestamp in a playbook body.
- [x] `--stub-macro macros.now=19700101-00-00` makes that call return the literal without spawning a subprocess.
- [x] `rg 'make_now' booping-python/src` returns nothing.
- [x] `playbooks/groom/playbook.md` renders its plan-directory stamp through `macro`.

---

### M7: Retire every sprints.md renderer and its documentation — 5 SP | done

**Goal**: `sprints.md` is seeded once as an Obsidian Bases fence and written by nothing thereafter.

**Verify**: `rg 'render_sprints|render-sprints|sprints\.md\.j2' --glob '!_reports' -n` returns only documentation prose, and `bin/booping scaffold vault.scaffold /tmp/v && grep -q '```base' /tmp/v/sprints.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Seed `sprints.md` in `vault.scaffold` with an Obsidian Bases fence scoped to `plans/`, one table view ordered by status, sp, title, summary, created and completed, sorted by created descending | `src/config.yaml`, `booping-python/tests/commands/scaffold_test.py` | 1 | done |
| 7.2 | Delete `commands/render_sprints.py`, its cli registration, `src/templates/sprints.md.j2`, `tests/commands/render_sprints_test.py`, `transition.py`'s `_dispatch_render_sprints` and its hook dispatch, and the `render-sprints` entry in `plan.hooks.post` | `booping-python/src/booping/commands/render_sprints.py`, `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/transition.py`, `src/templates/sprints.md.j2`, `src/config.yaml`, `booping-python/tests/commands/render_sprints_test.py`, `booping-python/tests/context/lifecycle_test.py`, `booping-python/tests/__fixtures__/on_exit_equivalence.yaml` | 2 | done |
| 7.3 | Strip `render_sprints()` and `discover_plans()` from the three hook scripts, leaving their remaining work and their self-contained contract intact | `playbooks/groom/_scripts/_plan_status.py`, `playbooks/retro/_scripts/close-working-set`, `playbooks/learn/_scripts/close-working-set` | 1 | done |
| 7.4 | Apply every documentation change this sprint implies: the five `CLAUDE.md` sections named below, plus the `documentation/` and `docs/` pages that describe `sprints.md` as a rendered artifact or name `render-sprints` | `CLAUDE.md`, `documentation/vault.md`, `documentation/project_config.md`, `documentation/quick_start.md`, `docs/template_plan_frontmatter.md`, `playbooks/_partials/plan_frontmatter.md`, `playbooks/retro/save/base.md`, `playbooks/learn/transition/base.md`, `src/templates/_partials/_plan_transitions.j2` | 1 | done |

#### Task 7.1 DoD

- [x] `bin/booping scaffold vault.scaffold {dir}` writes a `sprints.md` containing a `base` fence whose YAML parses.
- [x] The view is scoped to the vault's `plans/` folder and orders status, sp, title, summary, created and completed, sorted by created descending.
- [x] The folder-scoping filter expression is confirmed against current Obsidian Bases documentation before it is committed — `~/Dev/@A/notes/journal/VAULT_STATE.md` is the syntax reference for the fence shape, but it filters on a property, not a folder.
- [x] The seeded file renders as a table in Obsidian with no community plugin installed.
- [x] Scaffolding into a non-empty directory still aborts without `--force`.

#### Task 7.2 DoD

- [x] `bin/booping render-sprints` exits with argparse's unknown-command error.
- [x] `bin/booping transition` completes a move without attempting to render `sprints.md`, and its mutation report no longer carries a `render-sprints` line.
- [x] `just test` passes with the lifecycle fixture updated to the shortened post-hook list.

#### Task 7.3 DoD

- [x] Each script still performs its remaining mutations and exits 0 on a fixture workdir.
- [x] No script imports anything outside the standard library, and none references `sprints.md`.
- [x] `bin/booping playbook-transition retro awaiting-learning` still closes a working set.

#### Task 7.4 DoD

- [x] `CLAUDE.md` names `booping query` in `## CLI`, no longer names `booping render-sprints` anywhere, documents the query spec shape, `plans.glob` and `macros.*` in `## Config schema`, drops `render-sprints` from the `plan.hooks.post` vocabulary, and describes `sprints.md` as a seeded Obsidian Bases view in both `## Plan lifecycle` and `## Project vault layout`.
- [x] `rg 'render-sprints|render_sprints' CLAUDE.md documentation/ docs/ src/templates/ playbooks/ --glob '!_reports'` returns nothing.
- [x] Every remaining prose reference to `sprints.md` describes it as a live query, not a regenerated snapshot.
- [x] `just docs` builds clean under `--strict`.

---

## I/O contract

**Arguments / flags** — `booping query [--config DOTTED.PATH] [--glob PATTERN]... [--where K=V]... [--sort FIELD] [--columns A,B] [--output FORMAT] [--project PATH]`

- `--config` — dotted path into merged config whose value is the spec. Mutually exclusive with `--glob`.
- `--glob` — repeatable, ordered; the first glob claiming a slug wins.
- `--where` — repeatable; `k=v`, `k!=v`, `k:in=a,b`.
- `--sort` — field name, `-` prefix for descending. Absent means slug order.
- `--columns` — comma-separated projection, declared order preserved.
- `--output` — `table` (default), `json`, `yaml`, `paths`.
- `--project` — resolve against this vault instead of the attached project.
- `--stub-macro` — on `render`, `render-playbook` and `scaffold`: `DOTTED.PATH=LITERAL`, repeatable.

**stdin**: not read. **stdout**: the payload only, in the selected format. **stderr**: skipped-file warnings, ignored-project-tier-macro warnings, and errors.

**Exit codes**: `0` success, including zero matching rows (an empty table, `[]`, or nothing for `paths`); `1` user error — malformed `--where`, unknown `--config` path, non-mapping value at that path, both or neither of `--config` and `--glob`, unknown `--output`; `2` internal error — unreadable vault, `OSError` during traversal.

## Final Verification

- [ ] `just lint`, `just typecheck`, `just test` all pass.
- [ ] `just build` leaves `skills/` and `agents/` byte-identical.
- [ ] `just playbook-reports` run twice at different minutes leaves `playbooks/*/_reports/` byte-identical both times.
- [ ] `bin/booping query --help` reflects every flag in the I/O contract.
- [ ] Happy path and each exit-1 failure mode verified by invocation.
- [ ] `rg 'context\.plans|Plan\.load_all|render_sprints' --glob '!_reports' -n` returns nothing.
- [ ] No documentation, partial or playbook body describes `sprints.md` as a rendered or regenerated artifact.

## Out of scope

- The plan lifecycle state machine, `booping transition`, `vault-commit`, and dropping the `chat` and `help` skills — a separate sprint. Only the dead `render-sprints` post-hook is touched here.
- Project-tier macros and any opt-in mechanism for them.
- A reserved-key guard on the raw `config` mapping.
- Config-declared per-file-type schemas turning rows into pydantic models — the `Row` wrapper is the seam, the schemas come later.
- Migrating existing vaults' plan shapes; `plans.glob` covers all three shapes as shipped.
- `--where` operators beyond `=`, `!=`, `in`.

## CLAUDE.md impact

- `## CLI` — add `booping query`; remove `booping render-sprints`; note `--stub-macro` on `render`, `render-playbook` and `scaffold`.
- `## Config schema` — add the query spec shape, `plans.glob`, and `macros.*`; remove the `render-sprints` hook from the documented `plan.hooks.post` vocabulary.
- `## Plan lifecycle` — the `sprints.md` snapshot paragraph is replaced by the Bases-view description.
- `## Project vault layout` — `sprints.md` is a seeded Obsidian Bases view, not a rendered artifact.
- `## Layout` — `src/templates/sprints.md.j2` removed; `query.py` and `macros.py` added.
