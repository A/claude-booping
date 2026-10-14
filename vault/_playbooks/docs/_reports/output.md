A run ends with the project's documentation surfaces matched to the current state of the repo:
the spec set current, a reviewed run record listing what changed and where it landed, and every
affected surface rewritten in the tone and depth its audience needs. Steps already satisfied by
a current file are skipped rather than redone.

## Guidance

- Date & time: 2026-10-14
- The run workdir is `{vault}/docs/`; run records live under its `_runs/` subdirectory, never
  loose in `docs/` beside real documentation. Every `booping playbook-state` / `booping
  playbook-transition` call passes `--workdir {vault}/docs --target
  _runs/{YYYYMMDDHHmm}-{title}.md`, since the machine declares no `artifact:`.
- The spec set is the project specs tier records: the value records
  (`core.docs_playbook.queries.values`), reference/0001 (audience), reference/0002 (glossary —
  canonical terms every record and destination uses), reference/0003 (surfaces) and the story
  records, whose feature index is `core.docs_playbook.queries.features`, rendered and never
  stored. It is refreshed, never rebuilt. `{vault}/docs/documented.md` is the ledger of
  already-documented work; `research` reads it to surface only the delivered items still missing
  from it.
- A step that edits a record bumps its `updated_at` and never sets `reviewed` — that is the
  owner's (`src/specs/README.md`, Frontmatter); what its source does not settle it marks
  `[clarify]` / `[unknown]` per rule/0002.
- The spec set is **both this run's context and one of its targets** — reference/0003 lists it as
  the surface for Claude itself, so load it at every step that resolves audience or destination,
  `sync-specs` keeps it current from the confirmed change table before `targeting` reads it, and
  no destination is written from a set the same run found stale.
- Source files are never edited: every destination the `update` loop writes is markdown.
  Code-level documentation stays with `develop`.
- Roles drive tone in both `research` and `write` — a business-facing surface never gets
  implementation detail a technical one would carry.

## The `update` loop

`update` repeats once per row of the confirmed targeting plan — one instance per destination
document, `write` → `compact` → `verify` — and instances may run in parallel, but no two ever
touch the same file. The loop carries no state machine of its own: per-row progress (pending →
written → compacted → verified) is a column on the targeting-plan table in the run record body,
resumed from `updating` the same way `develop` resumes its milestone loop from plan-body
checkboxes, since a destination document cannot carry frontmatter.

## Runner-held state

Every step reports back what the runner must carry forward, never the raw reading behind it:
file paths written or to write next, the confirmed change table, the targeting plan, and the
changed/updated set. Heavy reads — the delivered-work sweep in `research`, the sub-agent writes
in the spec-set and `update` waves — stay in their sub-agent; only the summary returns.

Eval runs are proposed, never launched — the user triggers them.

## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `survey` | — | Report which spec records are missing or incomplete, with their open marks, and which delivered work is not yet documented, and open the run record carrying both — the run's cheap opening, settled before a single expensive read happens. | Confirm the run scope — which spec records to refresh, which delivered items to cover. The gate is the runner's, taken after the return lands and asked against the run record's two tables; a `present` spec record may still be picked for a refresh, and an undocumented item may still be dropped from scope |
| `briefing` | `survey` | Write the run record's briefing from the value records and the audience record — what the project is, who it serves, where it is heading — and name the vision drift against the previous run's. | Present the briefing and stop — the user confirms what the project is, who it serves and where it is heading. A named vision shift must be acknowledged in the answer; silence never counts |
| `roles` | `briefing` | Characterise the audiences that read this project's documentation — per role who it is, what it comes for, its depth ceiling, what is withheld, its voice and what it reads — refreshed in the `## Facts` of the audience record reference/0001, the audience layer every later step resolves "how deep, in what voice, for whom" against. | Confirm or refine — presented together with surfaces. Hold it at `awaiting-roles-targets-confirm`, presenting the audience record reference/0001 and the surfaces record reference/0003 in one pass; a refinement re-enters `spec-building`. The step itself never stops for the user |
| `targets` | `briefing` | Enumerate the repo's markdown documentation surfaces — plus the `CHANGELOG.md` this playbook introduces and the spec set the playbook reads — one fact each with its path, audience, depth ceiling and conventions, refreshed in the `## Facts` of the surfaces record reference/0003 and closed by a "Not surfaces" fact; return the surfaces so the runner gates on them without opening the record. | — |
| `research` | `roles`, `targets` | Read each in-scope delivered item in its own sub-agent and assemble the typed change table — one row per user-visible change, tied to the spec record it moves — written to the run record as the contract `sync-specs`, `targeting` and `record` all work from. | Extend, refine and confirm the change table, presented in chat from the `## Changes` section just written. An extension naming items that still have to be read sends the run back to this step, which reads only the added items and rewrites the section; confirmation is explicit — silence never counts, and the confirming edge stamps `changes_reviewed_at:` on the run record |
| `sync-specs` | `research` | Fold the confirmed change table into the spec records — value, audience, surfaces, glossary and story records — editing in place only what a row settles and marking what it does not, then running `booping specs check`, so every later step resolves "what does this project ship, for whom, at what depth" against current records. | — |
| `targeting` | `sync-specs` | Decide per confirmed change which role × surface combinations must be written and what each one must say — one row per destination document on the run record, which is both the authorisation every later write runs on and the loop's unit of parallelism. | Confirm the targeting plan before anything is written — this gate always fires, at every severity the run may be driven with. Hold it at `awaiting-targeting-confirm`, presenting the rows from the return; a rework answer — a destination, an assignment, or what a row must say — re-enters `targeting` over the same inputs plus the correction |
| `update` *(subgraph)* | `targeting` | once per destination document in the confirmed targeting plan; instances may run in parallel | — |
| `write` *(in update)* | — | Fold one targeting-plan row's assigned changes into its single destination markdown document — rewriting the sections that already own them, at the depth its roles allow, as a current-state snapshot with legacy narration removed — and return what landed where so the runner never opens the file. | — |
| `compact` *(in update)* | `write` | Split one freshly written destination document by section, compact each section twice — radically and gently — and merge per section, so filler goes and every clause the targeting row required still stands. | — |
| `verify` *(in update)* | `compact` | Check one destination document in a single pass against three failure modes — a claim the repo does not support, a passage past its audience's depth ceiling, and prose narrating what the project used to be — correcting each surgically in place while reading source read-only, and returning the findings source could not settle for the runner to record. | — |
| `changelog` | `update` | Write this run's user-visible entry in the repo's `CHANGELOG.md`, seeding the file when it is absent — one past-tense bullet per shipped change in the grammar the history already uses, with every non-user-visible row reported as omitted so the confirmed table is fully accounted for. | — |
| `record` | `changelog` | Close the run record — a `## Landed` table of every destination the loop touched plus the history row, and a `documented:` frontmatter list of the work items every one of whose changes is accounted for, so a dropped destination withholds its item and the next survey resurfaces it. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state docs --workdir <run workdir> --target {path}
```

### State: run

- Referenced by: outer graph
- Artifact: named per run — pass `--target {path}` (relative to the run workdir) on every call
- Initial status: `surveying`
- Advance: `booping playbook-transition docs <to> --target {path} --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `surveying` | `awaiting-scope-confirm` | survey opened the run record with the spec-set state and the undocumented set | — |
| `surveying` | `cancelled` | the user cancels the run | — |
| `awaiting-scope-confirm` | `surveying` | the user's scope answer needs a fresh survey — a different item range, or spec records the survey did not inspect | — |
| `awaiting-scope-confirm` | `briefing` | the user settled which spec records to refresh and which delivered items to cover, and at least one spec record needs work | explicit user confirmation captured — silence never counts |
| `awaiting-scope-confirm` | `researching` | the user settled the scope and every spec record is present and current — the spec waves are skipped | explicit user confirmation captured; the survey found no missing or incomplete spec record |
| `awaiting-scope-confirm` | `done` | the survey found nothing to do — spec set current, undocumented set empty — and the user closed the run | explicit user confirmation captured; the undocumented set is empty |
| `awaiting-scope-confirm` | `cancelled` | the user cancels the run | — |
| `briefing` | `awaiting-briefing-confirm` | briefing wrote the run record's `## Briefing` section, naming any vision shift against the previous run record's | — |
| `briefing` | `cancelled` | the user cancels the run | — |
| `awaiting-briefing-confirm` | `briefing` | the user reworks the briefing — what the project is, who it serves, where it is heading | — |
| `awaiting-briefing-confirm` | `spec-building` | the user confirms the briefing | explicit user confirmation captured — a vision shift is acknowledged in the answer, silence never counts |
| `awaiting-briefing-confirm` | `cancelled` | the user cancels the run | — |
| `spec-building` | `awaiting-roles-targets-confirm` | roles and targets each refreshed their record | — |
| `spec-building` | `cancelled` | the user cancels the run | — |
| `awaiting-roles-targets-confirm` | `spec-building` | the user wants roles or surfaces refined | — |
| `awaiting-roles-targets-confirm` | `researching` | the user confirms roles and surfaces, presented together | explicit user confirmation captured — silence never counts |
| `awaiting-roles-targets-confirm` | `cancelled` | the user cancels the run | — |
| `researching` | `awaiting-changes-confirm` | the per-item sub-agents returned and the typed change table is posted in chat | every in-scope delivered item carries a row, each typed |
| `researching` | `cancelled` | the user cancels the run | — |
| `awaiting-changes-confirm` | `researching` | the user adds items that still have to be read | — |
| `awaiting-changes-confirm` | `syncing-specs` | the user confirms the change table, extensions and refinements folded in | explicit user confirmation captured — silence never counts |
| `awaiting-changes-confirm` | `cancelled` | the user cancels the run | — |
| `syncing-specs` | `targeting` | sync-specs folded the confirmed table into the spec records | — |
| `syncing-specs` | `cancelled` | the user cancels the run | — |
| `targeting` | `awaiting-targeting-confirm` | targeting wrote the role × surface plan to the run record | one row per destination document, no two rows naming the same file |
| `targeting` | `cancelled` | the user cancels the run | — |
| `awaiting-targeting-confirm` | `targeting` | the user reworks rows — a destination, its assigned changes, or what each must say | — |
| `awaiting-targeting-confirm` | `updating` | the user confirms the targeting plan — this gate always fires | explicit user confirmation captured — silence never counts |
| `awaiting-targeting-confirm` | `cancelled` | the user cancels the run | — |
| `updating` | `writing-changelog` | every targeting-plan row left the loop | each row's progress column reads verified, or dropped with its reason |
| `updating` | `cancelled` | the user cancels the run | — |
| `writing-changelog` | `recording` | the run's entry is written to the repo's `CHANGELOG.md`, seeded if it was absent | — |
| `writing-changelog` | `cancelled` | the user cancels the run | — |
| `recording` | `done` | record closed the run record — what landed where — and listed the work items now documented | the run record's `documented:` list names every covered work item, and its landed table every destination written — `close-documented` reads the list |
| `recording` | `cancelled` | the user cancels the run | — |
| `done` | *(terminal)* | — | — |
| `cancelled` | *(terminal)* | — | — |

## Step: Survey

Report which spec records are missing or incomplete, with their open marks, and which delivered work is not yet documented, and open the run record carrying both — the run's cheap opening, settled before a single expensive read happens.

Review gate: stop after this step — "Confirm the run scope — which spec records to refresh, which delivered items to cover. The gate is the runner's, taken after the return lands and asked against the run record's two tables; a `present` spec record may still be picked for a refresh, and an undocumented item may still be dropped from scope"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step survey`.

## Step: Briefing

Write the run record's briefing from the value records and the audience record — what the project is, who it serves, where it is heading — and name the vision drift against the previous run's.

Review gate: stop after this step — "Present the briefing and stop — the user confirms what the project is, who it serves and where it is heading. A named vision shift must be acknowledged in the answer; silence never counts"; continue only on explicit user confirmation.

Tell a sub-agent — model fable, effort high — to get its instructions by calling this command: `booping render-playbook docs --step briefing`.

## Step: Roles

Characterise the audiences that read this project's documentation — per role who it is, what it comes for, its depth ceiling, what is withheld, its voice and what it reads — refreshed in the `## Facts` of the audience record reference/0001, the audience layer every later step resolves "how deep, in what voice, for whom" against.

Review gate: stop after this step — "Confirm or refine — presented together with surfaces. Hold it at `awaiting-roles-targets-confirm`, presenting the audience record reference/0001 and the surfaces record reference/0003 in one pass; a refinement re-enters `spec-building`. The step itself never stops for the user"; continue only on explicit user confirmation.

Tell a sub-agent — model fable, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step roles`.

## Step: Targets

Enumerate the repo's markdown documentation surfaces — plus the `CHANGELOG.md` this playbook introduces and the spec set the playbook reads — one fact each with its path, audience, depth ceiling and conventions, refreshed in the `## Facts` of the surfaces record reference/0003 and closed by a "Not surfaces" fact; return the surfaces so the runner gates on them without opening the record.

Tell a sub-agent — model fable, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step targets`.

## Step: Research
# Read the delivered items and build the typed change table

You receive the workdir (`{vault}/docs/`), the run record already on disk — its `## Briefing` and
the confirmed scope from its `## Scope` section, the delivered items this run covers — and the
spec records: the values and the feature index below, the audience record
`{vault}/specs/reference/0001-audience.md` and the surfaces record
`{vault}/specs/reference/0003-documentation-surfaces.md`. On a re-entry from the change gate you
also receive the items the user added; only those are read again.

This is the run's one expensive read, paid once and compressed. You read no work item yourself: each
is read in its own sub-agent, and what comes back to you is a row, never the item's text.

## The values

| Value | Kind | Summary | Path |
| --- | --- | --- | --- |
| Curated self-learning | value | The system gets better from its own runs, but only through the user and when the user wants it: a lesson becomes a rule after the user takes it, not after every run. | specs/value/0001-curated-self-learning.md |
| Minimal effective context | value | A step gets only what it needs. | specs/value/0002-minimal-effective-context.md |
| Single source | value | Each fact, decision and piece of structured data lives in one place and is referenced or rendered from there; a decision is kept together with its reason. | specs/value/0003-single-source.md |
| Analysable history | value | Plans, runs and their outcomes are kept across every project, so the history can be analysed: practices taken over from one project to another, benchmarks, quality comparison, problem analysis. | specs/value/0004-analysable-history.md |
| Stack-agnostic core | value | The core knows nothing about a stack or a project; specifics live in the global and the project tiers. | specs/value/0005-stack-agnostic-core.md |
| A constructor, not a fixed solution | value | Booping is a constructor — a framework for playbooks with a set of core mechanics — not a ready solution fixed to one task. | specs/value/0006-a-constructor-not-a-fixed-solution.md |
| Plans run to the end | value | The agent carries a plan through to the end on its own unless force majeure stops it. | specs/value/0007-plans-run-to-the-end.md |
| Effective human review | value | Every step where a human takes part is convenient and effective for that human. | specs/value/0008-effective-human-review.md |
| Adjustable control | value | The human can review the system deeply, or give the agent more freedom to act inside the values and boundaries. | specs/value/0009-adjustable-control.md |
| Proven to work | value | We know the system works as it should and can guarantee it high enough to call it reliable. | specs/value/0010-proven-to-work.md |
| Everything in one place | value | Everything is plain files, easy to look at from one place — for example Obsidian; symlinks back to the project repos keep it together. | specs/value/0011-everything-in-one-place.md |
| Quality at a rational cost | value | Booping is a work tool for professionals, so the quality of the result matters. | specs/value/0012-quality-at-a-rational-cost.md |
| Guides to the goal | value | The system is clear to the user and leads them to the goal by the hand, while letting a professional step aside and get there their own way. | specs/value/0013-guides-to-the-goal.md |
| Comfort for non-technical users | non-value | How comfortable booping is for people without a strong technical background is not optimised for; they are not its audience. | specs/value/0014-comfort-for-non-technical-users.md |


## The feature index

| Story | Summary | Status | Path |
| --- | --- | --- | --- |
| Playbook driver | The /playbook skill discovers a procedure across the core, global and project levels and drives it to completion. | done | specs/story/0001-playbook-driver.md |
| Run state machines | A run's state lives in per-playbook states: machines that only the booping CLI advances. | done | specs/story/0002-run-state-machines.md |
| Layered configuration | Config is a deep merge over the core, global and project levels, and any mapping in it can be a query spec or a scaffold tree. | done | specs/story/0003-layered-configuration.md |
| Targeted rules | An accepted rule's brief is injected into exactly the playbooks, steps, agents or skills its targets: list names. | done | specs/story/0004-targeted-rules.md |
| Plan and review templates | Groom and code-review offer plan and review templates the user authored in the Project Vault or at the global level. | done | specs/story/0005-plan-and-review-templates.md |
| User playbooks | Playbooks the user authors at the global level or in the Project Vault are discovered and run beside the core ones. | done | specs/story/0006-user-playbooks.md |
| External agents | Agents the plugin does not ship are wired into playbook agent slots through config and shaped per project by targeted rules. | done | specs/story/0007-external-agents.md |
| Template pipeline | Skill and agent bodies render in one runtime stage from src/templates/ with full project context, reproducibly when pinned. | done | specs/story/0008-template-pipeline.md |
| Quality gates | just ci runs lint, typecheck, pytest, snapshots, mdcheck and e2e in order, holding the plugin's behaviour. | done | specs/story/0009-quality-gates.md |
| pytest-txtar | The e2e corpus's case format and sandboxed runner ship as a standalone pytest plugin on PyPI. | done | specs/story/0010-pytest-txtar.md |
| Eval suites | Promptfoo suites beside each step guard its contract in a deterministic and an llm-rubric tier. | done | specs/story/0011-eval-suites.md |
| Migration shipping | The plugin ships Project Vault migrations, and every render surface is gated on a vault's applied watermark. | done | specs/story/0012-migration-shipping.md |
| Documentation site | The public MkDocs reference builds strictly and publishes to gh-pages on push to master. | done | specs/story/0013-documentation-site.md |
| Project setup | The setup playbook takes a repo from any state to a working booping project and re-runs without changing what is already set up. | done | specs/story/0014-project-setup.md |
| Project Vault migrations | The migrate playbook brings an existing Project Vault current with the plugin, one approval and one commit per migration. | done | specs/story/0015-vault-migrations.md |
| Groom | Groom shapes a feature, bug or refactor into a specified, estimated plan the user approved, ending at ready-for-dev. | done | specs/story/0016-groom.md |
| Develop | Develop executes a groomed plan one milestone at a time through a worker agent and closes it at done or fail. | done | specs/story/0017-develop.md |
| Retro | Retro mines a finished sprint's session logs, diff and the user's feedback into a standalone retrospective. | done | specs/story/0018-retro.md |
| Learn | Learn turns retrospective findings the user confirmed into rule records in the project specs tier or CLAUDE.md entries. | done | specs/story/0019-learn.md |
| Session metrics | A plan carries measured active minutes, tokens and models computed from Claude Code session logs. | done | specs/story/0020-session-metrics.md |
| Code review | The code-review playbook reviews a confirmed scope, collects the human verdict and applies only approved fixes. | done | specs/story/0021-code-review.md |
| Task tracker | The booping-tracker CLI carries every interaction with an issue tracker, and groom mirrors its run status and questions onto the tracker issue. | done | specs/story/0022-task-tracker.md |


## The fan-out

Read the audience and surfaces records yourself, then spawn one sub-agent per in-scope item — the
researcher agent `config.core.research_agent` names — all in a single message so they run in
parallel. Each brief carries:

- the one item's path, and nothing pointing past it: no sibling item, no commit range, no repo
  history — a sub-agent that wanders re-reads what another one already owns
- the record facts its row must be tied to: the briefing's vision in a line, the role names with
  the depth each one reads at (reference/0001), the surface paths with the audience and depth of
  each (reference/0003), and the story titles of the feature index. The role names and the surface
  paths are what the row's **Audience** and **Target files** cells are filled from, so a brief that
  omits them gets those two cells invented
- the fixed question — what changed for someone who uses this project, of which type, against which
  record — plus the row shape below and the instruction to return the row or rows alone

## The rows

One row per distinct change, at least one row per item. An item that produced nothing worth
documenting still gets a `chore` row with `none` in the spec-set effect column, so every in-scope
item is provably covered — the exit gate demands it, and `record` marks items documented from this
table. Ids run `C1`, `C2`, … in scope order; on a second pass the rows already written keep their
ids and their wording, and the added items continue the sequence.

Columns: `# | Work item | Type | What changed | Audience | Target files | Spec-set effect`.

- **Type** is a closed vocabulary — `vision shift`, `new feature`, `refactoring`, `feature drop`,
  `chore`. No sixth word.
- **What changed** is the user-visible effect, written in the project's own vocabulary and in the
  present tense. Never diff language, file lists or module names: a business-facing surface is
  served from this cell later, which is why roles and surfaces are read here and not only at
  targeting.
- **Audience** names the roles that consume this change, taken from reference/0001 by their own
  names — never a role invented here, never "everyone". A change no role outside the repo consumes
  says so with the one role that does.
- **Target files** names the surfaces the change plausibly belongs on, taken from
  reference/0003 by their own paths, vault-relative where that record writes them so. These are
  **candidates, not the plan** — `targeting` owns the destinations and may add, drop or split them
  against the surfaces' depth ceilings. A row whose change is already documented on a surface still
  names it, so the gate can see the overlap.
- **Spec-set effect** names each record a row moves and the edit it implies (`story/0004`: a
  criterion for directory-scoped targets; `reference/0001`: a new audience; a new story:
  *frontmatter query*), or `none`. The spec records are themselves a surface: a row that moves one
  names it under **Target files** too.

Audience and Target files are why reference/0001 and reference/0003 are read at this step. Filling
either from your own judgement rather than from those two records is the failure mode — a role or a
path that does not appear there does not exist.

## The file to write

The run record gains `## Changes`: the table, then one closing line giving the row count over the
item count, the count per type, and how many rows touch each record. One table per run — a second
pass rewrites the section in place rather than appending to it.

Write the section before you present anything, so a run resumed at the change gate in a later
session recovers the table from the record rather than from a context that is gone. The same section
is where the gate's fold lands: the record ends up carrying the confirmed table, not the draft.

Nothing else is written. The spec records are read-only here — `sync-specs` owns that write — no
work item's own file is touched, and no destination document is opened. No frontmatter of your own:
`changes_reviewed_at:` is the confirming edge's hook.

## Return format

```markdown
## Changed:
- [UPDATED] {vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md — `## Changes`, {n} rows over {m} items

## Notes:
- types: {n} vision shift, {n} new feature, {n} refactoring, {n} feature drop, {n} chore
- audience: {one clause per role any row names, with the row ids}
- target files: {one clause per surface any row names, with the row ids}
- spec-set effect: {one clause per record any row touches, or `none`}
- read: {m} items in {m} sub-agents

## Questions:
```

`## Questions:` is always empty — extending the change table is the gate's question, not the step's.
The runner presents the gate from these lines plus the section just written. No prose outside the
block.

## Step: Sync Specs

Fold the confirmed change table into the spec records — value, audience, surfaces, glossary and story records — editing in place only what a row settles and marking what it does not, then running `booping specs check`, so every later step resolves "what does this project ship, for whom, at what depth" against current records.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step sync-specs`.

## Step: Targeting
# Plan the role × surface writes

You perform this step yourself, in the driving conversation: you own the plan you present at the
gate that follows, and that gate always fires.

You have the workdir (`{vault}/docs/`), the run record whose change table the user has just
extended and confirmed, the feature index below, and spec records `sync-specs` has already folded
those changes into. Read the change table directly — each change's id, its type, what it touched,
and the record its spec-set effect names. Hand the record reads to `booping:booping-researcher`,
one brief covering the surfaces record `{vault}/specs/reference/0003-documentation-surfaces.md`
and the audience record `{vault}/specs/reference/0001-audience.md`, and ask for exactly what a row
needs back: per surface its path, format, audience, depth and whether this run seeds it or appends
to it; per role its depth ceiling, its voice and its withheld set. The two records never enter the
driving context whole; the documentation's structure comes from the surfaces record.

## The feature index

| Story | Summary | Status | Path |
| --- | --- | --- | --- |
| Playbook driver | The /playbook skill discovers a procedure across the core, global and project levels and drives it to completion. | done | specs/story/0001-playbook-driver.md |
| Run state machines | A run's state lives in per-playbook states: machines that only the booping CLI advances. | done | specs/story/0002-run-state-machines.md |
| Layered configuration | Config is a deep merge over the core, global and project levels, and any mapping in it can be a query spec or a scaffold tree. | done | specs/story/0003-layered-configuration.md |
| Targeted rules | An accepted rule's brief is injected into exactly the playbooks, steps, agents or skills its targets: list names. | done | specs/story/0004-targeted-rules.md |
| Plan and review templates | Groom and code-review offer plan and review templates the user authored in the Project Vault or at the global level. | done | specs/story/0005-plan-and-review-templates.md |
| User playbooks | Playbooks the user authors at the global level or in the Project Vault are discovered and run beside the core ones. | done | specs/story/0006-user-playbooks.md |
| External agents | Agents the plugin does not ship are wired into playbook agent slots through config and shaped per project by targeted rules. | done | specs/story/0007-external-agents.md |
| Template pipeline | Skill and agent bodies render in one runtime stage from src/templates/ with full project context, reproducibly when pinned. | done | specs/story/0008-template-pipeline.md |
| Quality gates | just ci runs lint, typecheck, pytest, snapshots, mdcheck and e2e in order, holding the plugin's behaviour. | done | specs/story/0009-quality-gates.md |
| pytest-txtar | The e2e corpus's case format and sandboxed runner ship as a standalone pytest plugin on PyPI. | done | specs/story/0010-pytest-txtar.md |
| Eval suites | Promptfoo suites beside each step guard its contract in a deterministic and an llm-rubric tier. | done | specs/story/0011-eval-suites.md |
| Migration shipping | The plugin ships Project Vault migrations, and every render surface is gated on a vault's applied watermark. | done | specs/story/0012-migration-shipping.md |
| Documentation site | The public MkDocs reference builds strictly and publishes to gh-pages on push to master. | done | specs/story/0013-documentation-site.md |
| Project setup | The setup playbook takes a repo from any state to a working booping project and re-runs without changing what is already set up. | done | specs/story/0014-project-setup.md |
| Project Vault migrations | The migrate playbook brings an existing Project Vault current with the plugin, one approval and one commit per migration. | done | specs/story/0015-vault-migrations.md |
| Groom | Groom shapes a feature, bug or refactor into a specified, estimated plan the user approved, ending at ready-for-dev. | done | specs/story/0016-groom.md |
| Develop | Develop executes a groomed plan one milestone at a time through a worker agent and closes it at done or fail. | done | specs/story/0017-develop.md |
| Retro | Retro mines a finished sprint's session logs, diff and the user's feedback into a standalone retrospective. | done | specs/story/0018-retro.md |
| Learn | Learn turns retrospective findings the user confirmed into rule records in the project specs tier or CLAUDE.md entries. | done | specs/story/0019-learn.md |
| Session metrics | A plan carries measured active minutes, tokens and models computed from Claude Code session logs. | done | specs/story/0020-session-metrics.md |
| Code review | The code-review playbook reviews a confirmed scope, collects the human verdict and applies only approved fixes. | done | specs/story/0021-code-review.md |
| Task tracker | The booping-tracker CLI carries every interaction with an issue tracker, and groom mirrors its run status and questions onto the tracker issue. | done | specs/story/0022-task-tracker.md |


A story `sync-specs` created this run is not in the index above — its path is in `sync-specs`'
return.

## The section to write

`{vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md` gains a `## Targeting plan`. Nothing else — no
destination document is opened or written here, and the spec records are read-only to you even
where the planning exposes a gap in them.

One table row per destination document:

| Column | Holds |
| --- | --- |
| **Destination** | the file's path — a concrete markdown file, never a directory |
| **Roles** | names taken from the audience record, never invented |
| **Changes** | the change table's ids assigned to this file |
| **Must say** | one clause per assigned change, already pitched at the depth those roles allow |
| **Progress** | `pending` |

- **No two rows name the same file.** Rows are the loop's unit of parallelism — `update` spawns
  one instance per row — so a change touching three surfaces is folded into three existing rows,
  never given a row of its own.
- No row names `CHANGELOG.md`: the changelog has its own step and its own surface.
- Oversharing is settled here once. A change that matters to a plugin user and not to a
  contributor gets a row for the one surface and not the other, at that role's ceiling, so `write`
  never re-litigates audience fit per file.
- A change is placed under the story it moves — for a new-feature row, the story `sync-specs`
  created for it. A change no story covers is placed by surface alone, its **Must say** clause
  opening `no story —`; never a home invented for it.
- A closing `## Not targeted` list names every confirmed change that gets no row, each with the
  reason it needs no document. Changes that land nowhere are stated, never quietly dropped.
- Write no frontmatter: `targeting_reviewed_at:` is the confirming edge's hook.
- A rework rewrites the whole section rather than appending, preserving any Progress value a row
  has already reached.

```markdown
## Targeting plan

| Destination | Roles | Changes | Must say | Progress |
| --- | --- | --- | --- | --- |
| `README.md` | Plugin user | C1, C3 | C1: the Statuses narrative now describes retro as its own track, plan statuses ending at `done`. C3: code review is queued from plan frontmatter, one line, no mechanics. | pending |
| `documentation/vault.md` | Playbook author, Plugin user | C2 | `specs/rule/` records carry `targets:`; describe the current shape only — no per-surface-file narration. | pending |

## Not targeted

- C5 (chore) — CI job ordering in `just ci`; no user-visible effect and no surface documents job order.
```

A change table that is entirely chores gets the heading, an empty table and a `## Not targeted`
list holding every change — then the gate asks whether to close the run rather than enter the loop.

Write the section, then compose the return: it is the gate's presentation verbatim, so the user
confirms the rows from it without opening the file.

## Return format

```markdown
## Changed:
- [UPDATED] {vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md — targeting plan, {n} destinations, {m} of {k} confirmed changes assigned

## Notes:
- {destination} — {roles} — {change ids}: {what it must say, in a clause}
- not targeted: {change id} ({type}) — {why no document needs it}
- loop: {n} update instances, no two rows sharing a file

## Questions:
```

One `## Notes:` line per row in table order, then one per not-targeted change, then the loop line.
`## Questions:` stays empty — the plan question is the gate itself. No prose outside the block.

## Subgraph: update

Instructions:
- After: targeting
- Repeat: once per destination document in the confirmed targeting plan; instances may run in parallel
- Inner waves: 1. `write` 2. `compact` 3. `verify`

## Step: Write

Fold one targeting-plan row's assigned changes into its single destination markdown document — rewriting the sections that already own them, at the depth its roles allow, as a current-state snapshot with legacy narration removed — and return what landed where so the runner never opens the file.

Part of: update (repeated)

Tell a sub-agent — model fable, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step write`.

## Step: Compact

Split one freshly written destination document by section, compact each section twice — radically and gently — and merge per section, so filler goes and every clause the targeting row required still stands.

Part of: update (repeated)

Tell a sub-agent — model opus, effort high — to get its instructions by calling this command: `booping render-playbook docs --step compact`.

## Step: Verify

Check one destination document in a single pass against three failure modes — a claim the repo does not support, a passage past its audience's depth ceiling, and prose narrating what the project used to be — correcting each surgically in place while reading source read-only, and returning the findings source could not settle for the runner to record.

Part of: update (repeated)

Tell a sub-agent — model opus, effort high — to get its instructions by calling this command: `booping render-playbook docs --step verify`.

## Step: Changelog

Write this run's user-visible entry in the repo's `CHANGELOG.md`, seeding the file when it is absent — one past-tense bullet per shipped change in the grammar the history already uses, with every non-user-visible row reported as omitted so the confirmed table is fully accounted for.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step changelog`.

## Step: Record

Close the run record — a `## Landed` table of every destination the loop touched plus the history row, and a `documented:` frontmatter list of the work items every one of whose changes is accounted for, so a dropped destination withholds its item and the next survey resurfaces it.

Tell a sub-agent — model opus, effort low — to get its instructions by calling this command: `booping render-playbook docs --step record`.
