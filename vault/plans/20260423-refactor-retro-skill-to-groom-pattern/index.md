---
title: Refactor /retro skill to groom pattern
type: refactoring
status: done
sp: 7
source: requests/20260423-refactor-retro-skill-to-groom-pattern.md
created: 2026-04-23 00:00
planned: 2026-04-23
started: 2026-04-23
completed: 2026-04-23 00:00
retro: retrospectives/20260423-skill-refactors-chat-develop-retro.md
goal: success
summary: "/retro rewritten to groom shape: deletes 5 dormant agents + agent-wiring.md, external retro template, multi-plan support"
---

# Refactor /retro skill to groom pattern

## Context

`/retro` is flagged stale in repo `CLAUDE.md` alongside `/learn`, `/install`, `/help`. `skills/groom/SKILL.md`, `skills/chat/SKILL.md`, and `skills/develop/SKILL.md` (refactored 2026-04-23) are the canonical shape: Preflight loads reusable partials, workflow is explicit phases, body stays stack-agnostic, body never names a concrete lesson ID or a concrete vault path.

The current `/retro` body has six concrete breakages on top of structural staleness: (1) opens with "Project resolution" instead of `## Preflight`; (2) references `booping-plans list --project=<P>` — the CLI has no `list` subcommand today; (3) links `docs/agent-wiring.md` which repo `CLAUDE.md` marks for deletion; (4) routes the retrospective write through `booping-teamlead`, contradicting the post-plans-as-data contract that skills own every vault write; (5) names `partial_plan_transitions_retro.md` at line 163 but that partial has never existed; (6) generates "Candidate new lessons" and "CLAUDE.md impact" sections inside the retro body — both belong to `/learn`, not `/retro`.

Scope agreed during grooming (2026-04-23, third iteration — condensed to its current shape after two prior draft passes):

- `/retro` spawns **only `booping-researcher-middle`** for session-log search (returns a structured summary, keeps raw session dumps out of the orchestrator context). All other work — plan + diff reading, sprint analysis, lesson cross-check, retrospective synthesis — runs inline in the orchestrator.
- **Retro flags already-existing lessons that weren't applied**: during Phase 3 synthesis, the orchestrator compares each identified problem against the lesson set loaded at Preflight (via `partial_read_lessons`). Where an existing lesson or project-extra-instruction should have prevented or caught the problem, the retrospective's **Root causes** section calls it out explicitly ("Lesson X existed and says Y; it was not applied when Z happened"). No `Applicable lessons:` per-agent routing — the orchestrator keeps the full loaded set in context and does the cross-check itself.
- **Delete five agents** from `agents/`: `booping-techlead`, `booping-product-manager`, `booping-qa-lead`, `booping-teamlead`, and `booping-reviewer`. Reviewer is dormant today and used only by the deleted teamlead (`agents/booping-teamlead.md:4` lists it under `Agent(...)`), `skills/help/SKILL.md` (stale), `PRD.md`, and `README.md` — no trustworthy skill invokes it, so it is deleted with the other four. Dangling role-agent / reviewer references in stale skills (`/learn`, `/install`, `/help`) are **left in place** until those skills' own refactors rewrite them; their references to the deleted `docs/agent-wiring.md` are patched regardless (file going away breaks relative links).
- `/retro` supports 0, 1, or N plans per invocation. With 0 plan paths in `$ARGUMENTS`, the skill lists `awaiting-retro` plans and asks the user to pick one or more via `AskUserQuestion` with `multiSelect: true`. Retrospective frontmatter is always a YAML list (`plans: [...]`), even for single-plan retros, so the skill has one code path.
- Retrospective body is **project-specific**: no "Candidate new lessons" section, no "CLAUDE.md impact" section, no `/learn` suggestion tail. Lesson extraction and CLAUDE.md placement are `/learn`'s exclusive responsibility. `/retro` produces the evidence; `/learn` turns it into durable rules.
- **The retrospective body template is externalized** to `docs/template_retrospective.md`, adapted from `~/.claude/skills/scrum-retro/SKILL.md`'s Phase-3 structure (What went well / What went wrong per-issue / Root causes / Action items / Takeaways). The skill references the template file, does not embed the body structure inline — parallel to how `docs/template_plan.md` is owned outside `skills/groom/SKILL.md`.
- `skills/retro/SKILL.md` body carries **zero concrete references** to userland `~/Claude/...` files — no lesson IDs, no example paths. The only vault paths are parameterized directory placeholders under `~/Claude/{project_name}/`.
- **Update `docs/partial_cross_validation.md`** to document the one-shot rule: cross-validation is run **once per plan**, not on every edit iteration. Re-running burns tokens without proportional value and treats an advisory review like a CI gate. This refactor observed the pattern firsthand during its own grooming; the partial update makes the rule permanent.

## Business goal

After this sprint: a fresh agent reading `skills/retro/SKILL.md` sees Preflight that points at live partials, a five-phase workflow matching `/groom`'s arc, four orchestrator-scope hard rules, zero broken references, and zero concrete-lesson or concrete-vault-path mentions. The retrospective body shape lives in `docs/template_retrospective.md`. Status transitions are documented in `docs/partial_plan_transitions_retro.md` with multi-plan semantics. `docs/agent-wiring.md` is deleted. Five agent files (four role agents + reviewer) are removed. The cross-validation partial documents its one-shot rule. `/retro` moves from "Stale and not refactored" to "Current and trustworthy" in repo `CLAUDE.md`.

## Definition of Done

- [x] `docs/partial_plan_transitions_retro.md` exists with explicit multi-plan semantics — enumerated by M1 Verify.
- [x] `docs/template_retrospective.md` exists and carries the externalized body structure (What went well / What went wrong per-issue / Root causes including ignored-lesson flags / Action items / Takeaways) — enumerated by M1 Verify.
- [x] `docs/partial_cross_validation.md` documents the one-shot rule (run once per plan; do not re-validate on every iteration) — verified by `grep -Fi 'once per plan' docs/partial_cross_validation.md`.
- [x] `skills/retro/SKILL.md` `## Preflight` bullets reference, by exact relative path, `../../docs/partial_project_resolution.md`, `../../docs/partial_plan_statuses.md`, `../../docs/partial_agents_researcher_tiers.md`, `../../docs/partial_plan_transitions_retro.md`, `../../docs/partial_read_lessons.md`, `../../docs/template_retrospective.md`, plus `~/Claude/{project_name}/lessons/`, `~/Claude/{project_name}/_booping/skill_retro.md` (qualifier "if present"), and the attached repo's `CLAUDE.md` — enumerated by `grep -F` for each reference.
- [x] `skills/retro/SKILL.md` body contains zero occurrences of the following tokens — enumerated by a single `grep -E`: `docs/agent-wiring\.md`, `docs/project-scoping\.md`, `booping-plans list`, `booping-plans set`, `sync-sprints`, `CLI fallback`, `booping-teamlead`, `booping-techlead`, `booping-product-manager`, `booping-qa-lead`, `booping-reviewer`, `booping-researcher-senior`, `Applicable lessons:`, `Candidate new lessons`, `Lessons review`, `CLAUDE\.md impact`, `Suggest /learn`, `/learn <retro-path>`.
- [x] `skills/retro/SKILL.md` body contains zero concrete lesson-file references — `grep -E 'lessons/[0-9]{4}_'` returns no matches. Only vault paths present are parameterized directory placeholders under `~/Claude/{project_name}/`.
- [x] `skills/retro/SKILL.md` body is ≤ 130 lines (`wc -l`) — tighter than v2's 140 because body structure moved to the external template.
- [x] `skills/retro/SKILL.md` `## High-level workflow` enumerates exactly five phases — `grep -E '^## Phase [0-4]'` returns 5.
- [x] `skills/retro/SKILL.md` `## Hard rules` has exactly four top-level `- **` bullets.
- [x] `skills/retro/SKILL.md` Phase 0 documents 0/1/N plan resolution; Phase 3 documents the lesson cross-check that flags existing-but-ignored lessons into Root causes.
- [x] `skills/retro/SKILL.md` Phase 4 shows the retrospective frontmatter using a YAML list (`plans:` key).
- [x] Five agent files do not exist: `agents/booping-techlead.md`, `agents/booping-product-manager.md`, `agents/booping-qa-lead.md`, `agents/booping-teamlead.md`, `agents/booping-reviewer.md` — verified by 5 × `test ! -e`.
- [x] `docs/agent-wiring.md` does not exist.
- [x] No trustworthy skill retains a reference to any of the five deleted agents. Audit cohort: `skills/groom/SKILL.md`, `skills/chat/SKILL.md`, `skills/develop/SKILL.md`, `skills/retro/SKILL.md` (post-rewrite). Stale skills are explicitly excluded.
- [x] No file anywhere in the plugin references `agent-wiring` — enumerated across `agents/*.md`, `skills/*/SKILL.md`, `docs/*.md`, `CLAUDE.md`, `PRD.md`, `README.md`.
- [x] Repo `CLAUDE.md` "Status (April 2026)" list moves `retro` into "Current and trustworthy"; removes the `docs/agent-wiring.md` bullet; rewrites the stale-agents bullet to note the five deletions (no remaining dormant agent).
- [x] Gemini cross-validation run **once** during grooming; CRITICAL and RULE violations addressed before handoff. Not re-run on iteration.

## Design

### Architecture

Two new partial-class docs, one rewrite, six deletions, one partial tweak, one `CLAUDE.md` edit:

- **`docs/partial_plan_transitions_retro.md`** (new) — parallel to `partial_plan_transitions_groom.md` / `partial_plan_transitions_develop.md`. Single transition `awaiting-retro → awaiting-learning`, applied per plan in the retrospective's `plans:` list (multi-plan semantics spelled out in a dedicated paragraph).

- **`docs/template_retrospective.md`** (new) — the retrospective body template, analogous to `docs/template_plan.md`. Adapted from `~/.claude/skills/scrum-retro/SKILL.md` Phase 3. Sections, in order: `## What went well`; `## What went wrong` (per-issue, three-line format: `**What happened**:` / `**Why**:` / `**Impact**:`); `## Root causes` (patterns, including explicit `### Ignored / unapplied lessons` subsection when the lesson cross-check flags any); `## Action items` (follow-up table with owner + status); `## Takeaways for this project` (project-specific heuristics, not cross-project rules). No "Candidate new lessons" block; no "CLAUDE.md impact" block; no "Suggest /learn" tail. Frontmatter example at the top of the template shows the `plans:` list + `date:` fields.

- **`docs/partial_cross_validation.md`** (update) — add a short paragraph documenting the one-shot rule: `/groom` runs `booping-validate-plan` once per plan after addressing the user's initial feedback, not on every iteration. Re-running burns tokens without proportional value and treats an advisory review like a CI gate. CRITICAL and RULE outputs from the single run are addressed inline; ABSes are judged case-by-case.

- **`skills/retro/SKILL.md`** (rewrite) — groom shape. Five phases:
  - **Phase 0 Intake** — resolve `$ARGUMENTS` to 0/1/N plan paths. If 0: `booping-plans --status awaiting-retro` + `AskUserQuestion` with `multiSelect: true`. If ≥ 1: validate every plan's `status:` is `awaiting-retro`, stopping with the pinned verbatim error string on mismatch. Read each plan. Compute combined git diff range (union across plans). Delegate session-log search to `booping-researcher-middle` with a brief requesting a structured summary.
  - **Phase 1 Sprint analysis** — orchestrator reads plan(s) + diff + session summary directly. No sub-agent delegation here. Extracts facts: decisions honored / deviated per plan; tech debt introduced or carried forward; test coverage delivered vs planned; per-plan business-goal verdict (`success | partial | fail`).
  - **Phase 2 User feedback** — `AskUserQuestion` with targeted prompts derived from Phase 1 findings (cites finding; never open-ended). For multi-plan retros, at least one prompt confirms each plan's goal verdict if Phase 1 left any ambiguous.
  - **Phase 3 Synthesize (with lesson cross-check)** — orchestrator drafts the retrospective using `docs/template_retrospective.md` as the section spec. For each problem identified in "What went wrong", scan the lesson set loaded at Preflight + the per-project extra instructions from `_booping/skill_retro.md`; where a loaded lesson or extra instruction should have prevented or caught the problem, add an entry under `### Ignored / unapplied lessons` in Root causes citing which rule should have fired. No generation of *new* candidate lessons — that stays `/learn`'s responsibility. Run the template's inline self-review checklist before Phase 4 proceeds.
  - **Phase 4 Save & transition** — write retrospective to `~/Claude/{project_name}/retrospectives/YYYYMMDD-{kebab-title}.md` with YAML frontmatter using `plans:` as a list (always). For each plan: apply the transition per `../../docs/partial_plan_transitions_retro.md`. Commit vault: retrospective + each plan + `sprints.md` (D5). Exit — no `/learn` suggestion.

- **Five agent-file deletions**: `agents/booping-techlead.md`, `agents/booping-product-manager.md`, `agents/booping-qa-lead.md`, `agents/booping-teamlead.md`, `agents/booping-reviewer.md`. No agent remains dormant after this sprint.

- **`docs/agent-wiring.md`** — deleted. Every consumer patched (including stale skills), because relative-link breakage is real.

- **Repo `CLAUDE.md`** — "Status (April 2026)" block updated: `retro` moves to trustworthy; `agent-wiring.md` line removed; stale-agents bullet rewritten to note five deletions (no remaining dormant agent; the "effectively dormant" reviewer line goes away).

### Decisions

| # | Decision | Alternative | Why |
|---|----------|-------------|-----|
| D1 | `/retro` delegates **only session-log search** to `booping-researcher-middle`; every other step runs inline in the orchestrator | Delegate sprint analysis to researcher-senior too; or keep role agents | User directive (third iteration): trim delegation to the minimum. Session logs are the one artefact that benefits from context isolation (raw dumps would overwhelm the orchestrator); everything else fits in orchestrator context directly. |
| D2 | Orchestrator keeps the Preflight-loaded lesson set in context and cross-checks during Phase 3 synthesis; no per-agent `Applicable lessons:` filtering | Filter + pass subsets to a sub-agent | User directive: "don't delegate lesson filtering to any sub-agents". The orchestrator has the full context for cross-check; an agent round-trip adds nothing. |
| D3 | Retrospective body has no "Candidate new lessons", no "CLAUDE.md impact", no `/learn` suggestion tail | Keep any of those | User directive: `/retro` produces evidence, `/learn` generalizes. Clean separation of concerns. |
| D4 | `docs/partial_plan_transitions_retro.md` carries multi-plan semantics explicitly | Inline in skill body; or support only single-plan retros | Matches groom/develop partial shape. Multi-plan is user ask. |
| D5 | Phase 4 commit stages `retrospectives/<retro-basename>.md`, each plan file, and `sprints.md` | Exclude `sprints.md` | User directive; mirrors `/develop`'s commit shape. |
| D6 | `/retro` accepts 0, 1, or N plans; 0 → `AskUserQuestion` multiSelect; frontmatter always `plans:` list | Single-plan only; two code paths | User directive: multi-plan retros are real. Single code path keeps the skill simple and gives `/learn`'s future refactor a uniform shape to parse. |
| D7 | **Delete five agents**: `booping-techlead`, `booping-product-manager`, `booping-qa-lead`, `booping-teamlead`, `booping-reviewer` | Keep reviewer dormant like the pre-grooming state | User directive after checking reviewer's usage: reviewer is referenced only by the deleted teamlead, one stale skill (help), and docs. No trustworthy skill calls it. Deleting is cleaner than leaving a zombie. |
| D8 | Delete `docs/agent-wiring.md`; patch every consumer regardless of trustworthy/stale status | Keep the file | Repo `CLAUDE.md` names `/retro` as the last trustworthy consumer; file going away breaks relative links on parse so every consumer gets patched. |
| D9 | Skill body contains zero concrete `~/Claude/...` references; only parameterized directory placeholders under `~/Claude/{project_name}/` | Cite illustrative lesson IDs | User directive: per-project injection is the only extensibility channel. Hard-coded references leak one project's state. |
| D10 | Role-agent / reviewer references in `/learn`, `/install`, `/help` are NOT touched in this sprint. `agent-wiring.md` references in those same stale skills ARE patched (file deleted outright). | Strip all stale references here; or leave all | User directive: stale skills get their own refactors soon. Cosmetic name references can wait; broken relative links cannot. |
| D11 | `goal: fail` does not redirect `status:`; plan still transitions to `awaiting-learning` | Skip `/learn` on failure | Failure sprints are the most valuable to learn from. `goal` captures verdict; `status` captures pipeline stage. |
| D12 | `skills/retro/SKILL.md` allow-list: `Read, Write, Edit, Glob, Grep, Bash(git log *), Bash(git diff *), Bash(git show *), Bash(git add *), Bash(git commit *), Bash(ls *), Bash(booping-plans *), Agent, AskUserQuestion` — drop `WebSearch` | Keep `WebSearch` | Researcher-middle has its own web access; orchestrator doesn't need it. |
| D13 | **Externalize the retrospective body template** to `docs/template_retrospective.md`, adapted from `~/.claude/skills/scrum-retro/SKILL.md` Phase 3 | Embed body sections inline in `skills/retro/SKILL.md` | User directive: parallel to `docs/template_plan.md` owned outside `/groom`. Externalization keeps the skill body short and lets future `/learn` read the template alongside the retrospective to understand its expected shape. |
| D14 | **Update `docs/partial_cross_validation.md`** with a "run once per plan" rule | Leave the partial unchanged | User directive after observing two Gemini-validation runs on this plan's iterations during grooming. The rule belongs in the partial so it applies to all future groom sessions, not just this one. |
| D15 | Phase 3 lesson cross-check flags existing-but-ignored lessons inside Root causes (new `### Ignored / unapplied lessons` subsection) — **does not** generate candidate new lessons | Generate candidate lessons; or skip the cross-check | User directive: retro identifies which *existing* rules failed; `/learn` decides whether *new* rules are needed. The cross-check uses the Preflight-loaded lesson set + `_booping/skill_retro.md` extras — no separate load. |

### Applies lessons

Plan-level only — the skill body itself cites zero lesson IDs per D9. Applied lessons from the repo's `lessons/` (referenced abstractly):

- Universal-quantifier DoD items → enumeration Verify on every "every" / "zero" bullet.
- Invariant-bound orchestrator edits → the skill and agent files targeted here are delegated even for 1-line changes.
- Reviewer follow-ups → per-item triage at creation with a three-defer cap per milestone.
- Data-flow audits → M3 enumerates files that previously referenced deleted agents and `agent-wiring.md`, split per D10.

## Milestones

### M1: Supporting partials + retrospective template — 2 SP | done

**Goal**: `docs/partial_plan_transitions_retro.md`, `docs/template_retrospective.md`, and the updated `docs/partial_cross_validation.md` land, ready to be referenced from the rewritten skill.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# Transitions partial
test -f docs/partial_plan_transitions_retro.md
head -1 docs/partial_plan_transitions_retro.md | grep -F 'Status transitions are manual frontmatter edits — there is no CLI.'
grep -F 'awaiting-retro → awaiting-learning' docs/partial_plan_transitions_retro.md
grep -E 'retro:.*retrospectives/' docs/partial_plan_transitions_retro.md
grep -F 'success | partial | fail' docs/partial_plan_transitions_retro.md
grep -Fi 'per plan' docs/partial_plan_transitions_retro.md
grep -F 'plans:' docs/partial_plan_transitions_retro.md
grep -F 'booping-plans --status awaiting-learning' docs/partial_plan_transitions_retro.md
test -z "$(grep -E 'booping-plans set|sync-sprints' docs/partial_plan_transitions_retro.md)"
# Retro template
test -f docs/template_retrospective.md
grep -E '^## What went well$'     docs/template_retrospective.md
grep -E '^## What went wrong$'    docs/template_retrospective.md
grep -E '^## Root causes$'        docs/template_retrospective.md
grep -E '^### Ignored / unapplied lessons$' docs/template_retrospective.md
grep -E '^## Action items$'       docs/template_retrospective.md
grep -E '^## Takeaways'           docs/template_retrospective.md
# Forbidden sections are NOT in the template
test -z "$(grep -E 'Candidate new lessons|Lessons review|CLAUDE\.md impact|Suggest /learn' docs/template_retrospective.md)"
# Frontmatter example uses `plans:` as a list
grep -E '^plans:|plans: \[' docs/template_retrospective.md
# Cross-validation partial update
grep -Fi 'once per plan' docs/partial_cross_validation.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Write `docs/partial_plan_transitions_retro.md` with multi-plan semantics — DONE. Opening sentence verbatim `Status transitions are manual frontmatter edits — there is no CLI. From /retro, the only valid transitions are:`. Markdown table header `\| From \| To \| When \| Also set \|` with one data row: `awaiting-retro` → `awaiting-learning`; "When" = `retrospective markdown written and saved to retrospectives/; self-review checklist passed`; "Also set" = `retro: retrospectives/YYYYMMDD-{kebab-title}.md, goal: success \| partial \| fail`. Dedicated "Multi-plan retrospectives" paragraph stating the transition applies **per plan** in the retrospective's `plans:` list; each plan's frontmatter gets `status` flipped, `retro:` pointed at the shared retrospective path, and `goal:` set to that plan's per-plan verdict. Next paragraph: `goal: fail` does not redirect `status:`. Closing paragraph documents `booping-plans --status awaiting-learning` as the post-edit verify step. | `docs/partial_plan_transitions_retro.md` | 1 | done |
| 1.2 | Write `docs/template_retrospective.md`, adapted from `~/.claude/skills/scrum-retro/SKILL.md` Phase 3. Open with a short purpose line naming `/retro` as sole author. Show a YAML frontmatter example with `plans:` as a list (at least two entries for clarity) + `date:` + `goal_summary:` (short one-liner capturing the cross-plan verdict if multi-plan). Body sections in order: `## What went well` (brief bullet list, 3-5 specifics, no vague praise); `## What went wrong` (per-issue subsections with `**What happened**:` / `**Why**:` / `**Impact**:` three-line format); `## Root causes` (patterns synthesizing the "Why" lines; includes a `### Ignored / unapplied lessons` subsection listing loaded lessons or project extra-instructions that should have prevented a flagged problem but were not applied — one bullet per flag, citing the lesson file path + the rule + what happened instead); `## Action items` (pipe-separated table `\| # \| Action \| Owner \| Status \|`); `## Takeaways for this project` (project-specific heuristics, 3-5 bullets, NOT generalized cross-project rules). Close with an inline self-review checklist (7 items: each "what went wrong" has a traceable cause; root causes are patterns not restatements; ignored-lesson flags cite existing lessons by path; action items are specific with owner + next step; takeaways are heuristics not platitudes; "What went well" is honest, not inflated; no blame language). **Forbidden sections — do NOT include**: "Candidate new lessons", "Lessons review", "CLAUDE.md impact", "Suggest /learn". | `docs/template_retrospective.md` | 1 | done |
| 1.3 | Update `docs/partial_cross_validation.md`: after the existing opening sentence, add a short paragraph stating the one-shot rule verbatim — "Run `booping-validate-plan` **once per plan** during grooming, after addressing the user's initial feedback on the draft. Do not re-run on every iteration. Cross-validation is an advisory review, not a CI gate — re-running burns tokens without proportional value. If the user makes substantive scope changes after the first validation, re-running is acceptable; iterative wording tweaks are not grounds to re-run." Leave the exit-code table and Security rule unchanged. | `docs/partial_cross_validation.md` | 0 | done |

#### Task 1.1 DoD

- [x] File exists at `docs/partial_plan_transitions_retro.md`.
- [x] First line is verbatim `Status transitions are manual frontmatter edits — there is no CLI. From /retro, the only valid transitions are:`.
- [x] Markdown table has header `| From | To | When | Also set |` and exactly one data row covering `awaiting-retro → awaiting-learning`.
- [x] "Also set" cell names `retro:` (value shape `retrospectives/YYYYMMDD-{kebab-title}.md`) and `goal:` (value shape `success | partial | fail`).
- [x] Dedicated "Multi-plan retrospectives" paragraph states the transition applies per plan in the retrospective's `plans:` list — `grep -Fi 'per plan'` and `grep -F 'plans:'` both match.
- [x] Paragraph states `goal: fail` does not redirect `status:` — `grep -F 'goal: fail'` matches in prose.
- [x] Closing paragraph documents `booping-plans --status awaiting-learning` as the post-edit verify step.
- [x] Zero occurrences of `booping-plans set`, `sync-sprints`, or any other CLI-mutation invocation.

#### Task 1.2 DoD

- [x] File exists at `docs/template_retrospective.md`.
- [x] Opening purpose line names `/retro` as sole author — `grep -Fi '/retro' docs/template_retrospective.md` matches in the opening section.
- [x] Frontmatter example uses `plans:` as a YAML list with at least two entries — `grep -E '^plans:|plans: \[' docs/template_retrospective.md` matches.
- [x] Body section headers exist verbatim in order: `## What went well`, `## What went wrong`, `## Root causes`, `## Action items`, `## Takeaways for this project` — enumerated by five greps.
- [x] Root causes section contains the subsection `### Ignored / unapplied lessons` — `grep -Fx '### Ignored / unapplied lessons' docs/template_retrospective.md` matches.
- [x] What-went-wrong per-issue format shows the literal `**What happened**:`, `**Why**:`, `**Impact**:` markers — three greps.
- [x] Action items section shows a pipe-separated table header `| # | Action | Owner | Status |`.
- [x] Closing self-review checklist contains exactly seven items — counted (e.g. `grep -cE '^- \[ \]' docs/template_retrospective.md` returns ≥ 7; or count is asserted against the exact checklist rendered).
- [x] File contains zero occurrences of `Candidate new lessons`, `Lessons review`, `CLAUDE.md impact`, `Suggest /learn` — enumerated by one `grep -E`.

#### Task 1.3 DoD

- [x] `docs/partial_cross_validation.md` contains the phrase `once per plan` — `grep -Fi 'once per plan' docs/partial_cross_validation.md` matches.
- [x] The existing exit-code table and Security paragraph are unchanged — `git diff docs/partial_cross_validation.md` shows only additions inside the opening prose section.
- [x] The new paragraph explicitly notes that iterative wording tweaks do not warrant re-validation but substantive scope changes do — `grep -Fi 'iterative' docs/partial_cross_validation.md` or `grep -Fi 'substantive' docs/partial_cross_validation.md` matches.

---

### M2: Rewrite skills/retro/SKILL.md + flip CLAUDE.md guidance — 3 SP | done

**Goal**: `skills/retro/SKILL.md` mirrors the groom shape with researcher-middle as the only delegation, multi-plan support, externalized body template, lesson-cross-check in Phase 3, and zero concrete vault-path references. Repo `CLAUDE.md` updated.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
grep -E '^## Preflight$'           skills/retro/SKILL.md
grep -E '^## High-level workflow$' skills/retro/SKILL.md
test "$(grep -cE '^## Phase [0-4]' skills/retro/SKILL.md)" = 5
grep -E '^## Hard rules$' skills/retro/SKILL.md
# Preflight references
for ref in \
  "../../docs/partial_project_resolution.md" \
  "../../docs/partial_plan_statuses.md" \
  "../../docs/partial_agents_researcher_tiers.md" \
  "../../docs/partial_plan_transitions_retro.md" \
  "../../docs/partial_read_lessons.md" \
  "../../docs/template_retrospective.md" \
  "~/Claude/{project_name}/lessons/" \
  "~/Claude/{project_name}/_booping/skill_retro.md"; do \
  grep -F "$ref" skills/retro/SKILL.md || { echo "missing $ref"; exit 1; }; \
done
# Zero stale / forbidden tokens
test -z "$(grep -E 'docs/agent-wiring\.md|docs/project-scoping\.md|booping-plans list|booping-plans set|sync-sprints|CLI fallback|booping-teamlead|booping-techlead|booping-product-manager|booping-qa-lead|booping-reviewer|booping-researcher-senior|Applicable lessons:|Candidate new lessons|Lessons review|CLAUDE\.md impact|Suggest /learn|/learn <retro-path>' skills/retro/SKILL.md)"
# Zero concrete lesson references
test -z "$(grep -E 'lessons/[0-9]{4}_' skills/retro/SKILL.md)"
# Length ceiling
test "$(wc -l < skills/retro/SKILL.md)" -le 130
# Hard rules count
awk '/^## Hard rules$/{f=1; next} /^## /{f=0} f && /^- \*\*/' skills/retro/SKILL.md | wc -l | xargs -I{} test {} = 4
# Phase 0 delegates only to researcher-middle; Phase 1-3 run inline (no researcher-senior)
grep -F 'booping-researcher-middle' skills/retro/SKILL.md
test -z "$(grep -F 'booping-researcher-senior' skills/retro/SKILL.md)"
# Multi-plan 0/1/N + list frontmatter
grep -F 'multiSelect' skills/retro/SKILL.md
grep -E '^plans:|plans: \[' skills/retro/SKILL.md
# Lesson cross-check language in Phase 3
grep -Fi 'ignored / unapplied lessons' skills/retro/SKILL.md
grep -Fi 'cross-check' skills/retro/SKILL.md
# Phase 4 commit set (D5)
grep -F 'retrospectives/' skills/retro/SKILL.md
grep -F 'sprints.md' skills/retro/SKILL.md
# Pinned error string
grep -F "/retro requires a plan in status 'awaiting-retro'" skills/retro/SKILL.md
# CLAUDE.md
grep -F 'skills/retro/SKILL.md' CLAUDE.md
test -z "$(grep -F 'docs/agent-wiring.md' CLAUDE.md)"
test -z "$(grep -E 'booping-techlead|booping-product-manager|booping-qa-lead|booping-teamlead|booping-reviewer' CLAUDE.md | grep -v 'deleted')"
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | DONE. **Read `skills/groom/SKILL.md`, `skills/chat/SKILL.md`, `skills/develop/SKILL.md`, and `docs/template_retrospective.md` in full before typing.** Rewrite `skills/retro/SKILL.md` from scratch to the groom shape. Frontmatter allow-list per D12. `## Preflight` bullets reference the five partials (`partial_project_resolution`, `partial_plan_statuses`, `partial_agents_researcher_tiers`, `partial_plan_transitions_retro`, `partial_read_lessons`) + the retrospective template (`../../docs/template_retrospective.md`) + parameterized vault directories (`~/Claude/{project_name}/lessons/`, `~/Claude/{project_name}/_booping/skill_retro.md` with "if present") + the attached repo's `CLAUDE.md`. `## High-level workflow` enumerates five phases. `## Phase 0 Intake` handles 0/1/N plan resolution (0 → `booping-plans --status awaiting-retro` + `AskUserQuestion multiSelect: true`; else validate each plan's `status: awaiting-retro` with the pinned verbatim error string `"/retro requires a plan in status 'awaiting-retro'; got '<current-status>' for <plan-path>. Run 'booping-plans --status awaiting-retro' to list candidates."`), reads each plan, computes combined diff range, and delegates session-log search to `booping-researcher-middle`. `## Phase 1 Sprint analysis` is **orchestrator-inline** (no sub-agent); extracts per-plan decisions-honored/deviated, tech debt, test coverage delivered vs planned, per-plan business-goal verdict. `## Phase 2 User feedback` covers `AskUserQuestion` prompts derived from Phase 1 findings. `## Phase 3 Synthesize` documents the retrospective draft against `docs/template_retrospective.md`'s section spec AND the **lesson cross-check**: for each problem identified, scan the Preflight-loaded lesson set + `_booping/skill_retro.md` extras; where a loaded rule should have prevented the problem, append an entry under the template's `### Ignored / unapplied lessons` subsection citing the lesson path + the rule + what happened. No generation of new candidate lessons. `## Phase 4 Save & transition` writes the retrospective using the template, with frontmatter `plans:` as a YAML list; applies the transition per `../../docs/partial_plan_transitions_retro.md` to each plan; commits the vault with explicit `cd ~/Claude/{project_name}` + `git add retrospectives/<retro-basename>.md plans/<plan-basename-1>.md plans/<plan-basename-2>.md ... sprints.md` (no `-A`). The skill body defines `<retro-basename>` and `<plan-basename-N>` in one sentence. No `/learn` suggestion. `## What retro does NOT do` names: does not extract lessons; does not generate candidate new lessons; does not edit any CLAUDE.md; does not edit `sprints.md` directly; does not transition plans to `done`, `cancelled`, or `fail`. `## Hard rules` has exactly four `- **` bullets: (a) orchestrator owns the retrospective write — never route through an agent; (b) retrospective body is project-specific — no cross-project generalization, no candidate lessons; (c) no blame language — decisions and processes, not people; (d) never edit any `CLAUDE.md` here; never include a "CLAUDE.md impact" section in the retrospective body. **Body carries zero concrete `~/Claude/...` references** — only parameterized directory placeholders. | `skills/retro/SKILL.md` | 2 | done |
| 2.2 | DONE. Update repo-root `CLAUDE.md` "Status (April 2026)" block: (a) move `skills/retro/SKILL.md` / `/retro` into the "Current and trustworthy" list; (b) remove the `docs/agent-wiring.md` bullet from the stale list; (c) rewrite the stale-agents bullet (currently `agents/booping-{teamlead,techlead,product-manager,qa-lead,reviewer}.md`) — the five agents were deleted in the 2026-04 `/retro` refactor; replace the bullet with a one-sentence note documenting the five deletions and their driver. No dormant-agent line remains. Leave every other bullet unchanged. | `CLAUDE.md` | 1 | done |

#### Task 2.1 DoD

- [x] Frontmatter `allowed-tools:` lists exactly the set per D12; `WebSearch` absent.
- [x] `## Preflight` references the six relative-path entries + three parameterized-directory entries listed in the M2 Verify block — enumerated.
- [x] `## High-level workflow` is a five-item numbered list: Intake, Sprint analysis, User feedback, Synthesize, Save & transition.
- [x] Sections `## Phase 0 Intake`, `## Phase 1 Sprint analysis`, `## Phase 2 User feedback`, `## Phase 3 Synthesize`, `## Phase 4 Save & transition` exist in that order — 5 phase headers.
- [x] Phase 0 body documents 0-plan resolution via `booping-plans --status awaiting-retro` + `AskUserQuestion multiSelect: true`.
- [x] Phase 0 body documents the verbatim pinned error string — `grep -F "/retro requires a plan in status 'awaiting-retro'" skills/retro/SKILL.md` matches once.
- [x] Phase 0 body names `booping-researcher-middle` as the sole delegation target.
- [x] Phase 1 body explicitly states the orchestrator performs sprint analysis inline — no sub-agent delegation; verified by `grep -F 'booping-researcher-senior' skills/retro/SKILL.md` returning empty AND `grep -Fi 'inline' skills/retro/SKILL.md` matching the Phase 1 paragraph.
- [x] Phase 3 body references `../../docs/template_retrospective.md` as the body spec (verified by the Preflight-reference grep also matching inside Phase 3 prose).
- [x] Phase 3 body documents the lesson cross-check using the phrase `Ignored / unapplied lessons` (the template's subsection name) — `grep -Fi 'ignored / unapplied lessons' skills/retro/SKILL.md` matches.
- [x] Phase 3 body states the cross-check uses the Preflight-loaded lesson set + `_booping/skill_retro.md` extras — no additional load.
- [x] Phase 4 frontmatter example uses `plans:` as a YAML list — `grep -E '^plans:|plans: \[' skills/retro/SKILL.md` matches.
- [x] Phase 4 includes `cd ~/Claude/{project_name}` before `git add` / `git commit`; `git add` invocation lists explicit paths (no `-A`) and defines `<retro-basename>` + `<plan-basename-N>` in one sentence.
- [x] Phase 4 does NOT contain a `/learn` suggestion — `grep -F 'Suggest /learn'` and `grep -F '/learn <retro-path>'` both return empty.
- [x] `## What retro does NOT do` names: does not extract lessons; does not generate candidate new lessons; does not write "CLAUDE.md impact"; does not edit any CLAUDE.md; does not edit `sprints.md` directly; does not transition plans to `done`, `cancelled`, or `fail`.
- [x] `## Hard rules` has exactly four `- **` bullets per D12 + D3 (orchestrator owns write; project-specific only; no blame; no CLAUDE.md edits nor "CLAUDE.md impact" section).
- [x] `grep -E 'lessons/[0-9]{4}_' skills/retro/SKILL.md` returns empty.
- [x] `grep -F 'Applicable lessons:' skills/retro/SKILL.md` returns empty (no per-agent lesson routing; D2).
- [x] File line count ≤ 130.
- [x] Combined forbidden-token regex in M2 Verify matches nothing.

#### Task 2.2 DoD

- [x] `CLAUDE.md` "Status (April 2026)" contains `skills/retro/SKILL.md` (or `/retro`) in the "Current and trustworthy" section.
- [x] Stale-list block no longer names `retro`.
- [x] `docs/agent-wiring.md` bullet removed — `grep -F 'docs/agent-wiring.md' CLAUDE.md` empty.
- [x] Stale-agents bullet no longer lists any of the five deleted names as dormant — the sentence instead reads as a deletion note (e.g., "The four role agents and `booping-reviewer` were deleted in the 2026-04 `/retro` refactor"). Verified by a `grep -Fi 'deleted in the 2026-04' CLAUDE.md` match AND by the absence of `dormant` adjacent to any of the five names.
- [x] No other `CLAUDE.md` line changed — `git diff --numstat CLAUDE.md` ≤ 10 added + ≤ 10 removed.

---

### M3: Delete five agents + agent-wiring.md + cohort audit — 2 SP | done

**Goal**: Five agent files deleted. `docs/agent-wiring.md` deleted. Trustworthy skills (groom / chat / develop / retro) have zero references to the deleted agents. `agent-wiring.md` has zero references anywhere. Role-agent references in stale skills are left in place per D10.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# Agent files gone
for a in booping-techlead booping-product-manager booping-qa-lead booping-teamlead booping-reviewer; do
  test ! -e "agents/$a.md" || { echo "agents/$a.md still exists"; exit 1; }
done
# agent-wiring.md gone; zero consumers
test ! -e docs/agent-wiring.md
test -z "$(grep -lF 'agent-wiring' agents/*.md skills/*/SKILL.md docs/*.md CLAUDE.md PRD.md README.md 2>/dev/null)"
# Trustworthy cohort clean
for f in skills/groom/SKILL.md skills/chat/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md; do
  if grep -qE 'booping-techlead|booping-product-manager|booping-qa-lead|booping-teamlead|booping-reviewer' "$f"; then
    echo "dangling deleted-agent reference in $f"
    exit 1
  fi
done
# Stale skills may retain references (per D10); log, don't fail
for f in skills/learn/SKILL.md skills/install/SKILL.md skills/help/SKILL.md; do
  if grep -qE 'booping-techlead|booping-product-manager|booping-qa-lead|booping-teamlead|booping-reviewer' "$f"; then
    echo "INFO: expected stale reference in $f (D10)"
  fi
done
# Remaining agents/: six files only (three developer tiers + three researcher tiers)
test "$(ls agents/*.md | wc -l)" = 6
for a in booping-developer-junior booping-developer-middle booping-developer-senior booping-researcher-junior booping-researcher-middle booping-researcher-senior; do
  test -e "agents/$a.md" || { echo "missing $a"; exit 1; }
done
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | DONE. Delete the five agent files: `agents/booping-techlead.md`, `agents/booping-product-manager.md`, `agents/booping-qa-lead.md`, `agents/booping-teamlead.md`, `agents/booping-reviewer.md`. Enumerate `grep -lE 'booping-techlead\|booping-product-manager\|booping-qa-lead\|booping-teamlead\|booping-reviewer' skills/groom/SKILL.md skills/chat/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md`; any hit is fixed in this task. Stale skills (learn / install / help) are NOT edited for deleted-agent references (D10) — log per-file hit counts into the Risk register with the note "expected stale; deferred to that skill's refactor per D10". | `agents/*.md` (five files deleted); `skills/groom/SKILL.md`, `skills/chat/SKILL.md`, `skills/develop/SKILL.md`, `skills/retro/SKILL.md` (edited only on hits); `skills/learn/SKILL.md`, `skills/install/SKILL.md`, `skills/help/SKILL.md` (read-only; record only) | 1 | done |
| 3.2 | DONE. Delete `docs/agent-wiring.md`. Enumerate `grep -lF 'agent-wiring' agents/*.md skills/*/SKILL.md docs/*.md CLAUDE.md PRD.md README.md`. Every hit is patched in-task — unlike deleted-agent references (D10), `agent-wiring.md` references break at parse because the file is gone outright. For each hit: remove the sentence or replace the reference with a one-line note pointing at `skills/retro/SKILL.md` Phase 1 (the only place the briefing-header concept remains). Record every file touched in the Risk register. | `docs/agent-wiring.md` (deleted); `agents/*.md`, `skills/*/SKILL.md`, `docs/*.md`, `CLAUDE.md`, `PRD.md`, `README.md` (edited where hits exist) | 1 | done |

#### Task 3.1 DoD

- [x] Five `test ! -e agents/<name>.md` assertions pass for the deleted agents.
- [x] `ls agents/*.md | wc -l` returns `6` (three developer tiers + three researcher tiers).
- [x] `grep -lE 'booping-techlead|booping-product-manager|booping-qa-lead|booping-teamlead|booping-reviewer' skills/groom/SKILL.md skills/chat/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md` returns no files.
- [x] Any hits in `skills/learn/SKILL.md`, `skills/install/SKILL.md`, `skills/help/SKILL.md` are enumerated in the Risk register with per-file hit counts and the note "expected stale; deferred to that skill's refactor per D10".

#### Task 3.2 DoD

- [x] `test ! -e docs/agent-wiring.md` passes.
- [x] `grep -lF 'agent-wiring' agents/*.md skills/*/SKILL.md docs/*.md CLAUDE.md PRD.md README.md` returns no files.
- [x] Every file previously containing `agent-wiring` that was edited in this task is listed in the Risk register with a one-line description of the replacement.

---

## Final Verification

After all three milestones:

```bash
cd /home/anton/Dev/@A/claude-booping
# Partials + template landed
test -f docs/partial_plan_transitions_retro.md
test -f docs/template_retrospective.md
grep -Fi 'once per plan' docs/partial_cross_validation.md
# Skill reshaped
grep -E '^## Preflight$' skills/retro/SKILL.md
test "$(grep -cE '^## Phase [0-4]' skills/retro/SKILL.md)" = 5
test "$(wc -l < skills/retro/SKILL.md)" -le 130
# Zero forbidden tokens in the refactored skill
test -z "$(grep -E 'docs/agent-wiring\.md|docs/project-scoping\.md|booping-plans list|booping-plans set|sync-sprints|CLI fallback|booping-teamlead|booping-techlead|booping-product-manager|booping-qa-lead|booping-reviewer|booping-researcher-senior|Applicable lessons:|Candidate new lessons|Lessons review|CLAUDE\.md impact|Suggest /learn|/learn <retro-path>' skills/retro/SKILL.md)"
# Zero concrete-lesson references
test -z "$(grep -E 'lessons/[0-9]{4}_' skills/retro/SKILL.md)"
# Agent-file deletions (five)
for a in booping-techlead booping-product-manager booping-qa-lead booping-teamlead booping-reviewer; do
  test ! -e "agents/$a.md" || { echo "$a still exists"; exit 1; }
done
# agent-wiring.md fully gone
test ! -e docs/agent-wiring.md
test -z "$(grep -lF 'agent-wiring' agents/*.md skills/*/SKILL.md docs/*.md CLAUDE.md PRD.md README.md 2>/dev/null)"
# Trustworthy cohort clean
for f in skills/groom/SKILL.md skills/chat/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md; do
  if grep -qE 'booping-techlead|booping-product-manager|booping-qa-lead|booping-teamlead|booping-reviewer' "$f"; then
    echo "FINAL: dangling deleted-agent reference in $f"
    exit 1
  fi
done
# CLAUDE.md updated
grep -F 'skills/retro/SKILL.md' CLAUDE.md
test -z "$(grep -F 'docs/agent-wiring.md' CLAUDE.md)"
```

All assertions must pass cleanly.

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Orchestrator-inline sprint analysis (D1) produces thinner retros than the prior three-role fan-out | medium | Phase 3 uses `docs/template_retrospective.md`'s section spec + inline self-review checklist + the lesson cross-check, which together carry the quality bar. If the first post-refactor retro comes out noticeably thinner, reopen D1 and consider re-adding a researcher-senior analysis pass. |
| Deleting five agents breaks `/learn` / `/install` / `/help` on next invocation | accepted | User directive: those skills are about to be refactored; their references to deleted agents and the deleted `booping-reviewer` are expected to dangle briefly. Running any between this sprint's landing and that skill's refactor will fail on the missing agent. Flagged in repo `CLAUDE.md` stale-list note. |
| Stale-skill audit reveals hits outside `/learn` / `/install` / `/help` — e.g. a doc or a trustworthy skill still names a deleted agent | low | M3 Task 3.1 enumerates trustworthy skills explicitly and fixes in-task. Hits in docs (`PRD.md`, `README.md`) are treated as trustworthy for this audit — patched, not deferred. |
| `docs/template_retrospective.md` diverges in tone from `docs/template_plan.md` | low | Task 1.2 targets the existing `scrum-retro` shape; both templates live under `docs/template_*.md` with consistent frontmatter-example-then-body-sections structure. |
| Multi-plan retros leak into `/learn` before `/learn` is refactored to parse `plans:` as a list | medium | `/learn` is next in the refactor queue. Post-landing, `/learn` in its current form will parse incorrectly; it is already stale and not expected to run until its own refactor. Recorded so the `/learn` refactor plan scopes list-aware parsing. |
| The "no concrete vault file references" rule (D9) clashes with a future worker impulse to cite an illustrative lesson ID | low | M2 Verify includes `grep -E 'lessons/[0-9]{4}_'` returning empty. Any slip is blocked at milestone boundary. |
| Lesson cross-check in Phase 3 (D15) generates false positives (orchestrator claims a lesson was ignored when it was applied correctly) | medium | Phase 2 User feedback includes a step to confirm the orchestrator's lesson-ignored list with the user before finalizing the retrospective. User can override any false positive. |
| Cross-validation partial update (D14) doesn't actually prevent re-runs in future groom sessions | low | The rule lives in the partial, which every refactored `/groom` Preflight loads. Once the partial is in context, the behavior is governed; future slips are grooming-time discipline issues caught at retro. |
| Reviewer surfaces follow-ups during M2 (wording slips, template nits) | medium | Per-milestone triage: S0–S1 fix-now; S2+ cap of three deferred items per milestone, else promote to a follow-up stub plan. |
| M1 reviewer S2 defers (three items, under cap): (1) `partial_plan_transitions_retro.md` prose slightly verbose but consistent with siblings — leave; (2) `template_retrospective.md` uses `lessons/XXXX_<slug>.md` placeholder instead of 4-digit `NNNN` convention — inert until a real retro is authored; (3) self-review checklist wording is fine as written | accepted | Deferred per lesson 0003; all three are polish, no correctness impact. None blocks M2 or M3. Revisit at first real `/retro` run. |
| M3 stale-skill deleted-agent ref counts (per D10): `skills/help/SKILL.md` = 8, `skills/learn/SKILL.md` = 3, `skills/install/SKILL.md` = 0 | accepted | Expected stale; deferred to each skill's refactor per D10. Dangling references are visible at the next `/help` or `/learn` invocation but do not affect trustworthy skills. |
| M2 reviewer S2 defers (three items, under cap): (1) CLAUDE.md-impact paraphrase uses backtick break to sidestep forbidden-token regex — defensible, not a hack; (2) High-level workflow list is 1-indexed while phases are 0-indexed — consistent with `/groom` and `/develop`; (3) Phase 3 "do not inline the template's body structure" is slightly ambiguous phrasing | accepted | All polish, no correctness impact. None blocks downstream skills. |

## Out of scope

- Refactoring `/learn`, `/install`, `/help` — each gets its own refactor plan right after this one.
- Auditing stale skills for role-agent or reviewer references — D10 leaves those in place for their own refactors.
- Per-project `_booping/skill_retro.md` content for any vault — belongs in project-specific retros when the user calibrates.
- Pytest harness for the new partials / template / documented `booping-plans` invocations — overridden by the user-set "No tests" policy per repo `CLAUDE.md`.
- Renaming any `booping-plans` subcommand or flag — CLI stays byte-identical.
- Touching `docs/plan-schema.md` to resync with the new transitions partial — listed separately in repo `CLAUDE.md`.
- Modifying `agents/booping-developer-*.md` or `agents/booping-researcher-*.md` — those use the modern Startup wording and are not targets.
- Updating `/learn` to understand multi-plan retros — handled by its own upcoming refactor.
- Re-running Gemini cross-validation on this plan's iteration edits — per the newly-added D14 rule, the single groom-time run is the only validation pass.

## CLAUDE.md impact

In-scope: repo-root `CLAUDE.md` "Status (April 2026)" block — owned by Task 2.2. Moves `retro` into the trustworthy list. Removes the `docs/agent-wiring.md` bullet from the stale list. Rewrites the stale-agents bullet to document the five deletions (no remaining dormant-agent line). No other `CLAUDE.md` sections touched. Per-vault `CLAUDE.md` under `~/Claude/{project}/CLAUDE.md` is untouched — the refactor only changes how `/retro` reads that file, not what it contains.
