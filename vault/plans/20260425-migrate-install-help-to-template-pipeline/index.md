---
title: Migrate /install and /help skills to template pipeline
type: refactoring
status: cancelled
sp: 9
split_from: null
created: 2026-04-25 00:00
planned: 20260425 10:33
started: null
completed: 2026-04-26 12:25
retro: null
goal: null
superseded_by: plans/20260426-migrate-install-help-template-pipeline-cli.md
summary: "Migrate /install and /help to templates using config-resident skill summaries and a new _agents_roster.j2 macro"
---

# Migrate /install and /help skills to template pipeline

## Context

`/groom` shipped the template pipeline; `/develop`'s migration is `ready-for-dev`. `/install` and `/help` are still hand-authored under `skills/install/SKILL.md` and `skills/help/SKILL.md` and both reference infrastructure that no longer exists:

- Both preflight on `docs/partial_project_resolution.md`; `/install` also preflights on `docs/partial_agents_researchers_delegator.md`.
- `/install` Phase 3 delegates stack detection to `booping-researcher-junior` — an agent removed when the researcher tiers were consolidated to the single `booping-researcher` (sonnet, effort high) defined in `agents/booping-researcher.md`.
- `/help` lists all three retired researcher tiers in its **Agents** section, cites `docs/partial_agents_researchers_delegator.md` and `docs/partial_agents_strategy_mid_senior.md` as live references, prints a **Workflow** block with the pre-plans-as-data lifecycle (no `in-spec`, no `awaiting-plan-review`, no `awaiting-learning`), and ends with a See-also pointing at `PRD.md` (file does not exist in repo).

After this plan, both `SKILL.md` files are generated from templates under `src/templates/skills/`. Their rendered bodies use config-driven data wherever a structured surface exists (skill summaries, write-targets, agent rosters), and only literal prose for content with a single consumer (workflow ASCII, file skeletons live in `src/docs/` lazy-loads). Stale references to retired researcher tiers and obsolete partials are gone. `/help`'s Workflow block matches the current lifecycle (`backlog → in-spec → awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro → awaiting-learning → done`).

## Decisions

- **`/install` skips `_project_context.j2`.** The partial reports the resolved project/vault. `/install`'s job is to *create* the vault; its Phase 0 enumerates `~/Claude/*`, reads `.booping`, and summarizes state — covering and exceeding what the partial offers. `/help` does include `_project_context.j2` for the Quickstart personalization touch.
- **Keep `/install`'s Phase 0..5 structure.** The CLAUDE.md anti-pattern targets skills whose flow is the plan state machine. `/install` has no plan-transitions table — it bootstraps a vault and has genuinely sequential branches. Phases stay.
- **Move `/install`'s three vault-extension file skeletons to `src/docs/install_extension_files.md` and lazy-load.** Reason: the four-check IA pass (lesson 0004) flags hierarchy — top-level orchestrator prompts describe *what*/*when*; the *how* (60 lines of file templates) belongs one layer down. Trade-off accepted: one extra Read tool call per `/install` invocation in exchange for hierarchy correctness and a smaller skill body. The doc is one file with three sections (one per extension file); the skill body keeps the bullet that names the three target paths and lazy-loads the doc when entering Phase 4.
- **Render `/help`'s Skills table from config.** Extend `config.skills.<name>` with `summary` (one-line plugin-wide purpose; same as the SKILL.md `description` first sentence) and `writes` (string describing what the skill writes, free-form). Render the Skills table in `help.md.j2` via `{% for name, s in config.skills.items() %}`. Reason: removing the second source of truth — the table currently duplicates frontmatter `description` fields and will drift. Workflow block stays ASCII prose: cross-skill arrows aren't a structured surface worth modeling, the consequence of drift is small (state names match config and are spot-checked in DoD), and rendering ASCII art programmatically is more cost than benefit.
- **Introduce a dedicated `_agents_roster.j2` macro for `/help`'s Agents glossary.** Reason: `_available_agents.j2` is shaped for delegation context (good_for/bad_for bullets describing when a caller should pick this agent). `/help`'s Agents section is documentation describing each agent's plugin-wide role for a human reader — overloading the same macro couples two concerns. The new macro reads `config.skills.help.agents` and renders a description-style block. `_available_agents.j2` is unchanged.
- **`skills.install.agents.booping-researcher` is scoped narrowly** — Phase 3 stack detection only. Distinct `good_for`/`bad_for` from `/groom`.
- **Mandatory backup before template work.** Each migration milestone copies the authored `skills/<name>/SKILL.md` to `/tmp/<name>-skill-backup-{timestamp}.md` *before* the template file is created. Reason: `bin/booping-build` overwrites the destination; if an agent runs the build before the template is complete, source material is destroyed. The backup is the recovery path. Backup files are gitignored by `.tmp` convention and not committed.
- **No automated tests for this refactor.** Project policy is "No tests" (CLAUDE.md → CLI section). Verification is via `bin/booping-build` exit code, `git diff` review of regenerated files, `rg` confirmation that stale references are absent, and visual inspection against the claude-skill Quality Checklist. Acceptance is explicit (recorded here so retro doesn't revisit).

## Architecture

Load-time inputs for the rendered `skills/install/SKILL.md`:

- No `_project_context.j2` include — Phase 0 owns detection.
- `{{ available_agents.render("install") }}` — single-agent roster (`booping-researcher`) from `config.skills.install.agents`.
- Phase 4 lazy-loads `src/docs/install_extension_files.md` (the three skeletons) — link inline; not embedded.
- Inline Phase 0..5 prose with Phase 3 briefing template kept inline.
- `!`bin/booping-lessons`` — active lessons inlined before Hard rules.
- `!`bin/booping-extra-instructions skill_install.md`` — project-local extension inlined at end of body.

Load-time inputs for the rendered `skills/help/SKILL.md`:

- `{% include "_partials/_project_context.j2" %}` — `!`bin/booping-project-name`` inline, feeding the Quickstart personalization note.
- `{% for name, s in config.skills.items() %}` loop in body renders the **Skills** table from `config.skills.<name>.summary` and `.writes`.
- `{{ agents_roster.render("help") }}` — full plugin roster (researcher + two developers) rendered into the **Agents** section by the new `_agents_roster.j2` macro.
- Inline prose for Quickstart / Layout / Workflow / Hard rules / See also blocks. Workflow uses the current lifecycle; See also drops the dead `PRD.md` reference.
- `!`bin/booping-lessons`` and `!`bin/booping-extra-instructions skill_help.md``.

Skill/agent boundary: unchanged. `/install` owns every write under `~/Claude/{project}/`; the researcher agent returns a summary only. `/help` is read-only.

## Milestones

### M1: Config expansion + new macro — 2 SP | pending

**Goal**: `src/config.yaml` carries `skills.install.*`, `skills.help.*`, and a `summary` + `writes` field on every existing skill entry. New `src/templates/_partials/_agents_roster.j2` macro present and validated against a build. No skill-body changes yet; `skills/install/SKILL.md` and `skills/help/SKILL.md` still hand-authored. Existing generated `skills/groom/SKILL.md` unchanged byte-for-byte.

**Verify**: `bin/booping-build` exits 0; `git diff skills/groom/SKILL.md` is empty.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Extend `skills.<name>` schema with `summary` + `writes`; add entries for all skills (groom, install, help, chat, develop, retro, learn) | `src/config.yaml` | 1 | pending |
| 1.2 | Add `skills.install.agents.booping-researcher` (stack-detection scope) and `skills.help.agents` roster (researcher + developer-middle + developer-senior, plugin-wide role descriptions); add `effort` for both | `src/config.yaml` | — | pending |
| 1.3 | Author `src/templates/_partials/_agents_roster.j2` and confirm `bin/booping-build` still exits 0 (macro is unused at this point) | `src/templates/_partials/_agents_roster.j2` | 1 | pending |

Tasks 1.1 and 1.2 grouped — both small config-only edits. Task 1.3 is grouped with them as a single briefing per the ≤ 1 SP group threshold.

#### Task 1.1 DoD

- [ ] Every key under `skills.<name>` (groom, install, help, chat, develop, retro, learn) has a `summary` field — one sentence, plugin-wide purpose, sourced from the corresponding skill's frontmatter `description` first sentence (verbatim where it reads cleanly).
- [ ] Every key under `skills.<name>` has a `writes` field — free-form string describing what the skill writes (e.g. `"~/Claude/{project}/*, .booping"` for install; `"plan progress marks (DoD + status)"` for develop; `"—"` for help / chat-orient-only-side-effects).
- [ ] `bin/booping-build` exits 0.

#### Task 1.2 DoD

- [ ] `skills.install.effort: high` present.
- [ ] `skills.install.agents.booping-researcher.good_for` covers "scan stack-signal files (pyproject.toml, package.json, Cargo.toml, go.mod, Gemfile, Justfile, Makefile, .github/workflows, .pre-commit-config.yaml, README.md, CONTRIBUTING.md) and return a compact language + validations + hook-enforced vs manual + env summary".
- [ ] `skills.install.agents.booping-researcher.bad_for` covers "writing files under ~/Claude/" and "deciding stack defaults on the user's behalf".
- [ ] `skills.help.effort: low` present.
- [ ] `skills.help.agents` contains exactly three entries: `booping-researcher`, `booping-developer-middle`, `booping-developer-senior`.
- [ ] Each `skills.help.agents.<name>` entry's `good_for` / `bad_for` describes the agent's **plugin-wide role** (researcher: "wide reads, summarization, web research"; developer-middle: "1–2 SP tasks, batchable per briefing"; developer-senior: "3–4 SP design-judgment tasks, one per briefing"). Wording is **documentation-shaped**, not delegation-shaped — these bullets are read by humans browsing `/help`, not by an orchestrator deciding who to call.
- [ ] `bin/booping-build` exits 0.

#### Task 1.3 DoD

- [ ] `src/templates/_partials/_agents_roster.j2` exists and exports a `render(skill)` macro.
- [ ] The macro structure mirrors `_available_agents.j2` but renders documentation-shaped output: each agent rendered with name + `good_for` (relabeled or restructured to read as "Role" / "Suited to") + `bad_for` (relabeled to "Not used for"). Exact label wording is the implementer's choice; the test is "reads as documentation, not delegation guidance".
- [ ] `_available_agents.j2` is **unchanged** (`git diff src/templates/_partials/_available_agents.j2` is empty).
- [ ] `bin/booping-build` exits 0; macro is unused (no template imports it yet).

---

### M2: Render install.md.j2 + extension-files doc — 3 SP | pending

**Goal**: `skills/install/SKILL.md` is a generated artifact. Stale `booping-researcher-junior` reference replaced. `partial_agents_researchers_delegator.md` and `partial_project_resolution.md` no longer referenced from `/install`. Phase 0..5 structure preserved. The three vault-extension skeletons live in `src/docs/install_extension_files.md`, lazy-loaded from Phase 4.

**Verify**: `bin/booping-build && git diff skills/install/SKILL.md`; rendered body inspected against the claude-skill Quality Checklist; `src/docs/install_extension_files.md` reads cleanly as a standalone reference.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Backup current `skills/install/SKILL.md` and extract its three file skeletons into a new lazy-load doc | `/tmp/install-skill-backup-<ts>.md`, `src/docs/install_extension_files.md` | 1 | pending |
| 2.2 | Author `src/templates/skills/install.md.j2` and regenerate | `src/templates/skills/install.md.j2`, `skills/install/SKILL.md` | 2 | pending |

#### Task 2.1 DoD

**Sequence**:

1. `cp skills/install/SKILL.md /tmp/install-skill-backup-$(date +%Y%m%d-%H%M%S).md` — verify the backup file exists before any edit. Print the backup path so the user can recover if needed.
2. Create `src/docs/install_extension_files.md` containing:
   - One paragraph header explaining "These three files are written under `~/Claude/{project}/_booping/` by `/install` Phase 4. Each skeleton uses `{{placeholder}}` markdown markers as literal text — they are written as-is into the target file, with placeholders filled by `/install`'s orchestrator using the researcher's findings."
   - Three `## File: <path>` sections, each containing the corresponding skeleton transcribed verbatim from the current `skills/install/SKILL.md` Phase 4 (`agent_booping-developer.md`, `skill_groom.md`, `skill_develop.md`). Skeleton markdown is wrapped in fenced code blocks (` ```markdown ... ``` `) so that the `{{placeholder}}` markers display as code, not as live Jinja2 expressions consumed by any future templating layer.
- [ ] `/tmp/install-skill-backup-*.md` exists with the byte-identical content of the pre-migration `skills/install/SKILL.md`.
- [ ] `src/docs/install_extension_files.md` exists with three `## File:` sections.
- [ ] Each section's fenced code block matches the corresponding skeleton from the pre-migration SKILL.md byte-for-byte (running `diff -q` between extracted block and the SKILL.md skeleton produces no output).
- [ ] No skeleton placeholder is interpreted as a Jinja2 expression — `bin/booping-build` exits 0 even though the template pipeline does not (yet) reference this doc.

#### Task 2.2 DoD

**Sequence (order matters — `bin/booping-build` overwrites `skills/install/SKILL.md`)**:

1. **Confirm the backup from Task 2.1 exists.** If absent, halt and re-run Task 2.1.
2. Read `skills/install/SKILL.md` (or the backup) and transcribe its `allowed-tools` list verbatim into the new template's frontmatter. Keep `argument-hint`, `user-invocable`. Move `effort` to `effort: {{ config.skills.install.effort }}`.
3. Transcribe Phase 0..5 prose verbatim from the current `skills/install/SKILL.md`, **except**:
   - The two Preflight bullets ("Read and resolve project..." and "Read research agents...") are replaced with `{{ available_agents.render("install") }}`.
   - Phase 3 narrative replaces every mention of `booping-researcher-junior` with `booping-researcher`. Briefing fenced block preserved verbatim except the agent name.
   - Phase 4 replaces the three inline file skeletons with one paragraph naming the three target paths (`~/Claude/{project}/_booping/agent_booping-developer.md`, `~/Claude/{project}/_booping/skill_groom.md`, `~/Claude/{project}/_booping/skill_develop.md`) plus a single sentence "Each file's content is specified in [extension-file skeletons](../../src/docs/install_extension_files.md). Read that doc when entering Phase 4." The skip-if-exists rule and stack-mismatch guard prose stay inline (they're decision logic, not file content).
4. Use `src/templates/skills/groom.md.j2` as the reference for `!`bin/…`` inline-command syntax — copy the exact form (backtick + exclamation + backtick + path + backtick + backtick).
5. Run `bin/booping-build` once after the template is complete.

**Structural DoD**:

- [ ] Frontmatter: `effort: {{ config.skills.install.effort }}`; `allowed-tools` list transcribed verbatim from the pre-build `skills/install/SKILL.md` (including `Bash(booping-create-project:*)`, `Bash(booping-plans:*)`, `Agent`, `AskUserQuestion`, all `ls` / `pwd` entries).
- [ ] `argument-hint: "[project-name]"` and `user-invocable: true` preserved.
- [ ] Preflight section carries `{{ available_agents.render("install") }}` and nothing else.
- [ ] Phase 0 "Detect" unchanged in semantics: `pwd`, `ls ~/Claude/`, read `.booping` with `Glob` backup, summarize state.
- [ ] Phase 1 "Decide mode" unchanged: `AskUserQuestion` with new/attach/cancel, name resolution.
- [ ] Phase 2 "Scaffold" unchanged: `booping-create-project <project-name> <cwd>` for new; `.booping` write only for attach.
- [ ] Phase 3 "Detect stack" references `booping-researcher` (singular). Briefing fenced block preserved verbatim. `rg 'booping-researcher-junior' src/templates/skills/install.md.j2 skills/install/SKILL.md` returns zero matches.
- [ ] Phase 4 "Populate vault extensions" names the three target paths and lazy-loads `src/docs/install_extension_files.md`. Skip-if-exists rule and stack-mismatch guard preserved verbatim.
- [ ] Phase 5 "Verify & seed sprints.md" preserved verbatim, including the `booping-plans --format=md > ~/Claude/{name}/sprints.md` command.
- [ ] `!`bin/booping-lessons`` present before `Hard rules`.
- [ ] `!`bin/booping-extra-instructions skill_install.md`` present at end of body.
- [ ] `rg 'partial_project_resolution|partial_agents_researchers_delegator' skills/install/SKILL.md src/templates/skills/install.md.j2` returns zero matches.
- [ ] `Hard rules` section carried over verbatim.
- [ ] `bin/booping-build` regenerates cleanly; regenerated `skills/install/SKILL.md` checked in.
- [ ] `rg '\{\{\s*config\.' skills/install/SKILL.md` returns zero matches (no unresolved config expressions leaked into the rendered output).

---

### M3: Render help.md.j2 — 3 SP | pending

**Goal**: `skills/help/SKILL.md` is a generated artifact. Researcher-tier trio gone from the Agents section (rendered via the new `_agents_roster.j2` macro instead). Skills table renders from `config.skills.<name>.summary` + `.writes` (no second source of truth). Workflow block updated to the current plan lifecycle. Personalization uses `_project_context.j2`. Stale `PRD.md` See-also entry removed.

**Verify**: `bin/booping-build && git diff skills/help/SKILL.md`; rendered body inspected against the claude-skill Quality Checklist; visual read of the rendered Skills / Agents / Layout / Workflow blocks.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Backup current `skills/help/SKILL.md` | `/tmp/help-skill-backup-<ts>.md` | — | pending |
| 3.2 | Author `src/templates/skills/help.md.j2` and regenerate | `src/templates/skills/help.md.j2`, `skills/help/SKILL.md` | 3 | pending |

Task 3.1 grouped with 3.2 as one briefing.

#### Task 3.1 DoD

- [ ] `cp skills/help/SKILL.md /tmp/help-skill-backup-$(date +%Y%m%d-%H%M%S).md` succeeds.
- [ ] Backup file exists with byte-identical content of the pre-migration `skills/help/SKILL.md`.
- [ ] Backup path printed to user.

#### Task 3.2 DoD

**Sequence**:

1. **Confirm the backup from Task 3.1 exists.** If absent, halt and re-run Task 3.1.
2. Read `skills/help/SKILL.md` (or the backup); transcribe `allowed-tools`, `argument-hint`, `user-invocable` verbatim.
3. Transcribe Quickstart / Layout / Hard rules blocks verbatim.
4. Replace the **Skills** table with a Jinja2 loop:
   ```jinja
   | Slash | Purpose | Writes |
   |-------|---------|--------|
   {% for name, s in config.skills.items() -%}
   | `/{{ name }}` | {{ s.summary }} | {{ s.writes }} |
   {% endfor %}
   ```
   The loop iterates over `config.skills` in insertion order (PyYAML preserves mapping order in Python 3.7+; `bin/booping-build` uses `yaml.safe_load` which inherits this).
5. Replace the **Agents** section (current researcher-tier paragraphs + Developers sub-block) with `{{ agents_roster.render("help") }}`.
6. Rewrite the **Workflow** block to reflect the current lifecycle. The block stays ASCII-art prose. Spot-check against `config.plan.statuses` to confirm every state name in the prose appears as a key under `config.plan.statuses` (this is a verification step performed during authoring, not a runtime render). The arrows must read: `backlog → in-spec → awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro → awaiting-learning → done`, with terminal branches (`cancelled`, `fail`) called out and skill owners (`/groom` / `/develop` / `/retro` / `/learn`) annotated.
7. Replace the Preflight project-resolution bullet with `{% include "_partials/_project_context.j2" %}`.
8. Update **See also**: drop `PRD.md` (file does not exist in repo); replace `docs/partial_project_resolution.md` with `src/docs/how_to_initialize_project.md` (confirmed to exist at `/home/anton/.tmp/claude_booping_test/src/docs/how_to_initialize_project.md`); keep `README.md`.
9. Add `!`bin/booping-lessons`` before Hard rules and `!`bin/booping-extra-instructions skill_help.md`` at end of body.
10. Run `bin/booping-build`.

**Structural DoD**:

- [ ] Frontmatter: `effort: {{ config.skills.help.effort }}`; `allowed-tools` list transcribed verbatim.
- [ ] `argument-hint: "[topic: skills | agents | layout | workflow]"` and `user-invocable: true` preserved.
- [ ] Top of body: `{% include "_partials/_project_context.j2" %}`.
- [ ] Phase 0 "Dispatch topic" and Phase 1 "Render body" unchanged.
- [ ] **Quickstart** block preserved verbatim, including the command roster.
- [ ] **Skills** table is rendered by a `{% for name, s in config.skills.items() %}` loop reading `summary` and `writes`. Rendered output (`skills/help/SKILL.md`) shows one row per skill in `config.skills` insertion order; row content equals the corresponding `summary` and `writes` values (verified by spot-checking three rows against `src/config.yaml`).
- [ ] **Agents** section is rendered by `{{ agents_roster.render("help") }}`. The rendered body contains zero hard-coded mentions of `booping-researcher-junior`, `booping-researcher-middle`, `booping-researcher-senior`. Zero references to `docs/partial_agents_researchers_delegator.md` or `docs/partial_agents_strategy_mid_senior.md`.
- [ ] **Layout** block preserved verbatim.
- [ ] **Workflow** block: every state name in the ASCII art appears as a key in `config.plan.statuses` (the implementer runs `for s in $(grep -oE '\b(backlog|in-spec|awaiting-[a-z]+|ready-for-dev|in-progress|done|fail|cancelled)\b' skills/help/SKILL.md | sort -u); do grep -q "^    ${s}:" src/config.yaml && echo "OK $s" || echo "MISSING $s"; done`; every line is `OK`).
- [ ] **Hard rules**: `/help` never writes files, preserved verbatim.
- [ ] **See also**: `PRD.md` removed; `docs/partial_project_resolution.md` replaced with `src/docs/how_to_initialize_project.md`; `README.md` retained. No See-also entry points at a path that does not exist (verify each with `ls`).
- [ ] `!`bin/booping-lessons`` present before `Hard rules`.
- [ ] `!`bin/booping-extra-instructions skill_help.md`` present at end of body.
- [ ] `rg 'booping-researcher-(junior|middle|senior)' skills/help/SKILL.md src/templates/skills/help.md.j2` returns zero matches.
- [ ] `rg 'partial_project_resolution|partial_agents_researchers_delegator|partial_agents_strategy_mid_senior' skills/help/SKILL.md src/templates/skills/help.md.j2` returns zero matches.
- [ ] `bin/booping-build` regenerates cleanly; regenerated `skills/help/SKILL.md` checked in.
- [ ] `rg '\{\{\s*config\.' skills/help/SKILL.md` returns zero matches.

---

### M4: Prune legacy partials + CLAUDE.md / README.md — 1 SP | pending

**Goal**: every `docs/partial_*.md` whose last remaining consumer was `/install` or `/help` is deleted (likely zero this sprint, given remaining consumers in unmigrated skills). README.md researcher-tier rows replaced with the consolidated single-agent row. CLAUDE.md migration-status block updated.

**Verify**: `bin/booping-build` exits 0; rendered skills have no broken links; `rg` confirms zero dangling references to deleted files across `skills/ src/ agents/ bin/ docs/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Grep-then-delete unreferenced partials; clean up README.md researcher-tier table; update CLAUDE.md Status block | `docs/partial_*.md`, `CLAUDE.md`, `README.md` | 1 | pending |

#### Task 4.1 DoD

- [ ] For each candidate — `docs/partial_project_resolution.md`, `docs/partial_agents_researchers_delegator.md`, `docs/partial_agents_researchers_strategy_senior_middle_junior.md`, `docs/partial_agents_strategy_mid_senior.md` — run `rg <stem> skills/ src/ agents/ bin/ docs/`. Delete a file only if every remaining match is the file referencing itself.
  - Expected outcome: net deletion this sprint is zero, since `chat`, `develop`, `retro`, `learn` still reference `partial_project_resolution.md`; `chat`, `develop`, `retro` still reference `partial_agents_researchers_delegator.md`; `develop` still references `partial_agents_strategy_mid_senior.md`.
  - Document the outcome explicitly in the retro: "pruning waits until the last consumer migrates."
- [ ] `README.md` researcher-tier rows: every line matching the regex `booping-researcher-(junior|middle|senior)` is removed and replaced with a single row matching the format of `agents/booping-researcher.md` (one consolidated entry: name + one-line description). After the edit, `rg 'booping-researcher-(junior|middle|senior)' README.md` returns zero matches. **Stale here is defined precisely as: any line referencing `booping-researcher-junior`, `-middle`, or `-senior` by name. No other interpretation.**
- [ ] `CLAUDE.md` "Status (April 2026)" block: move `install` and `help` to the template-driven list; update the sentence about which skills are still hand-authored to read "`chat`, `develop`, `retro`, `learn` remain (and `develop`'s migration plan is `ready-for-dev`)".
- [ ] `CLAUDE.md` "Config schema" section: note that `skills.<name>.summary`, `skills.<name>.writes` are now populated for every skill, and that `skills.<name>.agents` covers `groom`, `install`, `help` (and `develop` when its plan ships).
- [ ] `bin/booping-build` exits 0.
- [ ] `rg '\{\{' skills/install/SKILL.md skills/help/SKILL.md` returns matches **only** inside the skeleton fenced blocks of `src/docs/install_extension_files.md` (which is referenced from install's body). The rendered SKILL.md files themselves contain zero `{{…}}` outside any preserved literal-syntax context (lazy-load doc).
  - Concretely: `rg '\{\{' skills/install/SKILL.md` and `rg '\{\{' skills/help/SKILL.md` both return zero matches. The skeletons live in the lazy-load doc, not in the skill body.

---

## Final Verification

- [ ] `bin/booping-build` regenerates `skills/groom/SKILL.md`, `skills/install/SKILL.md`, and `skills/help/SKILL.md` cleanly.
- [ ] `rg 'booping-researcher-(junior|middle|senior)' skills/ src/ agents/ docs/ README.md CLAUDE.md` returns zero results.
- [ ] `rg 'partial_project_resolution|partial_agents_researchers_delegator' skills/install/SKILL.md skills/help/SKILL.md src/templates/skills/install.md.j2 src/templates/skills/help.md.j2` returns zero results.
- [ ] Rendered `skills/install/SKILL.md` and `skills/help/SKILL.md` satisfy the claude-skill Quality Checklist (no stale state names, no `{{config.…}}` placeholder leaks, every referenced path exists, no prose duplicating a rendered table).
- [ ] `src/docs/install_extension_files.md` reads cleanly as a standalone reference; opening just this file gives a fresh agent enough context to write the three `_booping/` extension files.
- [ ] `/help`'s **Skills** rendered table matches `config.skills.<name>.summary` + `.writes` exactly (sample-check three rows).
- [ ] `/help`'s **Workflow** ASCII block uses only state names that appear as keys under `config.plan.statuses`.
- [ ] `CLAUDE.md` "Status" and "Config schema" sections reflect the migration.
- [ ] `README.md` researcher-tier table is consolidated to one row.

## Out of scope

- `/chat`, `/develop`, `/retro`, `/learn` migrations — separate plans (develop's is `ready-for-dev`; others pending).
- Deletion of `docs/partial_project_resolution.md`, `docs/partial_agents_researchers_delegator.md`, `docs/partial_agents_strategy_mid_senior.md`, `docs/partial_agents_researchers_strategy_senior_middle_junior.md` — blocked by remaining consumers in other skills; revisit when the last one migrates.
- Rendering `/help`'s **Workflow** block from config — cross-skill ASCII arrows aren't a structured surface worth modeling. State names are spot-checked against config in the DoD.
- Changes to `booping-create-project`, `booping-plans`, `booping-project-name`, or any other CLI under `bin/`.
- Changes to agent definition files `booping-researcher.md`, `booping-developer-{middle,senior}.md`.
- Extending `_available_agents.j2` to support documentation rendering — the new `_agents_roster.j2` macro handles that case in isolation.
- Automated tests of the rendering pipeline — project policy is "No tests" (CLAUDE.md). Verification is via `booping-build` exit, `rg`, `git diff`, and visual inspection.

## CLAUDE.md impact

Update "Status (April 2026)":

- Move `install` and `help` to the template-driven list (currently only `groom`; `develop` lands there when its plan ships).
- Adjust the sentence listing hand-authored skills: after this plan, only `chat`, `develop`, `retro`, `learn` remain (and `develop` has a `ready-for-dev` plan).

Under "Config schema" top-level keys section:

- Note `skills.<name>.summary` (one-line plugin-wide purpose) and `skills.<name>.writes` (free-form description of write-targets) — populated for every skill; consumed by `/help`'s rendered Skills table.
- Note that `skills.<name>.agents` now covers `groom`, `install`, `help` (and `develop` when its plan ships).
- Note the new partial `src/templates/_partials/_agents_roster.j2` (documentation-shaped agent rendering, distinct from `_available_agents.j2` which is delegation-shaped).

## Risk register

- **Cross-validation flagged "no automated tests" as a CRITICAL EXECUTION RISK.** Accepted: project policy is "No tests" (CLAUDE.md → CLI section). Verification is via `booping-build` exit, `rg` checks in DoD, `git diff` review of regenerated files, and visual inspection against the claude-skill Quality Checklist.
- **Net partial deletion this sprint may be zero.** Acceptable: deletions are gated on the last consumer migrating, and the remaining consumers (`chat`, `develop`, `retro`, `learn`) have their own migration plans pending or `ready-for-dev`. M4 still owns the README + CLAUDE.md updates regardless.
