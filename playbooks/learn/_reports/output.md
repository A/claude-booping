Turn retrospective findings into durable behavior changes routed to exactly one target each.

## Guidance

- The run's unit of work is a standalone retrospective, `retrospectives/{slug}.md`; its `plans:` frontmatter lists the plans it covers, for context only.
- The run workdir is the **vault root**; every `booping state` / `booping transition` call names `{vault}/retrospectives/{slug}.md` and `--playbook learn`, since the machine declares no `artifact:`.
- Plans are already `done` when learn runs and are never re-read for status or touched by it.
- Learn writes exactly two destinations: a rule record in this project's specs tier and the attached repo's `CLAUDE.md`.

## Single-location rule

Every accepted learning lands in **exactly one** destination. If a candidate would otherwise span both, decompose it into two distinct rows in the review table — one row per destination. The destinations and the rule target forms live below; do not restate them elsewhere.

## Targets

A rule is a `rule` record in this project's specs tier — `booping specs init --tier project` prints its root (format: `src/specs/README.md`). Its `targets:` frontmatter list is the rule's wiring to the things it must reach — exact names only, no globs, no wildcards, no negation — and its `brief:` is what reaches them:

1. `{playbook}` — the whole playbook. Target it when a rule affects several of its steps.
2. `{playbook}/{step}` — one step. Target it when a rule concerns that step alone.
3. `agent:{id}` — a core booping agent. Target it when a rule should guide the agent in everything it does.
4. `skill:{name}` — one skill. Target it when a rule tweaks or extends that skill's own method.

Several entries in one list are one rule, not a multi-target row. A rule with no valid target reaches nothing.

The table of contents below is the whole space. Pick the playbooks a candidate actually touches and fetch their targets — step summaries, rules already targeting them, addressable agents — with the command on each entry. Several names fetch in one call: `--set targets_for=a,b`.

Skills are not listed per playbook: `skill:playbook` is the only skill target.

### code-review

Review a confirmed scope — a sprint's plan, the latest commits, or a named target — through a detached findings pass, a human verdict on those findings, and an approved fix pass.

- Steps: `present`, `resolve`, `review`, `scope`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=code-review`

### develop

Execute a groomed plan by delegating every task to a worker agent, one milestone group at a time, then hand off a verified sprint to retro.

- Steps: `develop-loop`, `intake`, `provision`, `verify`, `wrap-up`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=develop`

### groom

Shape a feature, bug, or refactor into a specified, estimated, user-approved plan.

- Steps: `cross-review`, `draft-plan`, `intake`, `present`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=groom`

### learn

Turn retrospective findings into rules and repo CLAUDE.md facts, each routed to exactly one destination — extract atomic candidates, sweep for duplicates, confirm a review table with the user, write the accepted items, close the plans out.

- Steps: `dedup-sweep`, `extract-candidates`, `intake`, `review-table`, `transition`, `write`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=learn`

### makemigration

Author one new plugin-shipped vault migration — a `migrations/NNN_<slug>/migration.md` at the next id, in exactly the format `migrate` consumes.

- Steps: `survey`, `write-migration`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=makemigration`

### migrate

Bring a project vault up to date by applying every pending migration the plugin ships, in id order, on one up-front approval.

- Steps: `apply-migration`, `summarize`, `survey`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=migrate`

### playbook-authoring

Turn a procedure description into a working playbook — an interviewed brief, a confirmed step decomposition, an early manifest, and then per step a confirmed spec, test plan, fixtures, prompt, suite, and optimizer passes to green.

- Steps: `decompose`, `fixtures`, `interview`, `llm-tests`, `manifest`, `record-decision`, `regress-optimizer`, `smoke-optimizer`, `states`, `step-prompt`, `step-spec`, `step-suite`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=playbook-authoring`

### project-manager

The manager the user talks to — files what must outlive the session as an item and carries each through groom, develop, review and merge in the session's mode, supervised or autonomous.

- Steps: `intake`, `on-start`, `work`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=project-manager`

### retro

Generate a project- and plan-specific sprint retrospective — mine session logs, gather the user's raw feedback, triage issues, then save it and hand off to `/playbook learn`.

- Steps: `gather-feedback`, `intake`, `prepare`, `research-issues`, `save`, `synthesize`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=retro`

### setup

Take a repo from any starting state to a working booping project — machine-level config, then project-level vault — in one driven conversation.

- Steps: `setup-booping`, `setup-project`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=setup`

### specs

Work the project's specs records — set up a tier, settle values, record decisions, ideas and rules, review the set, sync it with the code and work its open items.

- Steps: `guide`
- Targets: `booping render playbooks/_partials/target_space.md --set targets_for=specs`

## Repo CLAUDE.md

The one non-rule destination: the attached repo's `CLAUDE.md`. Route a candidate here when it is a project fact that aids fresh-agent project understanding — a layout path, a CLI command, a code-side convention. One-bullet additions; no paragraph rewrites.


## Retrospectives awaiting learning

| Status | Title | Created | Primary plan | Path |
| --- | --- | --- | --- | --- |
| awaiting-learning | Session cleanup sweep | 1970-01-03 | plans/19700103-session-cleanup/index.md | retrospectives/197001031100_session-cleanup.md |





## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Rules

The following 1 rule(s) apply to this playbook. Never silently violate one; conflict → stop and flag. Read a rule's record when its brief is not enough.

- Write every accepted learning as a rule record in the project specs tier (targets, a self-sufficient one-or-two-line brief, Rule and Follows from) or as a repo CLAUDE.md bullet; never as a lesson file. [booping:rule/0001](${CLAUDE_PLUGIN_ROOT}/specs/rule/0001-lessons-are-rules.md)

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `intake` | — | Resolve the run's retrospective — from `$ARGUMENTS` as a `retrospectives/` path, or by picking one from the awaiting-learning list — validate it sits at learn's entry status, then read it in full and each plan in its `plans:` list for context, with the vault root as the workdir. | — |
| `extract-candidates` | `intake` | Decompose every retrospective insight into atomic candidates — one imperative rule per candidate, single concern, no bare internal IDs, one sentence per review-table cell — and route each to exactly one of the preamble's two destinations, holding the set in context for the sweep. | — |
| `dedup-sweep` | `extract-candidates` | Sweep every candidate against existing coverage — the rule records of the three specs tiers and the repo's `CLAUDE.md` — and record a per-candidate verdict: new, update-existing at the project rule already holding it, covered by a core or global rule, or a conflict flagged visibly for the review table. | — |
| `review-table` | `dedup-sweep` | Present the unified review table in the format the review-table doc owns — every candidate with its target and sweep verdict, conflicts flagged — and collect the user's accept / reject / add response asked once in prose, never per row; the recorded response is the run's consent to write. | — |
| `write` | `review-table` | Write every accepted row in one pass per destination — new rule records in the project specs tier at the number `booping specs next` hands out, in-place updates to the rule the sweep matched, one-line bullets into the repo's `CLAUDE.md` — with table acceptance as the sole consent and never a write outside the vault, its specs tier and the attached repo. | — |
| `transition` | `write` | Fire the exit transition — `booping transition {vault}/retrospectives/{slug}.md done --playbook learn` — whose hook commits the vault including the written rule records; commit any repo `CLAUDE.md` addition, and the rule records when the vault is outside the repo, separately in the repo working tree, then close on a report of items written per target. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping state {path} --playbook learn
```

### State: run

- Referenced by: outer graph
- Artifact: named per run — pass it as `{path}` on every call
- Initial status: `awaiting-learning`
- Advance: `booping transition {path} <to> --playbook learn`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `awaiting-learning` | `done` | every accepted row from the confirmed review table is written to its single target | user confirmed the review table — the accept / reject / add response is recorded; every accepted row written to its single target — rule records pass booping specs check |
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

The run workdir is the **vault root**, and the retrospective `{vault}/retrospectives/{slug}.md` is the file every state call names.

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
- **No bare internal IDs** — when referring to an existing rule or lesson, pair the ID with its title slug (e.g. `rule/0004 (questions-settled-in-grooming)`, not just `rule/0004`). Same for retro-internal codes; restate the underlying mechanic.
- **One sentence each in the report** — the review-table `Rule` and `Example` cells are one sentence each. The persisted rule record may elaborate the rule into a compact paragraph after approval.
- **Brief** — every rule candidate carries a `Brief`: one or two self-sufficient lines that reach the target, without restating what the agent checks or knows anyway (`src/specs/README.md`, rule frontmatter).

For each candidate, pick one of the two destinations named in the preamble — a rule record in the project specs tier, or a bullet in the repo's `CLAUDE.md`. When the destination is a rule, pick its `targets:` entries from the preamble's `## Targets` section.

Work the target space in two passes: read the table of contents there, shortlist the playbooks the candidates actually touch, then run the fetch command for exactly those (one call, names joined by commas) and pick entries from what comes back. Never guess a step name that the fetched targets did not show.

Nothing is presented to the user yet — the dedup sweep runs first, and the review table is the single surface where candidates appear.

## Step: Dedup Sweep
Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

The lookup set is:

- The rule records of all three specs tiers — `booping specs ls --tier {core,global,project} --type rule`, one call per tier; a tier that does not exist is skipped silently. Only the project tier is ever written.
- The attached repo's `CLAUDE.md` — the non-rule destination.

Skip silently when a file is absent.

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage anywhere in the lookup set.
- `update existing at rule/NNNN` — duplicate or refinement of a project rule; the candidate becomes an edit of that record in place.
- `covered by {ref}` — already covered by a core or global rule; shown in the review table and never written.
- `conflict with {ref}` — contradicts an existing rule; surface it in the review table as a visible flag.

## Step: Review Table
Render the review table in the [review table format](${CLAUDE_PLUGIN_ROOT}/docs/learn_review_table.md); a row's Targets cell draws on the preamble's `## Targets`.

Close the message by asking, in prose, for the user's accept / reject / add response over the whole table — never per row — then stop and wait; the user may ask back about a row before answering.

The confirmed response is what the exit edge's first gate names — record it. Nothing is written in this step.

## Step: Write
After the table is accepted, write every accepted row in a single pass per destination. No per-edit asks; table acceptance is the consent.

There are exactly two destinations (resolve each placeholder before writing):

- A rule record in this project's specs tier. Run `booping specs init --tier project` first — it creates the tier when absent, and its last stdout line is the tier root. Each new record is `{root}/rule/{NNNN}-{slug}.md`, `{NNNN}` from `booping specs next rule --tier project`, run per record; the record follows the rule record shape below. The `targets:` list is the row's Targets cell split on commas — one YAML list item per entry. Quote `title:`, `summary:` and `brief:`. A re-run after a partial failure reuses the record already written for a row — same `title` in the tier — instead of taking a new number.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault, its specs tier and the attached repo.

Rows by sweep verdict:

- `update existing at rule/NNNN` — edit that record in place, no fresh record, and bump `updated_at`. Extend, don't rewrite: add the row's content in the shape the record already uses, touch only prose the addition makes stale, and leave everything else — including the existing **Example** — byte-identical.
- `covered` — not written.
- `conflict with {ref}`, accepted — written as a new project rule whose `## Rule` opens with a `[clarify]` sentence naming `{ref}` as the departed rule and asking the owner for an ADR recording the departure.

After the last file is written, run `booping specs check --tier project`: an error on a written record is fixed in the record and the check re-run until it reports none — never by weakening the record's content.

The retrospective is the backstory, not the rule: however long the retro finding runs, the `## Rule` body stays a couple of sentences plus its one example. Never copy the retro's narrative, motivation, or timeline into a record.

The rule record shape:

```
---
type: rule
title: "{one-sentence rule as a prescriptive statement}"
summary: "{what the rule says and where it applies, one line, at most 200 characters}"
created_by: claude
created_at: {YYYY-MM-DD}                     # the run date
updated_at: {YYYY-MM-DD}                     # the run date; bumped on every in-place edit
status: accepted
targets:                                     # the row's Targets cell, one entry per item
  - {playbook}                               # or {playbook}/{step}, agent:{agent-id}, skill:{name}
brief: "{the row's Brief cell}"
sources: [{retrospective path relative to the repo root}]   # omit when the vault is outside the repo
---

## Rule

{The principle, imperative form. One compact paragraph; a short bullet list is fine when the rule has named sub-checks.}

**Example**: {One concrete case — what went wrong or right, in one or two lines.}

## Follows from

- [{value title}]({relative path to the value record}) — {vault inside the repo: the value a project or booping value names; vault outside: a fitting project-tier value}
- [Retro: {slug}]({relative path to retrospectives/{slug}.md}) — {vault inside the repo, no value names it: the retrospective}
- [clarify] Learnt from `retrospectives/{slug}.md` in the project vault, which a record outside the vault cannot link — see the [tier README](../README.md); link a value or settle the source.
  {vault outside the repo, no project-tier value fits: this exact item, the only one}
```

## Step: Transition
# Transition and commit

Everything accepted is on disk; nothing here re-drafts or re-opens the table.

## 1. Transition

Once every accepted item is written, advance the run per the `## State` section — naming `{vault}/retrospectives/{slug}.md`, the run's retrospective. The exit edge's hook commits that file together with the rule records this run wrote under the vault's `specs/`; when the vault is outside the repo the records live in the repo and are committed in §2. Plan frontmatter is never touched: the plans closed at develop and learn leaves them alone.

## 2. Repo commit

If `write` also wrote to the attached repo's `CLAUDE.md`, or — when the vault is outside the repo — wrote rule records under `{repo-path}/specs/`, commit those separately in the repo working tree (the transition only touches the vault, never the attached repo). Stage each written file by path, never `git add -A`:

```bash
cd {repo-path}
git add CLAUDE.md specs/rule/{NNNN-slug}.md
git commit -m "docs(specs): {short summary}"
```

Without rule records, stage `CLAUDE.md` alone and use `docs(claude-md): {short summary}`.

## 3. Closing report

Post in chat: the retrospective's path and its new status, then a table of the items written — each with its target path and whether it was a new write or an in-place update — and the rejected-row count. No `/playbook learn` re-offer; the retrospective is done.

## Replay

A replay that finds the accepted items already written re-fires nothing it does not need: a retrospective still at the entry status takes the transition alone; one already past it is only re-reported, with the transition line reading `already at {status} — no transition taken`.
