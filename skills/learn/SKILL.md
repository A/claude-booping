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
  - Bash(bin/booping-debug-mode:*)
  - Bash(bin/booping-project-name:*)
  - AskUserQuestion
effort: high
---



# booping — /learn

Turn retrospective findings into durable behavior changes routed to exactly one target each.

## Project Context

!`bin/booping-project-name`

On skill load, report the resolved project context back to the user verbatim so they can see which project and vault the skill is operating on.


## Plan Transitions

This table is the contract: the valid moves and their requirements — `Gates` (must hold before the move) and `On exit` (must be fulfilled when taking the move). Both are strict. When an internal action matches a `When` trigger, verify every `Gate` holds, fulfill every `On exit` requirement, update `status:` to the `To` value, then commit the change to the vault:

```bash
cd ~/Claude/{project}
git add plans/<plan-file>.md   # plus any sibling artifacts written in the same run
git commit -m "<to-status>: <kebab-title>"
```

One commit per transition. Sibling stubs written in the same run go in the same commit.

### `awaiting-learning` — Retro written; waiting for /learn to absorb lessons.

| To | When | Gates | On exit |
|----|------|-------|---------|
| `done` | All accepted learnings written | User confirmed the review table; Every accepted lesson written to its target file | set `completed: yyyymmdd hh:mm` |






## Routing Matrix

This matrix is the routing contract for /learn candidates. Every accepted learning lands in exactly one target — no duplicates across targets, no multi-target rows.

| Target | When to use | Lands at | Examples |
|--------|-------------|----------|----------|
| **Lesson** | Cross-framework principle reaching every skill — design heuristic, test discipline, IA rule. Concrete, short, with one example. | `lessons/{N}_<kebab>.md` | "Challenge code design by SOLID principles", "Use AAA in test cases", "Design skill template partials by information hierarchy" |
| **Skill extra instructions** | Tweak or extend a single skill's method (groom / develop / retro / learn / chat / install / help). | `_booping/skill_<skill>.md` | `skill_groom.md`, `skill_develop.md`, `skill_retro.md`, `skill_learn.md`, `skill_chat.md`, `skill_install.md`, `skill_help.md` |
| **Agent extra instructions** | Hook a single agent's behavior. Compact list. | `_booping/agent_<full-agent-name>.md` | `agent_booping-researcher.md`, `agent_booping-developer-middle.md`, `agent_booping-developer-senior.md` |
| **Repository CLAUDE.md** | Project-fact aiding fresh-agent project understanding — layout path, CLI command, code-side convention. One-bullet additions; no paragraph rewrites. | `<repo>/CLAUDE.md` | (single canonical target — no filename variants) |

If a candidate would otherwise span two targets, decompose into two distinct rows; never duplicate the same rule across targets.

The skill infers the exact filename per candidate; the example lists above are validation aids, not full enumerations.


!`bin/booping-debug-mode learn`

## High-level workflow

1. Intake — resolve retro path, validate `awaiting-learning` status.
2. Extract candidates — inline, decomposed into atomic rules, routed via the matrix.
3. Update-vs-create sweep — filtered read of existing lessons and extensions.
4. Present unified review table — user accepts / rejects / adds rows.
5. Write accepted items — one pass per target type, no per-edit prompts.
6. Framework review, transition, and commit.

## Single-location rule

Every accepted learning lands in **exactly one** target. If a candidate would otherwise span two targets, decompose it into two distinct rows in the review table — one row per target. The four targets, when-to-use tests, and example filenames live in the matrix rendered above; do not restate it elsewhere in this body.

---

## Phase 0 Intake

Resolve the retro path from `$ARGUMENTS`; if missing, default to the most recent file in `~/Claude/{project_name}/retrospectives/`. Read the retrospective file and follow its `plan:` frontmatter to the associated plan.

Validate entry status: the plan's `status:` must be `awaiting-learning`. On mismatch, STOP with this verbatim error:

> `/learn requires a plan in status 'awaiting-learning'; got '<current-status>' for <retro-path>. Run 'booping-plans --status awaiting-learning' to list candidates.`

## Phase 1 Extract candidates

Read the retrospective file and extract candidates for self-learning. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

For each candidate, pick a target from the matrix rendered above.

## Phase 1.5 Update-vs-create sweep

Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

1. Read every lesson under `~/Claude/{project_name}/lessons/` (skip silently if the directory is empty), `~/Claude/{project_name}/_booping/skill_learn.md` (skip silently if absent), and the attached repo's `CLAUDE.md` (skip silently if absent). Together these are the lookup set for the dup-check sweep. Do not invoke `bin/booping-lessons` or `bin/booping-extra-instructions` here — read the files directly so the eager-load bias is avoided.
2. For each candidate, read ONLY the `_booping/` files whose name matches a candidate-relevant skill or agent (filter, don't dump everything).

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage at any target.
- `update existing at target X` — duplicate or refinement of a rule already written at `X`; the candidate becomes an update to `X`, not a fresh write at a different target.
- `conflict with existing at target X` — surface to the user in the review table as a visible flag.

## Phase 2 Present unified review table

Render the review table using the format defined in [review table format](../../docs/learn_review_table.md). Use `AskUserQuestion` once to collect the user's accept / reject / add response.

Do not prompt per row. Do not inline the column-by-column documentation here — the template owns the format, the accept/reject syntax, and the user-added-row split rule.

## Phase 3 Write accepted items

After the table is accepted, write every accepted row in a single pass per target type. No per-edit `AskUserQuestion` calls; table acceptance is the consent.

Write paths use these templates (resolve each placeholder before writing):

- `lessons/{N}_<kebab>.md` — `{N}` is the next integer, computed from `ls lessons/` highest existing prefix + 1; body follows the lesson body shape inlined below.
- `_booping/skill_<name>.md` — per-skill extension in this project's vault.
- `_booping/agent_<name>.md` — per-agent extension in this project's vault.
- Repo `CLAUDE.md` — one-line bullet additions; no paragraph rewrites.


---
id: {{N}}                                      # monotonically-increasing integer; matches the filename prefix
title: {{One-sentence rule as a prescriptive statement}}
retro: retrospectives/YYYYMMDD-{{kebab-title}}.md   # the retro that surfaced this lesson
created: YYYY-MM-DD                            # date this lesson was extracted
---

**Rule**: {{The principle, imperative form. One sentence; at most a short bullet list if the rule has named sub-checks.}}

**Example**: {{One concrete case that illustrates the rule — what went wrong or right, in one or two lines. No motivation paragraphs, no multi-section "how to apply", no forbidden/edge-case lists. The retro carries the backstory; link it via `retro:` frontmatter.}}



## Phase 4 Framework review

List the plugin `skills/` and `agents/` directories with `ls`. For each skill or agent whose name appears in Phase 1's candidate list, read only that file (filter, don't dump everything). If a retro pattern indicates that a plugin skill or agent would benefit from a project-local extension, append additional rows to the review table and re-confirm with the user via `AskUserQuestion`.

Project-local extensions (`_booping/skill_<name>.md`, `_booping/agent_<name>.md`) are the default framework-review output regardless of flags.

## Phase 5 Transition + commit

Apply the `awaiting-learning → done` transition per the transitions table above: set `status: done` and `completed: <today>`. Run `booping-plans --status done` to confirm.

Commit the vault updates from the vault working directory:

```bash
cd ~/Claude/{project_name}
git add lessons/ _booping/ plans/<plan-filename>.md
git commit -m "learn: <kebab-retro-title> done"
```

If Phase 3 wrote to the attached repo's `CLAUDE.md`, commit that separately from the repo working directory:

```bash
cd <repo-path>
git add CLAUDE.md
git commit -m "docs(claude-md): <short summary>"
```

## What learn does NOT do

- Does **not** write methodology changes to `skills/*/SKILL.md` or `agents/*.md` in the plugin repo by default. Extensions land in the vault under `_booping/`.
- Does **not** transition plans to any status other than `awaiting-learning → done`.
- Does **not** regenerate `sprints.md`; `/chat` owns that.

## Hard rules

- (a) The orchestrator owns all reads and writes; there is no role-agent fan-out and no researcher delegation for classification.
- (b) Terminology for activation-gated behaviours (including plugin-side editing) belongs exclusively to the partials that own those behaviours; do not name or paraphrase their vocabulary here.
- (c) One rule per lesson file; bodies follow the lesson body shape included in Phase 3 above.
- (d) Every accepted learning lands in exactly one target. Multi-rule insights decompose into multiple rows; the same rule must never be routed to two targets simultaneously — decomposition is the only escape hatch.
- (g) Never propose a rule whose trigger is "try harder" or "be careful". The rule must be mechanically checkable.
- (h) Lesson bodies are compact: one **Rule** + one **Example**, per the lesson body shape included in Phase 3 above. No motivation paragraphs, no multi-section "how to apply", no forbidden/edge-case lists — backstory lives in the linked retro. Target is 20–40 lessons inlined at skill load without bloating context.
