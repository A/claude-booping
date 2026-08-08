---
status: done
title: Namespace core settings under config.core
type: refactoring
plan_status: ready-for-dev
sp: 51
split_from: null
created: 2026-08-05 18:30
planned: null
started: 20260805 12:10
completed: 2026-08-05 13:40
retro: null
goal: null
summary: "Move every core setting under config.core, retire the skills block and the
  plan lifecycle, ship migration 002"
commit: 354334871a5eb6914ac8f33ce41b48e1da3ad028
agents:
  research-codebase: a4f4e8e930d186fc3
reviewed_at: 20260805 12:08
sessions:
- 43e92726-771b-4c4a-8888-295c19fb4d64
- c13d2450-c628-4d05-94cd-ba60159cd645
metrics_active_minutes: 145
metrics_models:
- claude-opus-5
metrics_tokens_input: 758
metrics_tokens_output: 355675
metrics_tokens_cache_creation: 1489045
metrics_tokens_cache_read: 65059162
---

# Namespace core settings under config.core

## Context

`src/config.yaml` today mixes engine keys, cross-playbook keys and single-playbook keys at the top level with no convention separating them. Namespacing was started (`core.sprint`, `core.task_types`, `core.groom_playbook`) and stopped, so two conventions are live at once and `skills.<name>` still points at surfaces whose skills were retired.

After this plan, `home_dir` is the only top-level key besides `core`. Everything the shipped playbook set owns sits under `config.core`: a key one playbook owns at `core.{name}_playbook`, a key the development loop or several playbooks share directly under `core`. `core` becomes the worked example a user's own playbook namespace copies, and config stops carrying per-key validation so a user can declare whatever their playbooks read.

Three surfaces die alongside the move because the move exposes them as dead weight: the `skills:` block, the `chat` and `help` skills, and the whole `config.plan` lifecycle — whose transition machinery has one live caller and whose `plan_status:` mirror nothing reads.

## Decisions

- **`home_dir` stays top-level**: it resolves the vault before any namespace is reachable, so it cannot live inside one.
- **Placement rule**: playbook-owned → `core.{name}_playbook`; loop-wide or multi-playbook → `core.{key}`. Applied literally, including to the two scaffold trees (`core.setup_playbook.scaffold`, `core.playbook_authoring_playbook.scaffold`) — verbosity is the price of the convention being teachable.
- **`git` is develop-owned** → `core.develop_playbook.git`. Its only readers are `playbooks/_partials/_git_guide.j2` (imported by `develop/provision/base.md` alone) and develop's `develop-loop` / `wrap-up` bodies.
- **No config validation and no privileged keys**: `validate_skills()`, `SkillConfig` and `UNTRUSTED_PROJECT_KEYS` are all deleted. Config is a plain object deep-merged core → global → project with no schema gate and no per-key exception, so a user's playbook config needs no plugin change to be legal and a user who overrides `core.*` wrongly owns the result. `macros` merges from the project tier like any other key — accepted consequence: a repo carrying a local vault can declare argv that renders execute without a second permission decision.
- **`config.plan` is deleted, not relocated**: its only Python consumer is `commands/transition.py`; its template consumers are the two skills being deleted plus an already-orphaned partial. Each playbook's `playbook.yaml` statuses and its `core.{name}_playbook.status` key become the whole status vocabulary.
- **The `plan_status:` mirror goes with it**: nothing reads it. `_plan_status.py` and groom's three `plan-*` hooks are deleted, and the vault commit those scripts also performed is re-homed as an explicit `_scripts/commit-plan` hook on groom's edges so the side effect is not lost silently.
- **Retro's skip-and-mark-done becomes a local script**, not a state-machine edge. Correcting the earlier call: the move applies to *sibling* plans, and retro's machine writes only the primary's artifact, so a `done` state could never reach a sibling. `playbooks/retro/_scripts/drop-plan {slug}` is invoked once per skipped sibling by the step, exactly the shape `close-working-set` already uses for runtime-valued slugs.
- **One agents partial**: `playbooks/_partials/available_agents.md` and `src/templates/_partials/_available_agents.j2` are both retired in favour of `playbook_agents.md`, which groom already uses.
- **A fresh project starts current**: `booping-create-project` seeds `latest_migration` into the `.booping` marker at the highest shipped id, so a vault created against today's plugin never reports itself behind.
- **Compat is a shipped migration**: `migrations/002_config_core_namespacing/`, with the global tier called out as a manual step (the marker is per-vault and cannot gate a machine-level file).

## Architecture

Load-time inputs after the move:

```
src/config.yaml  ──deep-merge──>  ${XDG_CONFIG_HOME}/booping/config.yaml  ──>  {vault}/config.yaml
        │                                    (no validation pass)
        ├── home_dir                          read by Context.assemble before the vault resolves
        └── core
            ├── research_agent, macros, sprint, task_types, plans   read by shared partials
            └── {name}_playbook                                      read by that playbook only
```

One Python path names a config key by literal and therefore moves with it: `query.py`'s `DEFAULT_GLOB_PATH` (`plans.glob` → `core.plans.glob`, the fallback every spec without its own `glob` inherits). Three are removed rather than repointed: `context/config.py`'s `validate_skills` / `SkillConfig`, its `UNTRUSTED_PROJECT_KEYS` project-tier filter, and `commands/transition.py`. After that, `Config.load()` is a deep merge and nothing else.

## Milestones

### M1: Config tree rewrite — 11 SP | done

**Goal**: `src/config.yaml` carries only `home_dir` and `core`, and every render surface resolves against the new paths.

**Verify**: `bin/booping render-playbook groom --project playbooks/_fixtures/vault` and the same for `develop`, `retro`, `learn`, `code-review`, `setup`, `migrate`, `playbook-authoring` — each exits 0 with no `**STOP` notice; `just test`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Rewrite the config tree: move `research_agent`, `macros`, `plans`, `migrations.pending`, `git`, `playbook.scaffold`, `vault.scaffold` and every `skills.<name>` block to their `core.*` destinations; delete the `skills:` key | `src/config.yaml` | 3 | done |
| 1.2 | Repoint the one surviving Python config-path literal: `DEFAULT_GLOB_PATH` to `core.plans.glob` | `booping-python/src/booping/query.py` | 2 | done |
| 1.3 | Sweep every Jinja consumer onto the new paths | `src/templates/_partials/_playbook_driving.j2`, `playbooks/_partials/{sprint_planning,task_types,lesson_target_space,_git_guide}.md`, `playbooks/groom/playbook.md`, `playbooks/{retro,learn,develop,code-review}/playbook.md`, `playbooks/code-review/scope/opus-5.md`, `playbooks/migrate/survey/opus-5.md`, `playbooks/setup/setup-project/opus-5.md`, `playbooks/develop/{provision,develop-loop,wrap-up}/base.md`, `playbooks/groom/{draft-plan/opus-5.md,intake/fable-5.md}` | 4 | done |
| 1.4 | Update every test asserting an old config path | `booping-python/tests/context/config_test.py`, `booping-python/tests/utils_test.py`, `booping-python/tests/macros_test.py`, `booping-python/tests/rendering_test.py`, `booping-python/tests/test_render_playbook.py`, `booping-python/tests/commands/render_test.py` | 2 | done |

#### Task 1.1 DoD

- [x] Top level holds exactly `home_dir` and `core` — plus the `plan:` block, deliberately left for M5 to delete outright.
- [x] Every playbook that owns config has a `core.{name}_playbook` block: `groom`, `develop`, `retro`, `learn`, `code_review`, `setup`, `playbook_authoring`, `migrate`.
- [x] `core.groom_playbook.cross_review_agent` replaces `core.cross_review_agent`; no key stays at `core` that only one playbook reads.
- [x] No `skills:` key remains in the file.

#### Task 1.2 DoD

- [x] A query spec with no `glob` resolves through `core.plans.glob`.
- [x] `booping query --config core.groom_playbook.queries.latest_plans` returns rows against a vault.
- [x] `just typecheck` clean.

#### Task 1.3 DoD

- [x] `grep -rn "config\.skills\|config\.git\|config\.plan\|config\.research_agent\|'plans'\s*|" src playbooks` returns no live hit outside `_reports/` and `_specs/`.
- [x] Every touched playbook renders with no `**STOP` notice.

#### Task 1.4 DoD

- [x] `just test` green.
- [x] No test asserts on a config path that no longer exists.

---

### M2: Drop config validation — 2 SP | done

**Goal**: config is a plain deep-merged object — no key is schema-checked and no key is tier-restricted.

**Verify**: a config declaring an arbitrary `core.my_playbook.whatever` block loads and renders without warning; a project-tier `core.macros` entry resolves through `macro()`; `just test`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Delete `validate_skills()`, `SkillConfig` and `UNTRUSTED_PROJECT_KEYS`, their call sites and their tests | `booping-python/src/booping/context/config.py`, `booping-python/src/booping/context/__init__.py`, `booping-python/tests/context/config_test.py` | 2 | done |

#### Task 2.1 DoD

- [x] No unknown-field warning is emitted for any config key.
- [x] No key is dropped from any tier — a project-tier `core.macros` entry is callable via `macro()`.
- [x] `Config.load()` still deep-merges core → global → project in order, keeping `agents` shallow-merged.
- [x] `just lint` and `just typecheck` clean.

---

### M3: Delete the chat and help skills — 4 SP | done

**Goal**: `skills/` ships `code-review` and `playbook` only, with no orphaned template left behind.

**Verify**: `just build` produces no diff for the surviving skills; `bin/booping render src/templates/skills/code-review.md.j2` and `.../playbook.md.j2` render clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Delete both skills across all three layers plus their build-only frontmatter entries | `skills/chat/`, `skills/help/`, `src/files/skills/chat/`, `src/files/skills/help/`, `src/templates/skills/chat.md.j2`, `src/templates/skills/help.md.j2`, `src/config_files.yaml` | 2 | done |
| 3.2 | Delete the templates their removal orphans and the docs pages that describe them | `src/templates/docs/plan_lifecycle_overview.md.j2`, `src/templates/_partials/_plan_transitions.j2`, `documentation/chat.md`, `mkdocs.yml` | 2 | done |

#### Task 3.1 DoD

- [x] `ls skills/` shows `code-review` and `playbook` only.
- [x] `src/config_files.yaml` carries an `effort` entry per surviving skill and no others.
- [x] `just build` leaves `git diff -- skills/ agents/` empty.

#### Task 3.2 DoD

- [x] No file references `plan_lifecycle_overview` or `_plan_transitions` in code; three `documentation/` + `CLAUDE.md` prose mentions remain, owned by M8.
- [x] `mkdocs.yml` nav has no dead entry; `just docs` builds.

---

### M4: One agents partial — 5 SP | done

**Goal**: every delegation table renders from `playbook_agents.md` over a `core.{name}_playbook` block; both `available_agents` surfaces are gone.

**Verify**: `just playbook-reports` — each playbook's report still carries its agents table, byte-diff reviewed.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Point the four remaining playbooks at `playbook_agents.md` with their own config block and delete the old partial | `playbooks/{develop,retro,learn,code-review}/playbook.md`, `playbooks/_partials/available_agents.md` | 3 | done |
| 4.2 | Point the surviving `code-review` skill at `core.code_review_playbook` and delete the skill-side partial | `src/templates/skills/code-review.md.j2`, `src/templates/_partials/_available_agents.j2` | 2 | done |

#### Task 4.1 DoD

- [x] No file references `available_agents.md`.
- [x] Each of the four reports shows the same agent rows as before the change.
- [x] `playbooks/_partials/lesson_target_space.md` resolves per-playbook agents from `core.{name}_playbook.agents`.

#### Task 4.2 DoD

- [x] The rendered `code-review` skill shows its agents table and its owned status, both read from `core.code_review_playbook` — as an inlined table, not an include: `Tools.render` cannot reach `playbooks/_partials/` from the skill env, whose loader is rooted at `src/templates/`. Follow-up left open.
- [x] No file references `_available_agents.j2`.

---

### M5: Retire the plan lifecycle — 11 SP | done

**Goal**: `config.plan`, the `transition` and `vault-commit` commands, and the `plan_status:` mirror are gone; every plan-state write goes through `playbook-transition` or a playbook's own `_scripts/`.

**Verify**: a full groom run against the fixture vault reaches `ready-for-dev` with the plan committed at each superstate boundary; `just test`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Delete the `plan:` config block, the `transition` and `vault-commit` subcommands and their tests | `src/config.yaml`, `booping-python/src/booping/commands/transition.py`, `booping-python/src/booping/commands/vault_commit.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/commands/transition_test.py`, `booping-python/tests/context/lifecycle_test.py` | 4 | done |
| 5.2 | Delete groom's status-mirror scripts and re-home their vault commit as an explicit hook | `playbooks/groom/_scripts/_plan_status.py`, `playbooks/groom/_scripts/plan-in-spec`, `playbooks/groom/_scripts/plan-awaiting-plan-review`, `playbooks/groom/_scripts/plan-ready-for-dev`, `playbooks/groom/_scripts/commit-plan`, `playbooks/groom/playbook.yaml` | 3 | done |
| 5.3 | Drop `plan_status:` from the plan frontmatter shape and fix the mislabelled comments | `playbooks/_partials/plan_frontmatter.md`, `docs/template_plan_frontmatter.md`, `docs/plan_templates/*.md` | 1 | done |
| 5.4 | Replace retro's `booping transition done` with a local per-sibling script and clear the stale transitions-table prose | `playbooks/retro/_scripts/drop-plan`, `playbooks/retro/intake/prompt.md`, `playbooks/retro/intake/base.md`, `playbooks/retro/_specs/states.md`, `playbooks/retro/_specs/steps/intake/index.md` | 3 | done |

#### Task 5.1 DoD

- [x] `bin/booping --help` lists neither `transition` nor `vault-commit`.
- [x] `context/lifecycle.py` survives unchanged — it is generic over any machine dict and still serves `playbook-transition`.
- [x] `just test` green with the lifecycle-specific tests removed, not skipped.

#### Task 5.2 DoD

- [x] Groom's edges that previously fired `script plan-*` now fire `script commit-plan`.
- [x] A groom transition still leaves one vault commit per superstate boundary.
- [x] No file writes `plan_status:`.

#### Task 5.3 DoD

- [x] The documented plan frontmatter carries `status:` only, with a comment matching what actually writes it.
- [x] No plan template references `plan_status`.

#### Task 5.4 DoD

- [x] `playbooks/retro/_scripts/drop-plan {slug}` stamps `status: done`, `goal: skipped` and `completed:` on that plan and commits the vault.
- [x] Retro's intake body names the script, one invocation per skipped sibling.
- [x] No file references `booping transition` in a live surface; `CLAUDE.md` and `documentation/vault.md` prose remain, owned by M8.

---

### M6: Migration seeding and migration 002 — 7 SP | done

**Goal**: a new project starts at the current watermark, and an existing vault is carried across the rename by a shipped migration.

**Verify**: `bin/booping-create-project smoke-test` writes a marker whose `latest_migration` equals the highest id under `migrations/`; `bin/booping render-playbook migrate` lists 002 for a vault at watermark 1.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Teach `marker-set` a `@latest` value resolving to the highest shipped migration id | `booping-python/src/booping/commands/marker_set.py`, `booping-python/src/booping/migrations.py`, `booping-python/tests/commands/marker_set_test.py` | 2 | done |
| 6.2 | Seed the marker at project creation on both the default and `--local` branches, and in the setup playbook's step | `bin/booping-create-project`, `playbooks/setup/setup-project/opus-5.md` | 2 | done |
| 6.3 | Author migration 002 for the config rename, with the global tier called out as a manual step | `migrations/002_config_core_namespacing/migration.md` | 3 | done |

#### Task 6.1 DoD

- [x] `booping marker-set latest_migration=@latest` writes the highest id under `migrations/`.
- [x] A literal integer still works and still validates.

#### Task 6.2 DoD

- [x] A freshly created project renders any playbook with no migration STOP notice.
- [x] Both the home-dir and `--local` branches write the key.

#### Task 6.3 DoD

- [x] Frontmatter carries `id: 2`, `title`, `summary`, matching `001_plans_to_dirs`'s shape.
- [x] The body's `## Commands` section rewrites every renamed key in a vault `config.yaml` and is idempotent on a vault that has none.
- [x] The body states that a global-tier config at `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` must be edited by hand, and names the key mapping.

---

### M7: Shared timestamps partial — 2 SP | done

**Goal**: any playbook renders the run's date without redeclaring the macro call.

**Verify**: `just playbook-reports groom` — the stubbed timestamps render as before.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Extract groom's `slug_ts` / `human_ts` into a shared partial and include it from groom | `playbooks/_partials/timestamps.md`, `playbooks/groom/playbook.md` | 2 | done |

#### Task 7.1 DoD

- [x] The partial sets both variables from `core.macros.date` and is includable by any playbook.
- [x] `just playbook-reports groom` produces no diff beyond the include.
- [x] The existing `--stub-macro` keys in the `playbook-reports` recipe still pin both formats.

---

### M8: Docs, reports and green build — 9 SP | done

**Goal**: every document describing config, the CLI surface or the lifecycle matches the code, and the committed reports are regenerated.

**Verify**: `just lint`, `just typecheck`, `just test`, `just playbook-reports`, `just docs` all clean; `git diff -- playbooks/*/_reports/` reviewed.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Rewrite CLAUDE.md's config-schema, CLI, layout and lifecycle sections against the new shape | `CLAUDE.md` | 4 | done |
| 8.2 | Update the docs site and the README's hand-maintained statuses narrative | `documentation/project_config.md`, `documentation/develop.md`, `documentation/groom.md`, `documentation/playbook.md`, `documentation/vault.md`, `documentation/integrating-external-agents.md`, `README.md` | 3 | done |
| 8.3 | Regenerate the committed reports and bump the fixture vault's watermark | `playbooks/*/_reports/output.md`, `playbooks/_fixtures/vault/.booping` | 2 | done |

#### Task 8.1 DoD

- [x] The config-schema section describes the placement rule and lists `core.{name}_playbook` per playbook.
- [x] The CLI section no longer lists `transition` or `vault-commit`.
- [x] No section describes `skills.<name>`, `plan.statuses` or `plan_status:`.

#### Task 8.2 DoD

- [x] No documentation page names a retired config path, command or skill.
- [x] README's Statuses section describes the per-playbook vocabulary that replaced the shared lifecycle.

#### Task 8.3 DoD

- [x] `just playbook-reports` exits 0 and no report carries a `**STOP` notice.
- [x] The fixture vault's `latest_migration` equals 2, so the reports are reproducible — pulled forward into M6, since shipping 002 is what made the stale watermark red.

---

## Final Verification

- [x] `just build` renders cleanly and `git diff -- skills/ agents/` is empty.
- [x] `just lint`, `just typecheck`, `just test` green.
- [x] `just playbook-reports` exits 0; the committed report diffs are reviewed and intentional.
- [x] A vault at watermark 1 renders the migration STOP notice and `/playbook migrate` lists 002; a vault at 2 renders normally.
- [x] A project-tier config declaring an invented `core.my_playbook.*` block loads with no warning.
- [x] A project-tier `core.macros` entry executes through `macro()` — no tier drops any key.

## Out of scope

- The plan lifecycle's *semantics* — which statuses exist per playbook and how they map onto each other. This plan deletes the shared vocabulary; it does not redesign the per-playbook machines.
- `bin/booping-create-project`'s hardcoded `mkdir` path — routing it through `core.setup_playbook.scaffold` stays open.
- Any change to `home_dir` resolution, the `.booping` marker's other keys, or the migration engine itself.
- The `code-review` and `playbook` skills' bodies beyond their config reads.

## CLAUDE.md impact

Sections to rewrite, owned by task 8.1: **Information ownership → `src/config.yaml`** (drop the "one key escapes the project tier" paragraph — no key does now), **Config schema** (the `macros` bullet loses its core-and-global-tiers-only rule), (every bullet naming a moved key, plus the `skills.<name>` and `plan.*` bullets), **Scaffold trees** (both tree paths), **CLI** (`transition` and `vault-commit` removed, `marker-set` gains `@latest`), **Layout** (`skills/` contents, the deleted templates), **Plan lifecycle** (deleted wholesale — replaced by a pointer to per-playbook `states:`), and **Editing conventions** (the `skills/` build-artefact rule now covers two skills).
