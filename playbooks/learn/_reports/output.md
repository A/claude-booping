Turn retrospective findings into durable behavior changes routed to exactly one target each.

## Guidance

- Learn handles plans in `awaiting-learning` status.
- The retrospective lives at `plans/{primary-slug}/retro.md`; its `plans:` frontmatter lists the working set the run covers, and the plan whose directory holds it is the **primary**.
- The run workdir is the primary plan's directory `plans/{primary-slug}/` — `index.md` there is the run artifact.
- Learn writes only to this project's vault (`_lessons/`, `_booping/`) and the attached repo's `CLAUDE.md` — **never** the global `~/.claude/CLAUDE.md` or any user-level scope.

## Single-location rule

Every accepted learning lands in **exactly one** target. If a candidate would otherwise span two targets, decompose it into two distinct rows in the review table — one row per target. The four targets, when-to-use tests, and example filenames live in the routing matrix below; do not restate it elsewhere.

## Routing Matrix

This matrix is the routing contract for learn candidates. Every accepted learning lands in exactly one target — no duplicates across targets, no multi-target rows.

| Target | When to use | Lands at | Examples |
|--------|-------------|----------|----------|
| **Lesson** | Behavior change reaching one or more playbooks, playbook steps, or agents — design heuristic, test discipline, IA rule. Concrete, short, with one example. Carries a `targets:` list; a lesson with no valid target reaches nothing. | `_lessons/{N}_{kebab}.md` | "Challenge code design by SOLID principles", "Use AAA in test cases", "Design skill template partials by information hierarchy" |
| **Skill extra instructions** | Tweak or extend a single skill's method (code-review / playbook). | `_booping/skill_{skill}.md` | `skill_code-review.md`, `skill_playbook.md` |
| **Agent extra instructions** | Hook a single agent's behavior. Compact list. | `_booping/agent_{full-agent-name}.md` | `agent_booping-researcher.md`, `agent_booping-developer.md` |
| **Repository CLAUDE.md** | Project-fact aiding fresh-agent project understanding — layout path, CLI command, code-side convention. One-bullet additions; no paragraph rewrites. | `{repo}/CLAUDE.md` (the attached repo's file — **never** the global `~/.claude/CLAUDE.md` or any user-level scope) | (single canonical target — no filename variants) |

If a candidate would otherwise span two targets, decompose into two distinct rows; never duplicate the same rule across targets. A lesson is the one target that carries its own routing: it lands in this project's `_lessons/` and its `targets:` list wires it to the playbooks, steps and agents it applies to — several entries in one list are one row, not a multi-target row.

The skill infers the exact filename per candidate; the example lists above are validation aids, not full enumerations.


## Plans awaiting learning

| Status | SP | Title | Created | Completed | Retro | Path |
| --- | --- | --- | --- | --- | --- | --- |
| awaiting-learning | 3 | Session cleanup sweep | 1970-01-03 | 19700103 11:00 | plans/19700103-session-cleanup/retro.md | plans/19700103-session-cleanup/index.md |





## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `intake` | — | Resolve the run's retrospective — from `$ARGUMENTS` as a retro path, or by picking a plan from the awaiting-learning list and following its `retro:` frontmatter — settle the working set from the retro's `plans:` list with the primary plan's directory as the workdir, validate every plan sits at learn's entry status, then read the retrospective in full and each plan for context. | — |
| `extract-candidates` | `intake` | Decompose every retrospective insight into atomic candidates — one imperative rule per candidate, single concern, no bare internal IDs, one sentence per review-table cell — and route each to exactly one target from the preamble's routing matrix, holding the set in context for the sweep. | — |
| `dedup-sweep` | `extract-candidates` | Sweep every candidate against existing coverage — the vault's lessons, the `_booping/` extensions, and the repo's `CLAUDE.md` — and record a per-candidate verdict: new, update-existing at the target already holding the rule, or a conflict flagged visibly for the review table. | — |
| `review-table` | `dedup-sweep` | Present the unified review table in the format the review-table doc owns — every candidate with its target and sweep verdict, conflicts flagged — and collect the user's accept / reject / add response in a single `AskUserQuestion` call, never per row; the recorded response is the run's consent to write. | — |
| `write` | `review-table` | Write every accepted row in one pass per target type — new lesson files at the next free number, in-place updates to the file the sweep matched, `_booping/` extension edits, one-line bullets into the repo's `CLAUDE.md` — with table acceptance as the sole consent and never a write outside the vault and the attached repo. | — |
| `transition` | `write` | Fire the exit transition from the workdir — `booping playbook-transition learn done` — whose hook moves every sibling plan to `done` and commits the vault including the written lessons and extensions; commit any repo `CLAUDE.md` addition separately in the repo working tree, then close on a report of items written per target. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state learn --workdir <run workdir>
```

### State: run

- Referenced by: outer graph
- Artifact: `index.md` (relative to the run workdir)
- Initial status: `awaiting-learning`
- Advance: `booping playbook-transition learn <to> --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `awaiting-learning` | `done` | every accepted row from the confirmed review table is written to its single target | user confirmed the review table — the accept / reject / add response is recorded; every accepted lesson written to its target file |
| `done` | *(terminal)* | — | — |

## Step: Intake
The current set of candidate plans is listed in the **Plans awaiting learning** table of the preamble.

Resolve `$ARGUMENTS` to a retrospective file path.

**No `$ARGUMENTS`**: branch on the plans-list size.

- **Zero plans**: STOP with `No plans at this run's entry status. Run the retro playbook first to write a retrospective.`
- **Exactly one plan**: auto-select it (do not call `AskUserQuestion` — it requires ≥2 options).
- **Multiple plans**: present the list via `AskUserQuestion` (single-select; one option per plan). Plans sharing one `retro:` value are one working set — offer the set as a single option, not one option per sibling.

Read the selected plan's `retro:` frontmatter to resolve the retrospective file.

**`$ARGUMENTS` provided**: treat it as the retrospective file path. Read it and follow its `plans:` frontmatter to the associated plans.

## Working set and workdir

The retrospective's `plans:` frontmatter is the **working set** — every plan this run absorbs lessons for. The plan whose directory holds the retrospective is the **primary**, and its directory `plans/{primary-slug}/` is the run workdir. A retrospective without a `plans:` list covers only the plan it was resolved from.

Validate every working-set plan's `status:` is the status the `## State` section names as this run's entry. On mismatch, STOP with this verbatim error:

> `learn playbook requires a plan in status '{entry-status}'; got '{current-status}' for {plan-path}. Use the list above to pick a candidate.`

Read the retrospective in full — it is the sole source the run extracts from. Read each working-set plan for context only: scope, decisions on record, what the retro's findings refer to.

## The report — posted in chat

```markdown
## Learn intake

Retrospective: {path}
Working set: {a table with columns: plan path, status, goal verdict from the retro's `goal_verdicts:` when present}
```

## Step: Extract Candidates
Extract candidates for self-learning from the retrospective read at `intake`. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

Each candidate must satisfy:

- **Imperative form** — `do X` or `don't Y`. Not "X happened" or "X is good".
- **Single concern** — if you can't state the rule without "and", "plus", or `;`, split it.
- **No bare internal IDs** — when referring to an existing lesson, pair the ID with its title slug (e.g. `lesson 0004 (information-architecture-pattern)`, not just `lesson 0004`). Same for retro-internal codes; restate the underlying mechanic.
- **One sentence each in the report** — the review-table `Rule` and `Example` cells are one sentence each. The persisted lesson file may elaborate the rule into a compact paragraph after approval.

For each candidate, pick a target from the routing matrix in the preamble. When the target is a lesson, pick its `targets:` entries from the target space below — the routing matrix decides *which kind of file* the candidate lands in, the target space decides *what the lesson is wired to*.

Work the target space in two passes: read the table of contents, shortlist the playbooks the candidates actually touch, then run the fetch command for exactly those (one call, names joined by commas) and pick entries from what comes back. Never guess a step name that the fetched targets did not show.

Nothing is presented to the user yet — the dedup sweep runs first, and the review table is the single surface where candidates appear.

## Lesson Target Space

Every lesson targets exactly one entry from the target space, written into its `targets:` frontmatter list. Entry forms — exact names only, no globs, no wildcards, no negation:

- `{playbook}` — the whole playbook, e.g. `code-review`
- `{playbook}/{step}` — one step of it, e.g. `code-review/present`
- `agent:{id}` — one agent, e.g. `agent:booping-developer`

The table of contents below is the whole space. Pick the playbooks a candidate actually touches and fetch their targets — step summaries, lessons already targeting them, addressable agents — with the command on each entry. Several names fetch in one call: `--set targets_for=a,b`.

### code-review

Review a confirmed scope — a sprint's plan, the latest commits, or a named target — through a detached findings pass, a human verdict on those findings, and an approved fix pass.

- Steps: `present`, `resolve`, `review`, `scope`
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for=code-review`

### develop

Execute a groomed plan by delegating every task to a worker agent, one milestone group at a time, then hand off a verified sprint to retro.

- Steps: `develop-loop`, `intake`, `provision`, `verify`, `wrap-up`
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for=develop`

### groom

Shape a feature, bug, or refactor into a specified, estimated, user-approved plan.

- Steps: `cross-review`, `draft-plan`, `intake`, `present`, `research-codebase`, `research-web`
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for=groom`

### learn

Turn retrospective findings into durable behavior changes routed to exactly one target each — extract atomic candidates, sweep for duplicates, confirm a review table with the user, write the accepted items, close the plans out.

- Steps: `dedup-sweep`, `extract-candidates`, `intake`, `review-table`, `transition`, `write`
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for=learn`

### migrate

Bring a project vault up to date by applying every pending migration the plugin ships, in id order, on one up-front approval.

- Steps: `apply-migration`, `summarize`, `survey`
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for=migrate`

### playbook-authoring

Turn a procedure description into a working playbook — an interviewed brief, a confirmed step decomposition, an early manifest, and then per step a confirmed spec, test plan, fixtures, prompt, suite, and optimizer passes to green.

- Steps: `decompose`, `fixtures`, `interview`, `llm-tests`, `manifest`, `record-decision`, `regress-optimizer`, `smoke-optimizer`, `states`, `step-prompt`, `step-spec`, `step-suite`
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for=playbook-authoring`

### retro

Generate a project- and plan-specific sprint retrospective — mine session logs, gather the user's raw feedback, triage issues, then save it and hand off to `/playbook learn`.

- Steps: `gather-feedback`, `intake`, `prepare`, `research-issues`, `save`, `synthesize`
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for=retro`

### setup

Take a repo from any starting state to a working booping project — machine-level config, then project-level vault — in one driven conversation.

- Steps: `setup-booping`, `setup-project`
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for=setup`

## Step: Dedup Sweep
Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

The lookup set is:

- `{home_dir}/_lessons/` — global lessons, shared across projects (the vault-home base is `booping config-get home_dir`). Read-only here; a duplicate found in it still becomes an update to that file.
- `{vault}/_lessons/` — this project's lessons, shadowing a global lesson of the same filename. The only root this run writes new lessons into.
- The vault's `_booping/` extension files and the attached repo's `CLAUDE.md` — the non-lesson targets.
- The vault's legacy `lessons/`, if it still exists — **read-only, duplicate context only**. Never write here and never route a row to it; a candidate already covered there is reported as such and, if accepted, written into `{vault}/_lessons/` with `targets:`.

Skip silently when a directory is empty or a file is absent.

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage at any target.
- `update existing at target X` — duplicate or refinement of a rule already written at `X`; the candidate becomes an update to `X`, not a fresh write at a different target.
- `conflict with existing at target X` — surface to the user in the review table as a visible flag.

## Step: Review Table
Render the review table using the format defined in [review table format](${CLAUDE_PLUGIN_ROOT}/docs/learn_review_table.md), with one added column: **Targets**.

Every row carries a Targets cell — comma-separated entries from the target space rendered in `extract-candidates`, using the three entry forms and exact names only, no globs or wildcards:

- `{playbook}` — the lesson applies to the whole playbook
- `{playbook}/{step}` — it applies to one step of it
- `agent:{id}` — it applies to one agent

A `lesson` row's Targets cell is written verbatim into the file's `targets:` frontmatter list, so it must be non-empty. Rows of any other type carry `—`: the file path is their routing.

Use `AskUserQuestion` once to collect the user's accept / reject / add response.

Do not prompt per row. Do not inline the column-by-column documentation here — the template owns the format, the accept/reject syntax, and the user-added-row split rule.

The confirmed response is what the exit edge's first gate names — record it. Nothing is written in this step.

## Step: Write
After the table is accepted, write every accepted row in a single pass per target type. No per-edit `AskUserQuestion` calls; table acceptance is the consent.

Write paths use these templates (resolve each placeholder before writing):

- `_lessons/{N}_{kebab}.md` — one rule per file, in this project's vault. `{N}` is the next integer, computed from `ls _lessons/` highest existing prefix + 1 (`1` when the directory is empty or absent — create it); body follows the lesson body shape inlined below. The `targets:` list is the row's Targets cell verbatim, one entry per line. The `retro:` frontmatter points at the run's retrospective, `plans/{primary-slug}/retro.md`.
- `_booping/skill_{name}.md` — per-skill extension in this project's vault.
- `_booping/agent_{name}.md` — per-agent extension in this project's vault.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault and the attached repo.

An `update existing at target X` row edits the file already holding the rule in place — no fresh file at another target.


---
id: {{N}}                                      # monotonically-increasing integer; matches the filename prefix
title: {{One-sentence rule as a prescriptive statement}}
targets:                                       # what this lesson is injected into; exact names only, no globs
  - {{playbook}}                               # or {{playbook}}/{{step}}, or agent:{{agent-id}}
retro: retrospectives/YYYYMMDD-{{kebab-title}}.md   # the retro that surfaced this lesson
created: YYYY-MM-DD                            # date this lesson was extracted
---

{{The principle, imperative form. One compact paragraph; a short bullet list is fine when the rule has named sub-checks.}}

**Example**: {{One concrete case that illustrates the rule — what went wrong or right, in one or two lines. No motivation paragraphs, no multi-section "how to apply", no forbidden/edge-case lists. The retro carries the backstory; link it via `retro:` frontmatter.}}

## Step: Transition
# Transition and commit

Everything accepted is on disk; nothing here re-drafts or re-opens the table.

## 1. Transition

Once every accepted item is written, advance the run per the `## State` section, from the workdir. The exit edge's hooks carry the sibling plans and commit them together with the `_lessons/` and `_booping/` files this run wrote; nothing here hand-edits plan frontmatter.

## 2. Repo `CLAUDE.md` commit

If `write` also wrote to the attached repo's `CLAUDE.md`, commit that separately in the repo working tree (the transition only touches the vault, never the attached repo):

```bash
cd {repo-path}
git add CLAUDE.md
git commit -m "docs(claude-md): {short summary}"
```

## 3. Closing report

Post in chat: the plans closed with their new statuses, then a table of the items written — each with its target path and whether it was a new write or an in-place update — and the rejected-row count. No `/playbook learn` re-offer; the working set is done.

## Replay

A replay that finds the accepted items already written re-fires nothing it does not need: a plan still at the entry status takes the transition alone; a plan already past it is only re-reported, with the transition line reading `already at {status} — no transition taken`.
