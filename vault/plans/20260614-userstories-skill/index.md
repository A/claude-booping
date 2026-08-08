---
title: Add /userstories skill — personas + value-first user-story authoring
type: feature
status: cancelled
sp: 17
split_from: null
created: 2026-06-14 00:00
planned: 20260614 12:28
started: null
completed: null
retro: null
goal: null
commit: 60b720ec0f4fa1683b9bbdb1e6a3965159afbf0e
summary: "New stateless /userstories skill: persona library + value-first epic/story authoring upstream of /groom"
---

# Add /userstories skill — personas + value-first user-story authoring

## Context

booping has no story-discovery step. Work enters at `/groom`, which assumes the problem is already framed. The user already authors user stories by hand (e.g. `@{client}/docs/User Stories.md`) in a compact `As a <persona> I can/want … so that …` style with inline `- Q:`/`A:` open-questions, but with no enforced structure, no persona reuse, and no value-first ordering.

This plan adds a new **stateless** skill `/userstories` (the `/code-review` pattern: chat output, no plan-lifecycle status), upstream of `/groom`. It:

- extracts/reuses **personas** from a persistent vault library (`~/Claude/{project}/personas/`), the "self-learning" surface;
- decomposes work into **epics ordered by deliverable value** (must-have value first, polish split to lower-priority stories), then into compact connextra **stories**, with **optional Gherkin scenarios** added only when a story has multiple behavioral paths;
- preserves the user's inline `- Q:`/`- A:` open-questions convention as a first-class part of the template;
- writes one **stories file per run** into `~/Claude/{project}/stories/` (skill suggests the filename), and **maintains existing stories**: before writing it scans `stories/*.md` for overlap and prefers updating an existing file over duplicating.

After this plan: `/userstories <scope>` produces a structured, maintained stories artifact and a growing persona library; lessons feed it via the standard `lessons/` + `_booping/skill_userstories.md` wiring; `/learn` can fold story-specific lessons into it.

## Decisions

- **Lifecycle placement**: stateless side-skill, no `config.plan.statuses` entry — mirrors `/code-review`. Output is a vault artifact wired manually into `/groom`, not a plan status. *Why*: keeps the lifecycle contract (and `sprints.md`, README narrative) untouched; stories are inputs to grooming, not plans.
- **Output artifact**: one stories file per run at `~/Claude/{project}/stories/{kebab-title}.md` following a fixed stories template; same shape whether scope is whole-project or a single feature. Skill proposes the filename. *Why*: user wants stories as standalone, manually-wired artifacts — not a single living backlog and not per-epic file sprawl.
- **Maintenance/dedup**: skill scans existing `stories/*.md` for scope overlap before writing and offers to update the overlapping file (keeping stories current) instead of creating a near-duplicate. *Why*: explicit user requirement — keep all stories up to date as features/info appear.
- **Personas**: persistent library `~/Claude/{project}/personas/<slug>.md`, one persona per file; each run reconciles extracted candidates against the library, reuses matches, proposes new ones tagged `[ASSUMPTION—VALIDATE]`, persists after user confirmation. *Why*: the requested self-learning surface; personas accumulate and are reused across runs.
- **Hierarchy**: epic → story → (optional) scenario. Epics carry a one-line value brief + MoSCoW priority and are ordered value-first. *Why*: matches the user's `_notes/User Stories Skill.md` value-first principle plus story-mapping best practice.
- **Story format**: compact connextra `As a <persona>, I want <action>, so that <value>.` with inline `- Q:`/`- A:` open-questions; Gherkin `Scenario: Given/When/Then` added only on signal (multiple paths / ambiguous done). *Why*: preserves the user's existing compact + open-questions style, adds rigor only where it pays.
- **Agents**: wire `booping-researcher` for heavy reads (whole-project codebase scan, scanning a large existing `stories/` corpus, domain web research). No developer agent — the skill owns vault writes directly, like `/groom` owns `plans/`. *Why*: no application-code edits at runtime.
- **Content split**: structured facts (agent wiring) → `src/config.yaml`; verbs/heuristics → skill body; long-form (stories-file structure, persona format, value-slicing, splitting/INVEST/scenario heuristics) → lazy-load `docs/*.md`.

## Architecture

Load-time inputs of the rendered skill (`src/templates/skills/userstories.md.j2`):

- `{% include "_partials/_project_context.j2" %}` — project name/path.
- `{{ available_agents.render("userstories") }}` — agent table from `config.skills.userstories.agents`.
- `{{ tools.render('_partials/_lessons.j2') }}` — live lessons.
- `{{ tools.render('_partials/_extra_instructions.j2', extra_instruction_key='skill_userstories') }}` — project extension.
- Lazy-load craft docs via `[label](${CLAUDE_PLUGIN_ROOT}/docs/<name>.md)`: stories template, persona format, value slicing, splitting/INVEST/scenarios.

Interaction with the rest of booping: no shared status; downstream coupling is a one-line hand-off mention from `/chat` and `/help` ("`/userstories <scope>` — derive personas + stories upstream of groom"). Vault surfaces: new `personas/` and `stories/` dirs scaffolded by `bin/booping-create-project`.

## Milestones

### M1: Config, vault scaffolding, thin shell — 4 SP | pending

**Goal**: `/userstories` is a buildable, loadable skill shell with its config entry; new projects scaffold `personas/` and `stories/`.

**Verify**: `just build` renders cleanly; `git diff -- skills/` shows the new `skills/userstories/SKILL.md`; `bin/booping render src/templates/skills/userstories.md.j2` renders (against the M4 body, or a placeholder body until M4) without `{{placeholder}}` leaks; scaffolding a throwaway project creates `personas/` + `stories/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `skills.userstories` block: `agents.booping-researcher` with `good_for`/`bad_for` scoped to whole-project/codebase scans, large existing-stories-corpus reads, and domain web research; no `status` key (stateless) | `src/config.yaml` | 1 | pending |
| 1.2 | Add `userstories: { effort: medium }` build-config entry | `src/config_files.yaml` | 1 | pending |
| 1.3 | Author thin shell: frontmatter (`name`, `description`, `argument-hint: [scope or brief reference]`, `user-invocable: true`, `allowed-tools` = Read/Write/Edit/Glob/Grep/`Bash(booping:*)`/`Bash(ls *)`/`Bash(cat ~/Claude/*)`/AskUserQuestion/Agent, `effort: {{ skills.userstories.effort }}`), body = single `!`booping render src/templates/skills/userstories.md.j2`` line | `src/files/skills/userstories/SKILL.md.j2` | 1 | pending |
| 1.4 | Read the existing dir-creation block in `bin/booping-create-project` first, then add `personas/` and `stories/` mirroring that exact pattern (+ any `.gitkeep`/marker the siblings use) | `bin/booping-create-project` | 1 | pending |

#### Task 1.1 DoD
- [ ] `config.skills.userstories.agents.booping-researcher` present with `internal: true`, `good_for`, `bad_for`.
- [ ] No `status` key under `skills.userstories` (stateless).
- [ ] `_available_agents.j2` resolves `userstories` without error when rendering.

#### Task 1.2 DoD
- [ ] `skills.userstories.effort` present in `src/config_files.yaml`.

#### Task 1.3 DoD
- [ ] `just build` produces `skills/userstories/SKILL.md` as a build artefact (not hand-edited).
- [ ] Frontmatter shape matches a sibling thin shell (e.g. `src/files/skills/chat/SKILL.md.j2`).
- [ ] `allowed-tools` includes every shell call the skill body issues and no more.

#### Task 1.4 DoD
- [ ] Existing scaffolding block read before editing; new dirs added with the same idiom (no new helper invented).
- [ ] Running `bin/booping-create-project` on a throwaway name creates `personas/` and `stories/` under the vault.
- [ ] Scaffolding style (markers/permissions) matches existing scaffolded dirs.

*Note*: this milestone's render check passes against a minimal placeholder body if M4 is not yet built; M4 replaces it. SUT order is M1 → M2/M3 (docs) → M4 (body references docs) → M5.

---

### M2: Artifact contracts — stories file template + persona file format — 3 SP | pending

**Goal**: the exact on-disk shape of a stories file and a persona file is fixed in lazy-load docs, locking the output contract.

**Verify**: docs render as plain markdown; a hand-written sample stories file and persona file conform; the compact style matches `@{client}/docs/User Stories.md` while adding the epic/priority structure.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `docs/userstories_template.md`: stories-file frontmatter (`title`, `created`, `updated`, `scope: project\|feature`, `personas: [<slug>…]`, `source`) + body structure: `## <Epic> (priority: must\|should\|could)` + one-line value brief, then `- As a <persona>, I want <action>, so that <value>.` bullets, nested `- Q:`/`- A:` open-questions, and optional indented `Scenario:`/Given/When/Then. Include a filled mini-example | `docs/userstories_template.md` | 2 | pending |
| 2.2 | `docs/userstories_personas.md`: persona-file frontmatter (`name`, `slug`, `role`, `created`) + body (`**Goal**`, `**Pains**`, `**Context**`), `[ASSUMPTION—VALIDATE]` tagging rule, slug convention, and the reconcile-vs-library rule (reuse match / propose new) | `docs/userstories_personas.md` | 1 | pending |

#### Task 2.1 DoD
- [ ] Frontmatter fields enumerated with types; `personas` references `personas/<slug>.md`.
- [ ] Body grammar shows epic → story → optional scenario with the inline `Q:`/`A:` convention.
- [ ] Compact connextra story line is the canonical form; mini-example present and valid.
- [ ] No prose duplicating heuristics owned by M3 docs (cross-link instead).

#### Task 2.2 DoD
- [ ] Persona frontmatter + body sections fixed; one filled example present.
- [ ] `[ASSUMPTION—VALIDATE]` usage rule stated.
- [ ] Slug/filename rule stated (`personas/<slug>.md`).

---

### M3: Craft docs — value slicing + splitting/INVEST/scenarios — 3 SP | pending

**Goal**: the judgment heuristics the skill lazy-loads are captured as docs: how to order epics by value, how to split stories, when to add scenarios.

**Verify**: docs render; each is linkable from the skill body; no overlap with M2 structural docs.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `docs/userstories_value_slicing.md`: epics built around deliverable value not features; must-have core path first, polish/edge cases split to lower-priority stories; MoSCoW at story level; vertical (not horizontal) slices. Ground in the user's value-first principle | `docs/userstories_value_slicing.md` | 1 | pending |
| 3.2 | `docs/userstories_splitting.md`: Humanizing-Work split patterns (workflow steps, CRUD, business-rule/data variations, defer-performance, spike, simple/complex), INVEST gate, "when to split vs when not", and **when to add a Gherkin scenario vs split into a separate story** (multiple When/Then = split signal; multiple paths/ambiguous done = scenario) | `docs/userstories_splitting.md` | 2 | pending |

#### Task 3.1 DoD
- [ ] Value-first ordering rule + polish-splits-out rule stated with a concrete example.
- [ ] MoSCoW mapping to story priority stated.
- [ ] Horizontal-slice anti-pattern called out.

#### Task 3.2 DoD
- [ ] Split patterns listed with one-line "when to use" each.
- [ ] INVEST gate present as a checklist.
- [ ] Scenario-vs-split decision rule stated explicitly.
- [ ] No restatement of the file structure owned by M2 (cross-link).

---

### M4: Skill body — 4 SP | pending

**Goal**: `src/templates/skills/userstories.md.j2` drives the full flow: ingest → personas → value-ordered epics → compact stories → optional scenarios → overlap-check → write/maintain stories file.

**Verify**: `bin/booping render src/templates/skills/userstories.md.j2` produces clean output (no `{{placeholder}}` leaks, lazy links resolve); a dry read confirms the phases cover personas reuse, value-first epics, compact format, inline `Q:`/`A:`, overlap/maintenance, and filename suggestion.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Author skill body with standard wiring (`_project_context`, `available_agents.render("userstories")`, `_lessons`, `_extra_instructions` key `skill_userstories`) and a Preflight (read lessons, `_booping/skill_userstories.md`) | `src/templates/skills/userstories.md.j2` | 1 | pending |
| 4.2 | Phases: (0) Ingest scope — feature brief / WIP notes / whole-project scan, delegating heavy reads to `booping-researcher` with a **bounded return contract** (researcher returns ONLY a structured summary of domain facts / actors / capability areas — no prose, no raw dumps); (1) Personas — extract, reconcile against `personas/` library, propose new `[ASSUMPTION—VALIDATE]`, then **hard-stop via `AskUserQuestion` and block until the user confirms** before persisting and proceeding; (2) Epics by deliverable value (lazy-load value-slicing doc); (3) Stories — compact connextra, split per patterns (lazy-load splitting doc), capture inline `Q:`/`A:`; (4) Scenarios — optional Gherkin on signal | `src/templates/skills/userstories.md.j2` | 2 | pending |
| 4.3 | Phase: overlap-check & write — overlap scan reads **only frontmatter** (`title`, `scope`, `personas`) + epic headings of existing `stories/*.md` (Glob + targeted Grep), never full bodies; for a large corpus delegate the scan to `booping-researcher` (bounded return: overlapping file paths + matched epics only). Prefer updating the overlapping file over duplicating; suggest a filename; **persist epics/stories progressively to the target stories file as they are produced** (the file is the working state, not chat history); set `updated:`; then present and iterate | `src/templates/skills/userstories.md.j2` | 1 | pending |

#### Task 4.1 DoD
- [ ] All four `!`command``/include/import wirings present and resolve.
- [ ] Preflight reads lessons + `_booping/skill_userstories.md`; no "never read lessons"-style residue.
- [ ] No stack-specific details in the body.
- [ ] Body passes the four-check IA pass (scoping / duplication / configurability / hierarchy) per lesson 0004 before saving.

#### Task 4.2 DoD
- [ ] Persona phase reconciles against the library and persists only after an explicit `AskUserQuestion` confirmation (no assumed consent / silent proceed).
- [ ] Epic phase orders by value and lazy-loads the value-slicing doc.
- [ ] Story phase emits compact connextra + inline `Q:`/`A:`; lazy-loads the splitting doc.
- [ ] Scenario phase adds Gherkin only on the documented signal.
- [ ] Heavy reads delegate to `booping-researcher` with a stated, bounded return shape (no unbounded prose) per lesson 0007.

#### Task 4.3 DoD
- [ ] Overlap scan reads frontmatter/headings only (or delegates a large corpus to `booping-researcher` with a bounded return); never bulk-`cat`s the corpus into orchestrator context.
- [ ] Update-vs-new-file is offered to the user; filename suggested, not silently chosen.
- [ ] Stories persist progressively to the target file (state anchored on disk, not chat).
- [ ] Written file conforms to `docs/userstories_template.md`; `updated:` set on edits.

---

### M5: Integration wiring, docs site, reference cleanup — 3 SP | pending

**Goal**: the skill is discoverable and all references that the new skill/dirs touch are made consistent in the same sprint.

**Verify**: `/chat` and `/help` render listing `/userstories`; `mkdocs build` succeeds with the new page in nav; `grep` for the skill name across README/CLAUDE.md/docs shows no dangling references.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Add `/userstories` hand-off line to `/chat` Phase 3 and to the `/help` command list | `src/templates/skills/chat.md.j2`, `src/templates/skills/help.md.j2` | 1 | pending |
| 5.2 | Author docs-site page + nav entry under Commands | `documentation/userstories.md`, `mkdocs.yml` | 1 | pending |
| 5.3 | Reference-consistency cleanup: add `/userstories` to README command/Quick-start surface (no Statuses change — stateless skill); update CLAUDE.md "Project vault layout" to document `personas/` + `stories/` and add `/userstories` to the skill set / "Adding a new skill" reference where skills are enumerated | `README.md`, `CLAUDE.md` | 1 | pending |

#### Task 5.1 DoD
- [ ] `/chat` Phase 3 hand-offs include `/userstories <scope>` with a one-line description.
- [ ] `/help` rendered command list includes `/userstories`.

#### Task 5.2 DoD
- [ ] `documentation/userstories.md` covers what the skill does, the stories/persona artifacts, and the upstream-of-groom relationship.
- [ ] `mkdocs.yml` nav lists the page under Commands; `mkdocs build` is clean.

#### Task 5.3 DoD
- [ ] README references `/userstories` (commands/quick-start); Statuses section untouched.
- [ ] CLAUDE.md "Project vault layout" documents `personas/` and `stories/`.
- [ ] No stale/dangling references to the skill name across `README.md`, `CLAUDE.md`, `docs/`, `documentation/`.

---

## Final Verification

- [ ] `just build` renders cleanly and `git diff -- skills/` shows only the intended `skills/userstories/SKILL.md` artefact.
- [ ] `bin/booping render src/templates/skills/userstories.md.j2` produces clean output (no stale names, no `{{placeholder}}` leaks, no prose duplicating rendered tables).
- [ ] All lazy-load links in the skill body resolve to existing `docs/*.md`.
- [ ] `_booping/skill_userstories.md` extension point inlines correctly (test with a stub file).
- [ ] Every authored prompt-bearing artefact (skill body + `docs/userstories_*.md`) passed the four-check IA pass (lesson 0004) before saving.
- [ ] `mkdocs build` succeeds.
- [ ] Project lint/typecheck/test as applicable: `just lint`, `just typecheck`, `just test` (only `bin/booping-create-project` changes touch Python-adjacent code; docs/templates are non-Python).

## Out of scope

- No `config.plan.statuses` changes — `/userstories` is stateless.
- No new `booping` CLI subcommand (no `render-stories` snapshot in v1); the skill writes markdown directly.
- No automatic promotion of a story into a `/groom` plan — coupling is a manual hand-off mention only.
- No new plan-template or review-template subsystem changes.
- No changes to `/groom`, `/develop`, `/retro`, `/learn` behavior beyond the `/chat` + `/help` discoverability lines.

## Risk register

- **State across a multi-phase stateless flow** (Gemini blind spot): handled by Task 4.3 — stories persist progressively to the target file on disk; the file, not chat history, is the working state.
- **O(N) context on overlap checks** (Gemini blind spot): handled by Task 4.3 — frontmatter/heading-only scan, with `booping-researcher` delegation (bounded return) for a large corpus.

## CLAUDE.md impact

- Update "Project vault layout (`~/Claude/{project}/`)" to document the new `personas/` and `stories/` dirs (Task 5.3).
- Add `/userstories` to the enumerated skill set where skills are listed (Task 5.3).
- No config-schema-shape changes beyond a new `skills.<name>` entry, which is already covered by the existing schema docs.

---

# Quality Checklist

## Frontmatter
- [x] Frontmatter matches the plan frontmatter template.
- [x] `sp` (17) equals the sum of per-task SP across milestones (M1 4 + M2 3 + M3 3 + M4 4 + M5 3).

## Content
- [x] Context names the behavior change (new rendered skill + vault artifacts), not "refactor internals".
- [x] DoD bullets are verifiable by reading rendered output or a diff.
- [x] Every task lists exact template / partial / config / doc paths.
- [x] Every task DoD uses checkboxes.
- [x] Every milestone has a `Verify` step including a rebuild/render.
- [x] Each milestone executable from a fresh session with only the plan as context (M4 references M2/M3 docs by path).

## Skill-design hygiene
- [x] Structured facts (agent wiring) go in `src/config.yaml`, not prose.
- [x] Single-consumer content (skill phases) lives in the skill body.
- [x] Long-form reference (stories template, persona format, value slicing, splitting) is lazy-load `docs/`, not inlined.
- [x] `!`commands`` used for dynamic content (project context, lessons, extra instructions).
- [x] No restated lifecycle flow — skill is stateless, no transitions table.
- [x] No stack-specific details in the skill body.

## Anti-patterns (must be absent)
- [x] No "TBD"/"TODO"/"implement later".
- [x] No task spanning unrelated concerns.
- [x] No prose duplicating a rendered table/partial.
- [x] No stale state names.

## External references validated
- [x] Template/config/doc paths reference real files (`src/config.yaml`, `src/config_files.yaml`, `src/files/skills/chat/SKILL.md.j2` pattern, `bin/booping-create-project`, `mkdocs.yml`, `documentation/`, `docs/`) — new files created by their tasks.
- [x] Lazy-load doc links resolve from the rendered skill location (`${CLAUDE_PLUGIN_ROOT}/docs/<name>.md`).

## CLAUDE.md impact
- [x] New `skills.<name>` entry + new vault dirs reflected in CLAUDE.md via Task 5.3.
</content>
</invoke>
