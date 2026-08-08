---
title: Plugin docs hygiene pass
type: refactoring
status: done
sp: 20
source: requests/20260423-plugin-docs-hygiene-pass.md
created: 2026-04-23 00:00
planned: 2026-04-23
started: 2026-04-23
completed: 2026-04-23 00:00
retro: skipped
goal: skipped
summary: "Partial renaming convention, dedup developer-agent partials, generic extra_instructions pattern, purge metrics/"
---

# Plugin docs hygiene pass

## Context

The booping plugin has accumulated drift during its mid-refactor phase (per `CLAUDE.md` "Status (April 2026)"). Concretely: five partials are named inconsistently with the `partial_<domain>_<strategy|role>` convention; developer agents inline the content of three partials as mirror copies guarded only by a "synced from" comment; researcher tier selection is documented as a single partial while developers already use the cleaner delegator/strategy split; two docs (`docs/plan-schema.md`, `docs/project-scoping.md`) describe a CLI (`booping-plans set`, `sync-sprints`) and marker file (`.booping-project`) that no longer match reality; the `metrics/` vault dir and `lesson-hits.md` writes are still referenced across six files even though the user wants them gone; lessons carry a `scope:` field that is dead convention; `partial_task_bug.md` is one paragraph; and branch-naming conventions are missing a lesson-routing pointer. This sprint absorbs all of it in one pass to avoid intermediate broken states across the partial-rename web.

## Business goal

Plugin internals are consistent, deduplicated, and free of stale references. A future `/groom` or `/develop` session can navigate the plugin by convention alone — partials are named `partial_<domain>_<strategy|role>.md`, delegators and strategies are split, the `extra_instructions` pattern is named and reused, and no vault directory or partial describes behavior that the plugin no longer performs.

## Definition of Done

- [ ] All five rename targets land with no dangling references (grep returns zero hits for old names in non-git tracked files).
- [ ] `docs/partial_agents_researchers_delegator.md` exists and catalogues the `senior/middle/junior` strategy; `docs/partial_agents_strategy_senior_middle_junior.md` holds the tier details that used to live in `partial_agents_researcher_tiers.md`.
- [ ] `docs/partial_extra_instructions.md` exists and is the single generic guide for the "read extension file by path, silent-skip if missing, common logic" pattern; developer agents and every refactored skill reference it for their project-extension read.
- [ ] `agents/booping-developer-{senior,middle}.md` no longer contain inlined copies of `partial_agents_developer_{rules,workflow,extra_instructions}.md`; the skill orchestrator folds them into every briefing via the developers-delegator template.
- [ ] `docs/partial_task_bug.md` carries guidance on: confirming the bug exists in code (obvious vs non-obvious triage), requesting more user detail when the report is ambiguous, and picking a test strategy (user-verifies vs automated check vs regression test).
- [ ] `docs/partial_plan_statuses.md` tells readers to regen `sprints.md` via `booping-plans --format=md > ~/Claude/{project}/sprints.md` after every status change.
- [ ] `docs/plan-schema.md` and `docs/project-scoping.md` are deleted; every reference to them is removed.
- [ ] `template_lesson.md` has no `scope:` field; existing lessons 0001–0004 have `scope:` stripped; `partial_learn_targets.md` and `partial_read_lessons.md` no longer reference the field.
- [ ] `partial_learn_targets.md` includes an example row or note that routes branch-naming-convention feedback to `skill-ext` (`_booping/skill_develop.md`).
- [ ] `~/Claude/claude-booping/metrics/` is deleted; every reference to `metrics/`, `lesson-hits.md`, or `sp-rollup.md` is removed from `skills/develop/SKILL.md`, `skills/help/SKILL.md`, `skills/install/template-claude-md.md`, `bin/booping-init`, `README.md`, `CLAUDE.md`, and `docs/partial_agents_strategy_mid_senior.md`.
- [ ] `CLAUDE.md` and `README.md` reflect the new partial names and pattern conventions; no reference remains to `partial_agent_delegator`, `partial_agents_mid_senior`, `partial_agents_researcher_tiers`, `partial_quality_checklist`, `partial_project_quality_checks`, `plan-schema.md`, `project-scoping.md`, or `metrics/`.
- [ ] `booping-plans --status backlog` shows this plan (smoke-check the frontmatter edits held).

## Design

### Architecture

The refactor operates within the plugin repo (`/home/anton/Dev/@A/claude-booping/`) and the vault (`~/Claude/claude-booping/`) for metrics deletion only. No user-facing behavior changes; the plugin's external contract (skills, slash commands) stays identical. Internal information architecture improves along four axes:

1. **Naming convention**: `partial_<domain>_<strategy-or-role>.md`. Strategy partials carry the `strategy_` prefix; delegator catalogues are named `<domain>_delegator.md`. Applied to both developers and researchers.
2. **Dedup by fold-in**: the `/develop` skill reads the three developer partials at briefing-construction time and concatenates them into the agent briefing. Agent bodies shrink to a one-line "follow the briefing contract" pointer + their unique `## Report format` block. Same single-source-of-truth principle already used by `/groom` for plan content.
3. **Generic `extra_instructions` pattern**: `docs/partial_extra_instructions.md` is the "guide" — it defines the semantics (read the file at the given path, silent-skip if absent, merge its content into the current operating context). Skills and agents reference the guide with a file argument. Replaces the per-role `partial_agents_developer_extra_instructions.md`.
4. **Stale content purge**: delete docs and directories that describe behaviors the plugin no longer performs.

The order of milestones matters: M1 must land before M2–M8 because downstream references depend on the new partial names. M3 consumes M1 (the renamed `partial_agent_developers_delegator.md` is where the briefing-fold template lives).

### Decisions

| # | Decision | Alternative considered | Why this one |
|---|----------|------------------------|--------------|
| D1 | Keep the 5 staged renames + `partial_agents_researchers_delegator.md` stub; absorb into M1. No git-restore. **M1 carries the authoritative rename mapping in its preamble so the milestone is reproducible even if the staged state is lost** (a developer picking up a clean checkout would redo the five `git mv` calls before Task 1.1). | Back out, start from clean baseline. | User confirmed (probe 1). Zero wasted effort; M1 treats the staged work as "half of its own output". Idempotency preserved via the rename table. |
| D2 | Developer-agent dedup via skill-folds-partials-into-briefing. Agent body becomes thin. `partial_agent_developers_delegator.md` gets a briefing-template section that reads the three partials at runtime and concatenates them. | (a) Agent reads hardcoded plugin paths — fragile to plugin relocation. (b) `bin/` sync script — adds a build step. (c) Keep current mirror. | User endorsed the "guide + file" pattern for extra_instructions (probe 2). Extending the same "skill owns reads" principle to rules/workflow is the cleanest: no path fragility, no build step, no dup. Mirrors `/groom`'s existing fold-plan-content pattern. |
| D3 | Generalize `partial_agents_developer_extra_instructions.md` into `partial_extra_instructions.md` (drop the developer-specific name). The generic guide carries the silent-skip + merge semantics. Developer agents name their specific file as an argument. | Keep per-role guides (one per role that uses the pattern). | User's phrasing — "give skills and agents keys and ask to read this file with the key" — explicitly requests the generic pattern (probe 2 notes). Per-role guides would duplicate the silent-skip boilerplate. |
| D4 | Delete `docs/plan-schema.md` and `docs/project-scoping.md` outright. | Rename to `partial_*` and rewrite to match current state. | User confirmed (probe 3). `plan-schema`'s status table duplicates `partial_plan_statuses`; its frontmatter table duplicates `template_plan_frontmatter`; its CLI section describes commands (`booping-plans set`, `sync-sprints`) that don't exist. `project-scoping`'s `.booping-project` + `projects.json` conventions are superseded by `partial_project_resolution.md` (`.booping` marker, no JSON registry). Nothing worth preserving. |
| D5 | Strip `scope:` from `template_lesson.md` and from lessons 0001–0004; update `partial_read_lessons.md` and `partial_learn_targets.md` to stop referencing it. | Keep the field but make it advisory. | User: "lessons shouldn't have scope they're shared between all skills." The field is not load-bearing anywhere — `partial_read_lessons.md:5` describes scope-filtering as optional ("may choose to skip"); no skill currently filters. Removal eliminates the gap between documentation and behavior. |
| D6 | Keep `partial_agents_developer_rules.md` and `partial_agents_developer_workflow.md` at their current names even though they're role-specific. | Rename to `partial_developer_rules.md` / `partial_developer_workflow.md` to drop the redundant `agents_` prefix. | Scope-limit: M3 already touches the agent refactor; renaming here adds cross-file churn without payoff. Current names are accurate (agent-specific rules; agent-specific workflow). Deferred to future hygiene if the pattern spreads. |
| D7 | One consolidated sprint, not sibling stubs. | Split into 3–4 smaller sprints (renames / dedup / stale-purge / bug-task). | The rename web is cross-cutting — breaking it across sprints guarantees broken intermediate states where skills reference not-yet-renamed partials. Single-sprint landing keeps the tree consistent. Total 17 SP is well under the 30–35 threshold. |

### Applies lessons

- `lessons/0001_every-loaded-lesson-leaves-a-plan-trace.md` — applied: this Applies-lessons section contains exactly one verdict line per loaded lesson (four bullets), and each lesson below cites the concrete DoD bullet or task it shaped. Trace coverage check lives in the Final Verification block (plan must have four Applies-lessons bullets; four lessons are loaded).
- `lessons/0002_audit-workers-emit-verifier-output.md` — applied: audit-class tasks M1 Task 1.3, M4 Task 4.3, and M8 Task 8.2 each carry an explicit `Verifier:` line naming the mechanical check and require the verifier's stdout/stderr in the Done report. Shaped: the DoD bullets on lines "Verifier output pasted" across those three tasks.
- `lessons/0003_refactor-grooms-probe-delegation-and-deletion-before-v1.md` — applied: delegation probe (D1+D2) and deletion probe (D4+D5 + metrics dir in M4) ran in Phase 1 via `AskUserQuestion` before this body was drafted. Answers recorded as Decisions D1–D5 in the Decisions table.
- `lessons/0004_information-architecture-pattern.md` — applied: IA four-check pass is required by the DoD of M3 Task 3.1 (new generic partial), M3 Task 3.3 (delegator rewrite), and M7 Task 7.1 (bug-task expansion) — every prompt-bearing artefact edited in this sprint is covered. Shaped: the explicit "IA four-check pass applied" checkbox in each of those task DoDs.

## Milestones

### M1: Absorb renames, propagate references — 3 SP | done

**Goal**: The five partial renames are fully reflected across every file that references them. No file still points at an old name.

**Rename mapping** (authoritative; the staged git-mv state, if preserved, already reflects this; if the tree is clean, redo these five `git mv` calls before the tasks below):

| Old path | New path |
|----------|----------|
| `docs/partial_agents_mid_senior.md` | `docs/partial_agents_strategy_mid_senior.md` |
| `docs/partial_agent_delegator.md` | `docs/partial_agent_developers_delegator.md` |
| `docs/partial_quality_checklist.md` | `docs/partial_plan_quality_checklist.md` |
| `docs/partial_project_quality_checks.md` | `docs/partial_development_quality_checks.md` |
| `docs/partial_agents_researcher_tiers.md` | `docs/partial_agents_strategy_senior_middle_junior.md` |

**Verify**:
```bash
! grep -rnE 'partial_agents_mid_senior|partial_agent_delegator\.md|partial_agents_researcher_tiers|partial_quality_checklist|partial_project_quality_checks' . --include='*.md' --exclude-dir=.git --exclude-dir=plans
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Update references to the four non-researcher renames across refactored skills and `partial_sprint_planning.md` | `skills/groom/SKILL.md`, `skills/develop/SKILL.md`, `docs/partial_sprint_planning.md`, `docs/partial_agent_developers_delegator.md` (body self-link) | 1 | done |
| 1.2 | Update references in stale-pile files for the four renames | `skills/help/SKILL.md`, `skills/install/template-claude-md.md` (only the lines touching renamed partials; do not attempt full stale-skill refactor) | 1 | done |
| 1.3 | Audit that no old name remains, capture verifier output. **Verifier:** `grep -rnE 'partial_agents_mid_senior\|partial_agent_delegator\.md\|partial_agents_researcher_tiers\|partial_quality_checklist\|partial_project_quality_checks' . --include='*.md' --exclude-dir=.git --exclude-dir=plans` | — | 1 | done |

**Task 1.1 DoD**
- [x] `skills/groom/SKILL.md:123` uses `partial_plan_quality_checklist.md`.
- [x] `skills/develop/SKILL.md:32,81` uses `partial_agent_developers_delegator.md`.
- [x] `skills/develop/SKILL.md:33,54,84` uses `partial_development_quality_checks.md`.
- [x] `docs/partial_sprint_planning.md:25` points at `partial_agent_developers_delegator.md`.
- [x] `docs/partial_agent_developers_delegator.md` internal link to the strategy file uses `partial_agents_strategy_mid_senior.md`.

**Task 1.2 DoD**
- [x] `skills/help/SKILL.md:58` link uses `docs/partial_agent_developers_delegator.md`.
- [x] `skills/help/SKILL.md:84` uses `partial_agent_developers_delegator`.
- [x] No change needed elsewhere in `skills/help/SKILL.md`, `skills/install/*` for these four renames unless they reference the old names (grep to confirm).

**Task 1.3 DoD**
- [x] Verifier output pasted in Done report: `grep -rnE 'partial_agents_mid_senior|partial_agent_delegator\.md|partial_agents_researcher_tiers|partial_quality_checklist|partial_project_quality_checks' . --include='*.md' --exclude-dir=.git --exclude-dir=plans` returns empty.

---

### M2: Researchers delegator + strategy split — 2 SP | done

**Goal**: Researchers use the same delegator/strategy split as developers. The strategy file carries the tier table; the delegator catalogues strategies.

**Verify**:
```bash
test -f docs/partial_agents_researchers_delegator.md && \
test -f docs/partial_agents_strategy_senior_middle_junior.md && \
! grep -rn 'partial_agents_researcher_tiers' . --include='*.md' --exclude-dir=.git --exclude-dir=plans
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Confirm `partial_agents_researchers_delegator.md` content (already stub-written); adjust phrasing for parity with `partial_agent_developers_delegator.md` | `docs/partial_agents_researchers_delegator.md` | 1 | done |
| 2.2 | Update skill references from `partial_agents_researcher_tiers.md` to `partial_agents_researchers_delegator.md` (entry point) | `skills/chat/SKILL.md:33,75`, `skills/develop/SKILL.md:30,87`, `skills/groom/SKILL.md:37`, `skills/retro/SKILL.md:36`, `skills/help/SKILL.md:54` | 1 | done |

**Task 2.1 DoD**
- [x] File exists; opens with the same purpose line (research delegation keeps orchestrator context clean).
- [x] Single strategy row links to `partial_agents_strategy_senior_middle_junior.md` with a one-line description naming the three tiers.
- [x] File is ≤15 lines (it's a catalogue, not a deep-dive).

**Task 2.2 DoD**
- [x] All five refactored-skill references point at `partial_agents_researchers_delegator.md`.
- [x] Stale-pile help reference points at the delegator too.

---

### M3: Developer agent dedup + generic `extra_instructions` guide — 5 SP | done

**Goal**: Agent bodies shrink to a unique `## Report format` + a pointer to the briefing. The `/develop` skill folds the three developer partials into every briefing. A new generic `partial_extra_instructions.md` replaces the per-role guide.

**Verify**:
```bash
test -f docs/partial_extra_instructions.md && \
! test -f docs/partial_agents_developer_extra_instructions.md && \
! grep -qE '^## Startup|^## Workflow|^## Hard rules' agents/booping-developer-senior.md && \
! grep -qE '^## Startup|^## Workflow|^## Hard rules' agents/booping-developer-middle.md && \
grep -q 'Contract:' docs/partial_agent_developers_delegator.md && \
grep -q 'Contract:' skills/develop/SKILL.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Write `docs/partial_extra_instructions.md` as the generic guide (silent-skip, merge-into-context semantics) | `docs/partial_extra_instructions.md` (new) | 1 | done |
| 3.2 | Delete `docs/partial_agents_developer_extra_instructions.md`; update developer-agent bodies to remove `## Startup`, `## Workflow`, `## Hard rules` sections; leave only frontmatter + a 2-sentence "follow the briefing contract; the Report format is below" + `## Report format` block | `docs/partial_agents_developer_extra_instructions.md` (delete), `agents/booping-developer-senior.md`, `agents/booping-developer-middle.md` | 1 | done |
| 3.3 | Rewrite the **briefing template** section of `docs/partial_agent_developers_delegator.md` to specify the new contract-fold shape: a `Contract:` block whose body is the literal concatenation of the three partial contents (rules + workflow + extra_instructions guide), followed by an `Extra instructions file:` line naming `~/Claude/{project}/_booping/agent_booping-developer.md`, followed by the existing task/decisions/files/DoD/Verify fields. The partial documents the SHAPE — no executable pseudocode — so a skill author reading it can implement the fold | `docs/partial_agent_developers_delegator.md` | 1 | done |
| 3.4 | Implement the contract-fold in `/develop`: in Phase 3 briefing construction, read the three partial files (paths resolvable from the skill's own `../../docs/` relative location), concatenate their bodies under a `Contract:` heading, prepend the `Extra instructions file:` line, and include the whole block at the top of every `Agent()` call's prompt argument. Add one explicit step to the Phase 3 pseudocode / workflow listing | `skills/develop/SKILL.md` | 1 | done |
| 3.5 | Update refactored-skill Preflight blocks that read `_booping/skill_<name>.md` to reference the generic guide | `skills/chat/SKILL.md`, `skills/develop/SKILL.md`, `skills/groom/SKILL.md`, `skills/retro/SKILL.md`, `skills/learn/SKILL.md` | 1 | done |

**Task 3.1 DoD**
- [x] File explains: purpose (externalize project-specific instructions), invocation shape (`guide + file` pattern), silent-skip on missing file, merge-into-current-operating-context on success, forbidden actions (don't scan siblings; don't edit the file).
- [x] File is ≤30 lines.
- [x] IA four-check pass applied (scoping: generic pattern, not role-specific; duplication: replaces the developer-specific guide; configurability: the `file` argument is the only parameter; hierarchy: sits under the general `docs/partial_*.md` namespace).

**Task 3.2 DoD**
- [x] `docs/partial_agents_developer_extra_instructions.md` removed via `git rm`.
- [x] Each developer agent's body section count (headings starting with `## `) is exactly 1 (`## Report format`).
- [x] A 1–2 sentence lead-in above `## Report format` says: briefing carries the operating contract; extra instructions (project extension) are included by the skill.
- [x] Agent frontmatter is unchanged.

**Task 3.3 DoD**
- [x] Briefing template section in the delegator partial is updated to show: a `Contract:` block that concatenates the three partials (names them explicitly), and an `Extra instructions file:` line naming the project-extension path.
- [x] The partial includes one sentence stating the skill reads these partials at runtime; agents do not scan the plugin tree.
- [x] IA four-check pass applied.

**Task 3.4 DoD**
- [x] `skills/develop/SKILL.md` Phase 3 workflow explicitly lists the contract-fold step (read the three partials, prepend `Contract:` block, prepend `Extra instructions file:` line) before the existing "Group and delegate" step.
- [x] The step names each of the three partial paths relative to the skill file (e.g. `../../docs/partial_agents_developer_rules.md`).
- [x] Grep-verifier: `grep -c 'Contract:' skills/develop/SKILL.md` returns ≥ 1.

**Task 3.5 DoD**
- [x] Each refactored skill's `_booping/skill_<name>.md` Preflight line references `partial_extra_instructions.md` with the specific file argument.
- [x] Grep-verifier: `grep -lE 'partial_extra_instructions' skills/*/SKILL.md` lists all five refactored skills.

---

### M4: Purge metrics dir + every reference — 3 SP | done

**Goal**: `~/Claude/claude-booping/metrics/` is gone; no skill, partial, template, or CLAUDE.md mentions it; `/develop` no longer attempts to write lesson-hits.

**Verify**:
```bash
! test -d ~/Claude/claude-booping/metrics && \
! grep -rnE 'metrics/|lesson-hits|sp-rollup' . --include='*.md' --exclude-dir=.git --exclude-dir=plans
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Remove metrics writes from `/develop` Phase 4 (step 4 and the metrics/lesson-hits.md line in step 5 commit) and the "always delegate" hard rule | `skills/develop/SKILL.md:98,103,118` | 1 | done |
| 4.2 | Remove metrics references from remaining files | `docs/partial_agents_strategy_mid_senior.md:24`, `README.md:79-81`, `skills/help/SKILL.md:45,46,69-71`, `skills/install/template-claude-md.md:14`, `bin/booping-init:50,57,80` | 1 | done |
| 4.3 | Delete the vault metrics dir + verifier sweep. **Verifier:** `grep -rnE 'metrics/\|lesson-hits\|sp-rollup' . --include='*.md' --exclude-dir=.git --exclude-dir=plans` | `~/Claude/claude-booping/metrics/` (delete), working-tree grep | 1 | done |

**Task 4.1 DoD**
- [x] `skills/develop/SKILL.md` Phase 4 step 4 is removed (or rewritten to not mention metrics); the commit command in step 5 no longer adds `metrics/lesson-hits.md`.
- [x] Hard rule at line 118 no longer exempts `metrics/lesson-hits.md`.

**Task 4.2 DoD**
- [x] Every listed file no longer mentions `metrics/`, `lesson-hits`, or `sp-rollup`.
- [x] `bin/booping-init`'s two `cat > metrics/...` blocks (lines 50 and 57) are removed along with the `mkdir metrics` it implies.
- [x] `docs/partial_agents_strategy_mid_senior.md` line 24 is rewritten to not reference metrics (the skill still owns vault writes; just doesn't write a metrics file anymore).

**Task 4.3 DoD**
- [x] `~/Claude/claude-booping/metrics/` is deleted.
- [x] Verifier output pasted in Done report: `grep -rnE 'metrics/|lesson-hits|sp-rollup' . --include='*.md' --exclude-dir=.git --exclude-dir=plans` returns empty (or only matches bin/booping-init comment-strings that reference the historical feature in an explanation — confirm by hand).

---

### M5: Delete stale docs — 1 SP | done

**Goal**: `docs/plan-schema.md` and `docs/project-scoping.md` are deleted; every reference to them is gone.

**Verify**:
```bash
! test -f docs/plan-schema.md && ! test -f docs/project-scoping.md && \
! grep -rnE 'plan-schema\.md|project-scoping\.md' . --include='*.md' --exclude-dir=.git --exclude-dir=plans
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Delete the two files; remove the one reference in `skills/install/template-claude-md.md:28` and `skills/help/SKILL.md:110`; leave CLAUDE.md mention for M8 to absorb | `docs/plan-schema.md` (delete), `docs/project-scoping.md` (delete), `skills/install/template-claude-md.md`, `skills/help/SKILL.md` | 1 | done |

**Task 5.1 DoD**
- [x] Both docs removed via `git rm`.
- [x] `skills/install/template-claude-md.md:28` no longer references `docs/plan-schema.md` (rewrite the "See X for the full 9-state status lifecycle" line to point at `partial_plan_statuses.md` or delete the line).
- [x] `skills/help/SKILL.md:110` no longer references `plan-schema.md`.
- [x] Verifier output pasted: `grep -rnE 'plan-schema\.md|project-scoping\.md' . --include='*.md' --exclude-dir=.git --exclude-dir=plans` empty.

---

### M6: Lessons `scope:` removal + learn_targets branch-routing — 2 SP | pending

**Goal**: `scope:` is gone from the template, gone from existing lessons, and removed from referring partials. `partial_learn_targets.md` includes an example showing branch-naming feedback routes to `skill-ext`.

**Verify**:
```bash
! grep -qE '^scope:' docs/template_lesson.md && \
! grep -qE '^scope:' ~/Claude/claude-booping/lessons/*.md && \
! grep -n 'scope:' docs/partial_read_lessons.md docs/partial_learn_targets.md && \
grep -q 'branch' docs/partial_learn_targets.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Remove `scope:` line from `template_lesson.md`; strip `scope:` from lessons 0001–0004 in the vault | `docs/template_lesson.md`, `~/Claude/claude-booping/lessons/0001_*.md` through `0004_*.md` | 1 | done |
| 6.2 | Rewrite `partial_read_lessons.md` line 5 to drop the scope-filter escape hatch; rewrite `partial_learn_targets.md` to remove the `scope:` reference and add a branch-naming routing example | `docs/partial_read_lessons.md`, `docs/partial_learn_targets.md` | 1 | done |

**Task 6.1 DoD**
- [x] Template no longer has `scope:` field in frontmatter.
- [x] `grep -lE '^scope:' ~/Claude/claude-booping/lessons/*.md` returns empty.

**Task 6.2 DoD**
- [x] `partial_read_lessons.md:5` no longer mentions `scope:`; the "load everything" default becomes explicit.
- [x] `partial_learn_targets.md` `Picked when` column for the `lesson` row no longer references `scope:`; new phrasing (e.g. "rule generalizes beyond a single skill or agent" without the scope-field clause).
- [x] `partial_learn_targets.md` has an example line showing branch-naming convention feedback routes to `skill-ext` with file `_booping/skill_develop.md`. Example may live as a row addition or a bullet note under the matrix.

---

### M7: Bug task expansion + plan-statuses regen note — 2 SP | done

**Goal**: `partial_task_bug.md` carries the fuller triage guidance; `partial_plan_statuses.md` tells readers to regen `sprints.md` after status changes.

**Verify**:
```bash
grep -q 'confirm the bug exists' docs/partial_task_bug.md && \
grep -q 'test strategy' docs/partial_task_bug.md && \
grep -q 'booping-plans --format=md' docs/partial_plan_statuses.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Expand `partial_task_bug.md` with: confirm-bug-exists (obvious vs non-obvious triage), when-to-ask-user-for-more-detail, test-strategy decision (user-verifies vs automated check vs regression test) | `docs/partial_task_bug.md` | 1 | done |
| 7.2 | Add sprints.md regen note to `partial_plan_statuses.md` as a footer paragraph below the status table | `docs/partial_plan_statuses.md` | 1 | done |

**Task 7.1 DoD**
- [x] Partial has ≥3 bullet or short-paragraph additions covering: (a) confirm the bug in code before planning the fix (obvious → proceed; non-obvious → ask user for repro steps / environment / expected vs actual); (b) decide test strategy (user manual verify vs automated check available now vs write a regression test that fails before the fix); (c) when the bug report is too thin to act on, ask before drafting.
- [x] IA four-check pass applied.

**Task 7.2 DoD**
- [x] `partial_plan_statuses.md` ends with a short note: "After any transition, regen `sprints.md` with `booping-plans --format=md > ~/Claude/{project}/sprints.md` so the snapshot stays current."

---

### M8: CLAUDE.md + README refresh — 2 SP | done

**Goal**: Repo-level docs reflect the new partial names, the `extra_instructions` pattern, the missing `metrics/`, and the deleted stale docs. The "When refactoring stale skills" guidance in CLAUDE.md points at the correct partials.

**Verify**:
```bash
! grep -nE 'partial_agents_mid_senior|partial_agent_delegator\.md|partial_agents_researcher_tiers|partial_quality_checklist|partial_project_quality_checks|plan-schema\.md|project-scoping\.md|metrics/' CLAUDE.md README.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Update `CLAUDE.md`: the "docs/" bullet drops `plan-schema.md`, the "stale" bullet drops the `plan-schema.md` line, the "Per-project quality checks" bullet references `partial_development_quality_checks.md`, the partial-list in "When refactoring stale skills" uses new names, and the "Partials that describe an agent family" paragraph is rewritten for the new delegator/strategy convention | `CLAUDE.md` | 1 | done |
| 8.2 | Update `README.md` (drop `metrics/` from the vault layout tree; any mention of the renamed partials uses new names) and run final-sweep grep. **Verifier:** `grep -rnE 'partial_agents_mid_senior\|partial_agent_delegator\.md\|partial_agents_researcher_tiers\|partial_quality_checklist\|partial_project_quality_checks\|plan-schema\.md\|project-scoping\.md\|metrics/\|lesson-hits\|sp-rollup' . --include='*.md' --exclude-dir=.git --exclude-dir=plans` | `README.md` | 1 | done |

**Task 8.1 DoD**
- [x] `CLAUDE.md` "Status" section's "Stale" list drops the plan-schema.md bullet.
- [x] "Per-project quality checks" references `partial_development_quality_checks.md`.
- [x] The partial-list in "When refactoring stale skills" names: `partial_agents_researchers_delegator`, `partial_agent_developers_delegator`, `partial_agents_strategy_mid_senior`, `partial_plan_quality_checklist`, `partial_development_quality_checks`.
- [x] The "agent family" paragraph describes the delegator (catalogue) + strategy (details) convention and names `partial_extra_instructions.md` as the generic extension pattern.

**Task 8.2 DoD**
- [x] `README.md` vault layout tree does not list `metrics/`, `lesson-hits.md`, `sp-rollup.md`.
- [x] No references to the five renamed partials under old names.
- [x] Verifier output pasted: `grep -rnE 'partial_agents_mid_senior|partial_agent_delegator\.md|partial_agents_researcher_tiers|partial_quality_checklist|partial_project_quality_checks|plan-schema\.md|project-scoping\.md|metrics/|lesson-hits|sp-rollup' . --include='*.md' --exclude-dir=.git --exclude-dir=plans` returns empty.

---

## Final Verification

```bash
# 1. No old partial names remain
! grep -rnE 'partial_agents_mid_senior|partial_agent_delegator\.md|partial_agents_researcher_tiers|partial_quality_checklist|partial_project_quality_checks' . --include='*.md' --exclude-dir=.git --exclude-dir=plans

# 2. Stale docs are gone, no references
! test -f docs/plan-schema.md && ! test -f docs/project-scoping.md
! grep -rnE 'plan-schema\.md|project-scoping\.md' . --include='*.md' --exclude-dir=.git --exclude-dir=plans

# 3. Metrics is gone everywhere
! test -d ~/Claude/claude-booping/metrics
! grep -rnE 'metrics/|lesson-hits|sp-rollup' . --include='*.md' --exclude-dir=.git --exclude-dir=plans

# 4. Generic extra_instructions guide exists; per-role guide is gone
test -f docs/partial_extra_instructions.md && ! test -f docs/partial_agents_developer_extra_instructions.md

# 5. Agent bodies are deduped
! grep -qE '^## Startup|^## Workflow|^## Hard rules' agents/booping-developer-senior.md
! grep -qE '^## Startup|^## Workflow|^## Hard rules' agents/booping-developer-middle.md

# 6. Lessons scope field is gone
! grep -qE '^scope:' docs/template_lesson.md
! grep -lE '^scope:' ~/Claude/claude-booping/lessons/*.md

# 7. Plan-status sprints.md regen note exists
grep -q 'booping-plans --format=md' docs/partial_plan_statuses.md

# 8. Plan surfaces as backlog
booping-plans --status backlog | grep -q plugin-docs-hygiene-pass
```

All eight commands must succeed.

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| M1 misses a reference → skill reads old partial name → fails silently at runtime | medium | M1 Task 1.3 runs the strict grep and blocks milestone close on empty output. |
| M3 shrinks agent bodies but the skill-folds-into-briefing pattern makes briefings bloat; a 3-task briefing with all three partials folded in is ~60 lines before task content | low | Accepted trade-off. Briefings are one-shot; cost is per-invocation token, not persistent context. `/groom` already folds plan content into briefings — pattern parity. |
| M3 Task 3.3 describes the fold in the delegator partial but without an implementation in `/develop`, developer briefings would have no operating contract | medium | M3 Task 3.4 explicitly implements the fold in `skills/develop/SKILL.md`. The Verify block for M3 greps for `Contract:` in both the delegator partial and the skill to confirm both sides landed. |
| M4 verifier may false-match on `bin/booping-init` if it retains metrics comments after removal | low | Task 4.2 mandates full removal of the cat-blocks, not just line edits. Manual confirm during grep. |
| M8 CLAUDE.md edit is large (five sections touched); high chance of missing a bullet | medium | Task 8.3 final-sweep grep blocks milestone close. If a bullet slips, grep catches it. |
| Uncommitted half-done state (staged renames) could be lost if git-restore is run by mistake during M1 | low | D1 explicitly keeps the staged state. Document "do not git-restore" in M1 Task 1.1 preamble if needed. No task in this plan calls git-restore. |

## Out of scope

- Refactor of stale skills (`skills/install/`, `skills/help/`, `bin/booping-init`) beyond the rename-reference updates and metrics removal. A dedicated skill-refactor sprint should ship those to the new contract later.
- Renaming `partial_agents_developer_rules.md` and `partial_agents_developer_workflow.md` to drop the `agents_` prefix (per D6).
- Introducing a `booping-sync-agents` build script (D2 alternative (b)) — not needed given the fold-into-briefing design.
- Adding a runtime check that verifies every lesson is `scope:`-free or every agent body has no `## Startup` heading — the M3 verifier commands cover this one-shot; a CI gate is out of scope.
- Multi-project vault cleanup — only `~/Claude/claude-booping/metrics/` is deleted. Other vault `metrics/` dirs (if any) are not touched because no other vault is attached to this plugin session.
- Rewriting `partial_branch_naming.md` — current content already covers the convention the user named (one branch per sprint, multi-repo same kebab, project-specific prefix in `_booping/skill_develop.md`). Only change here is M6's addition to `partial_learn_targets.md` pointing at `_booping/skill_develop.md` as the routing target for branch-convention feedback.
- Auditing `partial_cross_validation.md` for once-per-plan language — confirmed during Phase 1 probes (line 3: "Do not re-run on every iteration … iterative wording tweaks are not grounds to re-run"). Already correct; no edit needed.

## CLAUDE.md impact

Five sections of `CLAUDE.md` change (handled by M8 Task 8.1):

1. **Status (April 2026)** — "docs/" bullet drops `plan-schema.md`; "Stale" bullet drops the `plan-schema.md` line.
2. **Skill design** — "Per-project quality checks" references `partial_development_quality_checks.md`.
3. **When refactoring stale skills** — partial-list uses new names: `partial_agents_researchers_delegator`, `partial_agent_developers_delegator`, `partial_agents_strategy_mid_senior`, `partial_plan_quality_checklist`, `partial_development_quality_checks`.
4. **Closing paragraph on agent-family naming** — rewritten to describe delegator (catalogue) + strategy (details) + `partial_extra_instructions.md` (generic extension pattern).
5. Any stray metrics mention is removed.

No changes to the vault `CLAUDE.md` (`~/Claude/claude-booping/CLAUDE.md`) — its `/install`-era "metrics/" layout bullet is already flagged stale and will be addressed by the future install-refactor sprint.
