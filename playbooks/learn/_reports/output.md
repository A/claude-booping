Turn retrospective findings into durable behavior changes routed to exactly one target each.

## Guidance

- The run's unit of work is a standalone retrospective, `retrospectives/{slug}.md` in `awaiting-learning` status; its `plans:` frontmatter lists the plans it covers, for context only.
- The run workdir is the **vault root**; every `booping playbook-state` / `booping playbook-transition` call passes `--target retrospectives/{slug}.md`, since the machine declares no `artifact:`.
- Plans are already `done` when learn runs and are never re-read for status or touched by it.
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


## Retrospectives awaiting learning

| Status | Title | Created | Primary plan | Path |
| --- | --- | --- | --- | --- |
| awaiting-learning | Session cleanup sweep | 1970-01-03 | plans/19700103-session-cleanup/index.md | retrospectives/197001031100_session-cleanup.md |





## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `intake` | — | Resolve the run's retrospective — from `$ARGUMENTS` as a `retrospectives/` path, or by picking one from the awaiting-learning list — validate it sits at learn's entry status, then read it in full and each plan in its `plans:` list for context, with the vault root as the workdir. | — |
| `extract-candidates` | `intake` | Decompose every retrospective insight into atomic candidates — one imperative rule per candidate, single concern, no bare internal IDs, one sentence per review-table cell — and route each to exactly one target from the preamble's routing matrix, holding the set in context for the sweep. | — |
| `dedup-sweep` | `extract-candidates` | Sweep every candidate against existing coverage — the vault's lessons, the `_booping/` extensions, and the repo's `CLAUDE.md` — and record a per-candidate verdict: new, update-existing at the target already holding the rule, or a conflict flagged visibly for the review table. | — |
| `review-table` | `dedup-sweep` | Present the unified review table in the format the review-table doc owns — every candidate with its target and sweep verdict, conflicts flagged — and collect the user's accept / reject / add response in a single `AskUserQuestion` call, never per row; the recorded response is the run's consent to write. | — |
| `write` | `review-table` | Write every accepted row in one pass per target type — new lesson files at the next free number, in-place updates to the file the sweep matched, `_booping/` extension edits, one-line bullets into the repo's `CLAUDE.md` — with table acceptance as the sole consent and never a write outside the vault and the attached repo. | — |
| `transition` | `write` | Fire the exit transition from the vault root — `booping playbook-transition learn done --target retrospectives/{slug}.md` — whose hook commits the vault including the written lessons and extensions; commit any repo `CLAUDE.md` addition separately in the repo working tree, then close on a report of items written per target. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state learn --workdir <run workdir> --target {path}
```

### State: run

- Referenced by: outer graph
- Artifact: named per run — pass `--target {path}` (relative to the run workdir) on every call
- Initial status: `awaiting-learning`
- Advance: `booping playbook-transition learn <to> --target {path} --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `awaiting-learning` | `done` | every accepted row from the confirmed review table is written to its single target | user confirmed the review table — the accept / reject / add response is recorded; every accepted lesson written to its target file |
| `done` | *(terminal)* | — | — |

## Step: Intake
The current set of candidate retrospectives is listed in the **Retrospectives awaiting learning** table of the preamble.

Resolve `$ARGUMENTS` to a retrospective file path under `retrospectives/`.

**`$ARGUMENTS` provided**: treat it as that path — no lookup through any plan.

**No `$ARGUMENTS`**: branch on the table's size.

- **Zero rows**: STOP with `No retrospectives at this run's entry status. Run the retro playbook first to write one.`
- **Exactly one row**: auto-select it (do not call `AskUserQuestion` — it requires ≥2 options).
- **Multiple rows**: present them via `AskUserQuestion` (single-select; one option per retrospective).

Validate the selected retrospective's `status:` is the status the `## State` section names as this run's entry. On mismatch, STOP with this verbatim error:

> `learn playbook requires a retrospective in status '{entry-status}'; got '{current-status}' for {retro-path}. Use the list above to pick a candidate.`

## Workdir and covered plans

The run workdir is the **vault root**, and the retrospective is addressed by `--target retrospectives/{slug}.md` on every state call.

Read the retrospective in full — it is the sole source the run extracts from. Read each plan in its `plans:` list for context only: scope, decisions on record, what the retro's findings refer to. Plan `status:` is neither checked nor written here.

## The report — posted in chat

```markdown
## Learn intake

Retrospective: {path}
Plans covered: {a table with columns: plan path, goal verdict from the retro's `goal_verdicts:` when present}
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

## Targets

Every lesson names its targets in its `targets:` frontmatter list — exact names only, no globs, no wildcards, no negation:

1. `{playbook}` — the whole playbook. Target it when a lesson affects several of its steps.
2. `{playbook}/{step}` — one step. Target it when a lesson concerns that step alone.
3. `agent:{id}` — a core booping agent (researcher, developer). Target it when a lesson should guide the agent in everything it does.

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

- `_lessons/{N}_{kebab}.md` — one rule per file, in this project's vault. `{N}` is the next integer, computed from `ls _lessons/` highest existing prefix + 1 (`1` when the directory is empty or absent — create it); body follows the lesson body shape inlined below. The `targets:` list is the row's Targets cell verbatim, one entry per line. The `retro:` frontmatter points at the run's retrospective, `retrospectives/{slug}.md`.
- `_booping/skill_{name}.md` — per-skill extension in this project's vault.
- `_booping/agent_{name}.md` — per-agent extension in this project's vault.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault and the attached repo.

An `update existing at target X` row edits the file already holding the rule in place — no fresh file at another target. Extend, don't rewrite: add the row's content in the shape the file already uses, touch only prose the addition makes stale (a count in the title, a sibling reference), and leave everything else — including the existing **Example** — byte-identical.

The retrospective is the backstory, not the lesson: however long the retro finding runs, the persisted lesson body stays a couple of sentences plus its one example. Never copy the retro's narrative, motivation, or timeline into a lesson.


---
id: {{N}}                                      # monotonically-increasing integer; matches the filename prefix
title: {{One-sentence rule as a prescriptive statement}}
targets:                                       # what this lesson is injected into; exact names only, no globs
  - {{playbook}}                               # or {{playbook}}/{{step}}, or agent:{{agent-id}}
retro: retrospectives/{{slug}}.md              # the retro that surfaced this lesson
created: YYYY-MM-DD                            # date this lesson was extracted
---

{{The principle, imperative form. One compact paragraph; a short bullet list is fine when the rule has named sub-checks.}}

**Example**: {{One concrete case that illustrates the rule — what went wrong or right, in one or two lines. No motivation paragraphs, no multi-section "how to apply", no forbidden/edge-case lists. The retro carries the backstory; link it via `retro:` frontmatter.}}

## Step: Transition
# Transition and commit

Everything accepted is on disk; nothing here re-drafts or re-opens the table.

## 1. Transition

Once every accepted item is written, advance the run per the `## State` section — from the vault root, passing `--target retrospectives/{slug}.md` for the run's retrospective. The exit edge's hook commits that file together with the `_lessons/` and `_booping/` files this run wrote. Plan frontmatter is never touched: the plans closed at develop and learn leaves them alone.

## 2. Repo `CLAUDE.md` commit

If `write` also wrote to the attached repo's `CLAUDE.md`, commit that separately in the repo working tree (the transition only touches the vault, never the attached repo):

```bash
cd {repo-path}
git add CLAUDE.md
git commit -m "docs(claude-md): {short summary}"
```

## 3. Closing report

Post in chat: the retrospective's path and its new status, then a table of the items written — each with its target path and whether it was a new write or an in-place update — and the rejected-row count. No `/playbook learn` re-offer; the retrospective is done.

## Replay

A replay that finds the accepted items already written re-fires nothing it does not need: a retrospective still at the entry status takes the transition alone; one already past it is only re-reported, with the transition line reading `already at {status} — no transition taken`.
