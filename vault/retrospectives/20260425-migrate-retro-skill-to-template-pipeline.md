---
plans:
  - plans/20260425-migrate-retro-skill-to-template-pipeline.md
date: 2026-04-25
goal_summary: "/retro now mirrors /groom and /develop's template-driven shape — SKILL.md generated from src/templates/skills/retro.md.j2, retro effort + agent roster in config, orphan plan-transitions partial deleted, lessons + project-local extensions inlined via standard CLI commands. Plan's stated business_goal hit clean: success."
---

## What went well

- Three commits, every milestone DoD checked, Final Verification 6/6, sprint window 14:51 → 15:07 (planned to completed) — ~16 minutes elapsed for 5 SP.
- Decisions table held in full: single-tier `booping-researcher`, lazy retrospective-template link in Phase 4, duplicate lessons-load bullet dropped, repo-CLAUDE.md preflight bullet dropped, Phases 0–5 byte-identical (within the three named swaps). No silent deviation.
- Lesson 0004 four-check pass *did* land where M2 Task 2.1 DoD authorized it: `What retro does NOT do` shed four negative-residue bullets (`Does not generate candidate new lessons`, `Does not write a stale-CLAUDE.md impact analysis section`, `Does not edit any CLAUDE.md`, `Does not transition plans to done/cancelled/fail`) and `Hard rules` reshaped negatives into negative+positive pairs (e.g. "CLAUDE.md is out of scope — implications go in the retro body, never as edits"). Concrete win — the migration didn't just mechanically transcribe the legacy body.
- Mechanical Verify checks executed and recorded as zero-match: `rg 'booping-researcher-middle' skills/retro/SKILL.md src/templates/skills/retro.md.j2`, `rg -l 'partial_plan_transitions_retro' skills/ src/ agents/ bin/ docs/`. Lesson 0001 (universal-quantifier enumeration) applied correctly to plan-level Verify.
- Migration shape is now reproducible across three skills (groom → develop → retro). The pattern — M1 config expansion, M2 render template, M3 prune orphans + CLAUDE.md status — was followed without deviation. Future template migrations can lift the structure verbatim.
- Stale-reference cleanup was thorough: `booping-researcher-middle` (renamed to `booping-researcher` after `/develop`'s migration) eliminated repo-wide; `docs/partial_plan_transitions_retro.md` deleted with no broken-link residue; CLAUDE.md "Status (April 2026)" block updated in the same sprint, not deferred.

---

## What went wrong

### Out-of-plan reshaping of the migrated skill in the awaiting-retro window — recurring pattern, third instance

**What happened**: The committed sprint hit its DoD cleanly. Immediately after `fb53304` (M3 final commit), the user kept iterating on `/retro`'s rendered body — currently uncommitted in the working tree as `src/templates/_partials/_retrospective_template.j2`, `src/templates/_partials/_plan_lesson_check.j2`, `src/templates/_partials/_session_log_extraction.j2`, deletion of `docs/template_retrospective.md`, and substantive edits to `src/templates/skills/retro.md.j2` and the rendered `skills/retro/SKILL.md`. Researcher's session-log summary describes inline content redesign (Phase 1.5 lesson cross-check moved upstream into the agent brief, retrospective template embedded as a partial rather than lazy-loaded, `goal_verdict` per-plan added, several `What retro does NOT do` and `Hard rules` bullets cut on a second pass). None of this is in the migration plan.

**Why**: User's stated framing in Phase 3 — "Claude never writes prompts good, and I started to reshape it to fit strict goals." This is structural to how Claude authors prose: the rendered output of a mechanical migration *exposes* the next prose-quality problem the moment it lands. The plan's "shape migration only, byte-identical except 3 swaps" framing was correct for the mechanical work — bundling a full prose redesign into the same plan would have inflated scope and made M2 unreviewable. So the reshape is structurally inevitable; the question is only whether it lives inside the plan or in the awaiting-retro window.

**Impact**: Same pattern the 2026-04-23 retro called out ("Out-of-plan follow-up work during the awaiting-retro window"). Cost is plan-as-documentation fidelity: a future reader diffing `skills/retro/SKILL.md` against the plan that built it will find divergence. Third instance now (after 2026-04-23's `/develop` and `/retro` post-sprint shaping). The previous retro's Action 3 ("decide and record the in-session-shaping policy in repo CLAUDE.md") is still `Planned` two days later — this sprint reproduces the pattern that motivated it.

### Lesson 0004 four-check pass scoped narrowly in M2 — partial application, by design

**What happened**: M2 Task 2.1 DoD applied lesson 0004's four checks (Scoping, Duplication, Configurability, Hierarchy) only to `What retro does NOT do` and `Hard rules`. The rest of the rendered body — Phase 0–5, the new `Project Context` / `Plan Transitions` / `Available Agents` blocks injected by partials — did not get the same scrutiny in the migration sprint. The user's Phase 1 standout names exactly the patterns lesson 0004 lists: "still issues with borderline between ownership in skills, transitions in the config and duplications between, for example, skill body and templates included to the skill (like agents) guidance. The Claude Code oversharing information instead of narrow down into the responsibilities and available knowledge per component. We did quite a lot of such cases in reshaping."

**Why**: Per user's Phase 3 answer ("it's task specific in this case"), the narrow scope was correct for a "shape migration only" plan. Authoring a full four-check sweep over a freshly-rendered body before the user has even read the rendered output is premature — the issues only become visible once the includes resolve. The lesson's spirit reaches the whole rendered body; its application point in this sprint was deliberately constrained to fit the migration's mechanical character.

**Impact**: Not a plan failure — the narrow scoping was a defensible scope decision. The cost is that the four-check pass over the broader body is now happening in the awaiting-retro window (the uncommitted reshaping), not under any plan. So the application of lesson 0004 is happening, but invisibly to plans-as-documentation.

### Ignored / unapplied lessons

- `lessons/0004_information-architecture-pattern.md` — rule was "every prompt-bearing artefact must pass Scoping / Duplication / Configurability / Hierarchy". Applied correctly to the two sections M2 explicitly named (`What retro does NOT do`, `Hard rules`) — not a silent skip; the plan recorded the scope. Not extended to the rendered body's other sections (Phase 0–5, the partial-injected blocks), where the user's Phase 1 standout reports the four-check would have caught real ownership/duplication issues. The deliberate narrow scope is defensible (per user's Phase 3 answer); the gap is that the broader application is now happening unplanned in the awaiting-retro window.

---

## Root causes

1. **Mechanical-migration plans correctly stop at "render", but the rendered output exposes the next prose-quality problem the moment it lands.** This is structural — Claude's prose-authoring quality means the rendered body of a freshly-migrated skill always has shape-level issues that only become visible post-render. The plan can't pre-empt them without ballooning into a full redesign. The result is a predictable two-phase rhythm: planned mechanical migration → unplanned post-render reshape. This is the third instance in two days.

2. **The previous retro's Action 3 — "decide and record in-session-shaping policy in repo CLAUDE.md" — is still pending and is the structural fix for cause #1.** The pattern is now well-attested: three sprints, three reshapes during awaiting-retro. Whether the policy is "this is fine, document it as a project mode" or "split a follow-up plan before the reshape begins" matters less than that the policy gets recorded. Until it does, every template-pipeline migration ships into the same ambiguity.

---

## Action items

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Reaffirm the 2026-04-23 retro's Action 3 — decide and record the in-session-shaping policy in repo `CLAUDE.md`. Three reshapes in two days have now reproduced the pattern; the decision is overdue. (Note: `/retro` does not edit `CLAUDE.md`; this action is recorded for the user, not the skill.) | User | Planned (carried over from 2026-04-23) |
| 2 | Commit the uncommitted retro-skill reshaping under its own scope — either as ad-hoc work tagged in the commit message ("post-render shape pass") or as a small follow-up plan. The current half-staged working tree is itself the documentation gap. | User | Planned |

---

## Takeaways for this project

- **A "shape migration only" plan is the right scope for mechanical template-pipeline work — but expect a same-day post-render reshape, and either name it in the plan header or commit it under a separate scope.** Three sprints have now confirmed the rhythm: M1/M2/M3 lands the mechanical migration cleanly, the user reads the rendered output, the prose-shape issues become visible, the user reshapes. Pretending the reshape won't happen is what creates the plans-as-documentation drift.
- **Scoping lesson 0004's four-check pass to a named section (or two) inside an M-DoD is the right granularity for migration plans.** A whole-body four-check pass before the body is rendered is premature — the includes haven't resolved yet. The pattern that worked here was: M2 Task 2.1 listed `What retro does NOT do` and `Hard rules` explicitly as the in-scope four-check targets. Future migrations can lift this exact shape.
- **Mechanical Verify checks (rg-style universal-quantifier enumeration in plan DoD) carry the migration end-to-end with no manual review burden.** The Final Verification block's `rg 'booping-researcher-middle'` and `rg -l 'partial_plan_transitions_retro'` returning 0 was the entire signal needed. This is lesson 0001 working as intended at plan scale.
- **Stale-reference cleanup belongs inside the migration sprint, not after.** M3's pruning of `docs/partial_plan_transitions_retro.md` and CLAUDE.md "Status" update worked because the plan made them milestone tasks with their own DoD. Splitting them into a follow-up sweep would have left the working tree inconsistent for hours or days.

---

## Self-review checklist

- [x] Each "what went wrong" item has a traceable cause (plan decision, blind spot, or carried debt).
- [x] Root causes are patterns, not restatements of individual issues.
- [x] Ignored-lesson flags cite existing lessons by path and explain the gap.
- [x] Action items are specific with an owner and a clear next step.
- [x] Takeaways are heuristics, not platitudes — someone could apply them next sprint.
- [x] "What went well" is honest, not inflated to balance criticism.
- [x] No blame language — focus on decisions and processes, not people.
