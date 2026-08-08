---
title: Refactor /develop skill to groom pattern
type: refactoring
status: done
sp: 7
source: requests/20260423-refactor-develop-skill-to-groom-pattern.md
created: 2026-04-23 00:00
planned: 2026-04-23
started: 2026-04-23
completed: 2026-04-23 00:00
retro: retrospectives/20260423-skill-refactors-chat-develop-retro.md
goal: success
summary: "/develop rewritten to groom shape with new transitions/developer-tiers partials, hard rules orchestrator-only"
---

# Refactor /develop skill to groom pattern

## Context

`/develop` is on the stale list in repo `CLAUDE.md` alongside the other pre-refactor skills. `skills/groom/SKILL.md` (and now `skills/chat/SKILL.md` after the 2026-04-23 refactor) is the canonical shape: Preflight loads reusable partials, workflow is explicit phases, body stays stack-agnostic, hard rules are scoped to what the skill itself owns. `/develop`'s current body references `docs/project-scoping.md` (does not exist — live doc is `docs/partial_project_resolution.md`), invokes `booping-plans set` and `booping-plans sync-sprints` (the CLI is read-only per repo `CLAUDE.md` and the plans-as-data retro), carries a "CLI fallback" paragraph that describes how to recover from CLI failures that can no longer happen, duplicates the briefing-header template that already lives in `docs/agent-wiring.md`, and its Hard rules restate guard-rails already carried by each `booping-developer-*` agent's own Hard rules. A fresh agent reading `skills/develop/SKILL.md` today follows a mix of live and dead instructions.

The user asked for two things on top of the usual groom goals. First, maintenance simplicity: reuse partials where another skill already needs the same fragment; keep single-consumer fragments inline. Second, trust Opus — the orchestrator is a capable model, and the skill should stop guiding it to death with prose that repeats the developer agents' own Startup and Hard-rules sections. `~/.claude/skills/scrum-implement/SKILL.md` is cited as a lighter-touch prototype for reference.

Status transitions are already manual frontmatter edits per the plans-as-data contract. This refactor formalises the `/develop`-owned transitions (`ready-for-dev → in-progress`, `in-progress → awaiting-retro`, `in-progress → fail`) in a new `docs/partial_plan_transitions_develop.md` parallel to `docs/partial_plan_transitions_groom.md`, and extracts the SP→agent mapping into `docs/partial_developer_tiers.md` so any future skill that reasons about worker capacity has a single source of truth.

## Business goal

A fresh agent reading `skills/develop/SKILL.md` sees: Preflight that points at live partials, a phased workflow matching `/groom`'s arc, hard rules that name only what the orchestrator itself owns, and zero broken references. The file is materially shorter than today (~195 lines → ≤120) without losing the delegation invariant, branch naming, or the per-milestone execute → verify → review → commit loop. Status transitions get a dedicated transitions partial mirroring groom's. Legacy-content audit (lesson 0006) confirms no plugin-shipped agent or other refactored skill still claims `/develop`-owned behaviors that no longer exist.

## Definition of Done

- [x] `docs/partial_plan_transitions_develop.md` exists and documents the four transitions `/develop` owns (`ready-for-dev → in-progress`, `backlog → in-progress`, `in-progress → awaiting-retro`, `in-progress → fail`) with from/to/when/also-set rows — verified by `grep -F` for each transition arrow.
- [x] `skills/develop/SKILL.md` contains a `## Preflight` section whose bullets reference, by exact relative path, `../../docs/partial_project_resolution.md`, `../../docs/partial_plan_statuses.md`, `../../docs/partial_research_agents.md`, `../../docs/partial_plan_transitions_develop.md`, `../../docs/partial_developer_tiers.md`, plus `~/Claude/{project_name}/lessons/`, `~/Claude/{project_name}/_booping/skill_develop.md` (if present), and the attached repo's `CLAUDE.md` — verified by `grep -F` for each reference.
- [x] `skills/develop/SKILL.md` contains zero occurrences of the tokens `docs/project-scoping.md`, `booping-plans set`, `booping-plans sync-sprints`, `sync-sprints`, `CLI fallback` — verified by a single `grep -E` with all tokens.
- [x] `skills/develop/SKILL.md` body is ≤ 130 lines (wc -l) — target ≤120 with 10-line tolerance; strictly shorter than today's 194 lines.
- [x] `skills/develop/SKILL.md` `## High-level workflow` enumerates exactly five phases in order: Intake, Confirm scope, Branch, Execute, Finalize — verified by `grep -E '^## Phase [0-4]'` returning 5 rows in order.
- [x] `skills/develop/SKILL.md` `## Hard rules` contains exactly four bullets, each an orchestrator-scope invariant: always delegate, no worktree isolation, no scope additions, lessons are load-bearing. Guard-rails that belong to developer agents (monkey-patch smell, stop on Verify failure, flag unexpected test behaviour, Boy Scout Rule) are removed from this file — verified by counting `^- \*\*` bullets under `## Hard rules`.
- [x] Legacy-content audit (lesson 0006 cohort — plugin-shipped `agents/*.md` + all `skills/*/SKILL.md`): `grep -lE 'booping-plans set|booping-plans sync-sprints|docs/project-scoping\.md' agents/*.md skills/*/SKILL.md` returns no files. Mechanical CLI-reference swaps inside the stale skills (`retro`, `learn`, `install`, `help`) are in scope for M3; their broader bodies are not.
- [x] Repo-root `CLAUDE.md` "Status (April 2026)" list moves `develop` from the "Stale and not refactored" section into the "Current and trustworthy" section (or equivalent wording) — verified by `grep -F 'skills/develop/SKILL.md' CLAUDE.md` returning a line that is not under the stale heading.
- [x] Gemini cross-validation (`booping-validate-plan`) has been run; CRITICAL and RULE violations are addressed before handoff.

## Design

### Architecture

Two files change, one is added, one gets a one-line update:

- **`docs/partial_plan_transitions_develop.md`** (new) — parallel to `docs/partial_plan_transitions_groom.md`. Lists the three transitions `/develop` owns with from/to/when/also-set columns, the manual-edit workflow, and the post-transition verify command (`booping-plans --status <new-status>`). No CLI-mutation paths — matches the post-plans-as-data contract.
- **`docs/partial_developer_tiers.md`** (new) — the SP→agent mapping (1 → junior, 2–3 → middle, 4 → senior, 5 → refuse) with a one-line scope note per tier. Referenced by `skills/develop/SKILL.md` Phase 3 and by `docs/partial_sprint_planning.md` (cross-link for the "5 SP must be re-decomposed" rule).
- **`skills/develop/SKILL.md`** (rewrite) — full rewrite to the groom shape. Preflight loads the partials + vault artefacts. Five phases (Intake, Confirm scope, Branch, Execute, Finalize). Branch-prefix table stays inline (single consumer); SP→agent references the new partial. Briefing header is referenced from `docs/agent-wiring.md`, not duplicated. Multi-repo note is trimmed to a single paragraph — projects that need more flesh it out in their `_booping/skill_develop.md`.
- **Repo `CLAUDE.md`** — one-line update to the "Status (April 2026)" block so `skills/develop/SKILL.md` moves from stale to trustworthy. No other edits.
- **`agents/*.md`** — legacy-content audit only; fix any hits targeted per-file.

Two new partials: `partial_plan_transitions_develop.md` and `partial_developer_tiers.md`. Branch-prefix table and milestone-loop steps stay inline — single consumer, per chat-refactor D3.

### Decisions

| # | Decision | Alternative considered | Why this one |
|---|----------|------------------------|--------------|
| D1 | Create `docs/partial_plan_transitions_develop.md` | Inline the transition table in `skills/develop/SKILL.md` | Parallel to `partial_plan_transitions_groom.md` sets a pattern; `/retro` and `/learn` refactors will each want their own transitions partial. Establishing the file now avoids retrofit. |
| D2 | Extract SP→agent table to `docs/partial_developer_tiers.md` | Keep inline in `/develop` | User directive during grooming: extract coding-agent mapping into a partial. The mapping is declarative ("given SP N, use agent X") and overlaps with `partial_sprint_planning.md`'s "5 SP must be re-decomposed" rule — which can now reference the partial instead of carrying the rule alone. Future skills that need to reason about worker capacity (e.g. a planning skill that suggests task decomposition) get a single source of truth. |
| D3 | Keep branch-prefix table inline | Extract to `partial_branch_naming.md` | Same reason as D2: `/develop` is the sole consumer today. |
| D4 | Reference `docs/agent-wiring.md` for the briefing-header template instead of re-embedding it | Keep the inline briefing block verbatim | `agent-wiring.md` is already the canonical source; duplication means the file drifts. Reference keeps the skill short. |
| D5 | Drop the "CLI fallback" paragraph entirely | Shrink it to a one-liner | The fallback existed because `booping-plans set` / `sync-sprints` could fail; both commands are gone now. A shrunk fallback would describe a path that can no longer fire. |
| D6 | Trim Hard rules to orchestrator-scope invariants only (always delegate, no worktree isolation, no scope additions, lessons load-bearing) | Keep the current 9-bullet list | Each `booping-developer-*` agent already carries monkey-patch smell, Verify-failure diagnosis, flag-unexpected-tests, Boy Scout Rule in its own Hard rules. Restating them in the skill makes them drift-prone and contradicts the "trust Opus" directive. |
| D7 | Shrink Multi-repo sprints to one paragraph | Keep the current section | Only a minority of vaults span repos; per-project detail belongs in `_booping/skill_develop.md`. A one-paragraph pointer preserves discoverability without bloating the skill. |
| D8 | Keep `metrics/lesson-hits.md` append step in Phase 4 | Drop it (the file exists but shows all 0 hits today) | `metrics/lesson-hits.md` is the user-set metrics contract for the vault; it hasn't been hit because no sprint has reached `/retro` under the new lifecycle. The append step should stay; dropping it would silently retire the metric. |
| D9 | Audit cohort is `agents/*.md` + every `skills/*/SKILL.md` (including the stale `retro`, `learn`, `install`, `help`) | Limit audit to the already-refactored cohort (`groom`, `chat`) and park the rest | Lesson 0006 mandates fix-in-same-sprint for data-flow-adjacent drift. Rewriting a stale skill's CLI reference via `sed`/`Edit` is a mechanical swap orthogonal to the broader refactor each stale skill still needs; when those refactors run later, they'll rewrite the surrounding prose anyway — but until then, the reference should not point at a dead CLI. Docs (`PRD.md`, `docs/plan-schema.md`, `bin/booping-init`) fall outside the lesson-0006 cohort ("agents and skills") and remain their own refactor surface. |
| D10 | `/develop` does not transition to `done` / `cancelled` / `awaiting-learning` | Fold those transitions into the transitions partial | `/retro` moves `awaiting-retro → awaiting-learning`; `/learn` moves `awaiting-learning → done`; the user marks `cancelled`. The transitions partial documents only what `/develop` owns, matching groom's narrow-ownership pattern. |
| D11 | `/develop` accepts two entry states: `ready-for-dev` (the normal pickup) and `backlog` (user invokes `/develop` straight after groom confirmation without the `ready-for-dev` stopover). On the `backlog` entry path, `/develop` auto-fills both `planned: today` and `started: today` when transitioning to `in-progress`. | Require every plan to pass through `ready-for-dev` before `/develop` can claim it | Forcing the `ready-for-dev` stopover adds ceremony for zero benefit when the user just confirmed the plan and wants to start immediately. Auto-filling `planned` in the same transition preserves the lifecycle invariant (`planned` is the date the plan became executable) without asking the user to apply two frontmatter edits. `/groom` still sets `ready-for-dev` on normal user confirmation; the direct `backlog → in-progress` path is additive. |

### Applies lessons

- `lessons/0001_verify-block-universal-quantifiers.md` — every DoD bullet with "every", "each", or "zero occurrences" has a Verify line that enumerates via `grep` or line-count compare, never a spot-check.
- `lessons/0002_orchestrator-delegation-during-invariant-sprints.md` — this sprint's business goal names the `skills/develop/SKILL.md` rewrite as the canonical source; the orchestrator must delegate even one-line edits to that file during this sprint (file is invariant-bound).
- `lessons/0003_reviewer-followup-triage-rubric.md` — reviewer returns get per-item triage with the three-defer cap per milestone; applied inside each milestone's Risk notes, not only at sprint-end.
- `lessons/0006_agent-body-audit-after-dataflow-changes.md` — this refactor changes who owns the `/develop` skill body from "the stale legacy" to "the new groom-shape contract"; M3 runs an enumeration audit across the full cohort (`agents/*.md` + every `skills/*/SKILL.md`) for the three CLI-mutation / dead-path tokens, plus a targeted hard-rule-allow-list audit inside each hit file — same-sprint fix, not parked.

## Milestones

### M1: Add supporting partials — 3 SP | done

**Goal**: Two partials land, ready to be referenced from the rewritten Preflight + Phase 3.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# Both partials present
test -f docs/partial_plan_transitions_develop.md
test -f docs/partial_developer_tiers.md
# Transitions partial: four transitions (D10 + D11) + verify command + no CLI-mutation language
grep -F 'ready-for-dev → in-progress'  docs/partial_plan_transitions_develop.md
grep -F 'backlog → in-progress'        docs/partial_plan_transitions_develop.md
grep -F 'in-progress → awaiting-retro' docs/partial_plan_transitions_develop.md
grep -F 'in-progress → fail'           docs/partial_plan_transitions_develop.md
# Row 2 fills both planned and started in one edit
grep -E 'backlog.*planned.*started|backlog.*started.*planned' docs/partial_plan_transitions_develop.md
grep -F 'booping-plans --status' docs/partial_plan_transitions_develop.md
test -z "$(grep -E 'booping-plans set|sync-sprints' docs/partial_plan_transitions_develop.md)"
# Developer-tiers partial: four tiers, all agents named, refuse rule present
grep -F 'booping-developer-junior' docs/partial_developer_tiers.md
grep -F 'booping-developer-middle' docs/partial_developer_tiers.md
grep -F 'booping-developer-senior' docs/partial_developer_tiers.md
grep -Fi 'refuse' docs/partial_developer_tiers.md
grep -F '/groom'  docs/partial_developer_tiers.md  # re-decomposition pointer
# Sprint-planning partial cross-links the new developer-tiers partial
grep -F 'partial_developer_tiers.md' docs/partial_sprint_planning.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Write `docs/partial_plan_transitions_develop.md`: opening sentence matches groom's ("Status transitions are manual frontmatter edits — there is no CLI."); a from/to/when/also-set table with four rows covering the transitions per D10 + D11. Verbatim `From → To` pairs in order: (1) `ready-for-dev → in-progress`; (2) `backlog → in-progress`; (3) `in-progress → awaiting-retro`; (4) `in-progress → fail`. Verbatim `when` values: row 1 — `/develop claims a previously-confirmed plan at the start of Phase 3 (Execute), before spawning any worker agent`; row 2 — `user invokes /develop directly after groom confirmation, skipping the ready-for-dev stopover`; row 3 — `all milestones done, Final Verification green, every DoD checkbox marked [x]`; row 4 — `unrecoverable blocker after two documented fix attempts on the same milestone (user-approved abort)`. Verbatim `also set` values: row 1 — `started: YYYY-MM-DD (today)`; row 2 — `planned: YYYY-MM-DD (today), started: YYYY-MM-DD (today)`; row 3 — `completed: YYYY-MM-DD (today)`; row 4 — `completed: YYYY-MM-DD (today)`. After the table: a one-sentence note explicitly calling out that the row-2 path fills *both* `planned` and `started` in the same edit, because the plan skipped `ready-for-dev` where `planned` would normally be set. Then a paragraph on how to apply (Edit tool on frontmatter; the plan file is authoritative; match groom's phrasing). Closing paragraph documents the `booping-plans --status <new-status>` verify step, matching groom's wording. | `docs/partial_plan_transitions_develop.md` | 2 | done |
| 1.2 | Write `docs/partial_developer_tiers.md`: opening sentence names the partial's purpose ("Map a task's SP to the worker agent `/develop` spawns."); a markdown table with header `\| SP \| Agent \| Model \| Tier scope \|` and four data rows — `1` → `booping-developer-junior` / `haiku` / `mechanical 1-SP edits, no design judgment`; `2–3` → `booping-developer-middle` / `sonnet` / `predictable implementation, adjacent-code reading expected`; `4` → `booping-developer-senior` / `opus (reasoning high)` / `design-judgment tasks, edge-case thinking beyond the plan`; `5` → `refuse — kick back to /groom` / `—` / `research-grade: plan must re-decompose before execution`. After the table: one-paragraph rationale that cites `docs/partial_sprint_planning.md` for the "5 SP must be re-decomposed" rule. Then update `docs/partial_sprint_planning.md` to append a one-line cross-reference at the bottom of its "Scale (1–5)" section: `For the SP→agent mapping used by /develop, see [developer tiers](partial_developer_tiers.md).` | `docs/partial_developer_tiers.md`, `docs/partial_sprint_planning.md` | 1 | done |

#### Task 1.1 DoD

- [x] File begins with the sentence `Status transitions are manual frontmatter edits — there is no CLI.` (verbatim, matching `docs/partial_plan_transitions_groom.md` line 1 modulo the skill name).
- [x] File contains a GitHub-flavored markdown table whose header is `| From | To | When | Also set |` and whose body has exactly four data rows covering the transitions listed in D10 + D11.
- [x] Each "Also set" cell for a transition that auto-fills a date explicitly names the frontmatter field (`planned`, `started`, `completed`) and the value `YYYY-MM-DD (today)` — matching groom's convention so the pattern stays symmetrical.
- [x] Each "When" cell is populated with the verbatim trigger condition listed in Task 1.1; no empty or hand-written cells.
- [x] The `backlog → in-progress` row's "Also set" cell names **both** `planned` and `started` — a single edit writes both fields because the plan skipped the `ready-for-dev` stopover. Verified by `grep -F 'backlog' docs/partial_plan_transitions_develop.md | grep -F 'planned' | grep -F 'started'`.
- [x] Immediately after the table, one sentence explains that the `backlog → in-progress` path fills both `planned` and `started`, so a fresh agent reading the partial understands the combined-edit semantic.
- [x] File closes with a paragraph documenting `booping-plans --status <new-status>` as the post-edit verify step, phrased so a fresh agent knows to run it after each transition.
- [x] File contains zero occurrences of `booping-plans set`, `sync-sprints`, or any other CLI-mutation invocation.

#### Task 1.2 DoD

- [x] `docs/partial_developer_tiers.md` exists and opens with a one-sentence purpose line naming `/develop` as primary consumer.
- [x] File contains a markdown table with header `| SP | Agent | Model | Tier scope |` and exactly four data rows matching the mapping in Task 1.2.
- [x] Every `booping-developer-*` agent named in the table matches a file under `agents/` — verified by `for a in booping-developer-junior booping-developer-middle booping-developer-senior; do test -f agents/$a.md; done`.
- [x] The 5-SP row uses the phrase `refuse` (grep-detectable) and names `/groom` as the re-decomposition owner.
- [x] File's closing paragraph references `docs/partial_sprint_planning.md` so the "5 SP must be re-decomposed" rule's canonical home stays visible.
- [x] `docs/partial_sprint_planning.md` gains a single-line cross-reference at the bottom of its "Scale (1–5)" section pointing at `partial_developer_tiers.md` — verified by `grep -F 'partial_developer_tiers.md' docs/partial_sprint_planning.md`.
- [x] No other changes to `docs/partial_sprint_planning.md` — verified by `git diff --numstat docs/partial_sprint_planning.md` reporting ≤ 2 added + ≤ 0 removed lines.

---

### M2: Rewrite skills/develop/SKILL.md to groom shape — 3 SP | done

**Goal**: `skills/develop/SKILL.md` mirrors `/groom`'s Preflight-then-phases shape, references the new transitions partial, and drops every stale reference.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# Shape
grep -E '^## Preflight$'        skills/develop/SKILL.md
grep -E '^## High-level workflow$' skills/develop/SKILL.md
grep -E '^## Phase 0' skills/develop/SKILL.md
grep -E '^## Phase 1' skills/develop/SKILL.md
grep -E '^## Phase 2' skills/develop/SKILL.md
grep -E '^## Phase 3' skills/develop/SKILL.md
grep -E '^## Phase 4' skills/develop/SKILL.md
grep -E '^## Hard rules$' skills/develop/SKILL.md
# Preflight references each partial + vault artefact
for ref in \
  "../../docs/partial_project_resolution.md" \
  "../../docs/partial_plan_statuses.md" \
  "../../docs/partial_research_agents.md" \
  "../../docs/partial_plan_transitions_develop.md" \
  "../../docs/partial_developer_tiers.md" \
  "~/Claude/{project_name}/lessons/" \
  "~/Claude/{project_name}/_booping/skill_develop.md"; do \
  grep -F "$ref" skills/develop/SKILL.md || { echo "missing $ref"; exit 1; }; \
done
# Zero stale tokens
test -z "$(grep -E 'docs/project-scoping\.md|booping-plans set|booping-plans sync-sprints|sync-sprints|CLI fallback' skills/develop/SKILL.md)"
# Length ceiling
test "$(wc -l < skills/develop/SKILL.md)" -le 130
# Hard-rules bullet count: exactly 4 top-level `- **` bullets under `## Hard rules`
awk '/^## Hard rules$/{f=1; next} /^## /{f=0} f && /^- \*\*/' skills/develop/SKILL.md | wc -l | xargs -I{} test {} = 4
# Briefing header referenced, not duplicated
grep -F 'docs/agent-wiring.md' skills/develop/SKILL.md
# Developer-tiers partial is referenced; no inline SP→agent table
grep -F '../../docs/partial_developer_tiers.md' skills/develop/SKILL.md
for tier in booping-developer-junior booping-developer-middle booping-developer-senior; do
  hits=$(grep -cF "$tier" skills/develop/SKILL.md)
  test "$hits" -le 1 || { echo "inline tier mention: $tier ($hits)"; exit 1; }
done
# Repo CLAUDE.md status line updated
grep -F 'skills/develop/SKILL.md' CLAUDE.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | **Read `skills/groom/SKILL.md` and `skills/chat/SKILL.md` in full before typing** — those are the canonical shape for Preflight, phase headers, and Hard-rules bullet style; match their tone and structure. This file is invariant-bound for the sprint (lesson 0002): the executing agent is the developer worker `/develop` delegates this task to — no inline orchestrator edit, no direct Write by the `/develop` main context. Rewrite `skills/develop/SKILL.md` from scratch against the groom-shape template. New `## Preflight` bullets reference the four partials (`partial_project_resolution`, `partial_plan_statuses`, `partial_research_agents`, `partial_plan_transitions_develop`) + vault lessons + `_booping/skill_develop.md` + the attached repo's `CLAUDE.md`. `## High-level workflow` enumerates five phases. `## Phase 0 Intake` covers plan-path resolution, verifying the plan's current `status:` is one of the two valid entry states (`ready-for-dev` or `backlog`; any other status means `/develop` has no claim and must stop with a clear message), reading the plan + lessons + CLAUDE.md, spot-checking 2–3 named files (delegated to `booping-researcher-middle` when the set is large), and flagging lesson conflicts. `## Phase 1 Confirm scope` presents SP total, milestone list, applicable lessons, drift findings, and waits for the user's go/adjust. `## Phase 2 Branch` covers `git checkout -b <prefix>/<kebab-title>` with the prefix table inline (feature/bug/refactoring/other → feat/fix/refactor/chore); one branch per sprint; no worktree isolation. `## Phase 3 Execute` applies the entry transition per the transitions partial: if the plan was picked up from `ready-for-dev`, set `started: today`; if picked up directly from `backlog`, set both `planned: today` and `started: today` in the same edit (D11). Then loops per milestone: SP→agent tier resolution by reference to `docs/partial_developer_tiers.md` (no inline table), `TaskCreate` per task, delegate via `Agent()` using the briefing header documented in `docs/agent-wiring.md` (referenced, not duplicated), always-delegate even for 1-SP tasks, run milestone Verify, read DoD checkboxes, update milestone status, spawn `booping-reviewer` on the diff, apply lesson-0003 per-item triage, commit with `<prefix>(<scope>): M<n> <summary>`. `## Phase 4 Finalize` runs the plan's Final Verification, confirms all DoD `[x]` and all milestone statuses `done`, applies the `in-progress → awaiting-retro` transition, appends one row per consulted lesson to `metrics/lesson-hits.md`, commits the vault. Phase 4's commit lives in the **vault** (`~/Claude/{project}`), not the attached code repo — the skill body must include an explicit `cd ~/Claude/{project_name}` before `git add`, and the `git add` scope is explicitly listed (`git add plans/<plan-filename>.md metrics/lesson-hits.md sprints.md` — no `-A`, no catch-all). Phase 3 commits are inside the attached repo on the sprint branch; the two surfaces are separated by working directory. Suggests `/retro <plan-path>`. `## What develop does NOT do` lists: does not write application code itself (every task delegates); does not transition to `done`, `fail`-by-fiat, `cancelled`, or `awaiting-learning` (those belong to the user, `/retro`, or `/learn`). `## Hard rules` contains exactly four bullets: always delegate; no worktree isolation; no scope additions; lessons are load-bearing. A single paragraph mentions multi-repo sprints: one branch per repo under the same sprint title, sprint stays `in-progress` until the last repo lands, per-project detail lives in `_booping/skill_develop.md`. | `skills/develop/SKILL.md` | 2 | done |
| 2.2 | Update repo-root `CLAUDE.md` "Status (April 2026)" block: move `skills/develop/SKILL.md` from the "Stale and not refactored" list to the "Current and trustworthy" list. Leave every other bullet unchanged. | `CLAUDE.md` | 1 | done |

#### Task 2.1 DoD

- [x] `skills/develop/SKILL.md` frontmatter `allowed-tools:` lists at minimum `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `Agent`, `AskUserQuestion`, `TaskCreate`, `TaskUpdate` (pre-existing shape preserved unless D1–D10 mandate a change).
- [x] `## Preflight` section's bullets reference, by relative path, `../../docs/partial_project_resolution.md`, `../../docs/partial_plan_statuses.md`, `../../docs/partial_research_agents.md`, `../../docs/partial_plan_transitions_develop.md`, `../../docs/partial_developer_tiers.md` (exact strings present in file).
- [x] `## Preflight` also names `~/Claude/{project_name}/lessons/` and `~/Claude/{project_name}/_booping/skill_develop.md`. The `_booping/skill_develop.md` bullet ends with the qualifier "if present" so the orchestrator model knows to Read-with-graceful-skip rather than requiring the file.
- [x] `## High-level workflow` contains a five-item numbered list in order: Intake, Confirm scope, Branch, Execute, Finalize.
- [x] Sections `## Phase 0 Intake`, `## Phase 1 Confirm scope`, `## Phase 2 Branch`, `## Phase 3 Execute`, `## Phase 4 Finalize` each exist, in that order (verified by the Verify block).
- [x] Phase 0 body names both `ready-for-dev` and `backlog` as valid entry statuses, and states that any other status stops the skill with a clear message.
- [x] Phase 2 contains a branch-prefix table with rows for `feature`, `bug`, `refactoring`, `other` mapping to `feat/`, `fix/`, `refactor/`, `chore/`.
- [x] Phase 3 references `../../docs/partial_developer_tiers.md` for the SP→agent mapping and does NOT carry an inline SP→agent table — verified by `grep -F '../../docs/partial_developer_tiers.md' skills/develop/SKILL.md` matching, AND by `skills/develop/SKILL.md` containing ≤ 1 mention of each tier string (`booping-developer-junior`, `booping-developer-middle`, `booping-developer-senior`); multiple mentions signal an inline table was kept by mistake.
- [x] Phase 3 body references `docs/agent-wiring.md` as the briefing-header source; the inline briefing template from the pre-refactor body is removed.
- [x] Phase 3 body documents both entry paths (`ready-for-dev → in-progress` and `backlog → in-progress`) and names which fields to set per path, referring to `../../docs/partial_plan_transitions_develop.md` for the canonical table rather than re-listing it.
- [x] Phase 3 body includes the `booping-reviewer` spawn step and cites lesson 0003 for per-item triage.
- [x] Phase 4 body includes the `metrics/lesson-hits.md` append step.
- [x] Phase 4 body includes an explicit `cd ~/Claude/{project_name}` before the `git add` / `git commit` lines so the vault commit cannot leak into the attached code repo's working tree.
- [x] Phase 4 body's `git add` invocation lists explicit paths (`plans/<plan-filename>.md`, `metrics/lesson-hits.md`, `sprints.md`) — `git add -A` and `git add .` are forbidden in the documented command.
- [x] `## What develop does NOT do` section exists and names: does not write application code itself; does not own `done` / `cancelled` / `awaiting-learning` transitions.
- [x] `## Hard rules` section contains exactly four top-level bullets beginning with `- **` (verified by the awk block in Verify). The four bullets cover: always delegate; no worktree isolation; no scope additions; lessons are load-bearing.
- [x] File contains zero occurrences of the tokens `docs/project-scoping.md`, `booping-plans set`, `booping-plans sync-sprints`, `sync-sprints`, `CLI fallback` (verified by the Verify block's combined `grep -E`).
- [x] Total file line count (`wc -l skills/develop/SKILL.md`) is ≤ 130.

#### Task 2.2 DoD

- [x] Repo `CLAUDE.md` "Status (April 2026)" list contains `skills/develop/SKILL.md` (or `/develop` — match the file's own pattern) under the "Current and trustworthy" section.
- [x] The stale-list block no longer names `develop`.
- [x] No other line in `CLAUDE.md` is modified — verified by `git diff --numstat CLAUDE.md` reporting ≤ 2 added + ≤ 2 removed lines total (one move, so one line shifts sections). If the diff exceeds that envelope, stop and report; do not accept the change.

---

### M3: Legacy-content audit (lesson 0006 cohort) — 1 SP | done

**Goal**: No plugin-shipped agent and no `skills/*/SKILL.md` still references CLI-mutation paths or the dead `docs/project-scoping.md`. The three mechanical swaps are applied uniformly across every hit.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
# Full cohort audit: must return no files
test -z "$(grep -lE 'booping-plans set|booping-plans sync-sprints|docs/project-scoping\.md' agents/*.md skills/*/SKILL.md 2>/dev/null)"
# Docs-cohort (PRD, plan-schema, init) explicitly NOT cleaned here; record for parking
grep -lE 'booping-plans set|booping-plans sync-sprints|docs/project-scoping\.md' PRD.md docs/plan-schema.md bin/booping-init 2>/dev/null || true
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Run `grep -lE 'booping-plans set\|booping-plans sync-sprints\|docs/project-scoping\.md' agents/*.md skills/*/SKILL.md` to enumerate hits. For each hit, classify the context as **code-block** (inside a fenced `bash` block) or **prose** (anywhere else) and apply the matching swap below via targeted `Edit`. Record every file touched in the plan's Risk register.<br><br>**Additionally (lesson 0006 hard-rule audit):** for every file with a hit, grep that same file for `## Hard rules` and, within that section, for any allow-list bullet naming `sprints.md`, `booping-plans set`, or plan-status mutation. Remove or reword those bullets in the same Edit — stale hard-rules are the highest-severity drift per lesson 0006.<br><br>Then run the first grep against `PRD.md docs/plan-schema.md bin/booping-init` and append each hit to the Risk register as "Parked for docs-cohort refactor" — do not edit those files.<br><br>**Exact replacement strings:**<br>• `docs/project-scoping.md` → `docs/partial_project_resolution.md` (plain string swap; the surrounding sentence stays otherwise identical; applies equally to code-block and prose contexts).<br>• `booping-plans set ...` inside a fenced `bash` block → replace the entire line with the bash comment `# Manual frontmatter edit per docs/partial_plan_transitions_develop.md` (preserve indentation).<br>• `booping-plans set ...` in prose → replace the inline-code span (backticks and all) with the prose phrase `a manual frontmatter edit (see [plan transitions for /develop](../../docs/partial_plan_transitions_develop.md))` — adjust the relative path if the file is in `agents/` (no `../../` prefix; use `docs/partial_plan_transitions_develop.md`). Rewrite the surrounding sentence to stay grammatical.<br>• `booping-plans sync-sprints ...` inside a fenced `bash` block → delete the entire line plus any immediately-surrounding empty lines; `/chat`'s orient phase is now the sole regenerator of `sprints.md` and no other skill needs to invoke this path.<br>• `booping-plans sync-sprints ...` in prose → delete the inline-code span and any clause that named it (e.g. "…then runs `sync-sprints`…" → end the sentence after the prior clause). Rewrite to stay grammatical.<br><br>No agent personality tuning beyond the hard-rule audit and the minimum edit to keep prose grammatical. | `agents/*.md`, `skills/*/SKILL.md` (edits allowed where hits exist); `PRD.md`, `docs/plan-schema.md`, `bin/booping-init` (read-only, record only) | 1 | done |

#### Task 3.1 DoD

- [x] `grep -lE 'booping-plans set|booping-plans sync-sprints|docs/project-scoping\.md' agents/*.md skills/*/SKILL.md` returns no files.
- [x] Every file in the in-scope cohort that had a hit before this milestone is listed in the Risk register with a one-line description of which of the three swaps was applied (`project-scoping path swap`, `set-CLI → manual-edit swap (code|prose)`, `sync-sprints removal (code|prose)`) and the file path.
- [x] For every file in-scope cohort edited in this milestone, its `## Hard rules` section (if any) was re-read and any bullet naming `sprints.md`, `booping-plans set`, or plan-status mutation was removed or reworded — recorded as a separate Risk-register row if the edit was non-trivial.
- [x] Every docs-cohort file (`PRD.md`, `docs/plan-schema.md`, `bin/booping-init`) that still has a hit is listed in the Risk register under "Parked for docs-cohort refactor" with its filename and hit count.
- [x] No edits made to the docs-cohort in this milestone — verified by `git diff PRD.md docs/plan-schema.md bin/booping-init` being empty.

---

## Final Verification

After all three milestones:

```bash
cd /home/anton/Dev/@A/claude-booping
# Partial landed
test -f docs/partial_plan_transitions_develop.md
# Skill reshaped
grep -E '^## Preflight$' skills/develop/SKILL.md
grep -E '^## Phase [0-4]' skills/develop/SKILL.md | wc -l | xargs -I{} test {} = 5
test "$(wc -l < skills/develop/SKILL.md)" -le 130
# Zero stale tokens in the refactored skill
test -z "$(grep -E 'docs/project-scoping\.md|booping-plans set|booping-plans sync-sprints|sync-sprints|CLI fallback' skills/develop/SKILL.md)"
# Cohort audit clean (full agents/*.md + skills/*/SKILL.md)
test -z "$(grep -lE 'booping-plans set|booping-plans sync-sprints|docs/project-scoping\.md' agents/*.md skills/*/SKILL.md 2>/dev/null)"
# CLAUDE.md status updated
grep -F 'skills/develop/SKILL.md' CLAUDE.md
```

All five assertions must pass cleanly.

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Dropping Hard-rules bullets that duplicate developer-agent rules removes a load-bearing safety net if a future briefing path bypasses the agent (e.g. an orchestrator runs inline without delegation) | low | The "always delegate" hard rule makes the bypass itself a violation; the developer-agent rules are the right home for code-level guard-rails. Record an accepted-risk row for future retro. |
| Multi-repo orchestration guidance shrinks below what aurora-api needs when that vault adopts `/develop` | medium | D7 + `_booping/skill_develop.md` path documented in Preflight; aurora-api can flesh out multi-repo specifics in its own extension without touching the core skill. |
| Mechanical token swaps in `retro`, `learn`, `install`, `help` touch skills that haven't been fully refactored; a later structural refactor may redo the surrounding prose | low | M3 is restricted to the three specified token swaps (no structural rewrites). Each stale skill's future refactor plan re-reads the file end-to-end anyway; preserving the mechanical-swap trail via git blame is sufficient. |
| `docs/partial_plan_transitions_develop.md` diverges in tone/structure from `docs/partial_plan_transitions_groom.md`, making the two feel unrelated | low | M1 Task 1.1 DoD requires the opening sentence, column names, and closing verify-command pattern to mirror groom's. |
| Lesson 0004 (pytest harness exercising new documented CLI invocations) appears violated: the rewrite continues to document `booping-plans --status …` as the post-transition verify command but the plan adds no pytest | accepted | Repo `CLAUDE.md` `## CLI` section states `No tests. (User-set policy.)`. Project policy supersedes lesson 0004's default. Revisit if the user revokes the no-tests policy. |
| Reviewer surfaces follow-ups during M2 (wording slips, table-format nits) | medium | Lesson 0003 applied per-milestone: S0–S1 items are fix-now; S2+ accumulate up to 3 before promoting to a follow-up stub plan. **M2 review 2026-04-23**: 0 S0/S1, 2 S2 (deferred, see rows below), 1 S3 (nit, not actioned). |
| M2 reviewer S2 #1 (deferred): multi-repo paragraph sits under `## What develop does NOT do` without its own heading at `skills/develop/SKILL.md:122`, reads as a third "does NOT do" item for heading-scanning readers | low | Trivial to fix in a touch-up: add `## Multi-repo sprints` header (costs 1 line, stays ≤ 130) or move the paragraph to the end of Phase 2 Branch where it is topically adjacent. Not wired into DoD so deferred; revisit if `/develop` is rewritten again or if a second multi-repo vault adopts the skill. |
| M2 reviewer S2 #2 (deferred): intro paragraph at `skills/develop/SKILL.md:24` duplicates the wide-domain framing carried by Preflight + vault `CLAUDE.md`; neither `/groom` nor `/chat` carries the equivalent paragraph | low | Trim in a later sweep if the file needs to shrink below ~125 lines or when `/retro`, `/learn` get their refactors and intro prose is audited cohort-wide. Not a correctness issue. |
| Gemini cross-validation may flag the "trim Hard rules" decision as a behavioural regression | medium | D6 is listed explicitly so the validator sees the rationale. If Gemini flags it as CRITICAL, address before handoff; if ARCHITECTURAL BLIND SPOT only, accept with explicit justification in this row. Gemini 2026-04-23 did NOT flag D6; no action needed. |
| Gemini 2026-04-23 ABS: `_booping/skill_develop.md` "if present" — concern that a skill script would crash if the file is absent | accepted | Skills are prose instructions for the orchestrator model, not bash scripts; "if present" is a natural-language conditional the model handles via its Read tool with graceful fallback. Task 2.1 DoD now makes the qualifier explicit so the wording is unambiguous. No code-level fallback needed. |
| Gemini 2026-04-23 ABS: ambiguous git state between Phase 3 and Phase 4 | mitigated | Phase 4 body now explicitly lists its `git add` scope (`plans/<plan-filename>.md metrics/lesson-hits.md sprints.md` — no `-A`), and Phase 3 commits live in the attached repo on the sprint branch. The two commit surfaces are separated by repo path. |
| M3 edits (record per DoD 3.1): `skills/help/SKILL.md` — project-scoping path swap (prose, 1 hit) + hard-rule bullet rewording (`sprints.md` ownership → regen-by-chat + manual-transition wording; caught by M3 reviewer S1 after junior worker's first pass missed it); `skills/learn/SKILL.md` — project-scoping path swap (prose, 1 hit) + set-CLI → manual-edit swap (code, 1 block) + sync-sprints removal (code, 1 line) + CLI-fallback paragraph deletion (prose); `skills/retro/SKILL.md` — project-scoping path swap (prose, 1 hit) + DoD-bullet set-CLI reword (prose) + set-CLI → manual-edit swap (code+prose, 1 block) + sync-sprints removal (code, 1 line) + CLI-fallback paragraph deletion (prose) + hard-rule bullet rewording (`sprints.md` ownership claim → regen-by-chat + manual-transition wording). | recorded | Lesson 0006 hard-rule audit fired twice — once in `skills/retro/SKILL.md` (flagged by worker on first pass) and once in `skills/help/SKILL.md` (flagged by reviewer after worker missed it; fixed same milestone). `skills/learn/SKILL.md` Hard-rules section was clean. **Retro candidate:** worker briefing asserted Hard-rules audits were "no stale bullets found" without mechanical grep; reviewer had to catch the miss — see new risk row below. |
| M3 S1 miss pattern: junior worker asserted Hard-rules audit complete without a mechanical grep verifier; reviewer caught a stale `sprints.md` ownership bullet in `skills/help/SKILL.md` that the worker's self-report said did not exist. | accepted / retro-candidate | Future Hard-rules audits must ship with an explicit grep check (`grep -E 'sprints\\.md is owned\|booping-plans set\|sync-sprints\|status transitions.*CLI' <file>`) and record the command output, not a prose claim. Candidate for a lesson-0001 amendment or a new lesson on "assertions need verifiers" — defer to `/retro`. |
| Additional `skills/help/SKILL.md` drift parked for `/help` structural refactor: lines 36, 46, 47, 80, 91 each carry stale sprints.md-ownership claims (description prose, command-overview table, ASCII tree, flow diagram) that incorrectly name `/develop` as the sole writer. Not in M3 scope per Task 3.1 ("no prose rewrites beyond swap rules") — but same lesson-0006 drift class as the Hard-rule bullet. | parked | `/help` is on the stale-skills list in repo CLAUDE.md; its future structural refactor will rewrite these sections end-to-end. M3 is scoped to mechanical swaps + Hard-rules only per plan D9, so fixing them here would exceed scope. Record so the next `/help` refactor plan picks them up. |
| M3 docs-cohort hits parked for later docs refactor: `PRD.md` (1 hit), `docs/plan-schema.md` (6 hits), `bin/booping-init` (4 hits) — all untouched in this sprint per plan D9. | parked | Each of these will be cleaned by its own future refactor plan; preserving them here would exceed the M3 1-SP envelope and touch surfaces the plan's Out of scope section forbids. |

## Out of scope

- Refactoring the broader bodies of `/retro`, `/learn`, `/install`, `/help` — each gets its own refactor plan. M3 only applies the three mechanical token swaps; no structural rewrite of those skills here.
- Creating per-project `_booping/skill_develop.md` content for vaults beyond claude-booping — those belong in each project's own setup, not here.
- Adding a pytest harness for the new partial or for documented `booping-plans` invocations (lesson 0004) — explicitly overridden by the user-set "No tests" policy per repo `CLAUDE.md`.
- Renaming any `booping-plans` subcommand or flag — the CLI stays byte-identical across this refactor.
- Touching `docs/plan-schema.md` to resync with the new transitions — that file's stale CLI references are explicitly listed in repo `CLAUDE.md` "Status (April 2026)" as a separate refactor surface.
- Adjusting any `agents/booping-*.md` description tail beyond removing a stale CLI reference — agent personality/responsibility tuning belongs to `/learn`.

## CLAUDE.md impact

In-scope: the repo-root `CLAUDE.md` "Status (April 2026)" block — owned by Task 2.2. The `develop` entry moves from the "Stale and not refactored" list to the "Current and trustworthy" list. No other `CLAUDE.md` sections are touched. Per-vault `CLAUDE.md` under `~/Claude/{project}/CLAUDE.md` is untouched — the refactor only changes how `/develop` reads that file, not what it contains.
