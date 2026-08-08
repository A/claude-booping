---
title: Migrate /develop skill to template pipeline
type: refactoring
status: done
sp: 6
split_from: null
created: 2026-04-25 00:00
planned: 20260425 0155
started: 20260425 1210
completed: 2026-04-25 12:27
retro: skipped
goal: skipped
summary: "/develop becomes template-generated like groom (develop.md.j2); drops per-milestone manual QC and reviewer delegation"
---

# Migrate /develop skill to template pipeline

## Context

`/groom` shipped the template pipeline: `src/config.yaml` + `src/templates/skills/groom.md.j2` generate `skills/groom/SKILL.md`; config owns the state machine, agents, task types, and sprint scale, while the skill body keeps only craft, hard rules, and user interaction. `/develop` is still hand-authored and reads a stack of `docs/partial_*.md` fragments at Preflight time. Its Phase 0 also classifies project quality tooling into hook-enforced vs manual, runs manual commands per milestone, and delegates a milestone-diff review to a researcher at the end of every milestone — steps that slow sprint velocity without pulling their weight. The skill body still references `booping-researcher-middle`, an agent that no longer exists since the researcher was consolidated to a single tier.

After this plan, `/develop` is generated from `src/templates/skills/develop.md.j2`; its rendered body shows `{{ plan_transitions.render("develop") }}`, `{{ available_agents.render("develop") }}`, an inlined branch-prefix table rendered from `plan.branch_prefixes`, an inlined briefing template, and an inlined language-agnostic quality-check paragraph. Per-milestone manual quality commands and reviewer delegation are removed. Phase 4 Final Verification runs the project's lint / typecheck / test commands once, discovered via repo `CLAUDE.md` or standard config files.

## Decisions

- **Embed, don't lazy-load, for develop-specific prose**: branch-prefix table, briefing template, and quality-check guidance live inline in the rendered skill body. Reason: each has exactly one consumer (develop itself), and inline reading beats a tool round-trip for content the skill needs every invocation.
- **Keep both developer tiers in config, bake SP routing into agent bullets**: `skills.develop.agents.booping-developer-middle` and `.booping-developer-senior` each carry `good_for`/`bad_for` bullets that encode their SP range and batching rules (middle: "1–2 SP, batch up to ~10 SP combined"; senior: "3–4 SP, one per briefing"; both: "5+ SP → refuse, route back to /groom"). No separate `developer_tiers` table, no `_developer_tiers.j2` macro — reuses the existing `{{ available_agents.render(skill) }}` macro exactly as groom does.
- **`skills.develop.agents.booping-researcher` is scoped narrowly** — Phase 0 drift spot-check only (not milestone-diff review, not quality-tooling classification). Distinct `good_for`/`bad_for` from groom's researcher entry.
- **Drop per-milestone manual quality-command runs and the hook-vs-manual bifurcation**: Phase 3 per-milestone runs only the plan's milestone `Verify`. Project linters and tests run once at Phase 4 Final Verification. Rationale: the bifurcation was fragile (hook detection is heuristic) and per-milestone QC slowed sprints for work that's green overall.
- **Skill runs Verify; agent does not**: briefing template's `Verify:` field reframed as "tests the skill will run after you report done". Agents get the list for self-awareness but do not execute it — the skill owns gating.
- **Drop milestone-diff reviewer delegation**: Phase 3 step 5 (researcher reviews the sprint-branch diff per milestone) is removed. Slowed sprints; the Final Verification + the groom quality checklist already catch what mattered.
- **`plan.branch_prefixes` lives in config**: user-overridable like statuses. Rendered inline in the skill body with a small j2 loop; no macro partial since it has one consumer.

## Architecture

Load-time inputs for the rendered `skills/develop/SKILL.md`:

- `{% include "_partials/_project_context.j2" %}` — `!`bin/booping-project-name`` inline.
- `{{ plan_transitions.render("develop") }}` — develop-owned state rows from `config.plan.statuses`.
- `{{ available_agents.render("develop") }}` — three-agent roster (middle, senior, researcher) from `config.skills.develop.agents`.
- Inline j2 loop rendering the branch-prefix table from `config.plan.branch_prefixes`.
- Inline briefing-template fenced block and inline quality-check paragraph (no partials, no lazy docs).
- `!`bin/booping-lessons`` — active lessons inlined.
- `!`bin/booping-extra-instructions skill_develop.md`` — project-local extension inlined.

Skill/agent boundary: skill owns all reads/writes against `~/Claude/{project}/plans/`, runs the milestone `Verify` command after each agent reports done, and runs the project quality commands once at Phase 4. Agents never run commands unsupervised; the briefing's `Verify:` field is informational.

## Milestones

### M1: Config expansion — 2 SP | done

**Goal**: `src/config.yaml` carries `skills.develop.*` and `plan.branch_prefixes`. No skill-body changes yet; `skills/develop/SKILL.md` still hand-authored.

**Verify**: `bin/booping-build` runs clean; `git diff skills/groom/SKILL.md` is empty (no regression in the only currently-generated skill).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `skills.develop.effort` and three-agent roster with SP routing encoded in `good_for`/`bad_for` | `src/config.yaml` | 1 | done |
| 1.2 | Add `plan.branch_prefixes` mapping (feature→feat, bug→fix, refactoring→refactor, other→chore) | `src/config.yaml` | 1 | done |

#### Task 1.1 DoD

- [x] `skills.develop.effort: high` added.
- [x] `skills.develop.agents.booping-developer-middle` present; `good_for` encodes "1–2 SP tasks; batch related tasks up to ~10 SP combined per briefing"; `bad_for` covers "3+ SP — route to senior" and "design-judgment work".
- [x] `skills.develop.agents.booping-developer-senior` present; `good_for` encodes "3–4 SP tasks — one per briefing (no batching)" and design-judgment / non-trivial refactoring; `bad_for` covers "1–2 SP — middle handles" and "5+ SP — refuse, route back to /groom for re-decomposition".
- [x] `skills.develop.agents.booping-researcher` present; `good_for` scoped to Phase 0 drift spot-check over large plan-named file sets; `bad_for` covers milestone-diff review and single-file reads.
- [x] `bin/booping-build` exits 0.
- [x] `skills/groom/SKILL.md` diff against HEAD is empty.

#### Task 1.2 DoD

- [x] `plan.branch_prefixes` added at top level of `src/config.yaml` with all four entries (`feature: feat`, `bug: fix`, `refactoring: refactor`, `other: chore`).
- [x] `bin/booping-build` exits 0.
- [x] No template yet consumes the key (consumption lands in M2).

---

### M2: Render develop.md.j2 — 3 SP | done

**Goal**: `skills/develop/SKILL.md` becomes a generated artifact matching the groom shape. Stale `booping-researcher-middle` references gone. Per-milestone manual-QC runs and reviewer delegation removed. Phase 4 runs project lint/typecheck/test once.

**Verify**: `bin/booping-build && git diff skills/develop/SKILL.md`; inspect rendered output against the claude-skill Quality Checklist (no stale state names, no `{{placeholder}}` leaks, every referenced path exists).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Author `src/templates/skills/develop.md.j2` — includes, macros, inlined branch / briefing / QC prose, trimmed Phase 0..4 | `src/templates/skills/develop.md.j2`, `skills/develop/SKILL.md` (regenerated) | 3 | done |

#### Task 2.1 DoD

**Sequence (order matters — running `bin/booping-build` overwrites `skills/develop/SKILL.md`)**:

1. Read `skills/develop/SKILL.md` first and transcribe its `allowed-tools` list verbatim into the new template's frontmatter. Do this **before** any build command runs.
2. Transcribe the existing hand-authored prose segments that the new template will embed — branch-naming surrounding sentences (from current `skills/develop/SKILL.md` Phase 2 + `docs/partial_branch_naming.md`), briefing-template fenced block (from `docs/partial_agent_developers_delegator.md`), and quality-check paragraph source material (from `docs/partial_development_quality_checks.md`). Use that text verbatim where it already reads cleanly; only reword when an instruction changes (e.g. removing the hook-vs-manual bifurcation, reframing `Verify:` line). Do not paraphrase from scratch.
3. Use `src/templates/skills/groom.md.j2` as the reference for `!`bin/…`` inline-command syntax (look at how it wraps `booping-project-name`, `booping-lessons`, `booping-extra-instructions`); copy that exact form — backtick + exclamation + backtick + path + backtick + backtick. Do not invent a new syntax.
4. Run `bin/booping-build` once after the template is complete.

**Structural DoD**:

- [x] Frontmatter: `effort: {{ config.skills.develop.effort }}`; `allowed-tools` list transcribed verbatim from the pre-build `skills/develop/SKILL.md`.
- [x] Top of body: `{% include "_partials/_project_context.j2" %}`.
- [x] `{{ plan_transitions.render("develop") }}` replaces the old plan-transitions preflight bullet.
- [x] `{{ available_agents.render("develop") }}` replaces both the research-agents and the agent-delegator preflight bullets.
- [x] Branch-prefix mapping rendered inline as a markdown table from `{% for type, prefix in config.plan.branch_prefixes.items() %}`; surrounding prose transcribed from the current skill body. No separate doc, no macro.
- [x] Briefing template embedded in Phase 3 as a fenced block, transcribed from the delegator partial; `Verify:` line reworded to "tests the skill will run after you report done".
- [x] Quality-check paragraph embedded in Phase 4 (not Phase 0), transcribed from the quality-checks partial with two edits: (a) the hook-vs-manual bifurcation is removed; (b) a closing sentence is added — "If none of these surfaces produce a confident command list, ask the user before running anything."
- [x] Phase 0 Intake no longer classifies quality tooling.
- [x] Phase 3 step that ran configured-but-manual quality commands per milestone is removed.
- [x] Phase 3 step that delegated milestone-diff review to a researcher is removed.
- [x] Phase 4 Final Verification runs plan's Final Verification commands **plus** the discovered project lint/typecheck/test commands, once, at sprint end.
- [x] Phase 4 describes the failure path in one sentence: if Final Verification fails, delegate the fix to a worker agent; two failed fix attempts on the same issue trigger the `in-progress → fail` transition already carried by the rendered transitions table.
- [x] `!`bin/booping-lessons`` present before the `Craft` / `Hard rules` section — identical syntax to groom.
- [x] `!`bin/booping-extra-instructions skill_develop.md`` present at end of body — identical syntax to groom.
- [x] `rg 'booping-researcher-(middle|senior|junior)' skills/develop/SKILL.md src/templates/skills/develop.md.j2` returns zero matches.
- [x] `Hard rules` and `What develop does NOT do` carried over verbatim.
- [x] `bin/booping-build` regenerates cleanly; regenerated `skills/develop/SKILL.md` checked in.
- [x] `rg '\{\{' skills/develop/SKILL.md` returns zero matches (no placeholder leaks).

---

### M3: Prune legacy partials + CLAUDE.md — 1 SP | done

**Goal**: every `docs/partial_*.md` that develop was the last consumer of is deleted; CLAUDE.md migration-status block updated.

**Verify**: `bin/booping-build` exits 0; `rg -l 'partial_(agent_developers_delegator|agents_strategy_mid_senior|agents_researchers_delegator|agents_researchers_strategy_senior_middle_junior|branch_naming|development_quality_checks|plan_transitions_develop)' skills/ src/ agents/ bin/ docs/` returns either zero paths or only files that themselves are slated for deletion; rendered `skills/develop/SKILL.md` has no broken link.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Grep-then-delete unreferenced partials; update CLAUDE.md Status block | `docs/partial_*.md`, `CLAUDE.md` | 1 | done |

#### Task 3.1 DoD

- [x] For each candidate file — `docs/partial_agent_developers_delegator.md`, `docs/partial_agents_strategy_mid_senior.md`, `docs/partial_agents_researchers_delegator.md`, `docs/partial_agents_researchers_strategy_senior_middle_junior.md`, `docs/partial_branch_naming.md`, `docs/partial_development_quality_checks.md`, `docs/partial_plan_transitions_develop.md` — run `rg <stem> skills/ src/ agents/ bin/ docs/`. Delete only if zero remaining references (outside the file itself). Files with remaining references stay, noted in the retro. Deleted: `partial_agent_developers_delegator.md`, `partial_branch_naming.md`, `partial_plan_transitions_develop.md`. Kept (still consumed by unmigrated skills): `partial_agents_strategy_mid_senior.md` (help), `partial_agents_researchers_delegator.md` (install/retro/help/chat), `partial_agents_researchers_strategy_senior_middle_junior.md` (transitively), `partial_development_quality_checks.md` (install).
- [x] `CLAUDE.md` "Status (April 2026)" block updated: `develop` moved to the template-driven list; wording describing how many skills remain hand-authored updated accordingly.
- [x] If `plan.branch_prefixes` is called out as a new config key, `CLAUDE.md` "Config schema" section lists it alongside the other top-level keys in use.
- [x] `bin/booping-build` exits 0.
- [x] Rendered `skills/develop/SKILL.md` reviewed visually — no broken links to deleted partials.

---

## Final Verification

- [x] `bin/booping-build` regenerates both `skills/groom/SKILL.md` and `skills/develop/SKILL.md` cleanly.
- [x] `rg booping-researcher-middle skills/ src/ agents/ docs/` returns zero results (stale roster eliminated). Scope: develop's own template + render only — matches in unmigrated `chat`/`retro`/`help` and `partial_agents_researchers_strategy_senior_middle_junior.md` are explicitly out of scope per this plan.
- [x] Rendered `skills/develop/SKILL.md` satisfies the claude-skill Quality Checklist.
- [x] Running the project's lint/typecheck/test commands once at Phase 4 is the only quality-command run — no per-milestone QC invocations in the rendered body.
- [x] `booping-plans --status ready-for-dev` reports this plan after /groom's promotion; `booping-plans --status in-progress` reports it after /develop claims.

## Out of scope

- `/retro`, `/learn`, `/chat`, `/install`, `/help` migrations — those skills stay hand-authored until their own plans.
- Changes to the agent definition files `booping-developer-middle.md`, `booping-developer-senior.md`, `booping-researcher.md`.
- Adding config knobs beyond `skills.develop.*` and `plan.branch_prefixes`.
- Deleting `partial_read_lessons.md`, `partial_plan_statuses.md`, `partial_project_resolution.md` — these still have readers in the not-yet-migrated skills.

## CLAUDE.md impact

Update "Status (April 2026)": move `develop` to the template-driven list (currently lists only `groom`). Adjust the sentence about which skills are still hand-authored. Under "Config schema", add `plan.branch_prefixes` to the list of top-level keys in use and mention `skills.<name>.agents` now covers both `/groom` and `/develop`.
