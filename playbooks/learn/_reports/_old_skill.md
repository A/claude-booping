

# booping — /learn

Turn retrospective findings into durable behavior changes routed to exactly one target each.

## Project Context


```yaml
name: claude-booping
directory: /home/anton/Dev/@A/notes/projects/claude-booping
repo_directory: /home/anton/Dev/@A/claude-booping
git_commit: 41393376a1a791560c0042c1c2a4e2fe21679af4
```


On skill load, report the resolved project context back to the user verbatim so they can see which project and vault the skill is operating on.


## Plan Transitions

This table is the contract: the valid moves and their requirements — `Gates` (must hold before the move) and `On exit (auto)` (the mechanical mutations the move applies). When an internal action matches a `When` trigger, verify every `Gate` holds, then execute the move with one command — it applies every mechanical mutation (status, date stamps, commit snapshot, sprints.md, vault commit) deterministically:

```bash
booping transition <to-status> plans/<plan-file>.md [--also <artifact>...]
```

Pass every vault artifact the skill authored for this move (e.g. a retrospective file, a sibling stub plan) via `--also` so it lands in the same transition commit. Do not hand-edit `status:` or hand-run `git commit` — the command owns all of it. It prints a report of every mutation it applied (`<from> → <to>`, then one line per hook); the report is authoritative — do not re-read the plan to verify.

### `awaiting-learning` — Retro written; waiting for /learn to absorb lessons.

| To | When | Gates | On exit (auto) |
|----|------|-------|----------------|
| `done` | All accepted learnings written | User confirmed the review table; Every accepted lesson written to its target file | sets `completed` |






## Plan editing

After modifying any plan's SPs or status, run:

```bash
booping render-sprints
```


## Routing Matrix

This matrix is the routing contract for /learn candidates. Every accepted learning lands in exactly one target — no duplicates across targets, no multi-target rows.

| Target | When to use | Lands at | Examples |
|--------|-------------|----------|----------|
| **Lesson** | Cross-framework principle reaching every skill — design heuristic, test discipline, IA rule. Concrete, short, with one example. | `lessons/{N}_<kebab>.md` | "Challenge code design by SOLID principles", "Use AAA in test cases", "Design skill template partials by information hierarchy" |
| **Skill extra instructions** | Tweak or extend a single skill's method (groom / develop / retro / learn / chat / install / help). | `_booping/skill_<skill>.md` | `skill_groom.md`, `skill_develop.md`, `skill_retro.md`, `skill_learn.md`, `skill_chat.md`, `skill_install.md`, `skill_help.md` |
| **Agent extra instructions** | Hook a single agent's behavior. Compact list. | `_booping/agent_<full-agent-name>.md` | `agent_booping-researcher.md`, `agent_booping-developer.md` |
| **Repository CLAUDE.md** | Project-fact aiding fresh-agent project understanding — layout path, CLI command, code-side convention. One-bullet additions; no paragraph rewrites. | `<repo>/CLAUDE.md` (the attached repo's file — **never** the global `~/.claude/CLAUDE.md` or any user-level scope) | (single canonical target — no filename variants) |

If a candidate would otherwise span two targets, decompose into two distinct rows; never duplicate the same rule across targets.

The skill infers the exact filename per candidate; the example lists above are validation aids, not full enumerations.




## Plans awaiting learning


status	sp	title	created	planned	completed	retro	path
awaiting-learning	11	Booping Global Config + home_dir	2026-07-22	20260722 11:24	20260722 12:02	retrospectives/20260722-seven-plan-retro.md	plans/20260722-booping-global-config-home-dir.md
awaiting-learning	35	Benchmark framework core (claude-booping-bench) + develop reference case	2026-07-09	20260708 20:17	20260708 21:51	retrospectives/20260722-seven-plan-retro.md	plans/20260709-benchmark-framework-core.md
awaiting-learning	36	Bench scoring v2, judge kind, groom cases, compare reports	2026-07-09	20260709 06:51	20260709 12:35	retrospectives/20260722-seven-plan-retro.md	plans/20260709-benchmark-judge-groom-case-reports.md
awaiting-learning	5	Install stops seeding CLAUDE.md-duplicating extensions	2026-06-29	20260628 18:11	20260628 18:28	retrospectives/20260722-seven-plan-retro.md	plans/20260629-install-stop-seeding-duplicate-extensions.md
awaiting-learning	17	Local Vault Directories	2026-06-28		20260628 15:33	retrospectives/20260722-seven-plan-retro.md	plans/20260628-local-vault-directories.md
awaiting-learning	17	Actualize documentation site and README against v0.1.5	2026-06-14	20260614 13:25	20260614 14:05	retrospectives/20260722-seven-plan-retro.md	plans/20260614-actualize-docs-site-and-readme.md
awaiting-learning	10	Retire cli-agent wrapper subsystem; adopt the plannotator global-agent pattern	2026-06-10	20260610 16:04	20260610 20:02	retrospectives/20260722-seven-plan-retro.md	plans/20260610-simplify-cli-delegation-to-global-agent.md
awaiting-learning	9	Plannotator-backed code-review surface (global, booping-decoupled)	2026-06-08	20260608 21:02	20260610	retrospectives/20260610-plannotator-code-review-surface.md	plans/20260608-plannotator-code-review-surface.md


## High-level workflow

1. Intake — resolve retro path, validate `awaiting-learning` status.
2. Extract candidates — inline, decomposed into atomic rules, routed via the matrix.
3. Update-vs-create sweep — filtered read of existing lessons and extensions.
4. Present unified review table — user accepts / rejects / adds rows.
5. Write accepted items — one pass per target type, no per-edit prompts.
6. Transition and commit.

## Single-location rule

Every accepted learning lands in **exactly one** target. If a candidate would otherwise span two targets, decompose it into two distinct rows in the review table — one row per target. The four targets, when-to-use tests, and example filenames live in the matrix rendered above; do not restate it elsewhere in this body.

---

## Phase 0 Intake

The current set of plans in `awaiting-learning` is listed in the [Plans awaiting learning](#plans-awaiting-learning) block above (rendered at skill load).

Resolve `$ARGUMENTS` to a retrospective file path.

**No `$ARGUMENTS`**: branch on the plans-list size.
- **Zero plans**: STOP with `No plans in awaiting-learning. Run /retro first to write a retrospective.`
- **Exactly one plan**: auto-select it (do not call `AskUserQuestion` — it requires ≥2 options).
- **Multiple plans**: present the list via `AskUserQuestion` (single-select; one option per plan).

Read the selected plan's `retro:` frontmatter to resolve the retrospective file.

**`$ARGUMENTS` provided**: treat it as the retrospective file path. Read it and follow its `plans:` frontmatter to the associated plan.

Validate the resolved plan's `status:` is `awaiting-learning`. On mismatch, STOP with this verbatim error:

> `/learn requires a plan in status 'awaiting-learning'; got '<current-status>' for <plan-path>. Use the list above to pick a candidate.`

## Phase 1 Extract candidates

Read the retrospective file and extract candidates for self-learning. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

Each candidate must satisfy:

- **Imperative form** — `do X` or `don't Y`. Not "X happened" or "X is good".
- **Single concern** — if you can't state the rule without "and", "plus", or `;`, split it.
- **No bare internal IDs** — when referring to an existing lesson, pair the ID with its title slug (e.g. `lesson 0004 (information-architecture-pattern)`, not just `lesson 0004`). Same for retro-internal codes; restate the underlying mechanic.
- **One sentence each in the report** — the review-table `Rule` and `Example` cells are one sentence each. The persisted lesson file may elaborate the rule into a compact paragraph after approval.

For each candidate, pick a target from the matrix rendered above.

## Phase 1.5 Update-vs-create sweep

Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

Read every lesson under `~/Claude/{project_name}/lessons/`, every extension file under `~/Claude/{project_name}/_booping/`, and the attached repo's `CLAUDE.md`. Skip silently when a directory is empty or a file is absent. Together these are the lookup set for the dup-check sweep.

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage at any target.
- `update existing at target X` — duplicate or refinement of a rule already written at `X`; the candidate becomes an update to `X`, not a fresh write at a different target.
- `conflict with existing at target X` — surface to the user in the review table as a visible flag.

## Phase 2 Present unified review table

Render the review table using the format defined in [review table format](${CLAUDE_PLUGIN_ROOT}/docs/learn_review_table.md). Use `AskUserQuestion` once to collect the user's accept / reject / add response.

Do not prompt per row. Do not inline the column-by-column documentation here — the template owns the format, the accept/reject syntax, and the user-added-row split rule.

## Phase 3 Write accepted items

After the table is accepted, write every accepted row in a single pass per target type. No per-edit `AskUserQuestion` calls; table acceptance is the consent.

Write paths use these templates (resolve each placeholder before writing):

- `lessons/{N}_<kebab>.md` — one rule per file. `{N}` is the next integer, computed from `ls lessons/` highest existing prefix + 1; body follows the lesson body shape inlined below.
- `_booping/skill_<name>.md` — per-skill extension in this project's vault.
- `_booping/agent_<name>.md` — per-agent extension in this project's vault.
- Repo `CLAUDE.md` — the attached repo's `<repo>/CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — /learn only touches this project's vault and the attached repo.


---
id: {{N}}                                      # monotonically-increasing integer; matches the filename prefix
title: {{One-sentence rule as a prescriptive statement}}
retro: retrospectives/YYYYMMDD-{{kebab-title}}.md   # the retro that surfaced this lesson
created: YYYY-MM-DD                            # date this lesson was extracted
---

{{The principle, imperative form. One compact paragraph; a short bullet list is fine when the rule has named sub-checks.}}

**Example**: {{One concrete case that illustrates the rule — what went wrong or right, in one or two lines. No motivation paragraphs, no multi-section "how to apply", no forbidden/edge-case lists. The retro carries the backstory; link it via `retro:` frontmatter.}}



## Phase 4 Transition + commit

Take the exit transition from the transitions table above.

If Phase 3 also wrote to the attached repo's `CLAUDE.md`, commit that separately in the repo working tree (the transition only touches the vault, never the attached repo):

```bash
cd <repo-path>
git add CLAUDE.md
git commit -m "docs(claude-md): <short summary>"
```

