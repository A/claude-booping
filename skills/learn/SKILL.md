---
name: learn
description: Extract lessons from a retrospective and fold improvements into project-local skill/agent extensions under _booping/. Use after /retro writes a retrospective.
argument-hint: [retrospective file path]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(ls *)
  - Bash(test *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(grep *)
  - AskUserQuestion
effort: high
---

# booping — /learn

Turn retrospective findings into durable behavior changes routed to exactly one target each.

This skill is **wide-domain** — it must work across very different projects. Project-specific concerns live in `_booping/skill_learn.md`, lessons, and the vault `CLAUDE.md`. Do not bake them into this skill.

## Preflight

- Read and resolve project based on [project resolution principle](../../docs/partial_project_resolution.md).
- Read [plan statuses](../../docs/partial_plan_statuses.md).
- Read [plan transitions for /learn](../../docs/partial_plan_transitions_learn.md) — the only transition this skill owns.
- Read [learning targets](../../docs/partial_learn_targets.md) — the Type / Holds / Picked-when matrix this skill routes every candidate through.
- Read [partial_debug_delegator](../../docs/partial_debug_delegator.md) — cheap gate that runs the mechanical check and, only when active, loads `partial_debug_learn` to extend the type vocabulary defined in `partial_learn_targets`.
- Read [review-table template](../../docs/template_learn_review_table.md) — format for Phase 2's user-facing table.
- Read lessons per [read lessons](../../docs/partial_read_lessons.md).
- Read from `~/Claude/{project}/_booping/skill_learn.md`. Silently skip, if file doesn't exist.
- Read the attached repo's `CLAUDE.md` — project conventions.

## High-level workflow

1. Intake — resolve retro path, validate `awaiting-learning` status.
2. Extract candidates — inline, decomposed into atomic rules, routed via the matrix.
3. Update-vs-create sweep — filtered read of existing lessons and extensions.
4. Present unified review table — user accepts / rejects / adds rows.
5. Write accepted items — one pass per target type, no per-edit prompts.
6. Framework review, transition, and commit.

## Single-location rule

Every accepted learning lands in **exactly one** target. If a candidate would otherwise span two targets, decompose it into two distinct rows in the review table — one row per target. The `Type` vocabulary and routing tests live in [partial_learn_targets](../../docs/partial_learn_targets.md); do not restate the matrix here.

---

## Phase 0 Intake

Resolve the retro path from `$ARGUMENTS`; if missing, default to the most recent file in `~/Claude/{project_name}/retrospectives/`. Read the retrospective file and follow its `plan:` frontmatter to the associated plan.

Validate entry status: the plan's `status:` must be `awaiting-learning`. On mismatch, STOP with this verbatim error:

> `/learn requires a plan in status 'awaiting-learning'; got '<current-status>' for <retro-path>. Run 'booping-plans --status awaiting-learning' to list candidates.`

## Phase 1 Extract candidates

Read the retrospective's `What went wrong`, `Root causes`, `Action items`, and `Takeaways` sections. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

For each candidate, pick a target from the Type vocabulary using the matrix in [partial_learn_targets](../../docs/partial_learn_targets.md). The available type set for this run is `BASE_TYPES ∪ types-activated-by-loaded-partials` — trust the matrix as extended by whichever partials the Preflight loaded.

## Phase 1.5 Update-vs-create sweep

Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

1. `ls ~/Claude/{project_name}/lessons/` — enumerate existing lessons.
2. `ls ~/Claude/{project_name}/_booping/` — enumerate existing project-local extensions.
3. For each candidate, read ONLY the `_booping/` files whose name matches a candidate-relevant skill or agent (filter, don't dump everything).
4. Read the vault `CLAUDE.md` and the attached repo's `CLAUDE.md` in full (both are short).

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage at any target.
- `update existing at target X` — duplicate or refinement of a rule already written at `X`; the candidate becomes an update to `X`, not a fresh write at a different target.
- `conflict with existing at target X` — surface to the user in the review table as a visible flag.

## Phase 2 Present unified review table

Render the review table using the format defined in [template_learn_review_table](../../docs/template_learn_review_table.md). Use `AskUserQuestion` once to collect the user's accept / reject / add response.

Do not prompt per row. Do not inline the column-by-column documentation here — the template owns the format, the accept/reject syntax, and the user-added-row split rule.

## Phase 3 Write accepted items

After the table is accepted, write every accepted row in a single pass per target type. No per-edit `AskUserQuestion` calls; table acceptance is the consent.

Write paths use these templates (resolve each placeholder before writing):

- `lessons/{N}_<kebab>.md` — `{N}` is the next integer, computed from `ls lessons/` highest existing prefix + 1; body uses [template_lesson.md](../../docs/template_lesson.md).
- `_booping/skill_<name>.md` — per-skill extension in this project's vault.
- `_booping/agent_<name>.md` — per-agent extension in this project's vault.
- Vault `CLAUDE.md` and repo `CLAUDE.md` — one-line bullet additions; no paragraph rewrites.

Target types beyond these base five come from partials loaded in Preflight and carry their own write-path and commit guidance — defer to them.

## Phase 4 Framework review

List the plugin `skills/` and `agents/` directories with `ls`. For each skill or agent whose name appears in Phase 1's candidate list, read only that file (filter, don't dump everything). If a retro pattern indicates that a plugin skill or agent would benefit from a project-local extension, append additional rows to the review table and re-confirm with the user via `AskUserQuestion`.

Project-local extensions (`_booping/skill_<name>.md`, `_booping/agent_<name>.md`) are the default framework-review output regardless of flags. Any additional framework-review targets come from partials loaded in Preflight.

## Phase 5 Transition + commit

Apply the `awaiting-learning → done` transition per [partial_plan_transitions_learn](../../docs/partial_plan_transitions_learn.md): set `status: done` and `completed: <today>`. Run `booping-plans --status done` to confirm.

Commit the vault updates from the vault working directory:

```bash
cd ~/Claude/{project_name}
git add lessons/ _booping/ CLAUDE.md plans/<plan-filename>.md
git commit -m "learn: <kebab-retro-title> done"
```

If Phase 3 wrote to the attached repo's `CLAUDE.md`, commit that separately from the repo working directory:

```bash
cd <repo-path>
git add CLAUDE.md
git commit -m "docs(claude-md): <short summary>"
```

Any additional commit boundaries required by partials loaded in Preflight are those partials' own responsibility — do not inline their commit shape here.

## What learn does NOT do

- Does **not** write methodology changes to `skills/*/SKILL.md` or `agents/*.md` in the plugin repo by default. Extensions land in the vault under `_booping/`.
- Does **not** transition plans to any status other than `awaiting-learning → done`.
- Does **not** regenerate `sprints.md`; `/chat` owns that.
- Does **not** delegate candidate classification to role agents — those agents have been deleted.

## Hard rules

- (a) The orchestrator owns all reads and writes; there is no role-agent fan-out and no researcher delegation for classification.
- (b) Terminology for activation-gated behaviours (including plugin-side editing) belongs exclusively to the partials that own those behaviours; do not name or paraphrase their vocabulary here.
- (c) One rule per lesson file; bodies follow [template_lesson.md](../../docs/template_lesson.md).
- (d) Every accepted learning lands in exactly one target. Multi-rule insights decompose into multiple rows; the same rule must never be routed to two targets simultaneously — decomposition is the only escape hatch.
- (e) The matrix of types lives in [partial_learn_targets](../../docs/partial_learn_targets.md) — do not inline it here.
- (f) The review-table column-by-column documentation lives in [template_learn_review_table](../../docs/template_learn_review_table.md) — do not inline it here.
- (g) Never propose a rule whose trigger is "try harder" or "be careful". The `How to apply` section must be mechanically checkable.
