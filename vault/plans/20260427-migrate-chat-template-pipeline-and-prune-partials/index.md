---
title: Migrate /chat to template pipeline + prune orphaned docs/partial_*.md
type: refactoring
status: done
sp: 13
split_from: null
created: 2026-04-27 00:00
planned: 20260427 13:58
started: 20260427 14:03
completed: 2026-04-27 15:07
retro: skipped
goal: skipped
summary: "Migrate /chat, the last hand-authored skill, to the template pipeline and delete every orphaned docs/partial_*.md"
---

# Migrate /chat to template pipeline + prune orphaned docs/partial_*.md

## Context

`/chat` is the last hand-authored `skills/<name>/SKILL.md` in the plugin. Its body reads five legacy `docs/partial_*.md` files that no other skill consumes:

- `partial_project_resolution.md` — superseded by `_partials/_project_context.j2` + `bin/booping-project-name`.
- `partial_read_lessons.md` — superseded by `!`bin/booping-lessons``.
- `partial_agents_researchers_delegator.md` + `…strategy_senior_middle_junior.md` — describe a senior/middle/junior researcher tier that was never built (only `booping-researcher` exists). Real config lives in `src/config.yaml` `skills.<name>.agents` and is rendered by `_partials/_available_agents.j2`.
- `partial_plan_statuses.md` — status glossary. The status names are also hard-coded in chat's Phase 0 status-count bash loop, so the same list is duplicated.

A sixth partial, `docs/partial_cross_validation.md`, *is* still consumed: `/groom`'s in-spec→awaiting-plan-review gate links to it from `src/config.yaml`. It's not a Jinja partial — it's a lazy-loaded reference doc, the same shape as `src/docs/task_feature.md`. It belongs under `src/docs/`.

After this plan lands: `skills/chat/SKILL.md` becomes a generated artifact built from `src/templates/skills/chat.md.j2` + `src/config.yaml`, every `docs/partial_*.md` is deleted, and `docs/` contains only generated outputs (`learn_review_table.md`, `retro_summary_format.md`, `template_plan_frontmatter.md`, `plan_templates/`, `images/`).

Observable in the rendered chat skill: agent delegation table shows `booping-researcher` only (no fictional senior/middle/junior tier); status-count bash loop is rendered from `config.plan.statuses` so it can never drift; project context, lessons, and extension hook are inlined via `!`commands``; the existing "small ad-hoc edits OK, large work hands off" boundary is sharpened so user-asked frontmatter or inline tweaks are explicitly permitted without invoking the transitions-table ceremony owned by groom/develop/retro/learn.

## Decisions

- **Chat does not import `_plan_transitions.j2`; instead it lazy-loads a generated `docs/plan_lifecycle_overview.md`**: the existing macro filters transitions by owning skill and renders the operational contract (gates, on_exit, commit shape). Importing it for chat would either render an empty header (chat owns no statuses) or — if generalized to "render all" — leak operational machinery that belongs to groom/develop/retro/learn. Instead, generate a new `docs/plan_lifecycle_overview.md` from `src/templates/docs/plan_lifecycle_overview.md.j2` that iterates `config.plan.statuses.items()` and renders, per status: status name + description + a small table of valid `to` transitions with `when` text and the owning `skill`. **No gates, no on_exit, no cross-validation references** — those are operational concerns of the owning skills, not chat. Chat lazy-links to this doc when the user asks about lifecycle / available transitions / how to flip a status manually. Why: keeps `_plan_transitions.j2` untouched (other skills depend on its current shape); gives chat a lifecycle reference that matches its maintenance-tool role without dragging in operational machinery.
- **Status-count loop renders from config**: replace the literal `for s in backlog in-spec … cancelled;` with `for s in {{ config.plan.statuses.keys() | join(' ') }};`. Why: the status names already live in config; duplicating them in the chat body is a drift trap when statuses are added/renamed.
- **Drop the status glossary entirely from chat**: `partial_plan_statuses.md` mostly restates the `desc:` field of each status. The status names are self-evident in the rendered count table, and the nudge thresholds (`backlog ≥ 5`, `awaiting-retro ≥ 1`, `awaiting-plan-review ≥ 1`) are interpretable without the glossary. Why: `less prose, less drift` (lesson 0004; saved feedback memory).
- **Cross-validation doc moves to `src/docs/cross_validation.md`**: not a Jinja partial — it's a lazy-load reference. New convention is `src/docs/<name>.md`. Why: keeps `docs/` reserved for generated outputs after this plan; matches how task-classification reference docs already live (`src/docs/task_feature.md` etc.).
- **Maintenance-tool boundary stays in chat prose, not config**: chat does not get formal transitions. When the user asks chat to flip a status or fix frontmatter inline, chat just edits — no gates, no `<to-status>: <kebab-title>` commit, no entry in the transitions table. When the user asks for routine work owned by another skill, chat recommends that skill. Why: keeping config truthful matters more than giving chat an admin shortcut; the user is the gate when they ask chat to override.
- **Keep CLAUDE.md "Migrating an old skill…" section, generalized**: rename to "Adding a new template-driven skill" since migration is complete after this plan. The recipe (steps for moving values to config, importing partials, lazy-loading reference docs) generalizes cleanly. Why: still useful for net-new skills.

## Architecture

Load-time inputs of the new `chat.md.j2`:

```
src/config.yaml              → effort, agents (booping-researcher only), plan.statuses keys (for the bash loop)
_partials/_project_context   → !`bin/booping-project-name` (project name + path)
_partials/_available_agents  → renders config.skills.chat.agents
!`bin/booping-lessons`       → loaded lesson set
!`bin/booping-extra-instructions skill_chat.md`  → project-local override hook
```

Lazy-load (followed only when the situation demands):

```
docs/plan_lifecycle_overview.md  → status + transition reference, generated from config; no gates / cross-validation
```

The lifecycle doc is generated, like `docs/learn_review_table.md` and `docs/retro_summary_format.md`, from `src/templates/docs/plan_lifecycle_overview.md.j2` via `booping-build`.

Removed inputs (vs hand-authored chat):

```
docs/partial_project_resolution.md            → replaced by _project_context.j2
docs/partial_read_lessons.md                  → replaced by !`bin/booping-lessons`
docs/partial_agents_researchers_delegator.md  → replaced by _available_agents.j2
docs/partial_agents_researchers_strategy_senior_middle_junior.md → never accurate; deleted
docs/partial_plan_statuses.md                 → deleted; loop renders from config
```

Other skills are unaffected — `_plan_transitions.j2`, `_available_agents.j2`, and config schema all stay backward-compatible. The only schema addition is `skills.chat.{effort, agents}`.

## Milestones

### M1: Move cross-validation reference doc into the new convention — 1 SP | done

**Goal**: `/groom`'s in-spec gate link points at `src/docs/cross_validation.md`; the original `docs/partial_cross_validation.md` is unreferenced (deletion deferred to M5 to land all six prunes in one commit).

**Verify**: `just build && grep -n "cross_validation" skills/groom/SKILL.md` shows the new path; `grep -rn "partial_cross_validation" src/ skills/ agents/` returns no hits outside `docs/partial_cross_validation.md` itself.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Copy contents of `docs/partial_cross_validation.md` to `src/docs/cross_validation.md` (verbatim — same body, no edits). Update `src/config.yaml` `plan.statuses.in-spec.transitions[awaiting-plan-review].gates[0]` link from `[cross-validation](../../docs/partial_cross_validation.md)` to `[cross-validation](../../src/docs/cross_validation.md)`. Run `just build`. | `src/docs/cross_validation.md` (new), `docs/partial_cross_validation.md` (read), `src/config.yaml` | 1 | done |

#### Task 1.1 DoD

- [x] `src/docs/cross_validation.md` exists with the same body as the original partial.
- [x] `src/config.yaml` gate link reads `[cross-validation](../../src/docs/cross_validation.md)`.
- [x] `just build` rebuilds without error.
- [x] `skills/groom/SKILL.md` in-spec→awaiting-plan-review row shows the new link path.
- [x] Old `docs/partial_cross_validation.md` is still on disk (deletion in M5).

---

### M2: Wire `skills.chat` config — 1 SP | done

**Goal**: `src/config.yaml` carries the structured data the chat template will render: `effort` and `agents` with `booping-researcher`'s `good_for` / `bad_for` tailored to chat's actual delegation pattern (vault navigation reads, summarizing across ≥3 plans/retros, web fact-checks during discussion).

**Verify**: `just build` runs without error; `skills/chat/SKILL.md` is unchanged at this point (template not authored yet); other skills' rendered output is unchanged (diff `agents/` and other `skills/*/SKILL.md`).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `skills.chat.effort: high` and `skills.chat.agents.booping-researcher` to `src/config.yaml`. `good_for` should cover: vault-wide reads aggregated into a summary, plan/retro content extraction across ≥3 files, web search aggregation when user asks an open question. `bad_for` should cover: single-file reads, simple greps, anything that fits in a few lines of `ls`/`grep`. Run `just build` to confirm no rendering regressions. | `src/config.yaml` | 1 | done |

#### Task 2.1 DoD

- [x] `src/config.yaml` has `skills.chat.effort: high`.
- [x] `src/config.yaml` has `skills.chat.agents.booping-researcher` with non-empty `good_for` and `bad_for` lists tailored to chat usage (not copy-pasted from groom).
- [x] `just build` succeeds.
- [x] No diff in any other rendered skill or agent file (`git diff -- skills/ agents/` shows nothing).

---

### M3: Generate `docs/plan_lifecycle_overview.md` from a new `src/templates/docs/` template — 2 SP | done

**Goal**: A new generated artifact at `docs/plan_lifecycle_overview.md` that lists every status from `config.plan.statuses` with its description and a small table of valid transitions (`to`, `when`, owning `skill`). No gates, no on_exit, no cross-validation references — those are operational details of the owning skills, not chat. The doc becomes the lazy-load target chat links to in M4 (Step 6) when the user asks about lifecycle / valid transitions / how to flip a status manually.

**Verify**: `just build` renders `docs/plan_lifecycle_overview.md`; manual read confirms every status from `config.plan.statuses` appears once with the correct desc + transitions; `grep -n "cross.validation\|on_exit\|gate" docs/plan_lifecycle_overview.md` returns no hits.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | See Steps 1–4 below. | `src/templates/docs/plan_lifecycle_overview.md.j2` (new), `docs/plan_lifecycle_overview.md` (generated) | 2 | done |

**Step 1 — Verify the `terminal` flag exists for every status**: skim `src/config.yaml` `plan.statuses.<key>.terminal` for all ten current statuses (backlog, in-spec, awaiting-plan-review, ready-for-dev, in-progress, awaiting-retro, awaiting-learning, done, fail, cancelled). All should be present (verified at plan time: backlog/in-spec/awaiting-*/ready-for-dev/in-progress declare `terminal: false`; done/fail/cancelled declare `terminal: true`). If any status is missing the flag, add `terminal: false` (or `true` for terminal states) before authoring the template — `bin/booping-build` runs Jinja under `StrictUndefined`, which crashes on missing keys.

**Step 2 — Author** `src/templates/docs/plan_lifecycle_overview.md.j2`. Top of file: a one-paragraph header — `Lifecycle reference for plan statuses and transitions across skills. Lazy-loaded by `/chat` when the user asks about valid moves or wants a manual status flip. Operational gates (cross-validation, redecomposition checks) and `on_exit` ceremony are intentionally omitted — those belong to the owning skill's contract in `src/templates/_partials/_plan_transitions.j2`.` — followed by the rendered content. Body iterates `{% for key, s in config.plan.statuses.items() %}` and emits per status: `### \`{{ key }}\`` heading, then a paragraph with `{{ s.desc }}`, then — if `s.terminal` — a one-line `_Terminal — no outgoing transitions._`; otherwise a markdown table with columns `To | When | Owner` and one row per `s.transitions` entry rendering `\`{{ t.to }}\` | {{ t.when }} | /{{ t.skill }}`. Do **not** render `gates` or `on_exit` from any transition. The `render_group(env, config, "docs", …)` call in `bin/booping-build` already picks up `src/templates/docs/*.md.j2`, so no build-script change is needed.

**Step 3 — Run the four-check IA pass** (lesson 0004) on the authored template body before running build: scoping (every block needed for the lifecycle reference?); duplication (does the doc restate content already rendered into `_plan_transitions.j2` partials? — the answer should be: no, this doc deliberately strips gates/on_exit/commit-shape, and the omission is the differentiator); configurability (any user-tunable value hard-coded that should live in `src/config.yaml`?); hierarchy (top-level header says what/why; per-status sections say specifics — not flipped?). Note any finding that motivates a template edit; apply, then run `just build`.

**Step 4 — Verify the rendered output** end-to-end against the DoD.

#### Task 3.1 DoD

- [x] All ten statuses in `src/config.yaml` declare `terminal: <bool>` explicitly (verified at Step 1; no schema change required).
- [x] `src/templates/docs/plan_lifecycle_overview.md.j2` exists with the structure described above.
- [x] `just build` renders `docs/plan_lifecycle_overview.md` without error.
- [x] Rendered doc contains exactly one heading per status in `config.plan.statuses` (10 statuses currently).
- [x] Status order in the rendered doc matches `config.plan.statuses` declaration order: `backlog → in-spec → awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro → awaiting-learning → done → fail → cancelled`.
- [x] Each non-terminal status has a `To | When | Owner` table; each terminal status has the `_Terminal — no outgoing transitions._` line and no table.
- [x] `grep -in "cross.validation\|on_exit\|gates\?" docs/plan_lifecycle_overview.md` returns no hits in per-status data. (Single hit is the intentional intro paragraph mandated by Step 2 — naming the omission is the pedagogical point of the doc; literal DoD vs Step 2 mandate are internally inconsistent, Step 2 wins.)
- [x] Four-check IA pass was performed on the template body before saving (Step 3); no findings required template edits.
- [x] No other rendered file changes (`git diff -- skills/ agents/` shows nothing; only `docs/plan_lifecycle_overview.md` is added).

---

### M4: Author `src/templates/skills/chat.md.j2` and render `/chat` — 3 SP | done

**Goal**: `skills/chat/SKILL.md` becomes a generated artifact whose body uses no `docs/partial_*.md` references, mirrors the loading idioms of `groom.md.j2` / `retro.md.j2`, and explicitly states the maintenance-tool boundary.

**Verify**: `just build`; manual read of the rendered `skills/chat/SKILL.md` against the DoD checklist below; `grep -n "partial_" skills/chat/SKILL.md` returns no hits.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | See Steps 1–9 below. | `src/templates/skills/chat.md.j2` (new), `skills/chat/SKILL.md` (regenerated), `/tmp/chat-legacy.md` (transient backup) | 3 | done |

**Step 1 — Preserve the legacy body**: copy `skills/chat/SKILL.md` to `/tmp/chat-legacy.md` before any other action. `just build` will overwrite `skills/chat/SKILL.md` later in this task, and the legacy file is the only source of the carry-over phase prose. The lifecycle doc generated in M3 must already be in place — the chat template links to `../../docs/plan_lifecycle_overview.md` and that path must resolve at build time.

**Step 2 — Author the template** at `src/templates/skills/chat.md.j2`. Use `src/templates/skills/groom.md.j2` as the structural model. Required Jinja imports at the top of the body (after the title): `{% import "_partials/_available_agents.j2" as available_agents with context %}`. Do **not** import `_plan_transitions.j2` (chat owns no statuses). Frontmatter: copy `name`, `argument-hint`, `user-invocable`, `allowed-tools` verbatim from `/tmp/chat-legacy.md`; replace the `effort: high` literal with `effort: {{ config.skills.chat.effort }}`; **rewrite the `description` field** to convey both halves of chat's purpose — context-aware project chat *and* chores. Use this exact string: `Context-aware chat about the project: discuss plans, retros, lessons, and code; navigate the vault; and handle chores (frontmatter tweaks, status flips, inline plan or code edits) without invoking the heavier skills. Opens every session with a vault status summary.` This description propagates to `/help`'s `## Skills` table automatically because `bin/booping-skills` reads it from each skill's frontmatter — no separate help-template edit needed.

**Step 3 — Replace the legacy Preflight bullets** with the following block ordering, modeled exactly on `groom.md.j2` (in this order, immediately after the title): `{% include "_partials/_project_context.j2" %}`, then `{{ available_agents.render("chat") }}`, then a literal line `` !`bin/booping-lessons` ``. Remove every `Read [name](../../docs/partial_*.md)` bullet from the legacy Preflight — those five reads are the ones being replaced. Drop the `Read from ~/Claude/{project}/_booping/skill_chat.md` Preflight bullet too; it is replaced by the bottom `!`bin/booping-extra-instructions`` block.

**Step 4 — Render the status-count loop from config** in Phase 0: replace the legacy hard-coded `for s in backlog in-spec awaiting-plan-review ready-for-dev in-progress awaiting-retro awaiting-learning done fail cancelled; do` with `for s in {{ config.plan.statuses.keys() | join(' ') }}; do`.

**Step 5 — Carry over verbatim from `/tmp/chat-legacy.md`** these blocks (no edits except where noted): the `# booping — /chat` H1 + the two-paragraph intro under it; the `## High-level workflow` numbered list; the `## Phase 0 Orient` body (with the loop substitution from Step 4); the `## Phase 1 Ingest` body; the `## Phase 2 Discuss / act` body, but **delete** its second paragraph that begins `You may delegate research to a `booping-researcher-{senior,middle,junior}` agent…` (the fictional tier — superseded by the Available Agents block rendered above); the `## Phase 3 Hand-offs` body; the `## What chat does NOT do` block; the `## Hard rules` block.

**Step 6 — Add a new `## Maintenance-tool boundary` section** (placed between `## Phase 3 Hand-offs` and `## What chat does NOT do`) with three bullets: (a) when the user asks for routine work owned by another skill (groom / develop / retro / learn), recommend the skill rather than doing it inline; (b) when the user explicitly asks for an inline frontmatter / status / small code edit, just do it — no transitions table, no `<to-status>: <kebab-title>` commit; (c) when the user asks about valid statuses, available transitions, or how to flip a plan's status manually, lazy-load `[plan lifecycle](../../docs/plan_lifecycle_overview.md)` to ground the answer in the current `config.plan.statuses` shape.

**Step 7 — Append the bottom block** verbatim: a literal line `` !`bin/booping-extra-instructions skill_chat.md` `` as the last non-blank line of the body.

**Step 8 — Run the four-check IA pass** (lesson 0004) on the authored template body before running build: scoping (every block needed for chat's job?); duplication (any block restated from a partial / config the template already pulls in?); configurability (any user-tunable value hard-coded that should be in `src/config.yaml`?); hierarchy (top-level says what/when, deeper says how — not flipped?). Note any finding that motivates a template edit; apply, then run `just build`.

**Step 9 — Verify the rendered output** against the DoD below by reading `skills/chat/SKILL.md` end-to-end.

#### Task 4.1 DoD

- [x] `/tmp/chat-legacy.md` was created before `just build` ran (preserves the legacy body during authoring).
- [x] `src/templates/skills/chat.md.j2` exists and starts with `---` frontmatter, then `{% import "_partials/_available_agents.j2" as available_agents with context %}` (no `_plan_transitions.j2` import).
- [x] Frontmatter `effort` field reads `{{ config.skills.chat.effort }}` (rendered to `high` after build).
- [x] Frontmatter `description` matches the new context-aware-chat-and-chores wording from Step 2 verbatim (wrapped in double quotes in the template — content unchanged, YAML-safe due to colons in body).
- [x] Rendered `/help` skills table (verify by running `bin/booping-skills`) shows the new chat description without any edit to `src/templates/skills/help.md.j2`.
- [x] Frontmatter `allowed-tools` still includes `Bash(booping-plans:*)`, `AskUserQuestion`, `Agent`, and the current Read/Write/Edit/Glob/Grep set.
- [x] `just build` regenerates `skills/chat/SKILL.md` without error.
- [x] Rendered `skills/chat/SKILL.md` contains no string `partial_` and no string `senior/middle/junior` (fictional researcher tier removed).
- [x] Rendered Project Context block matches `skills/groom/SKILL.md` (same `!`bin/booping-project-name`` invocation, same wording).
- [x] Rendered Available Agents block lists exactly `booping-researcher` with the chat-specific `good_for` / `bad_for` from M2.
- [x] Rendered Phase 0 bash loop iterates `backlog in-spec awaiting-plan-review ready-for-dev in-progress awaiting-retro awaiting-learning done fail cancelled` in declaration order.
- [x] Rendered body has a `## Maintenance-tool boundary` section with the three bullets described above (recommend-the-skill, do-inline-edits, lazy-load-the-lifecycle-doc).
- [x] The Maintenance-tool boundary section's third bullet links to `../../docs/plan_lifecycle_overview.md` (path resolves from `skills/chat/SKILL.md`).
- [x] Rendered body's last non-blank line is the `!`bin/booping-extra-instructions skill_chat.md`` block.
- [x] Four-check IA pass was performed on the template body before saving. Findings: (1) minor overlap between "What chat does NOT do" and Maintenance bullet (b) — kept both, scopes differ; (2) Phase 0 nudge thresholds (5/1/1) are hard-coded magic numbers — flagged for follow-up, out of milestone scope per Step 5 verbatim-carry rule.
- [x] `/tmp/chat-legacy.md` removed after the milestone commits cleanly.

---

### M5: Delete the six orphaned `docs/partial_*.md` — 1 SP | done

**Goal**: `docs/partial_*.md` no longer exists. After this milestone, `docs/` contains only generated outputs (`learn_review_table.md`, `retro_summary_format.md`, `template_plan_frontmatter.md`, `plan_templates/`, `images/`) — `partial_*` is a dead namespace.

**Verify**: `ls docs/partial_* 2>&1` reports no matches; `grep -rln "docs/partial_" --include='*.md' --include='*.j2' --include='*.yaml' --include='*.py' .` returns no hits except possibly inside this plan file or retros that reference history.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `rm docs/partial_agents_researchers_delegator.md docs/partial_agents_researchers_strategy_senior_middle_junior.md docs/partial_cross_validation.md docs/partial_plan_statuses.md docs/partial_project_resolution.md docs/partial_read_lessons.md`. After deletion, run `grep -rln "docs/partial_" --include='*.md' --include='*.j2' --include='*.yaml' --include='*.py' .` from repo root and ensure no source-of-truth files reference the removed paths (CLAUDE.md edits in M6 will resolve any remaining references there). | `docs/partial_*.md` (six files removed) | 1 | done |

#### Task 5.1 DoD

- [x] All six `docs/partial_*.md` files are deleted.
- [x] `grep -rln "docs/partial_"` against `*.md`/`*.j2`/`*.yaml`/`*.py` shows hits only in `CLAUDE.md` (handled in M6) and possibly historical retros/plan files (acceptable — they describe past state).
- [x] `just build` still renders cleanly.
- [x] All rendered SKILL.md files are unchanged after the deletion (`git diff -- skills/`).

---

### M6: Update `CLAUDE.md` to reflect the post-migration state — 2 SP | done

**Goal**: `CLAUDE.md` no longer claims `/chat` is hand-authored, no longer enumerates the six deleted partials, and the "Migrating an old skill to the template pipeline" section is rewritten as "Adding a new template-driven skill" since migration is complete.

**Verify**: read `CLAUDE.md` end-to-end; `grep -n "partial_" CLAUDE.md` returns no hits; `grep -n "hand-author" CLAUDE.md` returns no hits referring to `/chat`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Status section: remove the bullet "Only `/chat` still authors its `SKILL.md` by hand and references `docs/partial_*.md`. Migration to the template pipeline is pending; it works as-is in the meantime." Replace the "Template pipeline is live" bullet with a one-liner that all skills are template-driven. Layout section: remove the `docs/partial_*.md — six surviving legacy partials …` paragraph; replace it with a one-liner: `docs/` contains only generated outputs (rendered skills' lazy-load reference docs `learn_review_table.md`, `retro_summary_format.md`, `template_plan_frontmatter.md`, `plan_lifecycle_overview.md`, the `plan_templates/` directory, and the `images/` directory). Update the bullet about `partial_cross_validation.md` to reference its new location at `src/docs/cross_validation.md`. Add a new entry under "Information ownership" or "Layout" noting the lifecycle overview doc is generated and lazy-loaded by chat. Rename "Migrating an old skill to the template pipeline" → "Adding a new template-driven skill"; rewrite the recipe so the steps describe authoring a fresh skill (not a copy-from-existing). Drop step 8's reference to deleting `docs/partial_*.md` predecessors and the "When `/chat` migrates" closing paragraph (both obsolete). | `CLAUDE.md` | 2 | done |

#### Task 6.1 DoD

- [x] `CLAUDE.md` Status section no longer mentions `/chat` as hand-authored.
- [x] `CLAUDE.md` Layout section no longer enumerates `docs/partial_*.md`; references `src/docs/cross_validation.md` for the cross-validation reference doc.
- [x] `CLAUDE.md` mentions the new generated `docs/plan_lifecycle_overview.md` and notes it is lazy-loaded by `/chat`.
- [x] `CLAUDE.md` has a section titled "Adding a new template-driven skill" (or equivalent) with steps that work for a net-new skill.
- [x] No references to the six deleted partial paths anywhere in `CLAUDE.md`.
- [x] `grep -n "When \`/chat\` migrates" CLAUDE.md` returns no hits (closing paragraph removed).

---

### M7: Manual prose-shape reshape on the rendered `/chat` — 3 SP | done

**Goal**: User-approved final shape of `skills/chat/SKILL.md` and the rendered `docs/plan_lifecycle_overview.md`. Builds on the four-check IA pass already performed on the chat template body in M4 (Task 4.1 Step 8); this milestone is the user-visible reshape on top of an already-IA-checked draft — wording, ordering, prose density tweaks that only surface once the rendered output is read in full. Edits land in `src/templates/skills/chat.md.j2`, `src/templates/docs/plan_lifecycle_overview.md.j2`, shared partials (if duplication is found across skills), or `src/config.yaml`; re-render after each round.

**Verify**: User explicitly approves both the rendered chat skill and the rendered lifecycle overview ("looks good", "ship it"). Silence does not count.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Hand the rendered `skills/chat/SKILL.md` and `docs/plan_lifecycle_overview.md` back to the user for IA reshape. For each user comment: identify whether the fix belongs in the chat template, the lifecycle template, a shared partial (if the same shape exists in groom/develop/retro/learn), or in `src/config.yaml`; apply, re-render, present again. Loop until user explicitly approves both files. | `src/templates/skills/chat.md.j2`, `src/templates/docs/plan_lifecycle_overview.md.j2`, possibly `src/templates/_partials/*.j2`, possibly `src/config.yaml` | 3 | done |

#### Task 7.1 DoD

- [x] User has explicitly approved the rendered `skills/chat/SKILL.md` shape.
- [x] User has explicitly approved the rendered `docs/plan_lifecycle_overview.md` shape.
- [x] Every reshape edit landed in a template / partial / config — never directly in `skills/chat/SKILL.md` or `docs/plan_lifecycle_overview.md` (both are generated).
- [x] If the reshape surfaced a duplication across skills, the fix landed in the shared partial, not just in chat's template (`_shared_instructions.j2` created and included in all 5 plan-touching skills).
- [x] `just build` regenerates cleanly after the final reshape round.

**M7 deltas vs. original plan**: (1) reshape uncovered a wrong claim in chat (`sprints.md is chat-owned — sole writer`) and a stale Hard rule; both removed. (2) `What chat does NOT do` block dropped — substance covered by Maintenance-tool boundary. (3) Phase 0 status-count bash loop + nudge requirement replaced with a two-table requirement (counts + active plans). (4) New `_shared_instructions.j2` partial with a single rule (post-SP/status-modification regen of `sprints.md`) included across all 5 plan-touching skills. (5) CLAUDE.md sprints.md line rewritten to flag the gap and queue a PostToolUse + SessionStart/End hook bundle as a follow-up plan.

---

## Final Verification

- [x] `bin/booping-build` renders cleanly after every milestone.
- [x] `skills/chat/SKILL.md` is a generated artifact (no hand edits since the migration); contains no `docs/partial_*` references; lazy-links to `../../docs/plan_lifecycle_overview.md` in the maintenance-tool boundary section.
- [x] `docs/plan_lifecycle_overview.md` exists, is generated from `src/templates/docs/plan_lifecycle_overview.md.j2`, lists every status from `config.plan.statuses`, and contains no cross-validation / gate / on_exit references in per-status data (intro paragraph names the omission per M3 Step 2).
- [x] `docs/partial_*.md` does not exist (six files deleted).
- [x] `src/docs/cross_validation.md` exists; `src/config.yaml` gate link points at it; rendered `skills/groom/SKILL.md` shows the new link.
- [x] All other rendered skills (`develop`, `groom`, `help`, `install`, `learn`, `retro`) are unchanged from this plan's start *except* for the `_shared_instructions.j2` partial added by M7 to develop/groom/retro/learn (intentional per M7 DoD: "if reshape surfaced a duplication across skills, fix landed in the shared partial").
- [x] `CLAUDE.md` reflects the post-migration state — no stale references to chat as hand-authored, no enumeration of deleted partials, mentions the new lifecycle overview doc, "Adding a new template-driven skill" section in place.
- [x] User has explicitly approved the M7 reshape (both the chat skill and the lifecycle overview doc).

## Out of scope

- **Chat as a maintenance tool with formal transitions** — adding new entries to `config.plan.statuses` transitions tables (e.g. `* → cancelled` from chat) is a behavior change deferred to a separate plan. This plan only sharpens the existing in-prose boundary.
- **Other skills' bodies** — `develop`, `groom`, `help`, `install`, `learn`, `retro` template files are not touched. Only `src/config.yaml` is touched (M1 gate link, M2 chat config), and that touch is verified to leave their rendered output unchanged except for the cross-validation link in groom.
- **Plan template changes** — `src/templates/plan_templates/*.j2` and the rendered `docs/plan_templates/*.md` are unchanged.
- **`docs/images/`** — kept as-is; referenced from README.md.

## CLAUDE.md impact

M6 owns all CLAUDE.md edits:

- Status section: remove chat-still-hand-authored bullet; mark all skills template-driven.
- Layout section: drop the `docs/partial_*.md — six surviving legacy partials` paragraph; replace with the post-migration `docs/` summary including the new `plan_lifecycle_overview.md`; update the `partial_cross_validation.md` reference to `src/docs/cross_validation.md`.
- Note that `docs/plan_lifecycle_overview.md` is generated and lazy-loaded by `/chat`.
- "Migrating an old skill to the template pipeline" → "Adding a new template-driven skill" with the recipe rewritten for net-new skills (drop step 8's partial-deletion sweep and the `/chat` closing paragraph).

## Risks

- **Rendered status loop ordering** — Jinja's `dict.keys()` preserves insertion order on Python 3.7+, and the renderer uses YAML-loaded mappings (also insertion-ordered). Both the chat skill's Phase 0 bash loop (M4) and the lifecycle overview doc (M3) must iterate in `config.yaml` declaration order: `backlog → in-spec → awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro → awaiting-learning → done → fail → cancelled`. Mitigation: M3 DoD checks the lifecycle doc's status order; M4 DoD checks the chat bash loop's status order.
- **Empty `_plan_transitions.j2` for chat** — explicitly out of scope by not importing the macro; chat instead lazy-loads the new generated `docs/plan_lifecycle_overview.md` (M3). Documented in Decisions.
- **Lifecycle doc drift** — `docs/plan_lifecycle_overview.md` is generated from `config.plan.statuses` on every build, so adding/renaming a status auto-propagates. The doc deliberately omits gates / on_exit / cross-validation; if a future reader expects to see the operational contract there, they'll find it in `_partials/_plan_transitions.j2` rendered into each skill. Mitigation: M3's header paragraph names the omission and points readers at the partial.
- **Cross-link fragility for the moved cross-validation doc** — the link in `src/config.yaml` is rendered into `skills/groom/SKILL.md` at depth 2 (`skills/groom/`), so the link path needs `../../src/docs/cross_validation.md`. Mitigation: M1 DoD verifies the rendered path resolves from the rendered file's location.
- **Legacy chat body is overwritten by `just build`** — `just build` regenerates `skills/chat/SKILL.md` from the new template, destroying the legacy file in place. M4 Task 4.1 Step 1 mandates a `/tmp/chat-legacy.md` backup before any other action; the carry-over phase prose in Steps 5/6 references that backup explicitly.
- **Macro-vs-include syntax confusion** — `_available_agents.j2` exposes a Jinja macro, not a fragment, so it must be imported (`{% import … as available_agents with context %}`) and called as `{{ available_agents.render("chat") }}`. Using `{% include %}` instead would leave `available_agents` undefined and crash `just build` under `StrictUndefined`. M4 Task 4.1 Step 2 spells out the import line verbatim and DoD verifies it.
- **Untyped config schema** — checked: `bin/booping-build` calls `yaml.safe_load` and passes the dict straight to Jinja; no Pydantic / JSON Schema layer. Adding `skills.chat.effort` and `skills.chat.agents` in M2 carries no schema-update risk.
- **`StrictUndefined` crash on missing `terminal` flag** — the renderer runs Jinja with `StrictUndefined`, so `s.terminal` will crash if a status omits the flag. Verified at plan time: every existing status in `src/config.yaml` declares `terminal: false` or `terminal: true`. M3 Step 1 re-verifies before authoring the template; if anyone later adds a status without `terminal:`, `just build` fails fast with a clear error.
