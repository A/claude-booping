---
title: Add /code-review skill with layered templates
type: feature
status: done
sp: 13
split_from: null
created: 2026-04-30 00:00
planned: 20260430 13:16
started: 20260430 13:18
completed: null
retro: null
goal: null
summary: "Add stateless /code-review skill with layered generic/language/framework/project templates and stack auto-discovery"
---

# Add /code-review skill with layered templates

## Context

The plugin has no skill for reviewing implementation. The user runs GLM-5.1 to generate code occasionally and wants Claude Code to review and fix the diff before they look at it. Today this is freeform `/chat` prompting — no checklist coverage, no stack-aware rules, no consistent severity labels.

`/code-review` slots between code generation and the user's own pass:

- **Stateless side-skill** like `/chat` — no plan-lifecycle status, no transitions, chat-only output, no persistent report file.
- **Layered templates**: a checklist file is one of `generic` / `language` / `framework` / `project` (vault-local). Skill loads every layer that matches the detected stack and runs all loaded checklists in sequence.
- **Stack discovery** is automatic: skill parses repo manifests (`pyproject.toml`, `package.json`, `Cargo.toml`, …), maps dependency keys to stack markers via `src/config.yaml`, and asks the user to confirm when tooling is ambiguous.
- **Skill-level dynamic checks** layer on top of static templates: lesson-compliance, plan-DoD alignment, and plan-intent-matches-implementation. These are plan-aware / lesson-aware and cannot live in static templates because they need `context.lessons` and `context.plans`.
- **Templates carry principles, not tools**. No `basedpyright` / `ruff` / `Django` baked in — references are abstract ("the project's configured type-checker / linter / ORM"), and stack discovery surfaces the concrete name back to the user.
- **User-custom templates** under `~/Claude/{project}/review_templates/` override or extend any layer by `name`. Project-specific concerns (e.g. our own `_yaml.py` consolidation rule) live there exclusively, never in plugin core templates.

After this plan: the user runs `/code-review <files-or-diff>`, the skill reports the detected stack and which templates it loaded, runs the layered checklists + dynamic checks, presents severity-labelled findings with exact-snippet fixes, and asks whether to apply them.

## Decisions

- **Skill shape** — side-skill, no plan status, no transitions block. Patterned on `/chat`'s lighter shell.
  - **Why**: stateless, no vault artifact produced.
- **Layered template loader** — `ReviewTemplate` pydantic model with `layer: Literal["generic", "language", "framework"]` (project-vault entries imply `source: project`, layer carried in their own frontmatter), and an optional `applies_to: list[str]` of stack markers. `load_all(plugin_root, vault)` mirrors `PlanTemplate` (override-by-name preserving core position).
  - **Why**: the user wants `craft` always loaded, `python` only on Python projects, future `django`/`temporal` loaded only when those frameworks are present. A flat list with `applies_to` filtering at consumption time is the simplest shape.
- **Stack discovery** — deterministic manifest parsing in M3 inside the skill body via `!`commands`` + a small Python helper module (`booping/context/stack.py`) that returns the detected `stack_markers: list[str]`. Marker mapping (e.g. `django` dep → `django` marker) lives in `src/config.yaml` under `code_review.stack_markers`.
  - **Why**: keeps the mapping data-driven and user-extensible without code changes.
- **Three core templates ship in M2**: `craft.md`, `security.md`, `python.md`. Framework templates (`django`, `temporal`) deferred — users can author them locally, and the loader supports them already.
- **Skill-level dynamic checks** rendered directly in the skill body Craft block (not as templates): lesson compliance, plan-DoD alignment, plan-intent matches implementation. These read `context.lessons` and `context.plans`.
- **Tool-name neutrality in templates** — items reference "the project's configured type-checker", not `basedpyright`. Stack discovery surfaces the concrete tool to the user when reporting setup. Lesson `0004` (information-architecture) and `0005` (sprint-internal cleanup) stay enforced via the skill body, not duplicated in templates.
- **Findings format** — severity-labelled (`BLOCKER` / `SUGGESTION` / `NIT`) bullets with exact-snippet fixes; chat-only; orchestrator may apply trivial inline nits, non-trivial fixes go to `booping-developer`.
- **Reshape milestone (M5)** — final pause for the user to read rendered skill body + three templates and adjust prose shape.

## Architecture

```
src/files/skills/code-review/SKILL.md.j2          (thin shell — frontmatter + render call)
        │ build (just build, src/config_files.yaml)
        ▼
skills/code-review/SKILL.md                        (build artefact)
        │ skill load — !`booping render src/templates/skills/code-review.md.j2`
        ▼
src/templates/skills/code-review.md.j2             (runtime body)
   ├── _project_context.j2
   ├── _available_agents.j2 ← config.yaml: skills.code-review.agents
   ├── _shared_instructions.j2
   ├── _review_template.j2  ← context.review_templates  (NEW partial; renders by layer)
   ├── _lessons.j2 + _extra_instructions.j2 (skill_code-review)
   └── Craft block: stack discovery, layered evaluation, dynamic checks, fix flow

context.review_templates loaded by Context.assemble() via:
  ReviewTemplate.load_all(plugin_root, vault)         ← NEW model
    core:    docs/review_templates/*.md     (frontmatter: name, description, layer, applies_to?)
    project: <vault>/review_templates/*.md  (override-by-name; layer from frontmatter)

stack discovery (runtime, in skill body):
  manifests: pyproject.toml | package.json | Cargo.toml | go.mod | Gemfile
  config.yaml: code_review.stack_markers maps dep keys → marker labels
  result: stack_markers passed to template selection
```

`_review_template.j2` renders the loaded checklists grouped by layer, plus a "User-custom templates extend or override any layer" hint pointing at `~/Claude/{project}/review_templates/`.

## Milestones

### M1: Layered template loader + stack-marker config — 3 SP | pending

**Goal**: `ReviewTemplate.load_all(plugin_root, vault)` works with `layer` + `applies_to` frontmatter; `Context.assemble()` exposes `context.review_templates`; `src/config.yaml` carries `code_review.stack_markers` mapping.

**Verify**: `just test` green. `bin/booping debug-context` shows `review_templates: []` (still empty — no templates yet) and `config.code_review.stack_markers` populated.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `ReviewTemplate` model: `name`, `description`, `path`, `body`, `source: Literal["core","project"]`, `layer: Literal["generic","language","framework"]`, `applies_to: list[str] = []`. `load_all(plugin_root, vault)` clones `PlanTemplate.load_all` shape, parsing the new frontmatter fields. | `booping-python/src/booping/context/review_template.py` | 1 | pending |
| 1.2 | Wire `review_templates` into `Context` model + `Context.assemble()` (mirror `plan_templates` handling, including the without-vault `Path("/dev/null")` path). Add `code_review.stack_markers` block to `src/config.yaml` with initial mappings (`django`, `temporalio`/`temporal`, `react`, `vue`, `axum`, `leptos`, `diesel`). | `booping-python/src/booping/context/__init__.py`, `src/config.yaml` | 1 | pending |
| 1.3 | Tests: core-only mode, project override replaces same-name core, position preserved, `layer` + `applies_to` parsed from frontmatter, default `applies_to=[]` when absent. Add fixtures: `plugin-root-minimal/docs/review_templates/sample.md` + `vault-full/review_templates/sample.md`. | `booping-python/tests/context/review_template_test.py`, fixture files | 1 | pending |

#### Task 1.1 DoD
- [ ] `ReviewTemplate` is a pydantic `BaseModel` with all listed fields.
- [ ] `layer` parsed from frontmatter; missing/invalid layer raises a clear error.
- [ ] `applies_to` defaults to `[]` when absent.
- [ ] Project entries override core by `name` (preserving core position).
- [ ] Missing `vault/review_templates/` returns core-only without error.

#### Task 1.2 DoD
- [ ] `Context.review_templates: list[ReviewTemplate] = []` field added.
- [ ] Both code paths in `Context.assemble()` populate `review_templates`.
- [ ] `src/config.yaml` has `code_review.stack_markers` with at least the seven mappings listed.
- [ ] `bin/booping debug-context` exposes both `review_templates` and `config.code_review.stack_markers`.

#### Task 1.3 DoD
- [ ] All four test cases pass under `just test`.
- [ ] Fixtures cover both `applies_to` present and absent.

---

### M2: Author core review templates (3 templates) — 2 SP | pending

**Goal**: Three core templates exist under `docs/review_templates/`, written in project voice. Tool-neutral references throughout. No project-specific anecdotes (those belong in vault-local templates).

**Verify**: `bin/booping debug-context | grep -A 2 review_templates` shows three core entries with correct `layer` + `applies_to`. Manual read-through confirms tight bullets and tool-neutral phrasing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Author `craft.md` (`layer: generic`, no `applies_to`). Items: SRP, Open/Closed & extensibility (where would the next feature land?), Dependency Inversion / DI seams, layered architecture & boundaries, responsibility-ownership clarity, DRY in utility modules, data access (N+1 regardless of ORM, transaction boundaries explicit). | `docs/review_templates/craft.md` | 1 | pending |
| 2.2 | Author `security.md` (`layer: generic`) — boundary input validation, secrets via env, auth before resource access, dependency hygiene + lockfile, injection prevention, output sanitisation. AND `python.md` (`layer: language`, `applies_to: [python]`) — type safety via the project's configured type-checker, style is linter-owned, tests favour DI + fakes over mocks (mocks at process edges only), specific exception types surfaced at the right boundary, comments only for WHY, idiomatic Python (context managers, pathlib, generators, no mutable defaults). | `docs/review_templates/security.md`, `docs/review_templates/python.md` | 1 | pending |

#### Task 2.1 DoD
- [ ] Frontmatter has `name: craft`, `description`, `layer: generic`, no `applies_to` (or empty list).
- [ ] Body opens with `# Quality Checklist` — no `# Review Body`.
- [ ] Each of the seven items is one tight checkbox bullet.
- [ ] No tool names hardcoded (no `mypy`, `ruff`, `Django`, etc.).
- [ ] No project-specific anecdotes (no Jinja, no `_yaml.py`, no `ChainableUndefined`).

#### Task 2.2 DoD
- [ ] `security.md` frontmatter `name: security`, `layer: generic`; six items covering the six security categories.
- [ ] `python.md` frontmatter `name: python`, `layer: language`, `applies_to: [python]`; six items as listed.
- [ ] Both bodies open with `# Quality Checklist` only.
- [ ] All items reference "the project's configured X" rather than naming a tool.

---

### M3: Skill body, partial, config, build — 5 SP | pending

**Goal**: `/code-review` is a registered skill with stack discovery, layered template selection, and skill-level dynamic checks. `just build` materialises its `SKILL.md`. Running `bin/booping render src/templates/skills/code-review.md.j2` produces a clean body listing loaded checklists by layer.

**Verify**: `just build` clean. `git diff -- skills/code-review/` shows the new build artefact. Skill body renders Available Review Checklists grouped by layer. `/code-review` invocable in Claude Code.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Add `_review_template.j2` partial. Renders `### Available review checklists` with three groups (Generic / Language / Framework) showing `<name> — <description> (<path>)`, plus a "Project-local templates: see `~/Claude/{project}/review_templates/`" hint. Reads `context.review_templates`; uses `applies_to` filtering only at skill runtime — partial just lists everything available. | `src/templates/_partials/_review_template.j2` | 1 | pending |
| 3.2 | Author skill body. Sections: project context include; available agents (renders from `config.skills.code-review.agents`); shared instructions; available checklists (via new partial); `_lessons.j2`; **Craft block** with explicit phases — (a) Identify target, (b) Stack discovery (read manifests, map deps to markers via `config.code_review.stack_markers`, report detected stack + tooling, ask user to confirm when ambiguous), (c) Template selection (load every template whose `applies_to` is empty or intersects detected markers; report loaded set), (d) Map blast radius (delegate to `booping-researcher` on diffs spanning ≥ ~5 files), (e) Run all loaded checklists, (f) **Skill-level dynamic checks** — lesson compliance (BLOCKER on violation), plan-DoD alignment (when user names a plan: cross-reference checkboxes), plan-intent match (verify mandated test methodology / pattern), (g) Present findings (severity-labelled, exact-snippet fixes), (h) Wrap up (apply-or-handle question; trivial inline, non-trivial via `booping-developer`); Hard rules (no commits without approval, linter-handled style filtered out, lesson violations BLOCKER, never edit app code beyond trivial nits, no persistent report); What `/code-review` does NOT do; `_extra_instructions.j2` for `skill_code-review`. | `src/templates/skills/code-review.md.j2` | 2 | pending |
| 3.3 | Add `code-review` entry to `src/config.yaml` `skills:` block with `agents` mapping: `booping-researcher` (`good_for`: blast-radius reads on large diffs aggregating into a summary; `bad_for`: single-file reads, small greps); `booping-developer` (`good_for`: applying user-approved non-trivial fixes; `bad_for`: trivial inline nits — orchestrator handles those). | `src/config.yaml` | 1 | pending |
| 3.4 | Author thin-shell `SKILL.md.j2` (frontmatter clone of `chat/SKILL.md.j2`; `allowed-tools` includes `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(git status *)`, `Bash(cat *)`, `Bash(booping:*)`, `Agent`, `AskUserQuestion`). Add `code-review: { effort: medium }` to `src/config_files.yaml`. Run `just build`; commit the rendered `skills/code-review/SKILL.md`. | `src/files/skills/code-review/SKILL.md.j2`, `src/config_files.yaml`, `skills/code-review/SKILL.md` (build artefact) | 1 | pending |

#### Task 3.1 DoD
- [ ] Partial groups output by layer (`generic`, `language`, `framework`); empty groups omitted.
- [ ] Project-local templates listed under their declared layer (not in a separate "project" group).
- [ ] Trailing hint points at `~/Claude/{project}/review_templates/`.
- [ ] `bin/booping render src/templates/skills/code-review.md.j2` (after M3.2) shows three checklists rendered under the right layer headings.

#### Task 3.2 DoD
- [ ] Craft block has all eight phases (a–h) in order.
- [ ] Stack-discovery phase explicitly lists which manifests to parse and references `config.code_review.stack_markers` for the mapping.
- [ ] User-confirmation step is explicit: skill asks before reviewing when tooling is ambiguous.
- [ ] Three skill-level dynamic checks (lesson compliance / plan-DoD / plan-intent) are present in phase (f), each with severity guidance.
- [ ] Hard rules block prohibits orchestrator code edits beyond trivial inline nits, prohibits commits without approval, calls out lesson-violation = BLOCKER, says no persistent report.
- [ ] Body has no transitions block, no `status:` reference (side-skill).
- [ ] No tool names baked in (skill body, like the templates, defers to discovered config).

#### Task 3.3 DoD
- [ ] `src/config.yaml` `skills.code-review.agents` populated for both agents.
- [ ] No `status:` field under `skills.code-review`.
- [ ] Rendered Available Agents section shows both agents.

#### Task 3.4 DoD
- [ ] `src/files/skills/code-review/SKILL.md.j2` shell renders correctly.
- [ ] `src/config_files.yaml` updated.
- [ ] `just build` regenerates `skills/code-review/SKILL.md` cleanly.
- [ ] `git diff -- skills/code-review/` after rebuild shows no source/artefact drift.

---

### M4: Stale-reference + docs cleanup — 2 SP | pending

**Goal**: All references to project layout, vault layout, skill inventory, and "Adding a new template-driven skill" reflect `/code-review` and `review_templates/`. Repo grep is consistent.

**Verify**: `git grep -nE 'plan_templates|review_templates' README.md CLAUDE.md docs/` reads cleanly. `git grep -n 'code-review\|/code-review' README.md CLAUDE.md` shows the skill mentioned alongside the rest of the inventory.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Update `CLAUDE.md`: add `~/Claude/{project}/review_templates/*.md` to "Project vault layout"; add `docs/review_templates/` to the Layout block; add a one-liner under "Information ownership → Project vault" listing `review_templates/`; mention `code_review.stack_markers` in the config schema section if relevant. | `CLAUDE.md` | 1 | pending |
| 4.2 | Update `README.md` skills inventory (if present) to include `/code-review`. Spot-check other top-level docs for stale skill lists. | `README.md` | 1 | pending |

#### Task 4.1 DoD
- [ ] `CLAUDE.md` Project vault layout lists `review_templates/*.md`.
- [ ] Layout block under `docs/` names `docs/review_templates/`.
- [ ] Information ownership section mentions `review_templates/` under Project vault.
- [ ] Config schema section mentions `code_review.stack_markers` (or a justification why omitted).

#### Task 4.2 DoD
- [ ] `README.md` skills inventory includes `/code-review`.
- [ ] No other top-level doc lists skills without including the new one.

---

### M5: Rendered prose reshape (HUMAN PAUSE) — 1 SP | pending

**Goal**: User reads the rendered skill body and the three core templates end-to-end and confirms the prose shape before the plan exits `in-progress`.

**Verify**: User explicitly approves ("looks good" / "ship it"). Silence does not count.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `/develop` runs `bin/booping render src/templates/skills/code-review.md.j2 --output /tmp/code-review-rendered.md` and reads the three template files; presents both back to the user with any reshape suggestions surfaced post-render (IA-pass per lesson 0004). User edits or approves. | (review only — no file edits unless reshape requested) | 1 | pending |

#### Task 5.1 DoD
- [ ] Rendered skill body presented to user.
- [ ] Three core templates presented to user.
- [ ] User explicitly approves OR requests reshape edits which are then applied.
- [ ] Final IA-pass: scoping / duplication / configurability / hierarchy.

---

## Final Verification

- [ ] `just build` renders cleanly.
- [ ] `bin/booping render src/templates/skills/code-review.md.j2` produces clean output (no `{{placeholder}}` leaks, no missing partials, three checklists listed under correct layer headings).
- [ ] `just lint` and `just typecheck` pass.
- [ ] `just test` passes — including the new `review_template_test.py` cases.
- [ ] `git diff -- skills/ agents/` after `just build` is clean (no source/artefact drift).
- [ ] User reshape approval recorded in M5.

## Out of scope

- No persistent review reports under `~/Claude/{project}/reviews/`. Output is chat-only.
- No new plan-lifecycle status. `/code-review` does not own a plan state.
- No CLI subcommands (no `bin/booping review …`). Skill body is the entry point.
- No automatic git commit of fixes. User approves; non-trivial fixes via `booping-developer`; orchestrator never commits during a review run.
- No framework templates (`django.md`, `temporal.md`, …) shipped this sprint. Loader supports them; users author locally or in a follow-up plan.
- No changes to `/groom`, `/develop`, `/retro`, `/learn`, `/chat`, `/help`, `/install`.

## Branch & PR

- **Stay on the current branch** `release/0.1.3` for the duration of this plan. Do **not** cut a new `feat/` branch despite the `feature` type — the user has explicitly bundled this work into the existing branch.
- **Open a PR at the end** of M5, after user reshape approval. Title: short, imperative; description: overview only (no test plan), per project convention.
- All milestone commits land on `release/0.1.3`.

## CLAUDE.md impact

Owned by M4.1:

- "Project vault layout" gains `review_templates/*.md`.
- "Layout" block gains `docs/review_templates/`.
- "Information ownership → Project vault" lists `review_templates/`.
- Config schema section mentions `code_review.stack_markers`.

---

# Quality Checklist

## Frontmatter

- [x] Frontmatter matches plan frontmatter shape.
- [x] `sp` (13) equals the sum of per-task SP across milestones (3 + 2 + 5 + 2 + 1).

## Content

- [x] Context names the behaviour change visible in rendered skills (a new `/code-review` skill renders), not "refactor internals".
- [x] DoD bullets are verifiable by reading the rendered output or a diff.
- [x] Every task lists exact template / partial / config paths.
- [x] Every task DoD uses checkboxes, not prose.
- [x] Every milestone has a `Verify` step.
- [x] Each milestone executable from a fresh session with only the plan as context.

## Skill-design hygiene

- [x] Structured facts (agent wiring, stack-marker mapping) go in `src/config.yaml`, not the skill body.
- [x] Single-consumer content (Craft block, Hard rules) lives in the skill body.
- [x] Long-form reference content (the checklists themselves) is lazy-loaded — each lives in its own `docs/review_templates/<name>.md` file, picked at runtime.
- [x] `!`commands`` are used for dynamic content (project context, lessons, extra instructions, the skill body itself).
- [x] No restated flow / state descriptions — `/code-review` is a side-skill, no transitions table to restate.
- [x] No stack-specific details in the skill body — they live in templates and stack-marker config.

## Anti-patterns (must be absent)

- [x] No "TBD", "TODO", "implement later", "details to follow".
- [x] No task spanning unrelated concerns (loader / templates / skill / docs are separate milestones).
- [x] No prose section that duplicates a rendered table or partial.
- [x] No "Phase 1..N" numbered workflow when a transitions table already carries the flow (n/a — side-skill; the Craft block's phases are unique to this skill, not a duplicated lifecycle).
- [x] No stale state names.

## External references validated

- [x] Template paths reference files that exist or are explicitly created in this plan.
- [x] Lazy-load doc links resolve from the rendered skill's location.

## CLAUDE.md impact

- [x] Layout, vault layout, information-ownership, and config-schema updates owned by M4.1 — never deferred (per lesson 0005).
