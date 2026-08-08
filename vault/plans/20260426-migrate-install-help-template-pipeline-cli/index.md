---
title: Migrate /install and /help to template pipeline (CLI-driven /help)
type: refactoring
status: done
sp: 13
split_from: null
created: 2026-04-26 00:00
planned: 20260426 12:44
started: 20260426 12:44
completed: 2026-04-26 13:22
retro: skipped
goal: skipped
supersedes: plans/20260425-migrate-install-help-to-template-pipeline.md
summary: "Migrate /install and /help to templates via new booping-skills/agents/workflow CLIs, no config-resident duplication"
---

# Migrate /install and /help to template pipeline (CLI-driven /help)

## Context

`/groom`, `/develop`, `/retro`, `/learn` are template-driven via `src/templates/skills/<name>.md.j2` + `src/config.yaml` + `src/templates/_partials/`. `/install` and `/help` are still hand-authored under `skills/install/SKILL.md` and `skills/help/SKILL.md`, and both reference infrastructure that no longer exists or is now scoped to other consumers:

- Both preflight on `docs/partial_project_resolution.md`; `/install` also preflights on `docs/partial_plan_statuses.md` and `docs/partial_agents_researchers_delegator.md`.
- `/install` Phase 3 delegates stack detection to `booping-researcher-junior` — an agent that no longer exists. Researcher tiers were consolidated into a single `booping-researcher` (the only researcher under `agents/`).
- `/help`'s Agents section lists all three retired researcher tiers (`-junior`, `-middle`, `-senior`) by name, cites two `partial_*.md` files for tier-selection guidance, and prints a Workflow ASCII block whose state names predate the current lifecycle.
- `/help`'s Skills table hard-codes seven rows that duplicate each skill's frontmatter `description` — a second source of truth that drifts every time a skill description changes.
- `/help`'s See-also points at `PRD.md` (does not exist) and `partial_project_resolution.md`.

After this plan, both `SKILL.md` files are generated artifacts. `/help`'s Skills, Agents, and Workflow sections are emitted at skill load by three new CLIs:

- `bin/booping-skills` reads `skills/*/SKILL.md` frontmatter → `## Skills` table (Slash + Purpose).
- `bin/booping-agents` reads `agents/*.md` frontmatter → `## Agents` table (Agent + Description + Model).
- `bin/booping-workflow` walks `config.plan.statuses` + `transitions` → `## Workflow` per-skill chains + terminal states.

All three follow the existing `bin/booping-plan-templates` shape (uv inline, plugin-resident, zero-arg). Source of truth stays in canonical homes: skill descriptions in skill frontmatter, agent descriptions in agent frontmatter, lifecycle in `config.plan.statuses`. No config-resident `summary`/`writes`/`agents-glossary` duplication.

`/install` Phase 3's stack detection is no longer an Agent delegation — the work (read ~10 stack-signal files, synthesize a structured summary) is small enough that the orchestrator does it directly. `Agent` leaves install's `allowed-tools`. The Phase 4 vault-extension skeletons move to `src/docs/install_extension_files.md` and are lazy-loaded — keeping the skill body free of 60 lines of file content (lesson 0004 hierarchy check). Researcher-tier names are scrubbed everywhere.

This plan supersedes the cancelled `plans/20260425-migrate-install-help-to-template-pipeline.md`. Differences: no `skills.<name>.{summary,writes,agents-glossary}` config additions (frontmatter is the source of truth, exposed via CLIs); no `_agents_roster.j2` macro (replaced by `bin/booping-agents`); `/install` Phase 3 drops Agent delegation entirely; everything else (skip `_project_context.j2` for install, lazy-load Phase 4 skeletons, mandatory backup, partial deletion gated on surviving consumers) carried over.

## Decisions

- **`/install` and `/help` get no `agents` entry in `config.yaml`.** `/help` is read-only display and never delegates — its Agents section is a glossary of plugin agents for the user, not delegation guidance for the orchestrator. `/install` Phase 3's stack scan is small and narrow (read ~10 fixed files, synthesize a summary) — well within orchestrator capability without spawning a sub-agent.
- **`/install` Phase 3 becomes orchestrator-direct (no `Agent` in allowed-tools).** The current Phase 3 briefing template stays — same fields, same structure — but it's followed inline by the orchestrator instead of dispatched to `booping-researcher-junior`. `Agent` removed from `allowed-tools`. Reduces latency, removes a dead reference to a non-existent agent tier, and aligns with "delegate only when the work justifies subagent overhead".
- **Three CLIs, each reading its canonical source of truth.** `bin/booping-skills` from `skills/*/SKILL.md` frontmatter, `bin/booping-agents` from `agents/*.md` frontmatter, `bin/booping-workflow` from `config.plan.statuses`. No config-resident description fields. Source of truth stays in one place; descriptions evolve where they're authored.
- **`/install` skips `_project_context.j2`.** The partial reports the resolved project/vault. `/install`'s job is to *create* the vault; its Phase 0 enumerates `~/Claude/*`, reads `.booping`, and summarizes state — covering and exceeding what the partial offers. A first-run `/install` has no `.booping` marker, so the partial would be misleading at skill load. `/help` does include `_project_context.j2` for Quickstart personalization.
- **Phase 0..5 structure stays for `/install`.** No plan-transitions table; install bootstraps a vault with genuinely sequential branches (detect → decide → scaffold → research stack → populate → verify).
- **Skills table → CLI extraction, not config schema.** Drop the legacy "Writes" column — that data is not in frontmatter, and the Layout section already shows artifact homes.
- **Workflow diagram → CLI from config.** `bin/booping-workflow` walks `config.plan.statuses`, groups by skill, emits per-skill chains plus loopback / parking / cancellation / failure annotations and a terminal-states callout. Today's curated prose annotations ("spawns booping-developer-{middle,senior} per task") are not in config and are dropped — net trade is auto-sync over curated prose.
- **`/install` Phase 4 skeletons lazy-load to `src/docs/install_extension_files.md`.** Lesson 0004 hierarchy check: 60 lines of file-content templates are *how*, belong one layer below the orchestrator skill body that describes *what* and *when*.
- **Mandatory backup before template work.** Each migration milestone copies the authored `skills/<name>/SKILL.md` to `/tmp/<name>-skill-backup-<timestamp>.md` *before* the template file is created. `bin/booping-build` overwrites the destination; if a build runs before the template is complete, source material is destroyed.
- **Partial deletion is gated on the LAST consumer migrating.** Of the partials this plan stops referencing, only `partial_agents_strategy_mid_senior.md` (consumer: /help only) and `partial_development_quality_checks.md` (consumer: /install Phase-4 skeleton only) become orphans this sprint. The other four (`partial_project_resolution`, `partial_plan_statuses`, `partial_agents_researchers_delegator`, `partial_agents_researchers_strategy_senior_middle_junior`) keep `/chat` as the last consumer and are NOT deleted.
- **Cross-validation: skipped.** Procedural migration following an established template precedent.
- **Final reshape milestone is in scope.** Per skill_groom user-instruction + lesson 0004; rendered skill bodies expose IA issues only post-render.

## Architecture

**Load-time inputs** for the rendered `skills/install/SKILL.md`:

```
src/templates/skills/install.md.j2
  ├── frontmatter.effort      ← config.skills.install.effort
  ├── (no _project_context.j2 include — Phase 0 owns detection)
  ├── (no available_agents render — install does not delegate)
  ├── inline Phase 0..5 prose
  │      ├─ Phase 3 = orchestrator-direct stack scan (no Agent dispatch)
  │      └─ Phase 4 lazy-loads src/docs/install_extension_files.md
  └── trailing !`bin/booping-extra-instructions skill_install.md`
```

**Load-time inputs** for the rendered `skills/help/SKILL.md`:

```
src/templates/skills/help.md.j2
  ├── frontmatter.effort      ← config.skills.help.effort
  ├── {% include _partials/_project_context.j2 %}     → !`bin/booping-project-name`
  ├── ## Skills      ← !`bin/booping-skills`           (reads skills/*/SKILL.md)
  ├── ## Agents      ← !`bin/booping-agents`           (reads agents/*.md)
  ├── ## Workflow    ← !`bin/booping-workflow`         (reads src/config.yaml)
  ├── inline Quickstart / Layout / Hard rules / See also
  └── trailing !`bin/booping-extra-instructions skill_help.md`
```

**Build flow**: `bin/booping-build` already iterates `src/templates/skills/*.md.j2` (`bin/booping-build:77`). No build-script changes.

**New CLIs** follow the `bin/booping-plan-templates` shape (uv inline script with `pyyaml`, repo-relative reads, plain stdout). Zero-arg, plugin-resident, no `.booping` dependency.

`bin/booping-skills` output sketch:

```
## Skills

| Slash | Purpose |
|-------|---------|
| `/chat` | General working mode for project discussion, vault navigation, and small ad-hoc tasks. ... |
| `/develop` | Execute a groomed plan milestone-by-milestone via sub-agents. ... |
| `/groom` | Deep-research a feature, bug, or refactor and produce a specified, estimated plan ... |
| `/help` | Show what booping is, the available commands, and how to use them. ... |
| `/install` | Scaffold a booping project under ~/Claude/{project}/ and attach it to the current repo. ... |
| `/learn` | Extract lessons from a retrospective and fold improvements into ... |
| `/retro` | Generate a project- and plan-specific sprint retrospective ... |
```

`bin/booping-agents` output sketch:

```
## Agents

| Agent | Description | Model |
|-------|-------------|-------|
| `booping-developer-middle` | Developer worker for booping. Implements one task at a time from a plan, briefed per task by the orchestrator. ... | sonnet |
| `booping-developer-senior` | Developer worker for booping. Implements one task at a time from a plan, briefed per task by the orchestrator. ... | opus |
| `booping-researcher` | Researcher for booping. Encapsulates heavy reads ... | sonnet |
```

`bin/booping-workflow` output sketch:

```
## Workflow

```text
/groom    backlog → in-spec → awaiting-plan-review → ready-for-dev
          (loopback: awaiting-plan-review → in-spec)
          (parking: in-spec → backlog)
          (cancellation: backlog/in-spec/awaiting-plan-review → cancelled)

/develop  ready-for-dev → in-progress → awaiting-retro
          (failure: in-progress → fail)

/retro    awaiting-retro → awaiting-learning
          (skip: awaiting-retro → done)

/learn    awaiting-learning → done

Terminal states: done · fail · cancelled
```
```

**Reference doc creations**:

| Source | Destination | Reason |
|--------|-------------|--------|
| `/install` Phase 4 inline skeletons (3 fenced blocks in current SKILL.md) | `src/docs/install_extension_files.md` (NEW) | Lesson 0004 hierarchy; lazy-load |
| `docs/partial_development_quality_checks.md` | `src/docs/development_quality_checks.md` (NEW) | Referenced inside install_extension_files.md skeleton; legacy partial deletable post-migration |

The other four legacy partials stay in place — `/chat` is still a consumer.

## Milestones

### M1: Config additions + new lazy-load docs — 1 SP | done

**Goal**: `src/config.yaml` carries only `skills.install.effort` and `skills.help.effort` (no agents entries). Two new lazy-load docs land under `src/docs/`. No skill-body or rendered-output changes yet.

**Verify**: `bin/booping-build` exits 0; `git diff skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md skills/learn/SKILL.md` is empty.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `skills.install.effort: high` and `skills.help.effort: low` under the existing `skills:` block. NO `agents` entries — install/help do not delegate (or, in install's case, no longer delegate after this plan). Author `src/docs/install_extension_files.md` (port the three Phase-4 skeletons from current `skills/install/SKILL.md` into three `## File: <path>` sections, fenced as ` ```markdown ` so `{{placeholder}}` markers display verbatim; the skill_develop.md skeleton inside this doc references `src/docs/development_quality_checks.md` instead of the legacy partial). Author `src/docs/development_quality_checks.md` (port body of `docs/partial_development_quality_checks.md`). | `src/config.yaml`, `src/docs/install_extension_files.md` (NEW), `src/docs/development_quality_checks.md` (NEW) | 1 | done |

#### Task 1.1 DoD

- [x] `config.skills.install.effort == "high"` and `config.skills.help.effort == "low"`. No `skills.install.agents` or `skills.help.agents` keys.
- [x] `bin/booping-build` exits 0; `git diff` against the four already-template-driven skill bodies returns empty.
- [x] `src/docs/install_extension_files.md` exists with three `## File:` sections matching the three current Phase-4 skeletons byte-for-byte (verify with `diff` between extracted blocks and the pre-migration SKILL.md skeletons).
- [x] `src/docs/install_extension_files.md`'s skill_develop.md skeleton references `src/docs/development_quality_checks.md` (not `docs/partial_development_quality_checks.md`).
- [x] `src/docs/development_quality_checks.md` exists; carries the hook-enforced vs configured-manual classification body of `docs/partial_development_quality_checks.md`, no `partial_` prefix or "Strategies" boilerplate.
- [x] Legacy `docs/partial_development_quality_checks.md` still on disk (deletion happens in M6).

---

### M2: Three new CLIs — 4 SP | done

**Goal**: three uv-inline scripts emit the `## Skills`, `## Agents`, and `## Workflow` sections for `/help` to inline at skill load via `!`commands``. All follow the `bin/booping-plan-templates` shape; all zero-arg, plugin-resident.

**Verify**: each script invoked from any cwd prints its corresponding markdown block and exits 0.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Author `bin/booping-skills`. uv inline script with `pyyaml`. Iterates `<repo>/skills/*/SKILL.md`, parses frontmatter, emits `## Skills` header + table with `Slash` (`/{name}`) and `Purpose` (full `description`) columns, sorted alphabetically by skill name. | `bin/booping-skills` (NEW) | 1 | done |
| 2.2 | Author `bin/booping-agents`. uv inline script with `pyyaml`. Iterates `<repo>/agents/*.md`, parses frontmatter, emits `## Agents` header + table with `Agent` (`{name}` in backticks), `Description` (full `description`), and `Model` (`{model}`) columns, sorted alphabetically by agent name. | `bin/booping-agents` (NEW) | 1 | done |
| 2.3 | Author `bin/booping-workflow`. uv inline script with `pyyaml`. Reads `<repo>/src/config.yaml`; walks `plan.statuses` + their `transitions`; groups by `skill`; for each lifecycle skill emits the primary forward chain `from → to → ...` plus labeled annotations for loopbacks, parking, cancellation, failure paths. Output: `## Workflow` header + a fenced `text` block. Terminal states (`done`, `fail`, `cancelled`) listed at the end. | `bin/booping-workflow` (NEW) | 2 | done |

Tasks 2.1, 2.2, 2.3 grouped (4 SP combined; within middle-agent ~10 SP batch limit). Senior agent acceptable for 2.3 alone if the implementer prefers (2 SP design judgment for chain-walk + annotation grouping).

#### Task 2.1 DoD

- [x] `bin/booping-skills` is executable; starts with `#!/usr/bin/env -S uv run --script` shebang.
- [x] Running it from any cwd outputs `## Skills` header + markdown table, one row per skill in `skills/`.
- [x] Each row's `Slash` is `/{name}` from frontmatter; `Purpose` is the full `description` value (no trimming).
- [x] Skills sorted alphabetically by name.
- [x] No "Writes" column — only `Slash | Purpose`.
- [x] Script exits 0 even when invoked outside a booping-initialized cwd.

#### Task 2.2 DoD

- [x] `bin/booping-agents` executable; uv shebang.
- [x] Output is a `## Agents` header + table with one row per `agents/*.md`, sorted alphabetically by name.
- [x] Columns: `Agent` (`` `{name}` ``), `Description` (full from frontmatter), `Model` (`{model}`).
- [x] Script exits 0 from any cwd; doesn't depend on `.booping`.
- [x] Output sketch matches the Architecture section's `bin/booping-agents` example (sketch is intent; reasonable formatting variations OK).

#### Task 2.3 DoD

- [x] `bin/booping-workflow` executable; uv shebang.
- [x] Output groups transitions by skill (`groom`, `develop`, `retro`, `learn`) — one labeled chain per skill.
- [x] Primary forward chain rendered as `from → to → ...` for each skill.
- [x] Loopbacks (`awaiting-plan-review → in-spec`), parking (`in-spec → backlog`), cancellation, failure paths each appear as labeled annotations.
- [x] Terminal states (`done`, `fail`, `cancelled`) listed at the end.
- [x] Script exits 0 from any cwd.
- [x] Output reproduces the architecture sketch (sketch is intent; reasonable formatting variations OK).

---

### M3: `install.md.j2` template — 2 SP | done

**Goal**: `skills/install/SKILL.md` is a generated artifact. Phase 3 stack scan becomes orchestrator-direct (no `Agent` in allowed-tools). All references to `booping-researcher-junior` removed. Phase 4 skeletons live in `src/docs/install_extension_files.md`, lazy-loaded. Three legacy preflight partial-reads dropped. Phase 0..5 structure preserved.

**Verify**: `bin/booping-build` clean; `diff` against pre-migration shows only intended deltas; `rg 'booping-researcher-(junior|middle|senior)|^\s+- Agent$' skills/install/SKILL.md src/templates/skills/install.md.j2` returns zero matches.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Backup current `skills/install/SKILL.md` → `/tmp/install-skill-backup-<ts>.md`. Print backup path. | `/tmp/install-skill-backup-<ts>.md` | — | done |
| 3.2 | Author `src/templates/skills/install.md.j2`. Mirror current SKILL.md body. Frontmatter: `effort: {{ config.skills.install.effort }}`. Drop `Agent` from `allowed-tools` (no delegation in Phase 3 anymore); drop the three Preflight partial-read bullets entirely (`/install` no longer needs `_project_context.j2`, `partial_plan_statuses.md`, or `partial_agents_researchers_delegator.md`). Phase 3 prose: rewrite to "the orchestrator reads the listed stack-signal files directly and synthesizes the field-structured summary inline" — preserve the field list (language, validations, hook_enforced_commands, configured_manual_commands, env_notes) and the file list (pyproject.toml, package.json, Cargo.toml, go.mod, Gemfile, Justfile, Makefile, .github/workflows/, .pre-commit-config.yaml, README.md, CONTRIBUTING.md). Phase 4: replace inline three skeletons with one paragraph naming the three target paths + lazy-load reference to `src/docs/install_extension_files.md`. Skip-if-exists rule and stack-mismatch guard preserved verbatim. Append `!`bin/booping-extra-instructions skill_install.md`` at end. Add `Bash(bin/booping-extra-instructions:*)` to `allowed-tools`. | `src/templates/skills/install.md.j2` (NEW), `skills/install/SKILL.md` (regenerated by build) | 2 | done |

#### Task 3.1 DoD

- [x] `cp skills/install/SKILL.md /tmp/install-skill-backup-$(date +%Y%m%d-%H%M%S).md` succeeds.
- [x] Backup file exists with byte-identical content of pre-migration `skills/install/SKILL.md`.
- [x] Backup path printed.

#### Task 3.2 DoD

**Sequence**:

1. Confirm Task 3.1 backup exists. If absent, halt.
2. Read backup; transcribe `allowed-tools` minus `Agent` (drop). Add `Bash(bin/booping-extra-instructions:*)`. Move `effort` to `effort: {{ config.skills.install.effort }}`.
3. Transcribe Preflight: replace its three bullets entirely. New Preflight body: empty section, OR a single bullet "Phase 0 enumerates `~/Claude/*` and reads `.booping` directly — no preflight reads required." (Implementer's choice — terseness wins.)
4. Transcribe Phase 0..5 prose with the Phase 3 + Phase 4 changes described in the task.
5. Use `src/templates/skills/groom.md.j2` as reference for `!`bin/…`` syntax.
6. Run `bin/booping-build`.

**Structural DoD**:

- [x] `src/templates/skills/install.md.j2` exists; `bin/booping-build` exits 0.
- [x] Frontmatter: `effort: {{ config.skills.install.effort }}` (renders to `high`); `argument-hint: "[project-name]"` and `user-invocable: true` preserved; all current `allowed-tools` entries preserved EXCEPT `Agent` (dropped); new `Bash(bin/booping-extra-instructions:*)` added.
- [x] Preflight section has zero references to `partial_project_resolution`, `partial_plan_statuses`, or `partial_agents_researchers_delegator`.
- [x] Phase 0 "Detect" semantics unchanged (pwd, ls ~/Claude/, .booping read with Glob backup, summary).
- [x] Phase 1 "Decide mode" unchanged.
- [x] Phase 2 "Scaffold" unchanged.
- [x] Phase 3 "Detect stack" prose names the orchestrator as the executor (no Agent dispatch). The field list (language, validations, hook_enforced_commands, configured_manual_commands, env_notes) and file list (pyproject.toml, package.json, …) are preserved verbatim from the pre-migration briefing. `rg 'booping-researcher-junior|booping-researcher-middle|booping-researcher-senior' src/templates/skills/install.md.j2 skills/install/SKILL.md` returns zero matches.
- [x] Phase 4 names the three target paths and contains a lazy-load reference to `src/docs/install_extension_files.md`. Skip-if-exists rule and stack-mismatch guard preserved verbatim. `rg '## Stack' skills/install/SKILL.md` returns zero matches (the pre-migration skeleton heading is gone).
- [x] Phase 5 "Verify & seed sprints.md" preserved verbatim, including `booping-plans --format=md > ~/Claude/{name}/sprints.md`.
- [x] `!`bin/booping-extra-instructions skill_install.md`` present at end of body as the last non-empty line.
- [x] `rg 'partial_project_resolution|partial_plan_statuses|partial_agents_researchers_delegator|partial_development_quality_checks' skills/install/SKILL.md src/templates/skills/install.md.j2` returns zero matches.
- [x] `Hard rules` section preserved verbatim.
- [x] `rg '\{\{\s*config\.' skills/install/SKILL.md` returns zero matches.

---

### M4: `help.md.j2` template — 2 SP | done

**Goal**: `skills/help/SKILL.md` is a generated artifact. Skills, Agents, Workflow sections become `!`commands``. Stale references gone. See-also cleaned up.

**Verify**: `bin/booping-build` clean; `diff` shows Quickstart / Layout / Hard rules byte-identical; Skills + Agents + Workflow now CLI-driven; `rg 'booping-researcher-(junior|middle|senior)' skills/help/SKILL.md src/templates/skills/help.md.j2` returns zero matches.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Backup current `skills/help/SKILL.md` → `/tmp/help-skill-backup-<ts>.md`. | `/tmp/help-skill-backup-<ts>.md` | — | done |
| 4.2 | Author `src/templates/skills/help.md.j2`. Frontmatter: `effort: {{ config.skills.help.effort }}`; `allowed-tools` augmented with `Bash(bin/booping-skills:*)`, `Bash(bin/booping-agents:*)`, `Bash(bin/booping-workflow:*)`, `Bash(bin/booping-project-name:*)`, `Bash(bin/booping-extra-instructions:*)`. Body order: `_project_context.j2` include → Quickstart → `!`bin/booping-skills`` → `!`bin/booping-agents`` → Layout → `!`bin/booping-workflow`` → Hard rules → See also (drop `PRD.md` and `partial_project_resolution.md` bullets; keep `README.md`) → trailing `!`bin/booping-extra-instructions skill_help.md``. Phase 0 dispatch logic preserved verbatim. | `src/templates/skills/help.md.j2` (NEW), `skills/help/SKILL.md` (regenerated by build) | 2 | done |

#### Task 4.1 DoD

- [x] `cp skills/help/SKILL.md /tmp/help-skill-backup-$(date +%Y%m%d-%H%M%S).md` succeeds.
- [x] Backup file exists with byte-identical content of pre-migration `skills/help/SKILL.md`.

#### Task 4.2 DoD

**Sequence**:

1. Confirm Task 4.1 backup exists.
2. Transcribe `allowed-tools`, `argument-hint`, `user-invocable` verbatim from backup; augment with the five new `Bash(bin/booping-*:*)` entries.
3. Transcribe Quickstart / Layout / Hard rules blocks verbatim.
4. Replace Skills section with `!`bin/booping-skills``.
5. Replace Agents section with `!`bin/booping-agents``.
6. Replace Workflow section with `!`bin/booping-workflow``.
7. Replace Preflight section with `{% include "_partials/_project_context.j2" %}`.
8. Update See also: drop `PRD.md` (verify with `ls /home/anton/Dev/@A/claude-booping/PRD.md` — file does not exist); drop `docs/partial_project_resolution.md`; keep `README.md`.
9. Append `!`bin/booping-extra-instructions skill_help.md`` at end.
10. Run `bin/booping-build`.

**Structural DoD**:

- [x] `src/templates/skills/help.md.j2` exists; `bin/booping-build` exits 0.
- [x] Frontmatter: `effort: {{ config.skills.help.effort }}` (renders to `low`); `allowed-tools` augmented with the five `Bash(bin/booping-*:*)` entries.
- [x] Top of body (after frontmatter): `## Project Context` block from `_project_context.j2`.
- [x] Phase 0 "Dispatch topic" and Phase 1 "Render body" prose preserved.
- [x] Quickstart block byte-identical to pre-migration.
- [x] Skills section is the literal text `!`bin/booping-skills`` (load-time inline).
- [x] Agents section is the literal text `!`bin/booping-agents`` (load-time inline). Zero hard-coded mentions of `booping-researcher-junior`, `-middle`, `-senior` and zero references to `partial_agents_researchers_delegator.md` or `partial_agents_strategy_mid_senior.md`.
- [x] Layout block byte-identical to pre-migration.
- [x] Workflow section is the literal text `!`bin/booping-workflow``.
- [x] Hard rules block byte-identical (`/help` never writes files).
- [x] See also has no `PRD.md` bullet and no `partial_project_resolution.md` bullet; `README.md` preserved.
- [x] Trailing `!`bin/booping-extra-instructions skill_help.md`` present as the last non-empty line.
- [x] `rg 'booping-researcher-(junior|middle|senior)' skills/help/SKILL.md src/templates/skills/help.md.j2` returns zero matches.
- [x] `rg 'partial_project_resolution|partial_agents_researchers_delegator|partial_agents_strategy_mid_senior' skills/help/SKILL.md src/templates/skills/help.md.j2` returns zero matches.
- [x] `rg '\{\{\s*config\.' skills/help/SKILL.md` returns zero matches.

---

### M5: Build + behavior verification — 1 SP | done

**Goal**: confirm both rendered skills load and behave correctly in a real Claude Code session and the live CLI outputs match the architecture sketches.

**Verify**: `bin/booping-build` clean. `/help` (no args) prints Quickstart unchanged + project-context block. `/help skills` prints CLI table covering every skill in `skills/`. `/help agents` prints CLI table covering every `agents/*.md`. `/help workflow` prints CLI diagram covering all four lifecycle skills + terminal states callout. `/install` Phase 0 + Phase 1 complete in a throwaway directory without errors.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Build, diff rendered SKILL.md files vs backups, live-test `/help` (no args, `skills`, `agents`, `layout`, `workflow`) and `/install` Phase 0–3 (Phase 3 in dry-mode — orchestrator does the read but doesn't write). Sanity-check `bin/booping-skills`, `bin/booping-agents`, and `bin/booping-workflow` outputs match the M2 sketches. Record outputs in plan as M5 evidence. | `skills/install/SKILL.md`, `skills/help/SKILL.md` (read-only) | 1 | done |

#### Task 5.1 DoD

- [x] `bin/booping-build` exits 0 with no stderr.
- [x] `diff /tmp/install-skill-backup-*.md skills/install/SKILL.md`: only the intended deltas (effort source, Preflight emptied of partial reads, Phase-3 wording shifted from Agent dispatch to direct read, Phase-4 lazy-load reference, trailing extra-instructions line, Agent removed from allowed-tools).
- [x] `diff /tmp/help-skill-backup-*.md skills/help/SKILL.md`: Quickstart / Layout / Hard rules byte-identical (modulo project-context block prepended); Skills + Agents + Workflow now `!`command`` lines; See-also has no PRD.md or partial_project_resolution.md bullets.
- [x] `/help skills` live output covers every skill in `skills/` (one row per skill).
- [x] `/help agents` live output covers every `agents/*.md` (one row per agent).
- [x] `/help workflow` live output covers every plan-lifecycle skill (`groom`, `develop`, `retro`, `learn`) and lists terminal states.
- [x] `/install` Phase 0 detect + Phase 1 decide-mode + Phase 3 stack-scan-without-Agent prompts complete without errors in a throwaway directory; abort before Phase 4 write.

---

### M6: Prune invalidated references + CLAUDE.md / README.md updates — 2 SP | done

**Goal**: orphaned partials this sprint actually invalidated are deleted; references to consolidated researcher tiers are scrubbed from README.md; CLAUDE.md updated; surviving partials (those `/chat` still consumes) are NOT deleted.

**Verify**: `rg 'partial_agents_strategy_mid_senior|partial_development_quality_checks' skills/ src/ docs/` returns zero matches anywhere after deletion. `rg 'booping-researcher-(junior|middle|senior)' README.md skills/ src/ agents/ docs/` returns zero matches. `bin/booping-build` re-runs cleanly. CLAUDE.md updated.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Delete the two orphaned partials. Run `rg 'partial_agents_strategy_mid_senior\|partial_development_quality_checks' skills/ src/ docs/` and confirm only matches are inside the two target files themselves. Delete the two files. Re-run grep — expect zero matches. **Do NOT delete** `partial_project_resolution.md`, `partial_plan_statuses.md`, `partial_agents_researchers_delegator.md`, `partial_agents_researchers_strategy_senior_middle_junior.md` — `/chat` still consumes them. | `docs/partial_agents_strategy_mid_senior.md` (DELETE), `docs/partial_development_quality_checks.md` (DELETE) | 1 | done |
| 6.2 | Update README.md: remove every line matching `booping-researcher-(junior|middle|senior)`; replace with one consolidated row matching `agents/booping-researcher.md`'s shape. Update CLAUDE.md "Status (April 2026)": list `chat` as the only hand-authored user-invocable skill. CLAUDE.md "Layout": narrow the `docs/partial_*.md` bullet to the surviving partials. CLAUDE.md "CLI": add bullets for `bin/booping-skills`, `bin/booping-agents`, and `bin/booping-workflow` (one-line each, mirroring `booping-plan-templates`). CLAUDE.md "Migrating an old skill" closing sentence: reflect `/chat` as the only blocker. | `README.md`, `CLAUDE.md` | 1 | done |

#### Task 6.1 DoD

- [x] Pre-deletion grep `rg 'partial_agents_strategy_mid_senior|partial_development_quality_checks' skills/ src/ docs/` returns matches only inside the two target files themselves.
- [x] Two files deleted from `docs/`.
- [x] Post-deletion grep returns zero matches across `skills/ src/ docs/`.
- [x] `bin/booping-build` re-runs cleanly after deletion.
- [x] `docs/partial_project_resolution.md`, `docs/partial_plan_statuses.md`, `docs/partial_agents_researchers_delegator.md`, `docs/partial_agents_researchers_strategy_senior_middle_junior.md` are still on disk.

#### Task 6.2 DoD

- [x] `rg 'booping-researcher-(junior|middle|senior)' README.md` returns zero matches; consolidated single-row entry exists.
- [x] CLAUDE.md "Status" section names only `/chat` as remaining hand-authored.
- [x] CLAUDE.md "Layout" section's `docs/partial_*.md` mention narrowed to surviving partials.
- [x] CLAUDE.md "CLI" section has new bullets for `bin/booping-skills`, `bin/booping-agents`, `bin/booping-workflow`.
- [x] CLAUDE.md "Migrating an old skill" closing line accurate post-deletion.
- [x] `git diff CLAUDE.md README.md` reviewed.

---

### M7: Prose-shape reshape pause — 1 SP | done

**Goal**: user reviews rendered `skills/install/SKILL.md` and `skills/help/SKILL.md` (with their live `!`command`` outputs visible) for IA issues that surface only post-render. Reshape edits land at source — `src/templates/`, `bin/booping-skills`, `bin/booping-agents`, or `bin/booping-workflow`.

**Verify**: user explicitly confirms "no further reshape needed", or all requested reshape edits applied at source and rebuild reviewed.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Present rendered SKILL.md files (with live CLI outputs) to user; collect IA feedback; apply edits at source; rebuild + re-run CLIs; re-present. Loop until user confirms no further changes. | source files as needed; rendered SKILL.md files as read-back targets | 1 | done |

#### Task 7.1 DoD

- [x] User has reviewed both rendered SKILL.md files including live `!`command`` outputs.
- [x] Either: user explicitly confirms "no reshape needed", OR every requested edit applied at source (`src/templates/`, `bin/booping-skills`, `bin/booping-agents`, or `bin/booping-workflow`) and rebuild reviewed.
- [x] No reshape feedback deferred to the awaiting-retro window.

---

## Final Verification

- [x] `bin/booping-build` regenerates cleanly (exit 0, no stderr).
- [x] `git status` clean except for intended additions/deletions.
- [x] Rendered `skills/install/SKILL.md` reviewed: no `Agent` in allowed-tools; Phase 3 prose names orchestrator as executor; Phase 4 lazy-loads `src/docs/install_extension_files.md`; trailing extra-instructions line in place.
- [x] Rendered `skills/help/SKILL.md` reviewed: project-context block + Skills `!`command`` + Agents `!`command`` + Workflow `!`command`` + trailing extra-instructions line.
- [x] `bin/booping-skills` exits 0 from any cwd; output covers every `skills/*/SKILL.md`.
- [x] `bin/booping-agents` exits 0 from any cwd; output covers every `agents/*.md`.
- [x] `bin/booping-workflow` exits 0 from any cwd; output covers every plan-lifecycle skill and lists terminal states.
- [x] `rg 'booping-researcher-(junior|middle|senior)' skills/ src/ agents/ docs/ README.md CLAUDE.md` returns zero matches outside the protected partial `docs/partial_agents_researchers_strategy_senior_middle_junior.md` (one match remains; clears when `/chat` migrates per the Out of scope section).
- [x] `rg 'partial_agents_strategy_mid_senior|partial_development_quality_checks' skills/ src/ docs/` returns zero matches.
- [x] CLAUDE.md "Status" + "Layout" + "CLI" + "Migrating an old skill" sections reviewed.
- [x] README.md researcher-tier table consolidated to one row.

## Out of scope

- **`/chat` migration**: separate effort; chat has its own preflight/orient logic and is the last consumer of four legacy partials.
- **Adding `description`/`writes`/`agents-glossary` to `config.yaml` per skill**: replaced by CLI extraction approach. Source of truth stays in canonical frontmatter.
- **Curated prose annotations in /help Workflow**: dropped in exchange for auto-sync.
- **Deletion of `partial_project_resolution.md`, `partial_plan_statuses.md`, `partial_agents_researchers_delegator.md`, `partial_agents_researchers_strategy_senior_middle_junior.md`**: blocked by `/chat`. Revisit during `/chat`'s migration.
- **Schema changes to `src/config.yaml`** beyond the install/help `effort` additions in M1.1.
- **Automated tests of the rendering pipeline** — project policy is "No tests". Verification via `booping-build` exit, `rg` checks, `git diff`, visual inspection.

## CLAUDE.md impact

Section: `## Status (April 2026)` — `chat` becomes the sole remaining hand-authored user-invocable skill (M6.2).

Section: `## Layout` — narrow the `docs/partial_*.md` bullet to surviving partials (M6.2).

Section: `## CLI` — add one-line bullets for `bin/booping-skills`, `bin/booping-agents`, and `bin/booping-workflow` (M6.2).

Section: `## Migrating an old skill to the template pipeline` — closing sentence adjusted to reflect `/chat` as the only blocker (M6.2).

No config-schema, partial-API, or rendered-artifact-path changes warranting other CLAUDE.md edits.
