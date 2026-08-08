---
title: src/files build pipeline for skills and agents
type: refactoring
status: done
sp: 13
split_from: null
created: 2026-04-30 00:00
planned: 20260430 01:08
started: 20260430 12:00
completed: 2026-04-30 13:00
retro: skipped
goal: skipped
summary: "Render skills/agents from src/files/ templates via build-only config_files.yaml and `booping build`; reorganize docs/"
---

# src/files build pipeline for skills and agents

## Context

Today the plugin has three rendering boundaries that don't share a rule:

- **Skills / agents** at `skills/<name>/SKILL.md` and `agents/<name>.md` are **hand-authored thin shells** — frontmatter (`name`, `description`, `allowed-tools`, `effort`, `model`, …) plus a single `!`booping render src/templates/.../<name>.md.j2`` line. The frontmatter values, including `effort`, live in seven SKILL.md files and three agent files; there is no single place that lists "every skill's effort."
- **`src/docs/*.md`** are hand-authored static prose, lazy-loaded by skills via `${CLAUDE_PLUGIN_ROOT}/src/docs/<name>.md` links.
- **`src/templates/docs/*.md.j2`** are pre-rendered at build time (`just build-docs`) into `docs/<name>.md` and lazy-loaded via `${CLAUDE_PLUGIN_ROOT}/docs/<name>.md` links. Of the four current files, only one (`plan_lifecycle_overview.md.j2`) actually uses Jinja interpolation (`config.plan.statuses`); the other three are plain prose with a `.j2` extension. Same for `src/templates/plan_templates/*.md.j2` — none of the four use Jinja.

This forces every contributor to know which directory and link prefix applies to what kind of artefact, and lets the one config-derived doc (`docs/plan_lifecycle_overview.md`) drift silently from `src/config.yaml` until someone reruns `just build-docs`.

After this lands:

- Every committed file under `skills/` and `agents/` is **rendered** from a corresponding `src/files/<rel>.j2` template at build time using a build-only config.
- A new `src/config_files.yaml` carries frontmatter values that can't be set from the runtime template body — today, just `effort` per skill/agent. It is **not** project-overridable.
- A new `bin/booping build` subcommand renders the whole `src/files/` tree to its destinations. `just build` is one-shot; `just dev` watches.
- Structural parity (every `skills/<name>/SKILL.md` and `agents/<name>.md` has a corresponding `src/files/<rel>.j2`) is enforced as a milestone DoD check, not a permanent CLI subcommand. `git diff` after `just build` is the drift signal.
- All hand-authored static docs live at `docs/<name>.md` (no `.j2`). The single dynamic doc (`plan_lifecycle_overview`) becomes a runtime template under `src/templates/docs/`, invoked from `/chat` via `!`booping render src/templates/docs/plan_lifecycle_overview.md.j2`` instead of a doc URI link.
- `src/docs/`, `src/templates/docs/` (for static-prose docs), `src/templates/plan_templates/`, and the `just build-docs` target are all gone.

## Decisions

- **Directory name — `src/files/`**: chosen over `src/templates/files/` because these are not just templates but the **source of every committed root-level file**. Putting them at `src/files/` (sibling of `src/templates/`) advertises the role: this directory's tree mirrors the plugin root one-to-one. Alternatives considered: `prebuilt/` (too implementation-flavored), `manifest/` (suggests a single file in some ecosystems), `surface/` (abstract).
- **Separate `src/config_files.yaml`**: not a `files:` section inside `src/config.yaml`. Why: build-time and runtime configs should not be loadable through the same code path; the build is intentionally walled off from project overrides, and a separate file makes that wall obvious to anyone reading the repo. Templates in `src/files/**` access this config as `{{ skills.chat.effort }}` — no top-level `files.` prefix.
- **`config_files.yaml` is NOT project-overridable**: `~/Claude/{project}/config.yaml` deep-merge applies only to `src/config.yaml`. Why: the build runs in the plugin repo, not in user vaults. Project overrides are a runtime concept; baking them into shipped SKILL.md files is out of scope and would break "edit your project config and see changes immediately."
- **Today `config_files.yaml` carries only `effort`**: per skill and per agent. Other frontmatter fields (`description`, `allowed-tools`, `model`, `argument-hint`) stay literal in the per-file `.j2` templates. Why: those are file-specific, not structurally shared; pulling them into config without a clear consumer would just add indirection. The architecture leaves room to centralize more later (e.g. shared `Bash(booping:*)` baseline) — adding more keys is one-template, one-config-key.
- **No build trigger (manual for now)**: no pre-commit hook, no CI guard. `just build` is on the contributor; `just check` (drift check) catches discrepancies on demand. Why: pre-commit + CI guards are real infrastructure work and the user's flow today (single contributor, low merge cadence) doesn't justify it. Architecture leaves room to add a hook later — the `booping check` command is the foundation.
- **`just dev` watcher**: included in the same milestone as `just build`. Use `watchexec` (already commonly available) — Justfile shells out to it. Why: tight rebuild loop is the point of moving frontmatter into a build pipeline; without a watcher, every `effort` tweak is `edit + build + check`.
- **Dynamic-doc handling — runtime invocation, not static URI**: `docs/plan_lifecycle_overview.md` (only doc that uses dynamic config) is removed. Its template moves to `src/templates/docs/plan_lifecycle_overview.md.j2` (runtime template). The chat skill's lazy-load prose changes from `[plan lifecycle](docs/plan_lifecycle_overview.md)` to a `!`booping render src/templates/docs/plan_lifecycle_overview.md.j2`` invocation in the skill body, gated on a condition. Why: a static doc rendered from `src/config.yaml` at build time can drift from project overrides at runtime; runtime rendering eliminates the gap. No new CLI subcommand needed (`booping render` already does this).
- **All static docs live at `docs/<name>.md` (hand-authored)**: `src/docs/*.md` (7 files) move into `docs/`. `src/templates/docs/{learn_review_table, retro_summary_format, template_plan_frontmatter}.md.j2` (3 files, no Jinja interpolation) become `docs/<name>.md`. `src/templates/plan_templates/*.md.j2` (4 files, no Jinja) become `docs/plan_templates/*.md`. Why: docs are static prose; passing them through any template pipeline is ceremony with no consumer.
- **`docs/` is hand-authored from this point on**: not a build artefact. The previously-rendered `docs/plan_lifecycle_overview.md` is deleted. `docs/images/` stays.
- **All `${CLAUDE_PLUGIN_ROOT}/src/docs/...` link prefixes rewrite to `${CLAUDE_PLUGIN_ROOT}/docs/...`**: one URI prefix everywhere.
- **Reshape pause as final milestone**: per `skill_groom.md`. Why: skill / template work (build-time frontmatter generation, link rewrites) surfaces IA issues only after rendering the touched bodies side-by-side.

## Architecture

### New layout

```
src/
  config.yaml            # runtime config (project-overridable) — unchanged
  config_files.yaml      # NEW: build-only config; not overridable
  files/                 # NEW: mirrors plugin root for build-rendered files
    skills/
      chat/SKILL.md.j2
      develop/SKILL.md.j2
      groom/SKILL.md.j2
      help/SKILL.md.j2
      install/SKILL.md.j2
      learn/SKILL.md.j2
      retro/SKILL.md.j2
    agents/
      booping-developer-middle.md.j2
      booping-developer-senior.md.j2
      booping-researcher.md.j2
  templates/             # runtime templates (skill bodies, dynamic docs) — unchanged
    skills/<name>.md.j2
    agents/<name>.md.j2
    docs/plan_lifecycle_overview.md.j2   # NEW: lifted from src/templates/docs/, the only dynamic doc
    _partials/*.j2
docs/                    # NEW: single home for all static reference docs
  cross_validation.md
  development_quality_checks.md
  how_to_initialize_project.md
  install_extension_files.md
  task_{bug,feature,refactoring}.md
  learn_review_table.md
  retro_summary_format.md
  template_plan_frontmatter.md
  plan_templates/
    backend.md
    claude_skill.md
    cli.md
    frontend.md
  images/                # unchanged
skills/<name>/SKILL.md   # build artefact, rendered from src/files/skills/<name>/SKILL.md.j2
agents/<name>.md         # build artefact, rendered from src/files/agents/<name>.md.j2
```

Removed entirely:
- `src/docs/`
- `src/templates/docs/` (except the one runtime template that stays)
- `src/templates/plan_templates/`
- `docs/plan_lifecycle_overview.md`
- `just build-docs` target

### `src/config_files.yaml` shape

```yaml
skills:
  chat:    { effort: low }
  develop: { effort: low }
  groom:   { effort: high }
  help:    { effort: low }
  install: { effort: medium }
  learn:   { effort: high }
  retro:   { effort: medium }

agents:
  booping-developer-middle: { effort: medium }
  booping-developer-senior: { effort: high }
  booping-researcher:       { effort: high }
```

The build pass loads this file as a flat YAML — no merging, no project override.

### Build template shape

`src/files/skills/chat/SKILL.md.j2`:

```jinja
---
name: chat
description: "Context-aware chat about the project: ..."
argument-hint: [topic or artifact reference]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - ...
effort: {{ skills.chat.effort }}
---

!`booping render src/templates/skills/chat.md.j2`
```

The body line is identical across all skills (just the template path changes); only frontmatter varies. The `effort` line is the only Jinja interpolation today.

`src/files/agents/booping-developer-middle.md.j2`:

```jinja
---
name: booping-developer-middle
description: "Developer worker for booping. ..."
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
effort: {{ agents["booping-developer-middle"].effort }}
color: cyan
---

!`booping render src/templates/agents/booping-developer-middle.md.j2`
```

### `bin/booping build` subcommand

- Loads `src/config_files.yaml` directly (no `Context.assemble()`, no project resolution).
- Walks `src/files/**/*.j2`.
- For each template at `src/files/<rel>.j2`, renders it with the config_files YAML as the top-level Jinja context (so `{{ skills.chat.effort }}` resolves) and writes the rendered text to `<plugin_root>/<rel>` (drops the `.j2` suffix).
- Creates parent directories as needed.
- Prints a one-line `wrote <N> files` summary to stderr.
- Exit codes: `0` on success; `2` on render or write error.

### Justfile

Replace the `build-docs` target with:

```just
build:
    bin/booping build

dev:
    watchexec -w src/files -w src/config_files.yaml -- bin/booping build
```

(Remove the existing `build-docs` target.)

### Structural parity check (DoD-only)

Every `skills/<name>/SKILL.md` must have a sibling at `src/files/skills/<name>/SKILL.md.j2`; every `agents/<name>.md` at `src/files/agents/<name>.md.j2`. This is enforced as a milestone DoD step (a one-line shell check), not a CLI subcommand. After `just build`, the runtime drift signal is `git diff -- skills/ agents/` — empty means parity holds.

### Dynamic-doc lazy-load change in `/chat`

Today `src/templates/skills/chat.md.j2` ends with:

> When the user asks about valid statuses, available transitions, or how to flip a plan's status manually, lazy-load [plan lifecycle](${CLAUDE_PLUGIN_ROOT}/docs/plan_lifecycle_overview.md) to ground the answer in the current `config.plan.statuses` shape.

Replaced with a runtime invocation:

> When the user asks about valid statuses, available transitions, or how to flip a plan's status manually, run `bin/booping render src/templates/docs/plan_lifecycle_overview.md.j2` and use that output to ground the answer.

The Jinja template at `src/templates/docs/plan_lifecycle_overview.md.j2` keeps its current shape (already a runtime-renderable template; just lifted from `src/templates/docs/` to be the sole survivor of that directory).

### Static-doc URI rewrites

All `${CLAUDE_PLUGIN_ROOT}/src/docs/<name>.md` and `${CLAUDE_PLUGIN_ROOT}/docs/<name>.md` (where docs were previously pre-rendered) collapse to a single prefix: `${CLAUDE_PLUGIN_ROOT}/docs/<name>.md`. Affected files:

- `src/templates/_partials/_project_context.j2` (1 link)
- `src/templates/skills/learn.md.j2` (1 link)
- `src/templates/skills/install.md.j2` (1 link)
- `src/templates/skills/retro.md.j2` (1 link)
- `src/templates/skills/groom.md.j2` (3 links — task type doc URIs are in `src/config.yaml`)
- `src/templates/plan_templates/{backend,frontend,cli,claude_skill}.md.j2` (1 link each → these files themselves move to `docs/plan_templates/*.md`, link prefix updates in place before the move so they survive)
- `src/config.yaml` (`tasks[].doc_uri` × 3, currently `${CLAUDE_PLUGIN_ROOT}/src/docs/task_*.md`)

## Milestones

### M1: `src/files/` skeleton + `config_files.yaml` — 3 SP | done

**Goal**: every existing skill and agent has a corresponding `src/files/<rel>.j2` whose rendered output (when produced by hand-running Jinja with `config_files.yaml`) byte-matches the current on-disk file. The build pipeline doesn't exist yet, but the templates are in place and verifiable manually.

**Verify**: `for f in skills/*/SKILL.md agents/*.md; do diff -u "$f" <(uv --project booping-python run python -c "import yaml,jinja2; cfg=yaml.safe_load(open('src/config_files.yaml')); src='src/files/'+(f.replace('skills/','skills/').replace('SKILL.md','SKILL.md.j2') if 'skills/' in f else 'agents/'+f.split('/')[-1]+'.j2'); print(jinja2.Environment().from_string(open(src).read()).render(**cfg))" "$f"); done` produces no output (every file matches). (Approximate sketch — exact verifier comes in M2.)

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Create `src/config_files.yaml` with `skills:` and `agents:` sections holding the current `effort` values from each existing SKILL.md / agent.md frontmatter. Format: `<name>: { effort: <value> }`. | `src/config_files.yaml` | 1 | done |
| 1.2 | Create `src/files/skills/<name>/SKILL.md.j2` for each of the 7 skills. Each template's body is the literal frontmatter + `!`booping render src/templates/skills/<name>.md.j2`` body line, with `effort: {{ skills.<name>.effort }}` as the only Jinja interpolation. Preserve every other frontmatter line verbatim from the current SKILL.md. | `src/files/skills/{chat,develop,groom,help,install,learn,retro}/SKILL.md.j2` | 1 | done |
| 1.3 | Create `src/files/agents/<name>.md.j2` for each of the 3 agents. Same shape — verbatim frontmatter except `effort: {{ agents["<name>"].effort }}`. | `src/files/agents/{booping-developer-middle,booping-developer-senior,booping-researcher}.md.j2` | 1 | done |

#### Task 1.1 DoD

- [ ] `src/config_files.yaml` exists with `skills:` (7 entries) and `agents:` (3 entries) under it.
- [ ] Every `effort` value in the YAML matches the value in the corresponding current frontmatter.
- [ ] `uv --project booping-python run python -c "import yaml; yaml.safe_load(open('src/config_files.yaml'))"` succeeds.

#### Task 1.2 DoD

- [ ] 7 SKILL.md.j2 files exist under `src/files/skills/<name>/`.
- [ ] Each template's frontmatter is identical to the current SKILL.md frontmatter except the `effort:` line is `effort: {{ skills.<name>.effort }}`.
- [ ] Each template's body is `!`booping render src/templates/skills/<name>.md.j2``.

#### Task 1.3 DoD

- [ ] 3 agent .md.j2 files exist under `src/files/agents/`.
- [ ] Each template's frontmatter matches the current agent file except `effort: {{ agents["<name>"].effort }}`.
- [ ] Each template's body is `!`booping render src/templates/agents/<name>.md.j2``.

---

### M2: `bin/booping build` + Justfile — 3 SP | done

**Goal**: `just build` from the plugin repo renders `src/files/**/*.j2` to its destinations (matching the current on-disk SKILL.md / agent.md byte-for-byte). `just dev` watches `src/files/` and `src/config_files.yaml` and rebuilds on change. Structural parity (every committed file has a template, every template has a destination) is asserted as a one-shot DoD check.

**Verify**: `just build && git diff -- skills/ agents/` shows no changes (rendered output matches the existing checked-in files). `just dev` (background) detects a change to `src/config_files.yaml` and rewrites the affected file. The structural parity shell loop in M2's DoD exits 0. `cd booping-python && uv run pytest && uv run ruff check . && uv run basedpyright` all pass.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Implement `bin/booping build` subcommand: argparse subcommand with no flags. Loads `<plugin_root>/src/config_files.yaml` directly (no `Context.assemble()`). Walks `<plugin_root>/src/files/**/*.j2`. For each template, renders with the config YAML as Jinja kwargs (so `{{ skills.chat.effort }}` resolves) and writes to `<plugin_root>/<rel-without-.j2-suffix>`. Creates parent dirs. Print `wrote N files` to stderr on success. Exit 2 on render/write error. Wire into `cli.py`. Use the existing Jinja Environment from `rendering.py` (LenientUndefined, etc.) but with a fresh FileSystemLoader rooted at `<plugin_root>/src/files/`. | `booping-python/src/booping/commands/build.py`, `booping-python/src/booping/cli.py` | 2 | done |
| 2.2 | Tests: `tests/commands/build_test.py` against a fixture plugin tree (in-process — monkeypatches `rendering._plugin_root` because `get_plugin_root` resolves from the booping module's own `__file__`, not cwd; subprocess fixtures can't redirect it). Three cases: (a) build writes both files with correct content, (b) re-run is idempotent, (c) missing `src/files/` exits 2. | `booping-python/tests/commands/build_test.py` | 1 | done |
| 2.3 | Justfile: replace the existing `build-docs` target with `build` and `dev`. `build` runs `bin/booping build`. `dev` runs `watchexec -w src/files -w src/config_files.yaml -- bin/booping build`. | `justfile` | 0 | done |

(Task 2.3 folded into the M2 scope; SP 0 because it's a 5-line Justfile change verified by Task 2.1's manual run.)

#### Task 2.1 DoD

- [ ] `booping build` from inside the plugin repo renders every `src/files/**/*.j2`.
- [ ] Output paths drop the `.j2` suffix and mirror the source tree at the plugin root.
- [ ] Parent directories created automatically.
- [ ] `git diff` after `booping build` shows no changes (rendered output matches existing committed files).
- [ ] `booping build --help` documents no flags (no-arg).
- [ ] Run from a non-plugin directory: exits 2 with a clear error.

#### Task 2.2 DoD

- [ ] Three tests cover the three cases above.
- [ ] Tests use a fresh fixture plugin tree, not the live plugin root.
- [ ] `uv run pytest -q` passes.

#### Task 2.3 DoD

- [ ] `justfile` has `build` and `dev` targets; `build-docs` removed.
- [ ] `just build` succeeds.
- [ ] `just dev` requires `watchexec` (note in justfile comment if not assumed installed).

#### M2 cross-cutting DoD

- [ ] **Structural parity**: `for f in skills/*/SKILL.md agents/*.md; do test -f "src/files/$(echo "$f" | sed 's|^|$|; s|SKILL.md$|SKILL.md.j2|; s|^agents/\(.*\)$|agents/\1.j2|' | sed 's|^\$||')"; done` (or equivalent shell one-liner) reports every committed file has a `src/files/` source.
- [ ] **No orphan templates**: `for t in src/files/skills/*/SKILL.md.j2 src/files/agents/*.md.j2; do test -f "${t#src/files/}" || test -f "${t#src/files/}".md ; done` reports every template has a destination.
- [ ] `cd booping-python && uv run pytest && uv run ruff check . && uv run basedpyright` all green.
- [ ] Four-check IA pass on every prose change (CLI help text, stderr messages).

---

### M3: Docs migration — collapse `src/docs/`, `src/templates/docs/`, `src/templates/plan_templates/` — 4 SP | done

**Goal**: every static doc lives at `docs/<name>.md` (hand-authored). The single dynamic doc (`plan_lifecycle_overview`) lives at `src/templates/docs/plan_lifecycle_overview.md.j2` (runtime template) and is invoked from `/chat` via `!`booping render``. All `${CLAUDE_PLUGIN_ROOT}/src/docs/...` and `${CLAUDE_PLUGIN_ROOT}/docs/<rendered>.md` link prefixes collapse to `${CLAUDE_PLUGIN_ROOT}/docs/...`.

**Verify**: `git grep -nE 'src/docs/|src/templates/docs/[^p]|src/templates/plan_templates/' -- ':!plans/' ':!retrospectives/'` returns zero hits. Every `${CLAUDE_PLUGIN_ROOT}/...` link resolves to a file that exists. `bin/booping render src/templates/skills/chat.md.j2` renders without errors and the rendered body shows the `!`booping render src/templates/docs/plan_lifecycle_overview.md.j2`` invocation in place of the old static link.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Move all 7 files from `src/docs/*.md` → `docs/<name>.md` (no rename, no transform). Delete the now-empty `src/docs/` directory. | `docs/{cross_validation,development_quality_checks,how_to_initialize_project,install_extension_files,task_bug,task_feature,task_refactoring}.md`, `src/docs/` | 1 | done |
| 3.2 | Move 3 of 4 `src/templates/docs/*.md.j2` files (the static ones) into `docs/<name>.md` — drop the `.j2` extension since none of them use Jinja. The 4th (`plan_lifecycle_overview.md.j2`) is the dynamic doc and stays as a runtime template, but moves out of `src/templates/docs/` to land cleanly: keep its path at `src/templates/docs/plan_lifecycle_overview.md.j2` (this is the single survivor — `src/templates/docs/` ends up containing exactly that one file). Delete the old pre-rendered `docs/{learn_review_table,retro_summary_format,template_plan_frontmatter}.md` files where the new copies will replace them, and `docs/plan_lifecycle_overview.md`. | `docs/{learn_review_table,retro_summary_format,template_plan_frontmatter}.md`, removed `src/templates/docs/{learn_review_table,retro_summary_format,template_plan_frontmatter}.md.j2`, removed `docs/plan_lifecycle_overview.md` | 1 | done |
| 3.3 | Move 4 plan-template files: `src/templates/plan_templates/<name>.md.j2` → `docs/plan_templates/<name>.md` (drop `.j2`, no transform — none have Jinja). Delete `src/templates/plan_templates/`. The existing `docs/plan_templates/` already has these files (build artefacts of `just build-docs`); confirm byte-match and overwrite/normalize. | `docs/plan_templates/{backend,claude_skill,cli,frontend}.md`, removed `src/templates/plan_templates/` | 1 | done |
| 3.4 | Rewrite all `${CLAUDE_PLUGIN_ROOT}/src/docs/...` link prefixes to `${CLAUDE_PLUGIN_ROOT}/docs/...` across `src/templates/_partials/_project_context.j2`, `src/templates/skills/{learn,install,retro}.md.j2`, and `src/config.yaml` (`tasks[].doc_uri` × 3). Update `src/templates/skills/chat.md.j2` Phase 3 hand-off section: replace the `[plan lifecycle](${CLAUDE_PLUGIN_ROOT}/docs/plan_lifecycle_overview.md)` URI link with the runtime invocation `bin/booping render src/templates/docs/plan_lifecycle_overview.md.j2` (prose: "When the user asks ... run `bin/booping render src/templates/docs/plan_lifecycle_overview.md.j2` and use that output"). | `src/templates/_partials/_project_context.j2`, `src/templates/skills/{chat,learn,install,retro}.md.j2`, `src/config.yaml` | 1 | done |

#### Task 3.1 DoD

- [ ] All 7 files now live at `docs/<name>.md`.
- [ ] `src/docs/` directory removed.
- [ ] No content changes — only the path moved.

#### Task 3.2 DoD

- [ ] `docs/{learn_review_table,retro_summary_format,template_plan_frontmatter}.md` exist as hand-authored static prose, content matching the previously-rendered output.
- [ ] `docs/plan_lifecycle_overview.md` is removed from the working tree.
- [ ] `src/templates/docs/` contains exactly one file: `plan_lifecycle_overview.md.j2`.

#### Task 3.3 DoD

- [ ] `docs/plan_templates/{backend,claude_skill,cli,frontend}.md` exist (hand-authored, no `.j2` extension).
- [ ] `src/templates/plan_templates/` directory removed.
- [ ] `PlanTemplate.load_all()` still discovers all 4 plan templates (smoke test: `uv run python -c "from booping.context.plan_template import PlanTemplate; from pathlib import Path; print(len(PlanTemplate.load_all(Path('.'), Path('/dev/null'))))"` prints `4`).

#### Task 3.4 DoD

- [ ] `git grep -n 'src/docs/' -- ':!plans/' ':!retrospectives/'` returns zero hits.
- [ ] `git grep -n 'docs/plan_lifecycle_overview' -- ':!plans/' ':!retrospectives/'` returns zero hits (no static link to the deleted file).
- [ ] `bin/booping render src/templates/skills/chat.md.j2` shows the runtime invocation in the rendered output.
- [ ] `src/config.yaml` `tasks[].doc_uri` values use the new `${CLAUDE_PLUGIN_ROOT}/docs/...` prefix.

#### M3 cross-cutting DoD

- [ ] Four-check IA pass on each touched skill body before saving.
- [ ] Every `${CLAUDE_PLUGIN_ROOT}/...` link in the touched templates resolves to a file that exists.

---

### M4: CLAUDE.md + stale-reference cleanup — 2 SP | done

**Goal**: `CLAUDE.md` describes the new `src/files/` build pipeline, the `config_files.yaml` boundary, and the consolidated `docs/` tree. Every stale path reference is gone.

**Verify**: `git grep -nE 'build-docs|src/docs|src/templates/docs|src/templates/plan_templates' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` returns zero hits. `CLAUDE.md` `## Layout`, `## Information ownership`, `## Adding a new template-driven skill`, `## CLI`, and `## Editing conventions` reflect the new shape.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Update CLAUDE.md sections: `## Status` (note the new pipeline), `## Layout` (add `src/files/`, `src/config_files.yaml`; drop `src/docs/`, `src/templates/docs/`, `src/templates/plan_templates/`; update `docs/` description from "pre-rendered static output" to "hand-authored static reference docs"), `## Information ownership` (rename "Shared template fragments" subsection's reference from `src/docs/` to `docs/`), `## Adding a new template-driven skill` (mention that the SKILL.md thin shell is now generated from `src/files/skills/<name>/SKILL.md.j2`; mention the build-time `effort` source), `## CLI` (add `booping build`; remove `just build-docs` references), `## Editing conventions` (skills/agents are no longer hand-authored thin shells — edit `src/files/<rel>.j2` and run `just build`). | `CLAUDE.md` | 1 | done |
| 4.2 | Audit all remaining files for stale references. Run `git grep -nE 'build-docs\|src/docs\|src/templates/docs\|src/templates/plan_templates' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` and fix every hit. Particular attention to: `README.md`, every `src/templates/_partials/*.j2`, every `src/templates/skills/*.md.j2`, every `src/files/skills/<name>/SKILL.md.j2` (allowed-tools may need updates), `justfile`. | All matches from the audit grep | 1 | done |

#### Task 4.1 DoD

- [ ] `CLAUDE.md` `## Layout` section names `src/files/`, `src/config_files.yaml`, the `docs/` consolidation, and the runtime template at `src/templates/docs/plan_lifecycle_overview.md.j2`.
- [ ] `## Adding a new template-driven skill` describes the build-time pipeline.
- [ ] `## CLI` lists `booping build`.
- [ ] `## Editing conventions` no longer says SKILL.md / agent.md are hand-authored — they are build artefacts.
- [ ] Every removed path (`src/docs/`, `src/templates/docs/` for static docs, `src/templates/plan_templates/`, `just build-docs`) is no longer mentioned.

#### Task 4.2 DoD

- [ ] `git grep -nE 'build-docs|src/docs|src/templates/docs|src/templates/plan_templates' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` returns zero hits.
- [ ] `README.md` reflects the new path layout.

---

### M5: Reshape pause — render-time IA review — 1 SP | done

**Goal**: build the whole tree, render every touched skill / partial, and walk the output side-by-side with the user before transitioning. Apply prose-shape tweaks the user calls out.

**Verify**: explicit user sign-off captured in this plan.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `just build && just check` clean. Render `chat.md.j2`, `groom.md.j2`, `develop.md.j2`, `learn.md.j2`, `install.md.j2`, `retro.md.j2` via `bin/booping render`. Render the new `src/templates/docs/plan_lifecycle_overview.md.j2` via `bin/booping render`. Walk the user through the diff vs the pre-M1 baseline. Apply requested tweaks; capture sign-off. If new follow-up plans surface, file them as `backlog` stubs. | rendered output (transient); any prose tweaks land in `src/files/` or `src/templates/` source files | 1 | done |

#### Task 5.1 DoD

- [x] Every rendered skill / template reviewed by user.
- [x] Sign-off captured in this plan. (Anton, 2026-04-30: "ok, commit and push" — no tweaks requested.)
- [x] Follow-up stubs (if any) created with `status: backlog`. (None surfaced.)

---

## Final Verification

- [x] `just build` writes nothing new on a clean tree (idempotent, no diff).
- [x] Structural parity holds: every committed `skills/*/SKILL.md` and `agents/*.md` has a sibling `src/files/<rel>.j2`, and every template has a destination.
- [x] `bin/booping render src/templates/skills/<chat,develop,groom,help,install,learn,retro>.md.j2` all render without errors.
- [x] `bin/booping render src/templates/docs/plan_lifecycle_overview.md.j2` renders the lifecycle table from `src/config.yaml`.
- [x] `git grep -nE 'build-docs|src/docs|src/templates/docs/[^p]|src/templates/plan_templates' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` returns zero hits (the `[^p]` exclusion preserves the surviving `src/templates/docs/plan_lifecycle_overview.md.j2`).
- [x] `cd booping-python && uv run pytest && uv run ruff check . && uv run basedpyright` all green.
- [x] No test reads from `~/Claude/` or any path outside `booping-python/tests/__fixtures__/`.
- [x] Every `${CLAUDE_PLUGIN_ROOT}/...` link in skill bodies and partials resolves to a file that exists.
- [x] User sign-off on rendered output (M5) captured.

## Out of scope

- **Pre-commit hook or CI guard for build-drift detection**. Manual `just build` + `git diff` for now. If drift becomes a recurring problem, add a `booping check` subcommand later — DoD-only structural parity is the entry point today.
- **Project-overridable `config_files.yaml`**. Build-only file; no merge with `~/Claude/{project}/`.
- **Centralizing more frontmatter fields into `config_files.yaml`** (e.g. shared `Bash(booping:*)` allowed-tool baselines). Today only `effort` lives there. Future plans can add more.
- **Auto-regenerating `docs/` from any source**. After this lands, `docs/` is hand-authored — no build step touches it.
- **Generating an index for `docs/`** (e.g. README listing every doc file). YAGNI for now.
- **Removing `effort` from agent frontmatter** if the Claude Code harness ignores it. Out of scope; preserve current values.
- **Migrating runtime templates (`src/templates/*.md.j2`) into `src/files/`**. They stay separate — the distinction (build-time vs runtime rendering) is the architecture, not a wart to be smoothed over.
- **A test that renders every `src/files/` template and asserts the rendered SKILL.md has valid YAML frontmatter**. The build itself fails loudly on Jinja errors; YAML validity is a manual sanity check at first. Worth adding later as a `booping check --strict` mode if drift becomes a recurring problem.

## CLAUDE.md impact

Sections to update (covered in M4.1):

- `## Status` — bump the "Last updated" date and add a sentence about the build pipeline.
- `## Layout` — add `src/files/` and `src/config_files.yaml`; remove `src/docs/`; rename `docs/` from "pre-rendered static output" to "hand-authored static reference docs"; reduce `src/templates/docs/` to its single survivor.
- `## Information ownership` — the "Shared template fragments (`src/templates/_partials/`, `src/docs/`)" subsection's `src/docs/` reference becomes `docs/`.
- `## Adding a new template-driven skill` — step 5 ("Hand-author `skills/<name>/SKILL.md` as a thin shell") becomes "Author `src/files/skills/<name>/SKILL.md.j2` as a thin shell template; run `just build`."
- `## CLI` — add `booping build` and `booping check`; remove `just build-docs` from the Justfile bullet.
- `## Editing conventions` — first bullet ("Edits to `src/templates/skills/*.md.j2` ... are live ...") gets a partner: edits to `src/files/<rel>.j2` and `src/config_files.yaml` require `just build` to materialize. Remove the bullet that calls SKILL.md / agent.md "hand-authored thin shells" — they're now build artefacts.
