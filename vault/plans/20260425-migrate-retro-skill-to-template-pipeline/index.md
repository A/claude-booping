---
title: Migrate /retro skill to template pipeline
type: refactoring
status: done
sp: 5
split_from: null
created: 2026-04-25 00:00
planned: 20260425 14:51
started: 20260425 14:58
completed: 2026-04-26 01:56
retro: retrospectives/20260425-migrate-retro-skill-to-template-pipeline.md
goal: success
summary: "Migrate /retro to template pipeline: single booping-researcher tier, lazy-loaded retrospective template"
---

# Migrate /retro skill to template pipeline

## Context

`/groom` and `/develop` are now generated from `src/templates/skills/*.md.j2` against `src/config.yaml`. Their bodies use `{% include "_partials/_project_context.j2" %}`, `{{ plan_transitions.render(<skill>) }}`, `{{ available_agents.render(<skill>) }}`, and inline `!`bin/booping-lessons`` / `!`bin/booping-extra-instructions skill_<name>.md`` so lessons and project overrides arrive at load time without preflight reads.

`/retro` is still hand-authored at `skills/retro/SKILL.md`. Its Preflight loads nine items via markdown links to `docs/partial_*.md` and `docs/template_*.md`, including a duplicate lessons load and a `_booping/skill_retro.md` read bullet that the standard CLI now handles. It also references `booping-researcher-middle`, an agent that no longer exists since the researcher was consolidated to a single `booping-researcher` tier (see the develop migration retro). The `awaiting-retro` and `awaiting-learning` transitions are already in `src/config.yaml` — the data side of the contract is intact; only the skill body needs to be regenerated against it.

After this plan, `skills/retro/SKILL.md` is a generated artifact rendered from `src/templates/skills/retro.md.j2`. The Preflight section disappears in favor of (a) the project-context include, (b) the rendered transitions table, (c) the rendered agents roster, (d) the inline `!`bin/booping-lessons`` block, and (e) the inline `!`bin/booping-extra-instructions skill_retro.md`` at the foot of the body. The retrospective template moves from a preflight read to a lazy `[retrospective template](../../docs/template_retrospective.md)` link inside Phase 4 where it is actually used. The orphaned `docs/partial_plan_transitions_retro.md` is deleted.

## Decisions

- **Use the single-tier `booping-researcher`**: the rendered roster lists one researcher entry. Reason: matches the consolidation already applied to `/develop` and `/groom`; eliminates stale `booping-researcher-middle` references from the rendered body. Encode the narrow retro use case in `good_for`/`bad_for` bullets.
- **Lazy-load `template_retrospective.md` from Phase 4, not Preflight**: it is only needed when synthesizing in Phase 4. Reason: keeps the baseline skill body small per the project-wide "Lazy-load with `[doc](path)` references" principle. The link target stays at `docs/template_retrospective.md`; the file is not moved.
- **Drop the duplicate lessons-load bullet**: the legacy Preflight had two bullets that loaded `lessons/` (one via `partial_read_lessons.md`, one inline). The standard `!`bin/booping-lessons`` inlines the full lesson set once at load time; both bullets disappear.
- **Drop the explicit "Read attached repo's `CLAUDE.md`" Preflight bullet**: neither `/develop` nor `/groom` carries this in Preflight. `/retro` does not write code in the repo, so the agent-conventions concern is weak. If a phase needs the repo `CLAUDE.md`, it can read it then; nothing in the current retro body actually consumes it inline.
- **Keep all phase content verbatim except the surgical swaps named above**: Phases 0–5, "What retro does NOT do", and "Hard rules" are byte-identical post-migration. Reason: this is a shape migration, not a behavior change; minimizing prose drift makes the regenerated diff readable.

## Architecture

Load-time inputs for the rendered `skills/retro/SKILL.md`:

- `{% include "_partials/_project_context.j2" %}` — `!`bin/booping-project-name`` inline.
- `{{ plan_transitions.render("retro") }}` — `awaiting-retro` row from `config.plan.statuses` (the only state retro owns).
- `{{ available_agents.render("retro") }}` — single `booping-researcher` entry from `config.skills.retro.agents`.
- `!`bin/booping-lessons`` — active lessons inlined once.
- Lazy `[retrospective template](../../docs/template_retrospective.md)` — read in Phase 4 when synthesizing.
- `!`bin/booping-extra-instructions skill_retro.md`` — project-local extension inlined at end of body.

Skill/agent boundary unchanged: orchestrator owns all reads/writes against `~/Claude/{project}/`; the lone delegation is the Phase 0 session-log search to `booping-researcher`. The skill's commit step (Phase 5) keeps its current shape — staging the retrospective, the listed plan files, and `sprints.md`.

## Milestones

### M1: Config expansion — 1 SP | done

**Goal**: `src/config.yaml` carries `skills.retro.effort` and `skills.retro.agents.booping-researcher`. No template or rendered-skill changes yet — `skills/retro/SKILL.md` remains hand-authored after this milestone.

**Verify**: `bin/booping-build` exits 0; `git diff skills/groom/SKILL.md skills/develop/SKILL.md` is empty (no regression in already-generated skills).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `skills.retro` block — `effort: high` and a single-tier `booping-researcher` entry with retro-specific `good_for`/`bad_for` | `src/config.yaml` | 1 | done |

#### Task 1.1 DoD

- [x] `skills.retro.effort: high` added under the existing `skills:` map (alongside `develop` and `groom`).
- [x] `skills.retro.agents.booping-researcher.good_for` includes a bullet covering Phase 0 session-log search across `~/.claude/projects/` aggregated into a structured summary of user questions, blockers, detours.
- [x] `skills.retro.agents.booping-researcher.bad_for` covers: single-file reads (call Read directly); the Phase 2 sprint analysis (stays in the orchestrator); the Phase 4 lesson cross-check (stays in the orchestrator using the in-context lesson set).
- [x] `bin/booping-build` exits 0.
- [x] `git diff skills/groom/SKILL.md skills/develop/SKILL.md` is empty.

---

### M2: Render retro.md.j2 — 3 SP | done

**Goal**: `skills/retro/SKILL.md` becomes a generated artifact rendered from `src/templates/skills/retro.md.j2`. Stale `booping-researcher-middle` references gone. Preflight section removed; project context, transitions, agents, lessons, and project-local extension inline via the standard partials/CLI commands. Phases 0–5, "What retro does NOT do", and "Hard rules" preserved verbatim except where called out.

**Verify**: `bin/booping-build && git diff skills/retro/SKILL.md`; inspect the rendered output against the claude-skill Quality Checklist (no stale state names, no `{{placeholder}}` leaks, every referenced path exists).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Author `src/templates/skills/retro.md.j2` — frontmatter, imports, partials/macros, Phase 0–5 + hard rules + NOT-do block transcribed from existing skill body, lazy retrospective-template link in Phase 4, extra-instructions inline at end | `src/templates/skills/retro.md.j2`, `skills/retro/SKILL.md` (regenerated) | 3 | done |

#### Task 2.1 DoD

**Sequence (order matters — running `bin/booping-build` overwrites `skills/retro/SKILL.md`)**:

1. Read `skills/retro/SKILL.md` first and transcribe its `allowed-tools` list verbatim into the new template's frontmatter. Do this **before** any build command runs. The list includes the constrained Bash entries (`git log *`, `git diff *`, `git show *`, `git add *`, `git commit *`, `ls *`, `booping-plans *`) and `Agent`, `AskUserQuestion`.
2. Transcribe Phase 0 through Phase 5, "What retro does NOT do", and "Hard rules" verbatim from the current `skills/retro/SKILL.md` body. The only edits inside those sections: in Phase 0, replace any `booping-researcher-middle` reference with `booping-researcher`; in Phase 4, replace the bare prose reference to `template_retrospective.md` with a lazy markdown link `[retrospective template](../../docs/template_retrospective.md)` (the link still resolves from `skills/retro/SKILL.md`).
3. Use `src/templates/skills/groom.md.j2` and `src/templates/skills/develop.md.j2` as the reference for `!`bin/…`` inline-command syntax (backtick + exclamation + backtick + path + backtick + backtick); copy that exact form. Do not invent a new syntax.
4. Run `bin/booping-build` once after the template is complete.

**Structural DoD**:

- [x] Frontmatter: `name: retro`, `description` carried over verbatim, `argument-hint` carried over verbatim, `user-invocable: true`, `effort: {{ config.skills.retro.effort }}`, `allowed-tools` list transcribed verbatim from the pre-build `skills/retro/SKILL.md`.
- [x] Top of body: `# booping — /retro` heading and the existing two-paragraph opening (description + "retrospective artifact is the sole output…" + "wide-domain" sentence) carried over verbatim from the current skill body.
- [x] `{% include "_partials/_project_context.j2" %}` placed immediately after the opening paragraphs — replaces the `partial_project_resolution.md` Preflight bullet.
- [x] `{{ plan_transitions.render("retro") }}` placed after the project-context include — replaces both the `partial_plan_statuses.md` and `partial_plan_transitions_retro.md` Preflight bullets.
- [x] `{{ available_agents.render("retro") }}` placed after the transitions table — replaces the `partial_agents_researchers_delegator.md` Preflight bullet.
- [x] `!`bin/booping-lessons`` placed before the `High-level workflow` section — replaces the `partial_read_lessons.md` Preflight bullet *and* the duplicate inline lessons-load bullet (both removed; only the CLI block remains).
- [x] Old `## Preflight` section deleted in its entirety; the per-section replacements above are the only thing standing in for it.
- [x] `## High-level workflow` section: carried over verbatim, with `template_retrospective.md` references reworded to read "the retrospective template" so the lazy link in Phase 4 is the single load point. Six numbered bullets preserved.
- [x] Phase 0 through Phase 5 carried over verbatim except: Phase 0 final paragraph uses `booping-researcher` (no `-middle`); Phase 4 first paragraph uses the markdown link `[retrospective template](../../docs/template_retrospective.md)` instead of bare `template_retrospective.md`. Every other sentence — including Phase 5's commit block, the verbatim STOP error message in Phase 0, the `plans:` YAML snippet — is unchanged.
- [x] `## What retro does NOT do` and `## Hard rules` sections carried over from the existing skill body, then run through lesson `0004`'s four-check pass before saving — every negative rule must pair with an active positive direction (e.g. "Does **not** edit `lessons/`" pairs with "record the implication in the retro body and instruct the user to run `/learn`"). Drop any negative residue without a positive counterpart; do not blind-transcribe.
- [x] `!`bin/booping-extra-instructions skill_retro.md`` present at the very end of body — identical syntax to groom/develop. The legacy `Read from ~/Claude/{project}/_booping/skill_retro.md` Preflight bullet is gone.
- [x] Legacy "Read the attached repo's `CLAUDE.md`" Preflight bullet is gone (no equivalent in groom or develop preflights; Phase 0/Phase 5 do not consume it inline).
- [x] `rg 'booping-researcher-middle' skills/retro/SKILL.md src/templates/skills/retro.md.j2` returns zero matches.
- [x] `rg '\{\{' skills/retro/SKILL.md` returns zero matches (no placeholder leaks).
- [x] `rg 'partial_(plan_transitions_retro|project_resolution|plan_statuses|agents_researchers_delegator|read_lessons)' skills/retro/SKILL.md` returns zero matches (no leftover legacy partial links).
- [x] Rendered `skills/retro/SKILL.md` checked in alongside the template.

---

### M3: Prune orphaned partial + CLAUDE.md — 1 SP | done

**Goal**: `docs/partial_plan_transitions_retro.md` deleted (retro was its sole consumer); CLAUDE.md "Status" block updated to reflect that retro is now template-driven.

**Verify**: `bin/booping-build` exits 0; `rg -l 'partial_plan_transitions_retro' skills/ src/ agents/ bin/ docs/` returns no paths; rendered `skills/retro/SKILL.md` has no broken link.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Verify `partial_plan_transitions_retro.md` is unreferenced, delete it; update CLAUDE.md Status block | `docs/partial_plan_transitions_retro.md`, `CLAUDE.md` | 1 | done |

#### Task 3.1 DoD

- [x] `rg 'partial_plan_transitions_retro' skills/ src/ agents/ bin/ docs/` (excluding the file itself) returns zero matches.
- [x] `docs/partial_plan_transitions_retro.md` deleted with `git rm`.
- [x] CLAUDE.md "Status (April 2026)" block updated: bullet listing template-driven skills now reads "`/groom`, `/develop`, and `/retro`" (or equivalent); the bullet listing hand-authored holdouts drops `retro` and reads `chat`, `learn`, `install`, `help`.
- [x] No other `docs/partial_*.md` files deleted by this task — `partial_project_resolution.md`, `partial_plan_statuses.md`, `partial_agents_researchers_delegator.md`, `partial_read_lessons.md`, and `template_retrospective.md` all still have readers in unmigrated skills (verify by grep before declaring done).
- [x] `bin/booping-build` exits 0.
- [x] Rendered `skills/retro/SKILL.md` reviewed visually — no broken links to the deleted partial.

---

## Final Verification

- [x] `bin/booping-build` regenerates `skills/groom/SKILL.md`, `skills/develop/SKILL.md`, and `skills/retro/SKILL.md` cleanly.
- [x] `rg 'booping-researcher-middle' skills/retro/SKILL.md src/templates/skills/retro.md.j2` returns zero matches.
- [x] `rg -l 'partial_plan_transitions_retro' skills/ src/ agents/ bin/ docs/` returns zero matches.
- [x] Rendered `skills/retro/SKILL.md` satisfies the claude-skill Quality Checklist — no stale state names, no `{{placeholder}}` leaks, every lazy link resolves, `Hard rules` and `What retro does NOT do` carried over verbatim.
- [x] Side-by-side spot-check of pre/post-migration `skills/retro/SKILL.md` confirms phase content is byte-identical except for the three intentional edits (researcher tier rename, retrospective-template lazy link, removed Preflight section).
- [x] `booping-plans --status ready-for-dev` reports this plan after /groom's promotion; `booping-plans --status in-progress` reports it after /develop claims.

## Out of scope

- `/chat`, `/learn`, `/install`, `/help` migrations — those skills stay hand-authored until their own plans.
- Changes to `template_retrospective.md` content or location (lazy-link reference only — file unmoved, unchanged).
- Changes to `agents/booping-researcher.md` or to `awaiting-retro` / `awaiting-learning` transitions in `src/config.yaml` — the data side of the contract is already correct.
- Behavior changes in any phase — Phases 0–5 are byte-identical post-migration except for the three explicit swaps in M2's task DoD.
- Deleting any `docs/partial_*.md` other than `partial_plan_transitions_retro.md` (rest still have readers in unmigrated skills).

## CLAUDE.md impact

Update "Status (April 2026)": move `/retro` from the hand-authored holdouts to the template-driven list. The remaining holdouts are `chat`, `learn`, `install`, `help`. No other section needs changes — config schema is unchanged (only a new `skills.retro.*` block under the existing `skills.<name>.*` pattern that is already documented).
