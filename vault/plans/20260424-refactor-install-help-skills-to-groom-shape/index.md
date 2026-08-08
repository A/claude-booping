---
title: Refactor /install and /help to groom shape; excise vault CLAUDE.md across the plugin
type: refactoring
status: done
sp: 15
source: requests/20260424-refactor-install-help-skills-to-groom-shape.md
created: 2026-04-24 00:00
planned: 2026-04-24
started: 2026-04-24
completed: 2026-04-24 00:00
retro: skipped
goal: skipped
summary: "/install and /help rewritten to groom shape; excises vault CLAUDE.md; booping-init -> booping-create-project"
---

# Refactor /install and /help to groom shape; excise vault CLAUDE.md across the plugin

## Context

Repo `CLAUDE.md` flags `skills/install/` and `skills/help/` as **stale and not refactored to the new contract — treat as broken until updated**. The 2026-04-23 refactor pass landed `/groom`, `/chat`, `/develop`, `/retro`, `/learn` on the canonical Preflight-then-phases shape; `/install` and `/help` are the final two stragglers.

Current breakages on top of structural staleness:

- `/install` writes a `.booping-project` marker, but the canonical marker is `.booping` (per `docs/partial_project_resolution.md` and what `bin/booping-plans` actually reads).
- `/install` calls `booping-init`, whose body seeds a vault `sprints.md` skeleton with the defunct `booping-plans sync-sprints` language, a vault `CLAUDE.md` whose `Layout` block references the non-existent `booping-plans set` CLI, and does not create the `requests/` directory that `/groom` now writes to.
- `/install` Phase 5 bundles language, test command, lint command, and dev-environment notes into a single `_booping/agent_booping-developer.md` — conflating concerns. Developer agents implement plan instructions; they do not decide what to lint/test/CI. Test/lint commands belong to `/groom` (to populate `Final Verification`) and `/develop` (to classify hook-enforced vs configured-but-manual per `docs/partial_development_quality_checks.md`).
- `skills/install/template-claude-md.md` duplicates layout documentation already carried by the skills and by this repo's `CLAUDE.md`; it is the source template for the redundant vault CLAUDE.md boilerplate.
- `/help`'s layout diagram lists `├── CLAUDE.md` as a first-class vault artifact and tags `sprints.md` as `/develop only`. Neither matches current state: `/chat` owns `sprints.md` regeneration; vault CLAUDE.md is the target of this refactor's excision.
- Vault CLAUDE.md itself is a parallel-truth artifact: every project's vault currently carries a boilerplate Layout + Booping commands block that duplicates content already in the skills and the repo's own CLAUDE.md. `/chat`, `/develop`, `/learn`, `/retro`, `/groom` all reference it (read or document it as the source of project conventions). The user directive for this refactor is **full excision**: remove it across every trustworthy skill and partial so `_booping/skill_*.md` and `lessons/` become the sole vault-side extensibility channels.

## Business goal

See the `business_goal:` field above.

## Definition of Done

- [ ] `bin/booping-init` does not exist; `bin/booping-create-project` exists and is executable.
- [ ] `bin/booping-create-project` writes the `.booping` marker (not `.booping-project`), creates five directories (`plans retrospectives lessons _booping requests`), and writes neither `sprints.md` nor `CLAUDE.md` into the vault.
- [ ] No file anywhere in the plugin references `booping-init` — audited by `grep -rln 'booping-init' agents/ skills/ docs/ bin/ CLAUDE.md README.md PRD.md` returning no files.
- [ ] `skills/install/template-claude-md.md` does not exist.
- [ ] `skills/install/SKILL.md` opens with `## Preflight`, followed by `## High-level workflow` and six `## Phase N` headers (0 through 5).
- [ ] `skills/install/SKILL.md` references the canonical partials (`partial_project_resolution`, `partial_plan_statuses`, `partial_agents_researchers_delegator`) under Preflight — enumerated by per-partial `grep -F`.
- [ ] `skills/install/SKILL.md` zero occurrences of `.booping-project`, `booping-init`, `template-claude-md`, `template-claude-md.md` — enumerated by a single `grep -E`.
- [ ] `skills/install/SKILL.md` zero occurrences of `Write a project \`CLAUDE.md\``, `seed a CLAUDE.md`, or equivalent "skill writes vault CLAUDE.md" language — a positive check forbids the generation step.
- [ ] `skills/install/SKILL.md` Phase 3 documents `booping-researcher-junior` delegation for stack detection — `grep -F 'booping-researcher-junior' skills/install/SKILL.md` matches in the Phase 3 block.
- [ ] `skills/install/SKILL.md` Phase 4 documents writing exactly three extension files: `_booping/agent_booping-developer.md`, `_booping/skill_groom.md`, `_booping/skill_develop.md` — enumerated by three `grep -F`.
- [ ] `skills/install/SKILL.md` Phase 4 documents the skip-if-exists rule for attach mode (preserve user content) — `grep -Fi 'skip if exists'` or `grep -Fi 'preserve existing'` matches in the Phase 4 block.
- [ ] `skills/install/SKILL.md` `allowed-tools:` frontmatter lists `Agent` and `Bash(booping-create-project:*)`.
- [ ] `skills/help/SKILL.md` opens with `## Preflight` and `## High-level workflow`, with at least one `## Phase N` header.
- [ ] `skills/help/SKILL.md` zero occurrences of `.booping-project`; `.booping` (marker) is mentioned.
- [ ] `skills/help/SKILL.md` does NOT claim `sprints.md` is `/develop only`; does name `/chat` as the regenerator.
- [ ] `skills/help/SKILL.md` layout diagram includes `requests/` and excludes any `CLAUDE.md` line inside `~/Claude/{project}/`.
- [ ] `skills/help/SKILL.md` agents section reflects the active developer strategy (middle + senior only; no `developer-junior` row).
- [ ] Trustworthy skills — `skills/{chat,develop,learn,retro,groom}/SKILL.md` — contain zero Preflight bullets, body instructions, or Hard rules that **read or edit vault CLAUDE.md**. Audit by a single `grep -E` matching the forbidden patterns (`Read .*~/Claude/\{project_name\}/CLAUDE\.md`, `vault \`CLAUDE.md\``, `git add .*CLAUDE\.md` where the `cd` is to the vault).
- [ ] `docs/partial_learn_targets.md` zero occurrences of `vault-claude-md` and of `~/Claude/<project>/CLAUDE.md`.
- [ ] `docs/partial_project_resolution.md` documents that vault `CLAUDE.md` is no longer a booping artifact — `grep -Fi 'vault CLAUDE.md' docs/partial_project_resolution.md` matches.
- [ ] `~/Claude/claude-booping/CLAUDE.md` does not exist.
- [ ] Repo `CLAUDE.md` "Status (April 2026)" block moves `install` and `help` into **Current and trustworthy**; the **Stale** block no longer names either.
- [ ] Repo `CLAUDE.md` references `bin/booping-create-project` (not `bin/booping-init`); drops the `skills/install/template-claude-md.md` bullet from the stale list.
- [ ] `README.md` layout diagram drops the `CLAUDE.md` line from `~/Claude/{project}/`; drops `Notebook.md` and `notes/` (not created by `/install`); tags `sprints.md` as `/chat` — not `/develop only`.
- [ ] `README.md` sub-agent table drops the `booping-developer-junior` row (the active strategy is mid/senior per `partial_agent_developers_delegator.md`).
- [ ] Gemini cross-validation run once during grooming (per `docs/partial_cross_validation.md`'s one-shot rule); CRITICAL and RULE violations addressed before handoff.

## Design

### Architecture

Five milestones. One script rename, two skill rewrites, one template deletion, cross-skill excision of vault CLAUDE.md, and a cleanup sweep.

**M1 — `bin/booping-init` → `bin/booping-create-project`**. Rename in place. Modernize content: marker becomes `.booping`; directory set becomes `plans retrospectives lessons _booping requests`; no `sprints.md` or `CLAUDE.md` seeded. Update the only two consumers: `skills/install/SKILL.md` (post-rewrite reference) and repo `CLAUDE.md` (the stale-list bullet).

**M2 — Rewrite `skills/install/SKILL.md` to groom shape; delete the template file**. New structure:

- `## Preflight` loads `partial_project_resolution`, `partial_plan_statuses`, and `partial_agents_researchers_delegator` — the same set `/chat` loads, minus the `partial_read_lessons` load (install doesn't operate against an existing lesson set; a fresh vault has none yet).
- `## High-level workflow` enumerates six numbered phases.
- `## Phase 0 Detect` — list `~/Claude/`, check `Read` on `<cwd>/.booping`. Short state summary.
- `## Phase 1 Decide mode` — `AskUserQuestion` with `new`, `attach`, `cancel` options. `$ARGUMENTS`-as-project-name pre-fills `new`.
- `## Phase 2 Scaffold` — new mode: invoke `booping-create-project <project-name> <cwd>` via the `Bash(booping-create-project:*)` allow-list entry. The executable is on PATH when the plugin is enabled (`bin/` is auto-added). `<project-name>` is the kebab-cased name resolved in Phase 1 (from `$ARGUMENTS` or the CWD basename via the user's confirmation); `<cwd>` is the absolute path reported by `pwd` at skill start — the skill body shows both explicitly so the worker doesn't guess. Attach mode: only write `.booping` with the user's confirmation (content: one line `project_name: <selected-name>`).
- `## Phase 3 Detect stack` — delegate to `booping-researcher-junior`. Brief: scan the attached repo for `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Gemfile`, `Justfile`, `Makefile`, `.github/workflows/*`, `.pre-commit-config.yaml`, and any project README/CONTRIBUTING that documents dev commands. Return a compact summary with these fields: `language` (e.g. "Python 3.12", "Rust 1.80"); `validations` (a list of `{command, role}` pairs covering every validation the project offers — tests, linters, typecheckers, formatters, security scanners, coverage, doctest, anything runnable — do NOT restrict to "test" + "lint"); `hook_enforced_commands` (the subset of `validations` that fires from `.pre-commit-config.yaml` or an equivalent CI/hook config); `configured_manual_commands` (the complement — validations configured but not hook-fired); `env_notes` (Docker Compose, required services, env vars needed before commands run). Orchestrator owns the write — agent returns summary, not a file. Researcher returns `unknown` for any field it can't resolve.
- `## Phase 4 Populate vault extensions` — present researcher findings as `AskUserQuestion` defaults so the user can confirm/override. Then write THREE extension files. **Exact file body skeletons** (use these verbatim in the skill, substituting `{{placeholders}}` at skill-run time):

  **`_booping/agent_booping-developer.md`** — stack + conventions only, no commands:
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

  **`_booping/skill_groom.md`** — catalogue of validations groom can draw from when sizing milestone `Verify` and `Final Verification` blocks, plus optional sizing calibration:
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

  {{"Sprint cap: {{value}} SP." if user supplied — else "(default — see docs/partial_sprint_planning.md)"}}
  ```

  **`_booping/skill_develop.md`** — quality-check classification + env notes:
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

  - In **attach mode**: skip the write for any file that already exists non-empty. Print a one-line note per preserved file (`preserved existing: <path>`). Files that exist but are empty (e.g. a `booping-create-project`-created stub) can be overwritten.
  - **Stack-mismatch guard (attach mode)**: when `_booping/agent_booping-developer.md` is preserved, compare the researcher's detected `language` value against the first non-heading line under the existing file's `## Stack` header. If they differ, prompt the user via `AskUserQuestion` with three options — `keep existing`, `overwrite with detected`, `append new stack section` — before proceeding. This prevents silently feeding a new Python repo with an old Rust vault's context.
- `## Phase 5 Verify & seed sprints.md` — print `ls ~/Claude/{name}/`, confirm `.booping` content, then run `booping-plans --format=md > ~/Claude/{name}/sprints.md` to seed the snapshot (downstream skills like `/develop`'s Phase 4 commit include `sprints.md` in `git add` and would crash on a fresh vault that never ran `/chat`). `booping-plans` reads a project with no plans cleanly — it emits just the header + separator row, matching what `/chat`'s orient would regenerate. Suggest `/chat` or `/groom` as next step.
- `## Hard rules` — three bullets: never overwrite an existing `~/Claude/{name}/` without confirmation; never write `.booping` without asking; never edit the attached repo's own `CLAUDE.md` (only writes under `~/Claude/{project}/`).

Delete `skills/install/template-claude-md.md` outright; its content is obsolete.

**M3 — Rewrite `skills/help/SKILL.md` to groom shape**. Structure:

- `## Preflight` — lean. Read `partial_project_resolution` (to detect whether we're inside an attached repo for the "first time in a repo" hint); no lesson load, no researcher delegation. Body stays inline.
- `## High-level workflow` — two numbered phases (Dispatch topic → Render body).
- `## Phase 0 Dispatch topic` — decide which body section(s) to print based on `$ARGUMENTS`: empty → Quickstart; `{skills, agents, layout, workflow}` → matching section; anything else → full help.
- `## Phase 1 Render body` — inline sections (Quickstart / Skills / Agents / Layout / Workflow / Hard rules / See also), regenerated with current facts: `.booping` marker; `/chat` as sole writer of `sprints.md`; no CLAUDE.md in the layout diagram; `requests/` included; developer-agent roster matches the active strategy (mid/senior); `/learn` description trimmed to one line.
- `## Hard rules` — single bullet: never write files; hand off scaffolding to `/install`.

**M4 — Excise vault `CLAUDE.md` from trustworthy skills + partials.** Edits:

- `skills/chat/SKILL.md` — remove the `Read ~/Claude/{project_name}/CLAUDE.md — vault and project conventions.` Preflight bullet; update the wide-domain paragraph to drop the `, and the vault CLAUDE.md` clause.
- `skills/develop/SKILL.md` — remove `the vault CLAUDE.md` from the Phase 0 read list; keep the `repo CLAUDE.md` read (unaffected); update the wide-domain paragraph.
- `skills/learn/SKILL.md` — drop the Preflight `vault CLAUDE.md` language; in Phase 1.5, delete the "Read the vault `CLAUDE.md`" line; in Phase 3, delete the "Vault `CLAUDE.md` and repo `CLAUDE.md` — one-line bullet additions" bullet and leave the repo-CLAUDE.md bullet; update Phase 5's `git add` command to drop `CLAUDE.md` from the vault commit.
- `skills/retro/SKILL.md` — update the wide-domain paragraph; hard-rule `Never edit any \`CLAUDE.md\` here` stays (still applies to repo CLAUDE.md).
- `skills/groom/SKILL.md` — update the wide-domain paragraph to drop the `, CLAUDE.md,` clause; update the Phase 1 "Re-read constraints" line to drop vault CLAUDE.md.
- `docs/partial_learn_targets.md` — delete the `vault-claude-md` row entirely. Five base types become four.
- `docs/partial_project_resolution.md` — append a short closing paragraph documenting the excision: vault `CLAUDE.md` is no longer a booping artifact; project-specific overrides live in `_booping/skill_<name>.md` and `_booping/agent_<name>.md`; lessons flow through `~/Claude/{project}/lessons/`.

**M5 — Cleanup sweep**. Delete `~/Claude/claude-booping/CLAUDE.md`. Update repo `CLAUDE.md` "Status (April 2026)" block (move install + help into trustworthy; drop the bin/booping-init + template-claude-md.md stale-list bullets; rename booping-init → booping-create-project in the CLI block). Update `README.md` layout diagram (drop CLAUDE.md, Notebook.md, notes/; tag sprints.md with `/chat`; ensure `requests/` is listed) and sub-agent table (drop `booping-developer-junior` row; keep mid + senior).

### Decisions

| # | Decision | Alternative | Why |
|---|----------|-------------|-----|
| D1 | `/help` stays orchestrator-pure. `/install` delegates only **stack detection** to `booping-researcher-junior` (narrow lookup; haiku tier). All other install work runs inline in the orchestrator. | Researcher-middle for install; dynamic skill enumeration for help | User directive. Stack detection is classic junior-tier territory (scan manifests, return summary). `/help` prints static orientation content; a live scan of `skills/*` is drift-resistant but over-engineered for a tour page. |
| D2 | Rename `bin/booping-init` → `bin/booping-create-project`; modernize in place | Delete outright and inline the scaffold in the skill | User directive. A named script is clearer than `mkdir -p ...` + `Write` chains inside the skill; parallel to `bin/booping-plans` and `bin/booping-validate-plan`. |
| D3 | Delete `skills/install/template-claude-md.md` | Modernize in place | User directive. The template seeds vault CLAUDE.md boilerplate that duplicates skill-side documentation — the redundancy is precisely what D4 excises. |
| D4 | **Full excision** of vault `CLAUDE.md` as a booping artifact. No trustworthy skill reads or edits it; `docs/partial_learn_targets.md` drops the `vault-claude-md` target; `docs/partial_project_resolution.md` documents the excision | Keep as optional-if-present; or stop seeding only | User directive. The boilerplate in every vault CLAUDE.md duplicates skill docs; real project-specific overrides already belong in `_booping/` and `lessons/`. Full excision eliminates the parallel-truth artifact. |
| D5 | Standardize the CWD marker on `.booping` | Keep `.booping-project` | Canonical per `docs/partial_project_resolution.md` and what `bin/booping-plans` reads today. `/install` is the sole remaining writer of `.booping-project`. |
| D6 | `/help` body stays **inline** in `skills/help/SKILL.md` | Externalize to `docs/template_help.md` | User directive. Single-file keeps dispatch logic and body co-located; drift-risk is low because the body is tightly scoped and reviewed at each skill refactor. |
| D7 | `bin/booping-create-project` creates `plans/ retrospectives/ lessons/ _booping/ requests/`; writes no `sprints.md`, no `CLAUDE.md` | Seed both | `requests/` is missing in the current script (`/groom` writes there, so install must create it). `sprints.md` is `/chat`-owned and regenerated via `booping-plans --format=md` on first chat run. `CLAUDE.md` excised per D4. |
| D8 | Delete `~/Claude/claude-booping/CLAUDE.md` in-scope; leave other users' vaults (`aurora-api`, `dotfiles`, `smoketest`, `_backup`) untouched | Sweep all `~/Claude/*/CLAUDE.md`; or leave claude-booping's in place | User directive. The project's own vault is authoritative to this refactor. Other vaults are user-owned state — users can clean up manually once the consumer skills stop reading the file. |
| D9 | `/install` writes **three** extension files: `_booping/agent_booping-developer.md` (stack + conventions only, no commands); `_booping/skill_groom.md` (a **catalogue of available validations** — tests, linters, typecheckers, formatters, security scanners, coverage, doctest — each with a short role; groom picks the right subset per milestone `Verify` and for `Final Verification`); `_booping/skill_develop.md` (hook-enforced vs configured-but-manual classification + env notes) | Keep the single `agent_booping-developer.md` with all four fields; or hardcode "test + lint" in the groom extension | User correction during grooming: (1) developer agents implement plan instructions; they don't decide CI/lint/test — those commands belong to the skills that invoke them; (2) the groom extension must NOT hardcode "run tests, run linters" — different projects have different validation surfaces (typecheck, security, doctest). Leaving a full catalogue lets the LLM pick the right subset per milestone instead of blanket-running everything. |
| D10 | In attach mode, `/install` Phase 4 **skips** writing any of the three extension files that already exist non-empty | Overwrite with fresh content; or always prompt | Preserves user-curated extensions in existing vaults. Attach mode is for hooking an additional repo into an already-configured project — the user has likely hand-edited those files. Empty stub files left by `booping-create-project` can still be overwritten because their content is zero. |
| D11 | `skills/help/SKILL.md` Preflight loads only `partial_project_resolution`; no lesson load, no delegator read | Mirror `/chat`'s fuller Preflight | Help is a stateless orientation skill. Reading lessons for every `/help` invocation adds cost without value — the skill's output doesn't branch on lesson content. |
| D12 | Agents section in `/help` and `README.md` reflects the **active** developer strategy (mid + senior), not the full on-disk roster (junior/mid/senior). The junior tier file exists but is not referenced by any active strategy partial | List all three tiers for completeness | User-facing docs describe what skills actually invoke. Active strategy is the source of truth; listing a dormant tier in user docs invites the same "stale roster" failure mode this refactor series has been unwinding. |
| D13 | Phase 5 **seeds `sprints.md`** by running `booping-plans --format=md > ~/Claude/{name}/sprints.md` immediately after scaffold | Leave `sprints.md` absent and rely on first `/chat` invocation to create it | Gemini cross-validation (2026-04-24) flagged the absence risk: `/develop`'s Phase 4 commit includes `sprints.md` in its `git add`, and would crash on a fresh vault that went `/install` → `/groom` → `/develop` without a `/chat` step. `booping-plans` on a plans-empty vault emits just header + separator, matching what `/chat`'s orient would regenerate. Seeding is cheap and idempotent. |
| D14 | Attach-mode **stack-mismatch guard**: when preserving `_booping/agent_booping-developer.md`, compare the researcher's detected `language` with the first non-heading line under the existing file's `## Stack` header. On mismatch, `AskUserQuestion` with three options — `keep existing / overwrite with detected / append new stack section` | Silent skip always; or always overwrite with researcher findings | Gemini cross-validation (2026-04-24) flagged the silent-mismatch failure mode (Python vault attached to a TypeScript repo would feed agents Python context). User control at the moment of detection beats discovering the mismatch during the first sprint. |

### Applies lessons

Every lesson loaded at this groom's Preflight gets an explicit verdict below (per lesson 0001):

- **`lessons/0001_every-loaded-lesson-leaves-a-plan-trace.md`** — **applied**. This section is the explicit per-lesson verdict trace. Each DoD item with an `audit`/`zero`/`every`-shape bullet carries an enumeration verifier in the Milestone Verify block (see M2 / M4 Verify).
- **`lessons/0002_audit-workers-emit-verifier-output.md`** — **applied**. M2, M3, M4, M5 DoD audit items each name the exact verifier command (`grep -F …`, `test ! -e …`). Worker Done reports on those items must include the command + its stdout per the lesson.
- **`lessons/0003_refactor-grooms-probe-delegation-and-deletion-before-v1.md`** — **applied**. Today's groom ran two `AskUserQuestion` probes upfront (delegation boundaries → D1; deletion candidates → D2, D3, D4, D8) before drafting any plan body. D1 was re-opened after the user noted stack detection as a valid narrow-lookup delegation.
- **`lessons/0004_information-architecture-pattern.md`** — **applied**. All four checks hit this plan:
  - *Scoping*: D9 separates developer-agent concerns (implement plan) from groom/develop concerns (run checks). The developer-agent extension no longer carries commands.
  - *Duplication*: D4 eliminates vault CLAUDE.md's encoded duplication of skill documentation.
  - *Configurability*: D6 keeps help body inline (configurability preferred over hierarchy for a single-file tour); D9's three-file split puts each piece of project configuration next to its consumer.
  - *Hierarchy*: D1's researcher-junior delegation pattern matches the established agents-delegator hierarchy (skill → delegator → strategy → agent).

## Milestones

### M1: Rename + modernize bin/booping-create-project — 2 SP | done

**Goal**: `bin/booping-init` no longer exists; `bin/booping-create-project` writes the `.booping` marker, creates the five vault directories (including `requests/`), and seeds no `sprints.md` or `CLAUDE.md`. Every repo reference to `booping-init` is updated or removed.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# Rename landed
test ! -e bin/booping-init
test -x bin/booping-create-project
# Modernized content
grep -F "'.booping'" bin/booping-create-project
test -z "$(grep -F '.booping-project' bin/booping-create-project)"
test -z "$(grep -F 'sprints.md' bin/booping-create-project)"
test -z "$(grep -F 'CLAUDE.md' bin/booping-create-project)"
test -z "$(grep -F 'sync-sprints' bin/booping-create-project)"
test -z "$(grep -F 'booping-plans set' bin/booping-create-project)"
grep -F 'requests' bin/booping-create-project
grep -F 'plans' bin/booping-create-project
grep -F 'retrospectives' bin/booping-create-project
grep -F 'lessons' bin/booping-create-project
grep -F '_booping' bin/booping-create-project
# Repo-wide references to `booping-init` purged
# (install skill still references the rename; updated in M2. For M1, only bin/ + README/PRD/CLAUDE.md must be clean.)
test -z "$(grep -lF 'booping-init' README.md PRD.md 2>/dev/null)"
# Smoke-test: running the script against a tmp project creates the expected layout (no sprints.md, no CLAUDE.md)
TMPROOT="$(mktemp -d)/smoketest-proj"
bin/booping-create-project smoketest-proj "$TMPROOT"
test -d "$TMPROOT/plans"
test -d "$TMPROOT/requests"
test -d "$TMPROOT/retrospectives"
test -d "$TMPROOT/lessons"
test -d "$TMPROOT/_booping"
test ! -e "$TMPROOT/sprints.md"
test ! -e "$TMPROOT/CLAUDE.md"
rm -rf "$TMPROOT"
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Rename `bin/booping-init` → `bin/booping-create-project` via `git mv`. Modernize the script: (a) marker path becomes `.booping` instead of `.booping-project`; (b) marker content stays `project_name: $PROJECT` on one line (this is what `bin/booping-plans` `resolve_project` parses — confirmed at `bin/booping-plans:47`); (c) `mkdir -p` set becomes `plans retrospectives lessons _booping requests` (adding `requests/`); (d) delete the heredoc that seeds `sprints.md`; (e) delete the heredoc that seeds `CLAUDE.md`; (f) update the usage-line comment and echo to reference `booping-create-project`; (g) keep the absolute-path smoketest branch. Shebang and `set -euo pipefail` stay. | `bin/booping-init` (deleted via rename), `bin/booping-create-project` (target) | 1 | done |
| 1.2 | Sweep every repo file for `booping-init` references; update or remove. Known hits at groom time: `CLAUDE.md` (Stale-list bullet); `skills/install/SKILL.md` (two hits deferred to M2's full rewrite — record that M1 leaves the skill dangling until M2 lands). Scope for this task: the repo-root `CLAUDE.md` + `README.md` + `PRD.md`. The install skill update is M2's responsibility and MUST NOT block M1. Patch every hit outside `skills/install/SKILL.md`. Record each patched file in the Risk register with a one-line description of the replacement. **Verifier** (run in the Done report, include command + full output in a fenced block per lesson 0002): `grep -rln 'booping-init' agents/ skills/ docs/ bin/ README.md PRD.md 2>/dev/null \| grep -v 'skills/install/SKILL.md'` — expected output: empty. Additionally: `grep -F 'booping-init' CLAUDE.md` — expected: empty (the bullet is either removed or replaced with `bin/booping-create-project`). | `CLAUDE.md`, `README.md`, `PRD.md` (edited only on hits); `skills/install/SKILL.md` (intentionally deferred to M2) | 1 | done |

#### Task 1.1 DoD

- [x] `test ! -e bin/booping-init` passes.
- [x] `test -x bin/booping-create-project` passes.
- [x] `grep -F "'.booping'" bin/booping-create-project` matches; `grep -F '.booping-project' bin/booping-create-project` is empty.
- [x] `mkdir -p` line in the script names all five dirs (`plans retrospectives lessons _booping requests`) — verified by five `grep -F` matches on the mkdir line.
- [x] Zero occurrences of `sprints.md`, `CLAUDE.md`, `sync-sprints`, `booping-plans set` in the script.
- [x] Usage comment + final echo mention `booping-create-project` (not `booping-init`).
- [x] Smoketest snippet from the M1 Verify block runs to completion with all `test` assertions passing.

#### Task 1.2 DoD

- [x] `grep -lF 'booping-init' README.md PRD.md` returns no files.
- [x] Repo `CLAUDE.md` either removes the `bin/booping-init` bullet from the stale list (deferred to M5 for the full Status-block rewrite) OR replaces it with a placeholder comment — either is acceptable for this task because M5 rewrites the block wholesale.
- [x] Risk register row records each file touched with a one-line description of the replacement.

---

### M2: Rewrite skills/install/SKILL.md to groom shape + delete template — 4 SP | done

**Goal**: `/install` mirrors the groom-shape contract with six phases, a researcher-junior delegation in Phase 3, and a three-file extension write in Phase 4. `skills/install/template-claude-md.md` is deleted; no skill references it.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# Template gone
test ! -e skills/install/template-claude-md.md
# Structure
grep -E '^## Preflight$'           skills/install/SKILL.md
grep -E '^## High-level workflow$' skills/install/SKILL.md
test "$(grep -cE '^## Phase [0-5] ' skills/install/SKILL.md)" = 6
grep -E '^## Hard rules$'          skills/install/SKILL.md
# Preflight references
for ref in \
  "../../docs/partial_project_resolution.md" \
  "../../docs/partial_plan_statuses.md" \
  "../../docs/partial_agents_researchers_delegator.md"; do
  grep -F "$ref" skills/install/SKILL.md || { echo "missing $ref"; exit 1; }
done
# Stale/forbidden tokens absent
test -z "$(grep -E '\.booping-project|booping-init|template-claude-md' skills/install/SKILL.md)"
# No "writes vault CLAUDE.md" language
test -z "$(grep -Ei 'Write a project .?CLAUDE\.md|seed a CLAUDE\.md|write the vault .?CLAUDE\.md|create a CLAUDE\.md' skills/install/SKILL.md)"
# Phase 3 researcher-junior delegation
awk '/^## Phase 3 /{f=1; next} /^## /{f=0} f' skills/install/SKILL.md | grep -F 'booping-researcher-junior'
# Phase 4 three-file write
awk '/^## Phase 4 /{f=1; next} /^## /{f=0} f' skills/install/SKILL.md | grep -F '_booping/agent_booping-developer.md'
awk '/^## Phase 4 /{f=1; next} /^## /{f=0} f' skills/install/SKILL.md | grep -F '_booping/skill_groom.md'
awk '/^## Phase 4 /{f=1; next} /^## /{f=0} f' skills/install/SKILL.md | grep -F '_booping/skill_develop.md'
# Skip-if-exists for attach mode
awk '/^## Phase 4 /{f=1; next} /^## /{f=0} f' skills/install/SKILL.md | grep -Ei 'skip.*exist|preserve existing'
# Marker canonical
grep -F '.booping' skills/install/SKILL.md
# Script name
grep -F 'booping-create-project' skills/install/SKILL.md
# Allowed-tools includes Agent + the new bash allows
grep -E '^[[:space:]]*-[[:space:]]*Agent[[:space:]]*$' skills/install/SKILL.md
grep -F 'Bash(booping-create-project:*)' skills/install/SKILL.md
grep -F 'Bash(booping-plans:*)' skills/install/SKILL.md
# Phase 5 seeds sprints.md (D13)
awk '/^## Phase 5 /{f=1; next} /^## /{f=0} f' skills/install/SKILL.md | grep -F 'booping-plans --format=md'
awk '/^## Phase 5 /{f=1; next} /^## /{f=0} f' skills/install/SKILL.md | grep -F 'sprints.md'
# Phase 4 stack-mismatch guard (D14)
awk '/^## Phase 4 /{f=1; next} /^## /{f=0} f' skills/install/SKILL.md | grep -Fi 'mismatch'
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Rewrite `skills/install/SKILL.md` from scratch to groom shape. **Read `skills/groom/SKILL.md`, `skills/chat/SKILL.md`, and `skills/retro/SKILL.md` in full before typing** so Preflight formatting and phase tone match. Frontmatter keeps `name: install`, `description`, `argument-hint: "[project-name]"`, `user-invocable: true`, `effort: high`; `allowed-tools:` becomes exactly: `Read, Write, Edit, Glob, Bash(ls ~/Claude/*), Bash(ls ~/Claude), Bash(ls -1 ~/Claude/*), Bash(ls -1 ~/Claude), Bash(ls -la ~/Claude/*), Bash(ls -la ~/Claude), Bash(pwd), Bash(booping-create-project:*), Bash(booping-plans:*), Agent, AskUserQuestion`. `## Preflight` loads `partial_project_resolution`, `partial_plan_statuses`, and `partial_agents_researchers_delegator` (all three by relative path `../../docs/…`). `## High-level workflow` is a six-item numbered list (Detect → Decide mode → Scaffold → Detect stack → Populate vault extensions → Verify & seed sprints.md). `## Phase 0 Detect` — native-tool detection per current skill (`ls ~/Claude/` + `Read` on `<cwd>/.booping`); one-paragraph state summary. `## Phase 1 Decide mode` — `AskUserQuestion` with `new / attach / cancel`; resolve project name (kebab-case, from `$ARGUMENTS` or CWD basename, confirmed by user). `## Phase 2 Scaffold` — new mode invokes `booping-create-project <project-name> <cwd>` via the `Bash(booping-create-project:*)` allow; `<cwd>` is captured via `pwd` at skill start; attach mode writes only `.booping` with user confirmation (content `project_name: <selected-name>`). `## Phase 3 Detect stack` — delegate to `booping-researcher-junior` with a compact brief listing target manifests (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Gemfile`, `Justfile`, `Makefile`, `.github/workflows/*`, `.pre-commit-config.yaml`) and the expected summary shape: `language`, `validations` (list of `{command, role}` pairs covering EVERY validation the project offers — tests, linters, typecheckers, formatters, security scanners, coverage, doctest — not restricted to "test + lint"), `hook_enforced_commands` (subset of validations that fires from a hook/CI config), `configured_manual_commands` (the complement), `env_notes`; researcher returns `unknown` for any field it can't resolve. `## Phase 4 Populate vault extensions` — present researcher findings as `AskUserQuestion` defaults (one prompt per field; user confirms or overrides); then write THREE extension files per D9 using the **exact skeletons** inlined in this plan's Design section (copy the fenced code blocks from the M2 architecture bullet into the skill body). Document the skip-if-exists rule for attach mode per D10 — verbatim "Skip writing any file that already exists non-empty; print `preserved existing: <path>` for each preserved file." In attach mode, also perform the D14 stack-mismatch guard on `_booping/agent_booping-developer.md`: compare the researcher's detected `language` with the first non-heading line under the existing file's `## Stack` header; on mismatch, run `AskUserQuestion` with three options (`keep existing` / `overwrite with detected` / `append new stack section`). `## Phase 5 Verify & seed sprints.md` — print `ls ~/Claude/{name}/`, confirm `.booping`, then run `booping-plans --format=md > ~/Claude/{name}/sprints.md` via Bash (the `Bash(booping-plans:*)` allow covers this) per D13, then suggest `/chat` or `/groom`. `## Hard rules` — three `- **` bullets as specified in Design. Delete every reference to `template-claude-md`, `booping-init`, `.booping-project`, and vault `CLAUDE.md` writes. | `skills/install/SKILL.md` (full rewrite) | 3 | done |
| 2.2 | Delete `skills/install/template-claude-md.md`. Every reference outside `CLAUDE.md` (which M5 rewrites wholesale) must be patched in this task. **Verifier** (run in the Done report, include command + full output in a fenced block per lesson 0002): (1) `test ! -e skills/install/template-claude-md.md` — expected: exits 0. (2) `grep -rlF 'template-claude-md' agents/ skills/ docs/ README.md PRD.md 2>/dev/null` — expected: empty. The `CLAUDE.md` hit is the single known exception and is explicitly out of scope for this task. | `skills/install/template-claude-md.md` (deleted); any additional hits outside `skills/install/SKILL.md` (already handled by 2.1) and `CLAUDE.md` (deferred to M5) | 1 | done |

#### Task 2.1 DoD

- [x] Frontmatter `allowed-tools:` matches the task-spec list exactly — **9** `Bash(...)` entries (six `ls` variants + `Bash(pwd)` + `Bash(booping-create-project:*)` + `Bash(booping-plans:*)`) + `Read`, `Write`, `Edit`, `Glob`, `Agent`, `AskUserQuestion`. Plan text originally said "10 Bash" — corrected to 9 to match the enumerated list in the task description, which is the actual spec.
- [x] `## Preflight` bullets match the three references in the M2 Verify loop.
- [x] `## High-level workflow` is a six-item numbered list with the exact phase names.
- [x] Phases `## Phase 0 Detect`, `## Phase 1 Decide mode`, `## Phase 2 Scaffold`, `## Phase 3 Detect stack`, `## Phase 4 Populate vault extensions`, `## Phase 5 Verify` exist in that order.
- [x] Phase 3 body names `booping-researcher-junior` and lists at least five of the target manifest filenames — 5x `grep -F`.
- [x] Phase 4 body names all three extension file paths — 3x `grep -F`.
- [x] Phase 4 body documents the skip-if-exists rule — `grep -Ei 'skip.*exist|preserve existing'`.
- [x] Phase 4 shows the three file body skeletons inline as fenced code blocks.
- [x] Phase 2 calls `booping-create-project` (not `booping-init`); `grep -F 'booping-init' skills/install/SKILL.md` is empty.
- [x] `## Hard rules` has exactly three `- **` bullets — `awk '/^## Hard rules$/{f=1; next} /^## /{f=0} f && /^- \*\*/' skills/install/SKILL.md | wc -l` returns 3.
- [x] `grep -E '\.booping-project|template-claude-md' skills/install/SKILL.md` is empty.
- [x] `grep -Ei 'Write a project .?CLAUDE\.md|seed a CLAUDE\.md|create a CLAUDE\.md' skills/install/SKILL.md` is empty.

#### Task 2.2 DoD

- [x] `test ! -e skills/install/template-claude-md.md` passes.
- [x] `grep -rlF 'template-claude-md' agents/ skills/ docs/ README.md PRD.md 2>/dev/null` returns no files. (`CLAUDE.md` is intentionally excluded — M5 owns its rewrite.)

---

### M3: Rewrite skills/help/SKILL.md to groom shape with current content — 2 SP | done

**Goal**: `/help` mirrors the groom-shape contract with a lean Preflight and a two-phase body. Every stale fact is fixed: `.booping`, `/chat` owns `sprints.md`, no vault `CLAUDE.md` in the layout, `requests/` is listed, developer-agent roster matches the active mid/senior strategy.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
grep -E '^## Preflight$'           skills/help/SKILL.md
grep -E '^## High-level workflow$' skills/help/SKILL.md
test "$(grep -cE '^## Phase [0-9] ' skills/help/SKILL.md)" -ge 2
# Canonical marker
grep -F '.booping' skills/help/SKILL.md
test -z "$(grep -F '.booping-project' skills/help/SKILL.md)"
# sprints.md ownership
test -z "$(grep -F '/develop only' skills/help/SKILL.md)"
grep -F '/chat' skills/help/SKILL.md
# Layout diagram hygiene
grep -F 'requests/' skills/help/SKILL.md
test -z "$(grep -E '^\s*├── CLAUDE\.md|^\s*└── CLAUDE\.md' skills/help/SKILL.md)"
# No dormant developer tier
test -z "$(grep -F 'booping-developer-junior' skills/help/SKILL.md)"
grep -F 'booping-developer-middle' skills/help/SKILL.md
grep -F 'booping-developer-senior' skills/help/SKILL.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Rewrite `skills/help/SKILL.md` from scratch. Frontmatter keeps `name: help`, `description`, `argument-hint: "[topic: skills \| agents \| layout \| workflow]"`, `user-invocable: true`, `effort: low`; `allowed-tools:` becomes exactly `Read, Bash(ls *)`. `## Preflight` loads only `partial_project_resolution` (per D11); no lesson load. `## High-level workflow` enumerates two phases: Dispatch topic → Render body. `## Phase 0 Dispatch topic` — empty `$ARGUMENTS` → Quickstart block; `{skills, agents, layout, workflow}` → matching inline section; anything else → full document. `## Phase 1 Render body` — the inline sections (Quickstart / Skills / Agents / Layout / Workflow / Hard rules / See also). Body rewrite: **Skills table** lists only the seven user-invocable skills, `/install` and `/help` first, then `/chat /groom /develop /retro /learn`, in that order; each row's `Writes` column reflects current truth (e.g. `/install` writes `~/Claude/{project}/*`, `.booping`; `/chat` writes `sprints.md`; `/develop` writes plan progress only; `/learn` writes `lessons/`, `_booping/*.md`). **Agents section** lists researchers (junior/middle/senior) and developers (**middle, senior only** per D12; junior exists on disk but is not in the active strategy). **Layout diagram** shows `~/Claude/` → `{project}/` with `plans/`, `requests/`, `retrospectives/`, `lessons/`, `_booping/`, `sprints.md` — and **no** `CLAUDE.md`, `Notebook.md`, or `notes/`. Annotate `sprints.md` with `# regenerated by /chat`. **Workflow** block shows the same five-skill arc as before but updated: `/chat` regenerates `sprints.md` on orient; `/groom` writes to `requests/` + `plans/`; `/retro` transitions `awaiting-retro → awaiting-learning`. **Hard rules** — one bullet: never write files; hand off scaffolding to `/install`. **See also** — README.md and `docs/partial_project_resolution.md`. Project resolution line at the top of Quickstart reads `Current project resolution: .booping marker in CWD → ask.` | `skills/help/SKILL.md` (full rewrite) | 2 | done |

#### Task 3.1 DoD

- [x] `## Preflight` is present and loads `partial_project_resolution` only (no `partial_read_lessons`, no delegator reads) — verified by `grep -F 'partial_read_lessons' skills/help/SKILL.md` returning empty.
- [x] `## High-level workflow` is a two-item numbered list (Dispatch topic → Render body).
- [x] `## Phase 0 Dispatch topic` and `## Phase 1 Render body` both exist (phase headers use em-dash: `## Phase 0 — Dispatch topic` / `## Phase 1 — Render body` — matches the Verify regex).
- [x] Skills table lists exactly seven rows (one per user-invocable skill) — verified by counting `|` lines in the table.
- [x] Agents section contains `booping-researcher-{junior,middle,senior}` (or three explicit rows); developers section lists `booping-developer-middle` and `booping-developer-senior` only.
- [x] `grep -F 'booping-developer-junior' skills/help/SKILL.md` returns empty.
- [x] Layout diagram contains `requests/` and does NOT contain `CLAUDE.md`, `Notebook.md`, or `notes/` inside the `~/Claude/{project}/` tree.
- [x] Hard rules has exactly one `- **` bullet.

---

### M4: Excise vault CLAUDE.md from trustworthy skills + partials — 4 SP | done

**Goal**: Vault `CLAUDE.md` ceases to be a first-class artifact across the plugin. No trustworthy skill reads or edits it; `docs/partial_learn_targets.md` drops the target; `docs/partial_project_resolution.md` documents the excision.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# No vault CLAUDE.md reads/edits in trustworthy skills
for f in skills/chat/SKILL.md skills/develop/SKILL.md skills/learn/SKILL.md skills/retro/SKILL.md skills/groom/SKILL.md; do
  # Forbidden: Read of the vault CLAUDE.md, or "vault CLAUDE.md" prose phrase, or git add including vault CLAUDE.md
  if grep -E 'Read.*~/Claude/\{project_name\}/CLAUDE\.md|the vault `CLAUDE\.md`|vault `CLAUDE\.md`' "$f"; then
    echo "FAIL: vault CLAUDE.md still referenced in $f"; exit 1
  fi
done
# /learn Phase 5 commit no longer stages vault CLAUDE.md
awk '/^## Phase 5 /{f=1; next} /^## /{f=0} f' skills/learn/SKILL.md | grep -F 'git add' | grep -F 'lessons/ _booping/' | grep -vF 'CLAUDE.md'
# partial_learn_targets drops the row
test -z "$(grep -F 'vault-claude-md' docs/partial_learn_targets.md)"
test -z "$(grep -F '~/Claude/<project>/CLAUDE.md' docs/partial_learn_targets.md)"
# partial_project_resolution documents the excision
grep -Fi 'vault CLAUDE.md' docs/partial_project_resolution.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Edit `skills/chat/SKILL.md`. Use semantic anchors (grep-matched phrases), not line numbers. (a) Delete the Preflight bullet whose text is verbatim `Read \`~/Claude/{project_name}/CLAUDE.md\` — vault and project conventions.` — anchor: the leading `- Read \`~/Claude/{project_name}/CLAUDE.md\``. (b) In the wide-domain paragraph (the paragraph whose first sentence ends with `Project-specific behavior lives in \`_booping/skill_chat.md\`, lessons, and the vault \`CLAUDE.md\`.`), replace that sentence with `Project-specific behavior lives in \`_booping/skill_chat.md\` and lessons.`. No other edits. | `skills/chat/SKILL.md` | 1 | done |
| 4.2 | Edit `skills/develop/SKILL.md`. Use semantic anchors. (a) In Phase 0, the sentence `Read the plan file, the vault \`CLAUDE.md\`, and the repo \`CLAUDE.md\`.` (anchored by `Read the plan file, the vault`) becomes `Read the plan file and the repo \`CLAUDE.md\`.`. (b) In the wide-domain paragraph (the paragraph starting `This skill is **wide-domain**`), the clause ` live in \`_booping/skill_develop.md\`, lessons, and the vault \`CLAUDE.md\`` becomes ` live in \`_booping/skill_develop.md\` and lessons`. No other edits. | `skills/develop/SKILL.md` | 1 | done |
| 4.3 | Edit `skills/learn/SKILL.md` and `docs/partial_learn_targets.md`. Use semantic anchors. (a) In `skills/learn/SKILL.md`'s wide-domain paragraph (first paragraph starting `This skill is **wide-domain**`), the clause ` live in \`_booping/skill_learn.md\`, lessons, and the vault \`CLAUDE.md\`` becomes ` live in \`_booping/skill_learn.md\` and lessons`. (b) Preflight: no change. (c) In Phase 1.5, delete the bullet whose text begins `Read the vault \`CLAUDE.md\` and the attached repo's \`CLAUDE.md\` in full` and replace with `Read the attached repo's \`CLAUDE.md\` in full.`. (d) In Phase 3, delete the bullet `- Vault \`CLAUDE.md\` and repo \`CLAUDE.md\` — one-line bullet additions; no paragraph rewrites.` and replace with `- Repo \`CLAUDE.md\` — one-line bullet additions; no paragraph rewrites.`. (e) In Phase 5's first `git add` line (anchored by `git add lessons/ _booping/ CLAUDE.md plans/<plan-filename>.md`), drop ` CLAUDE.md` — result: `git add lessons/ _booping/ plans/<plan-filename>.md`. (f) In `docs/partial_learn_targets.md`, delete the entire `vault-claude-md` table row (anchored by `\| \`vault-claude-md\``). Four base types remain. **Verifier:** `grep -F 'vault-claude-md' docs/partial_learn_targets.md` returns no matches; the row deletion reduces the data-row count by one. | `skills/learn/SKILL.md`, `docs/partial_learn_targets.md` | 1 | done |
| 4.4 | Edit `skills/retro/SKILL.md`, `skills/groom/SKILL.md`, and `docs/partial_project_resolution.md`. Use semantic anchors. (a) `skills/retro/SKILL.md`: in the wide-domain paragraph, the sentence `Project-specific concerns live in \`_booping/skill_retro.md\`, lessons, and the vault \`CLAUDE.md\`.` becomes `Project-specific concerns live in \`_booping/skill_retro.md\` and lessons.`. (b) `skills/groom/SKILL.md`: in the wide-domain paragraph (first paragraph after the title), the clause ` live in lessons, \`CLAUDE.md\`, and \`_booping/skill_groom.md\`` becomes ` live in lessons and \`_booping/skill_groom.md\``. (c) `skills/groom/SKILL.md` Phase 1 "Understand": the **Re-read constraints** bullet's text `the relevant \`CLAUDE.md\` sections, project extensions, and applicable lessons` becomes `project extensions and applicable lessons`. (d) `skills/groom/SKILL.md` "What groom does NOT do" section: the bullet ending `…Those live in \`_booping/skill_groom.md\`, lessons, and \`CLAUDE.md\`.` becomes `…Those live in \`_booping/skill_groom.md\` and lessons.`. (e) Append a new closing paragraph to `docs/partial_project_resolution.md` (below the existing bullet list): `\n\n## Vault CLAUDE.md excised\n\nVault \`CLAUDE.md\` is no longer a booping artifact. Project-specific overrides live in \`~/Claude/{project_name}/_booping/skill_<name>.md\` and \`~/Claude/{project_name}/_booping/agent_<name>.md\`; cross-cutting rules flow through \`~/Claude/{project_name}/lessons/\`. Skills never read or edit vault \`CLAUDE.md\`.`. | `skills/retro/SKILL.md`, `skills/groom/SKILL.md`, `docs/partial_project_resolution.md` | 1 | done |

#### Task 4.1 DoD

- [x] `grep -F "~/Claude/{project_name}/CLAUDE.md" skills/chat/SKILL.md` is empty.
- [x] `grep -F 'vault \`CLAUDE.md\`' skills/chat/SKILL.md` is empty.
- [x] The Preflight section still has at least four bullets (only one was removed — now 5).

#### Task 4.2 DoD

- [x] Phase 0 line reads `Read the plan file and the repo \`CLAUDE.md\`.` (or equivalent phrasing without `vault`).
- [x] `grep -F 'vault \`CLAUDE.md\`' skills/develop/SKILL.md` is empty.
- [x] `grep -F 'the repo \`CLAUDE.md\`' skills/develop/SKILL.md` still matches (unaffected).

#### Task 4.3 DoD

- [x] `grep -F 'vault \`CLAUDE.md\`' skills/learn/SKILL.md` is empty.
- [x] Phase 5 `git add` line: `grep -F 'git add lessons/ _booping/ plans/' skills/learn/SKILL.md` matches; `grep -F 'git add lessons/ _booping/ CLAUDE.md' skills/learn/SKILL.md` is empty.
- [x] `docs/partial_learn_targets.md` no longer contains a row with `vault-claude-md` or `~/Claude/<project>/CLAUDE.md` — two `grep -F` return empty.
- [x] The matrix still has four rows of data — counted via `awk '/^\| `/{count++} END{print count}' docs/partial_learn_targets.md` returning 4 (or equivalent).

#### Task 4.4 DoD

- [x] `grep -F 'vault \`CLAUDE.md\`' skills/retro/SKILL.md skills/groom/SKILL.md` is empty.
- [x] `grep -F 'vault CLAUDE.md' docs/partial_project_resolution.md` matches the new closing paragraph.
- [x] `docs/partial_project_resolution.md` closing paragraph explicitly names `_booping/skill_<name>.md`, `_booping/agent_<name>.md`, and `lessons/` as the replacement channels — three `grep -F`.

---

### M5: Cleanup — delete claude-booping vault CLAUDE.md + update repo CLAUDE.md + README — 3 SP | done

**Goal**: `~/Claude/claude-booping/CLAUDE.md` is gone. Repo `CLAUDE.md` "Status (April 2026)" block reflects the new trustworthy set + renamed script. `README.md` layout diagram + sub-agent table match current truth.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# Vault CLAUDE.md deletion (in the project's own vault only)
test ! -e ~/Claude/claude-booping/CLAUDE.md
# Repo CLAUDE.md Status block
grep -F 'skills/install/SKILL.md' CLAUDE.md | head -1 | grep -vE 'Stale|treat as broken'
grep -F 'skills/help/SKILL.md'   CLAUDE.md | head -1 | grep -vE 'Stale|treat as broken'
test -z "$(grep -F 'bin/booping-init' CLAUDE.md)"
grep -F 'bin/booping-create-project' CLAUDE.md
test -z "$(grep -F 'skills/install/template-claude-md.md' CLAUDE.md)"
# Stale block no longer lists /install or /help
awk '/Stale and \*\*not refactored/{f=1} /^## /{f=0} f' CLAUDE.md | grep -E 'skills/install|skills/help|install/SKILL|help/SKILL'
test $? -ne 0  # grep returns 1 when no match — that's the pass case
# README layout diagram
test -z "$(grep -F '│   ├── CLAUDE.md' README.md)"
test -z "$(grep -F 'Notebook.md' README.md)"
test -z "$(grep -F '├── notes/' README.md)"
grep -F 'requests/' README.md
# sprints.md attribution
test -z "$(grep -F 'written ONLY by /develop' README.md)"
# Developer roster
awk '/Developer agents —/{f=1; next} /^## /{f=0} f' README.md | grep -F 'booping-developer-junior'
test $? -ne 0  # junior row removed
awk '/Developer agents —/{f=1; next} /^## /{f=0} f' README.md | grep -F 'booping-developer-middle'
awk '/Developer agents —/{f=1; next} /^## /{f=0} f' README.md | grep -F 'booping-developer-senior'
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Delete `~/Claude/claude-booping/CLAUDE.md`. Commit from the vault: `cd ~/Claude/claude-booping && git rm CLAUDE.md && git commit -m "vault: drop CLAUDE.md per plugin refactor"`. Do NOT touch any other vault under `~/Claude/` — per D8, other users' vaults are out of scope. | `~/Claude/claude-booping/CLAUDE.md` (deleted) | 1 | done |
| 5.2 | Update repo `CLAUDE.md` "Status (April 2026)" block wholesale: (a) the **Current and trustworthy** list now contains `skills/groom`, `skills/chat`, `skills/develop`, `skills/retro`, `skills/learn`, `skills/install`, `skills/help`, plus `agents/booping-researcher-{senior,middle,junior}.md`, `agents/booping-developer-{junior,middle,senior}.md`, `bin/booping-plans`, `bin/booping-create-project`, and `docs/` contents; (b) the **Stale** list is reduced to whatever actually remains stale (if anything) — `bin/booping-init` line removed, `skills/install/template-claude-md.md` line removed, `skills/{install,help}` lines removed. If the stale list is empty after these removals, replace it with "Nothing currently stale — if you spot drift, file it as a new groom request." Replace `bin/booping-init` everywhere it still appears in the file with `bin/booping-create-project` (one hit at groom time; verify by grep at task time). | `CLAUDE.md` | 1 | done |
| 5.3 | Update `README.md`: (a) layout diagram: remove the `├── CLAUDE.md  # project instructions` line, the `├── Notebook.md  # active scratch pad` line, and the `├── notes/  # freeform research, user stories` line; annotate `├── sprints.md  # regenerated by /chat` (replacing `# sprint registry — written ONLY by /develop`); add `├── requests/  # /groom input: user-request files` under `plans/`. (b) sub-agent table: remove the `booping-developer-junior` row; keep `booping-developer-middle` and `booping-developer-senior` with updated role descriptions matching `partial_agents_strategy_mid_senior.md` (middle: 1–2 SP batched; senior: 3–4 SP design-judgment). Leave all other README content untouched. | `README.md` | 1 | done |

#### Task 5.1 DoD

- [x] `test ! -e ~/Claude/claude-booping/CLAUDE.md` passes.
- [x] `cd ~/Claude/claude-booping && git log --oneline -1 -- CLAUDE.md` shows a deletion commit (SHA `a04e20b`).
- [x] Other vaults under `~/Claude/` are not touched — `aurora-api`, `dotfiles`, `smoketest` CLAUDE.md files still exist.

#### Task 5.2 DoD

- [x] `grep -F 'skills/install' CLAUDE.md` matches under the "Current and trustworthy" heading, NOT under "Stale" — stale block replaced with "Nothing currently stale" sentence.
- [x] `grep -F 'skills/help' CLAUDE.md` matches under "Current and trustworthy".
- [x] `grep -F 'bin/booping-init' CLAUDE.md` is empty.
- [x] `grep -F 'bin/booping-create-project' CLAUDE.md` matches.
- [x] `grep -F 'skills/install/template-claude-md.md' CLAUDE.md` is empty.

#### Task 5.3 DoD

- [x] `grep -F 'CLAUDE.md' README.md` matches only outside the layout diagram (it may still appear in prose elsewhere).
- [x] Layout diagram has no `Notebook.md`, no `notes/`, no `CLAUDE.md` line.
- [x] Layout diagram has a `requests/` line.
- [x] `grep -F 'written ONLY by /develop' README.md` is empty.
- [x] Sub-agent table: `grep -F 'booping-developer-junior' README.md` is empty.

---

## Final Verification

After all five milestones:

```bash
cd /home/anton/Dev/@A/claude-booping
# M1
test ! -e bin/booping-init
test -x bin/booping-create-project
# M2
test ! -e skills/install/template-claude-md.md
grep -E '^## Preflight$' skills/install/SKILL.md
test "$(grep -cE '^## Phase [0-5] ' skills/install/SKILL.md)" = 6
grep -F 'booping-researcher-junior' skills/install/SKILL.md
grep -F '_booping/agent_booping-developer.md' skills/install/SKILL.md
grep -F '_booping/skill_groom.md' skills/install/SKILL.md
grep -F '_booping/skill_develop.md' skills/install/SKILL.md
test -z "$(grep -E '\.booping-project|booping-init|template-claude-md' skills/install/SKILL.md)"
# M3
grep -E '^## Preflight$' skills/help/SKILL.md
test -z "$(grep -F '.booping-project' skills/help/SKILL.md)"
test -z "$(grep -F 'booping-developer-junior' skills/help/SKILL.md)"
test -z "$(grep -F '├── CLAUDE.md' skills/help/SKILL.md)"
# M4 — vault CLAUDE.md excision across trustworthy skills
for f in skills/chat/SKILL.md skills/develop/SKILL.md skills/learn/SKILL.md skills/retro/SKILL.md skills/groom/SKILL.md; do
  if grep -E 'Read.*~/Claude/\{project_name\}/CLAUDE\.md|vault `CLAUDE\.md`' "$f"; then
    echo "FINAL FAIL: vault CLAUDE.md still in $f"; exit 1
  fi
done
test -z "$(grep -F 'vault-claude-md' docs/partial_learn_targets.md)"
grep -Fi 'vault CLAUDE.md' docs/partial_project_resolution.md
# M5
test ! -e ~/Claude/claude-booping/CLAUDE.md
grep -F 'bin/booping-create-project' CLAUDE.md
test -z "$(grep -F 'bin/booping-init' CLAUDE.md)"
test -z "$(grep -F 'skills/install/template-claude-md.md' CLAUDE.md)"
test -z "$(grep -F '├── CLAUDE.md' README.md)"
test -z "$(grep -F 'written ONLY by /develop' README.md)"
```

All assertions must pass cleanly.

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `bin/booping-create-project` called from M1's smoketest in CI (or local) encounters a pre-existing `~/Claude/smoketest-proj`, errors, and blocks validation | low | The Verify block uses `mktemp -d` to choose a unique path; the script's existing `if [ -d "$ROOT" ]; then echo "Project already exists"; exit 1; fi` guard behaves correctly on a fresh tmp dir. |
| Attach-mode skip-if-exists (D10) leaves a partially-configured vault when only some of the three extension files exist | medium | M2 Phase 4 logs `preserved existing: <path>` per skipped file, surfacing the partial state to the user immediately. A future `/chat` orient will also flag the mismatch. Not a blocker for this sprint. |
| Attach-mode **stack mismatch** — preserving `_booping/agent_booping-developer.md` when the new attached repo's stack differs silently feeds agents the old vault's language context (Gemini-flagged, 2026-04-24) | medium | D14's stack-mismatch guard in Phase 4 runs the comparison and prompts the user via `AskUserQuestion` before proceeding. The worker Done report for Phase 4 includes the comparison output. |
| `sprints.md` absent on a fresh vault crashes `/develop` Phase 4's `git add sprints.md` when the user path is `/install` → `/groom` → `/develop` without a `/chat` step (Gemini-flagged, 2026-04-24) | medium | D13 seeds `sprints.md` in `/install` Phase 5 via `booping-plans --format=md`. First `/chat` orient overwrites with the regenerated snapshot; seeding is idempotent. |
| Researcher-junior stack detection returns an incorrect or thin summary for unusual stacks (monorepos, polyglot repos, exotic build tools) | medium | Findings are presented as **defaults** via `AskUserQuestion`, not auto-written. The user confirms or overrides each field. Briefing tells the researcher to return `unknown` for any field it can't resolve — the user fills it in manually. |
| `/chat` Preflight change (removing vault CLAUDE.md read) breaks a chat session that relied on project-specific instructions there | medium | For the only vault we delete in-scope (`~/Claude/claude-booping/`), the file's contents are layout boilerplate + a Project-specific notes section. The notes are all observations already encoded in this repo's root `CLAUDE.md` or in skill bodies. Other vaults keep their file on disk; consumer skills simply stop reading it — no runtime error, just unreferenced content. |
| Removing the `vault-claude-md` target from `docs/partial_learn_targets.md` (M4 Task 4.3) leaves future retros with lessons that no longer have a home when the rule is a vault-fact | low | The matrix still carries `skill-ext`, `agent-ext`, and `lesson` — any project-fact-shaped rule now decomposes into a `skill-ext` (if skill-specific), an `agent-ext` (if agent-specific), or a `lesson` (if cross-cutting). The decomposition rule in `partial_learn_targets.md` already covers this. |
| Gemini cross-validation flags the three-file extension write (D9) as over-engineered for a single project config | low | The split is user-driven and matches the scoping check in lesson 0004. If Gemini raises this as an Architectural Blind Spot, record in the Risk register with explicit user acceptance per `partial_cross_validation.md`. |
| M2 Task 2.1 agent executes Phase 4's three-file skeletons without respecting attach-mode skip-if-exists | medium | Task 2.1 DoD explicitly requires the skip-if-exists language in Phase 4's body; M2 Verify enforces a `grep -Ei 'skip.*exist\|preserve existing'` check. Worker must produce text matching this — the prose change IS the task output. |
| Excising vault CLAUDE.md across five skills in M4 collides with an in-progress session in another repo where vault CLAUDE.md is still relied on | low | Only `~/Claude/claude-booping/CLAUDE.md` is deleted in this sprint (D8). Consumer skills stop reading vault CLAUDE.md, so existing files in other vaults become dead data — they do not break any skill. Users aware of the refactor can delete their own vault CLAUDE.md when convenient. |
| The smoketest in M1 Verify assumes `bin/booping-create-project` on PATH; it may not be on PATH until plugin reload | low | Verify block uses `bin/booping-create-project …` (repo-relative path), not `booping-create-project` (PATH lookup). |
| Reviewer surfaces follow-ups during M2/M4 (wording slips, phase-body nits) | medium | Per-milestone triage: S0–S1 fix-now; S2+ cap of three deferred items per milestone, else promote to a follow-up stub plan. |

## Out of scope

- Other users' vault `CLAUDE.md` files (`~/Claude/aurora-api/CLAUDE.md`, `~/Claude/dotfiles/CLAUDE.md`, `~/Claude/smoketest/CLAUDE.md`, `~/Claude/_backup/CLAUDE.md`) — per D8, users clean up manually once the consumer skills stop reading the file.
- `docs/template_plan.md` + `docs/partial_plan_quality_checklist.md` `CLAUDE.md impact` section — that refers to **repo** CLAUDE.md (not vault); unchanged.
- `docs/partial_development_quality_checks.md` mention of "the repo `CLAUDE.md`" — that's the attached-repo CLAUDE.md, not vault; unchanged.
- Dynamic skill/agent enumeration in `/help` (rejected in favor of inline body per D6).
- Researcher delegation for `/help` (rejected per D1).
- `booping-developer-junior` agent file itself — stays on disk as an inactive tier. Removing it is a separate strategy decision and belongs in a different plan.
- Restructuring `docs/partial_learn_targets.md` beyond the single row deletion (e.g. renaming the matrix, renumbering types).
- Pytest harness for `bin/booping-create-project` — overridden by the user-set "No tests" policy per repo `CLAUDE.md`.
- Migrating existing plans' Verify blocks to reference project-seeded extension files — plan rewrites are out of scope; the next `/groom` run per project naturally picks up the new extensions.

## CLAUDE.md impact

In-scope: repo-root `CLAUDE.md` "Status (April 2026)" block — owned by Task 5.2. Moves `/install` and `/help` into the "Current and trustworthy" list. Renames `bin/booping-init` → `bin/booping-create-project` wherever it appears. Drops `bin/booping-init` and `skills/install/template-claude-md.md` from the stale list. Consolidates any remaining stale entries or marks the list empty. No other `CLAUDE.md` sections touched. Per-vault `CLAUDE.md` under `~/Claude/{project}/` is being **excised** as a booping artifact (D4) — not updated, not maintained; `~/Claude/claude-booping/CLAUDE.md` is deleted in-scope per D8.
