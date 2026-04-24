---
name: install
description: Scaffold a booping project under ~/Claude/{project}/ and attach it to the current repo. Use when onboarding a new repo or formalizing an existing one.
argument-hint: "[project-name]"
user-invocable: true
effort: high
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash(ls ~/Claude/*)
  - Bash(ls ~/Claude)
  - Bash(ls -1 ~/Claude/*)
  - Bash(ls -1 ~/Claude)
  - Bash(ls -la ~/Claude/*)
  - Bash(ls -la ~/Claude)
  - Bash(pwd)
  - Bash(booping-create-project:*)
  - Bash(booping-plans:*)
  - Agent
  - AskUserQuestion
---

# booping — /install

Bootstrap the current repo as a booping project. This skill scaffolds the vault under `~/Claude/{project}/`, writes the `.booping` marker in the attached repo, and seeds project-local extensions under `_booping/`.

This skill is **wide-domain** — it must work across very different projects (backends, frontends, content sites, CLIs). Project conventions live in `~/Claude/{project}/_booping/skill_<name>.md` and `~/Claude/{project}/_booping/agent_<name>.md`, never in this skill.

## Preflight

- Read and resolve project based on [project resolution principle](../../docs/partial_project_resolution.md).
- Read [plan statuses](../../docs/partial_plan_statuses.md).
- Read [research agents](../../docs/partial_agents_researchers_delegator.md) — delegate narrow stack detection to `booping-researcher-junior`.

## High-level workflow

1. Detect state.
2. Decide mode (new / attach / cancel).
3. Scaffold (new: run `booping-create-project`; attach: write `.booping` only).
4. Detect stack (delegate to `booping-researcher-junior`).
5. Populate vault extensions (three files in `_booping/`).
6. Verify & seed `sprints.md`.

---

## Phase 0 Detect

Capture the current working directory once via a `pwd` shell call at skill start; downstream phases reuse that absolute path instead of guessing.

Run detection with native tools — no shell pipes, no `grep`, no `cat`. In parallel:

1. `ls ~/Claude/` — list existing booping projects. Ignore dot-entries when summarizing.
2. Read `<cwd>/.booping`. If the Read returns "file does not exist", treat that as "no marker". Use `Glob` (`.booping`) as a backup detection path.

Summarize the detected state in one paragraph before asking anything. Example: *"I see projects `aurora-api`, `aurora-frontend` under `~/Claude/`. CWD `/home/you/Dev/new-thing` has no marker."*

## Phase 1 Decide mode

Use `AskUserQuestion` with three options:

- **new** — create a new project for this CWD.
- **attach** — attach this CWD to an existing project (list them from Phase 0).
- **cancel** — do nothing.

If `$ARGUMENTS` supplies a project name, default to `new` with that name (still confirm).

Resolve the project name: kebab-cased, defaulting to the CWD basename. The user confirms or overrides before proceeding. The resolved name flows into Phase 2 as `<project-name>`.

## Phase 2 Scaffold

**New mode**:

1. Invoke the scaffolder via the `Bash(booping-create-project:*)` allow-list entry:

   ```
   booping-create-project <project-name> <cwd>
   ```

   where `<project-name>` is the kebab-cased name resolved in Phase 1 and `<cwd>` is the absolute path captured via `pwd` at skill start. The executable is on PATH when the plugin is enabled (`bin/` is auto-added). The script creates `~/Claude/{project-name}/` with five directories — `plans`, `retrospectives`, `lessons`, `_booping`, `requests` — and writes a `.booping` marker in `<cwd>` with content `project_name: {project-name}`. No `sprints.md` and no `CLAUDE.md` are seeded.

**Attach mode**:

1. Only write `.booping` in the CWD, after explicit user confirmation. Content: one line `project_name: <selected-name>`. Do NOT touch anything under `~/Claude/{name}/`.

## Phase 3 Detect stack

Delegate to `booping-researcher-junior` via the `Agent` tool (haiku tier, narrow lookup). The orchestrator owns every write in later phases — the agent returns a summary only.

Briefing shape:

```
Brief: Scan the attached repo at {{cwd}} for stack signals. Read only these files if present:
pyproject.toml, package.json, Cargo.toml, go.mod, Gemfile, Justfile, Makefile,
.github/workflows/*, .pre-commit-config.yaml, README.md, CONTRIBUTING.md.

Return a compact summary with these fields (each on its own line):
  language: <e.g. "Python 3.12", "Rust 1.80", "TypeScript 5 + React 19">
  validations: <list of {command, role} pairs covering EVERY validation the project offers —
    tests, linters, typecheckers, formatters, security scanners, coverage, doctest — do NOT
    restrict to "test" + "lint">
  hook_enforced_commands: <subset of validations that fires from .pre-commit-config.yaml
    or an equivalent CI/hook config>
  configured_manual_commands: <the complement — configured but not hook-fired>
  env_notes: <Docker Compose, required services, env vars needed before commands run>

Return `unknown` for any field you can't resolve. No file writes; summary only.
```

## Phase 4 Populate vault extensions

Present the researcher's findings back to the user as `AskUserQuestion` defaults so they can confirm or override each field (one prompt per field, or one grouped prompt — either is fine).

Then write **three** extension files under `~/Claude/{project}/_booping/`:

- `~/Claude/{project}/_booping/agent_booping-developer.md` — stack + conventions for developer-agent tiers.
- `~/Claude/{project}/_booping/skill_groom.md` — validation catalogue + sizing calibration.
- `~/Claude/{project}/_booping/skill_develop.md` — quality-check classification + env notes.

Each file's skeleton is shown in its section below.

**Skip-if-exists rule (attach mode)**: if a target file already exists non-empty, skip the write and print `preserved existing: <path>` to the user. Files that exist but are empty (e.g. a stub created by `booping-create-project`) may be overwritten.

**Stack-mismatch guard (attach mode)**: when `_booping/agent_booping-developer.md` is preserved, compare the researcher's detected `language` value against the first non-heading line under the existing file's `## Stack` header. If they differ, prompt the user via `AskUserQuestion` with three options before proceeding:

- `keep existing`
- `overwrite with detected`
- `append new stack section`

This mismatch check prevents silently feeding a new Python repo with an old Rust vault's context.

### File 1 — `~/Claude/{project}/_booping/agent_booping-developer.md`

Stack + conventions only; no commands.

```markdown
# booping-developer (project extension)

Project-local stack and conventions for all active developer-agent tiers.

## Stack
{{language}}

## Conventions
{{conventions — e.g. "ruff for lint, mypy for typing, pytest for tests; prefer protocol over base class; no mocked DB in integration tests"}}

## Notes

- If a task touches areas outside the stack above, stop and escalate to the orchestrator before implementing.
- Always prefer the project's own commands over ad-hoc invocations. If the task specifies a Verify command, run that — don't substitute.
```

### File 2 — `~/Claude/{project}/_booping/skill_groom.md`

Catalogue of validations + optional sizing calibration.

```markdown
# groom (project extension)

Project-local facts for grooming.

## Available validations

Commands available in this project to validate changes. When writing a milestone's `Verify` block or the plan's `Final Verification` section, pick the subset that actually exercises what the milestone changed — don't blanket-run everything.

{{validations — one bullet per command with a short role description, e.g.:
- `just test` — unit + integration suite
- `just lint` — ruff check + ruff format --check
- `just typecheck` — basedpyright
- `pre-commit run --all-files` — full hook suite
— or `(none detected — populate this file manually when commands exist)` }}

## Sizing calibration

{{"Sprint cap: {{value}} SP." if user supplied — else "(default — see `src/config.yaml` → `sprint.default_threshold_sp`)"}}
```

### File 3 — `~/Claude/{project}/_booping/skill_develop.md`

Quality-check classification + env notes.

```markdown
# develop (project extension)

Project-local facts for development.

## Quality-check classification

Hook-enforced (runs automatically at commit, no skill action required):
{{hook_enforced_commands — one per line, or "(none)" if empty}}

Configured-but-manual (skill picks the relevant ones per milestone per docs/partial_development_quality_checks.md — not all need to run on every milestone):
{{configured_manual_commands — one per line, or "(none)" if empty}}

## Dev environment

{{env_notes — e.g. "Docker Compose up + Redis required before tests" — or "(none)"}}
```

## Phase 5 Verify & seed sprints.md

1. Print `ls ~/Claude/{name}/` so the user can see what landed.
2. Read `<cwd>/.booping` to confirm it exists and the content is correct (one line `project_name: {name}`).
3. Seed the snapshot so `/develop`'s Phase 4 commit doesn't crash on a fresh vault:

   ```bash
   booping-plans --format=md > ~/Claude/{name}/sprints.md
   ```

   `booping-plans` on a plans-empty vault emits header + separator cleanly, matching what `/chat`'s orient would regenerate. Seeding is idempotent so `/chat` can overwrite later.
4. Report next steps: suggest `/chat` (for exploration) or `/groom <topic>` (to spec work).

## Hard rules

- **Never overwrite an existing `~/Claude/{name}/` directory without confirmation.** If the target exists, default to attach-mode instead.
- **Never write `.booping` without asking.** Attach mode prompts for confirmation before writing the marker.
- **Never edit the attached repo's own `CLAUDE.md`.** This skill only writes under `~/Claude/{project}/`.
