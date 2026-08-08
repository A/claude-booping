A run ends with the project's documentation surfaces matched to the current state of the repo:
the spec set current, a reviewed run record listing what changed and where it landed, and every
affected surface rewritten in the tone and depth its audience needs. Steps already satisfied by
a current file are skipped rather than redone.

## Guidance

- Date & time: 2026-08-08 14:32
- The run workdir is `{vault}/docs/`; every `booping playbook-state` / `booping
  playbook-transition` call passes `--workdir {vault}/docs --target {YYYYMMDDHHmm}-{title}.md`,
  since the machine declares no `artifact:`.
- The spec set — `_specs/index.md` (briefing), `_specs/roles.md`, `_specs/targets.md`,
  `_specs/features.md` — persists across runs and is only ever refreshed, never rebuilt from
  scratch once established. `_specs/documented.md` is the ledger of already-documented work;
  `research` reads it to surface only the delivered items still missing from it.
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
| `survey` | — | Report which spec-set files are missing or incomplete and which delivered work is not yet documented, and open the run record carrying both — the run's cheap opening, settled before a single expensive read happens. | Confirm the run scope — which spec files to refresh, which delivered items to cover. The gate is the runner's, taken after the return lands and asked against the run record's two tables; a `present` spec file may still be picked for a refresh, and an undocumented item may still be dropped from scope |
| `briefing` | `survey` | Write the shaping briefing — what the project is, who it serves, where it is heading — and name the vision drift against the previous one. | Present the briefing and stop — the user confirms what the project is, who it serves and where it is heading. A named vision shift must be acknowledged in the answer; silence never counts |
| `roles` | `briefing` | Characterise the audiences that read this project's documentation — per role the depth ceiling, the tone and what must be withheld — written to `_specs/roles.md`, the audience layer every later step resolves "how deep, in what voice, for whom" against. | Confirm or refine — presented together with surfaces. Hold it at `awaiting-roles-targets-confirm`, presenting `_specs/roles.md` and `_specs/targets.md` in one pass; a refinement re-enters `spec-building`. The step itself never stops for the user |
| `targets` | `briefing` | Enumerate the repo's markdown documentation surfaces — plus the `CHANGELOG.md` this playbook introduces — one row each with its format and conventions, its audience described from the surface itself, and how deep it goes; close the set with a `## Not surfaces` section and return the rows so the runner gates on them without opening the file. | — |
| `feature-index` | `briefing` | Build the feature index — the features the project delivers, their capabilities and the groups they sit in — written to `_specs/features.md`; the groups are the documentation structure `targeting` places changes under, and the capability inventory `research` types each delivered item against. | Confirm features, capabilities and groups. Hold it at `awaiting-features-confirm`, on its own and after the roles-and-surfaces gate, presenting the index from the step's return lines; a refinement re-enters `spec-building`. The step itself never stops for the user |
| `research` | `roles`, `targets`, `feature-index` | Read each in-scope delivered item in its own sub-agent and assemble the typed change table — one row per user-visible change, tied to the spec file it moves — written to the run record as the contract `sync-specs`, `targeting` and `record` all work from. | Extend, refine and confirm the change table, presented in chat from the `## Changes` section just written. An extension naming items that still have to be read sends the run back to this step, which reads only the added items and rewrites the section; confirmation is explicit — silence never counts, and the confirming edge stamps `changes_reviewed_at:` on the run record |
| `sync-specs` | `research` | Fold the confirmed change table into the four `_specs/` files — briefing, roles, surfaces, feature index — rewriting in place only what a row targets, so every later step resolves "what does this project ship, for whom, at what depth" against a current spec set. | — |
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
| `awaiting-scope-confirm` | `surveying` | the user's scope answer needs a fresh survey — a different item range, or spec files the survey did not inspect | — |
| `awaiting-scope-confirm` | `briefing` | the user settled which spec files to refresh and which delivered items to cover, and at least one spec file needs work | explicit user confirmation captured — silence never counts |
| `awaiting-scope-confirm` | `researching` | the user settled the scope and every spec file is present and current — the spec waves are skipped | explicit user confirmation captured; the survey found no missing or incomplete spec file |
| `awaiting-scope-confirm` | `done` | the survey found nothing to do — spec set current, undocumented set empty — and the user closed the run | explicit user confirmation captured; the undocumented set is empty |
| `awaiting-scope-confirm` | `cancelled` | the user cancels the run | — |
| `briefing` | `awaiting-briefing-confirm` | briefing wrote `_specs/index.md`, naming any vision shift against the previous one | — |
| `briefing` | `cancelled` | the user cancels the run | — |
| `awaiting-briefing-confirm` | `briefing` | the user reworks the briefing — what the project is, who it serves, where it is heading | — |
| `awaiting-briefing-confirm` | `spec-building` | the user confirms the briefing | explicit user confirmation captured — a vision shift is acknowledged in the answer, silence never counts |
| `awaiting-briefing-confirm` | `cancelled` | the user cancels the run | — |
| `spec-building` | `awaiting-roles-targets-confirm` | roles, targets and feature-index each wrote their file | — |
| `spec-building` | `cancelled` | the user cancels the run | — |
| `awaiting-roles-targets-confirm` | `spec-building` | the user wants roles or surfaces refined | — |
| `awaiting-roles-targets-confirm` | `awaiting-features-confirm` | the user confirms roles and surfaces, presented together | explicit user confirmation captured — silence never counts |
| `awaiting-roles-targets-confirm` | `cancelled` | the user cancels the run | — |
| `awaiting-features-confirm` | `spec-building` | the user wants features, capabilities or groups refined | — |
| `awaiting-features-confirm` | `researching` | the user confirms the feature index | explicit user confirmation captured |
| `awaiting-features-confirm` | `cancelled` | the user cancels the run | — |
| `researching` | `awaiting-changes-confirm` | the per-item sub-agents returned and the typed change table is posted in chat | every in-scope delivered item carries a row, each typed |
| `researching` | `cancelled` | the user cancels the run | — |
| `awaiting-changes-confirm` | `researching` | the user adds items that still have to be read | — |
| `awaiting-changes-confirm` | `syncing-specs` | the user confirms the change table, extensions and refinements folded in | explicit user confirmation captured — silence never counts |
| `awaiting-changes-confirm` | `cancelled` | the user cancels the run | — |
| `syncing-specs` | `targeting` | sync-specs folded the confirmed table into briefing, roles, surfaces and feature index | — |
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

Report which spec-set files are missing or incomplete and which delivered work is not yet documented, and open the run record carrying both — the run's cheap opening, settled before a single expensive read happens.

Review gate: stop after this step — "Confirm the run scope — which spec files to refresh, which delivered items to cover. The gate is the runner's, taken after the return lands and asked against the run record's two tables; a `present` spec file may still be picked for a refresh, and an undocumented item may still be dropped from scope"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step survey`.

## Step: Briefing

Write the shaping briefing — what the project is, who it serves, where it is heading — and name the vision drift against the previous one.

Review gate: stop after this step — "Present the briefing and stop — the user confirms what the project is, who it serves and where it is heading. A named vision shift must be acknowledged in the answer; silence never counts"; continue only on explicit user confirmation.

Tell a sub-agent — model fable, effort high — to get its instructions by calling this command: `booping render-playbook docs --step briefing`.

## Step: Roles

Characterise the audiences that read this project's documentation — per role the depth ceiling, the tone and what must be withheld — written to `_specs/roles.md`, the audience layer every later step resolves "how deep, in what voice, for whom" against.

Review gate: stop after this step — "Confirm or refine — presented together with surfaces. Hold it at `awaiting-roles-targets-confirm`, presenting `_specs/roles.md` and `_specs/targets.md` in one pass; a refinement re-enters `spec-building`. The step itself never stops for the user"; continue only on explicit user confirmation.

Tell a sub-agent — model fable, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step roles`.

## Step: Targets

Enumerate the repo's markdown documentation surfaces — plus the `CHANGELOG.md` this playbook introduces — one row each with its format and conventions, its audience described from the surface itself, and how deep it goes; close the set with a `## Not surfaces` section and return the rows so the runner gates on them without opening the file.

Tell a sub-agent — model fable, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step targets`.

## Step: Feature Index

Build the feature index — the features the project delivers, their capabilities and the groups they sit in — written to `_specs/features.md`; the groups are the documentation structure `targeting` places changes under, and the capability inventory `research` types each delivered item against.

Review gate: stop after this step — "Confirm features, capabilities and groups. Hold it at `awaiting-features-confirm`, on its own and after the roles-and-surfaces gate, presenting the index from the step's return lines; a refinement re-enters `spec-building`. The step itself never stops for the user"; continue only on explicit user confirmation.

Tell a sub-agent — model fable, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step feature-index`.

## Step: Research
# Read the delivered items and build the typed change table

You receive the workdir (`{vault}/docs/`), the run record already on disk, the confirmed scope from
its `## Scope` section — the delivered items this run covers — and the spec set: the briefing
(`_specs/index.md`), the roles (`_specs/roles.md`), the surfaces (`_specs/targets.md`) and the
feature index (`_specs/features.md`). On a re-entry from the change gate you also receive the items
the user added; only those are read again.

This is the run's one expensive read, paid once and compressed. You read no work item yourself: each
is read in its own sub-agent, and what comes back to you is a row, never the item's text.

## The fan-out

Read the four spec files yourself, then spawn one sub-agent per in-scope item — the researcher agent
`config.core.research_agent` names — all in a single message so they run in parallel. Each brief
carries:

- the one item's path, and nothing pointing past it: no sibling item, no commit range, no repo
  history — a sub-agent that wanders re-reads what another one already owns
- the spec-set facts its row must be tied to: the briefing's vision in a line, the role names, the
  surface paths, the capability and group names of the feature index
- the fixed question — what changed for someone who uses this project, of which type, against which
  spec file — plus the row shape below and the instruction to return the row or rows alone

## The rows

One row per distinct change, at least one row per item. An item that produced nothing worth
documenting still gets a `chore` row with `none` in the spec-set column, so every in-scope item is
provably covered — the exit gate demands it, and `record` marks items documented from this table.
Ids run `C1`, `C2`, … in scope order; on a second pass the rows already written keep their ids and
their wording, and the added items continue the sequence.

Columns: `# | Work item | Type | What changed | Spec-set effect`.

- **Type** is a closed vocabulary — `vision shift`, `new feature`, `refactoring`, `feature drop`,
  `chore`. No sixth word.
- **What changed** is the user-visible effect, written in the project's own vocabulary and in the
  present tense. Never diff language, file lists or module names: a business-facing surface is
  served from this cell later, which is why roles and surfaces are read here and not only at
  targeting.
- **Spec-set effect** names each spec file a row moves and the edit it implies (`features.md`: new
  capability *frontmatter query* under the CLI group), or `none`.

## The file to write

The run record gains `## Changes`: the table, then one closing line giving the row count over the
item count, the count per type, and how many rows touch each spec file. One table per run — a second
pass rewrites the section in place rather than appending to it.

Write the section before you present anything, so a run resumed at the change gate in a later
session recovers the table from the record rather than from a context that is gone. The same section
is where the gate's fold lands: the record ends up carrying the confirmed table, not the draft.

Nothing else is written. `_specs/` is read-only here — `sync-specs` owns that write — no work item's
own file is touched, and no destination document is opened. No frontmatter of your own:
`changes_reviewed_at:` is the confirming edge's hook.

## Return format

```markdown
## Changed:
- [UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md — `## Changes`, {n} rows over {m} items

## Notes:
- types: {n} vision shift, {n} new feature, {n} refactoring, {n} feature drop, {n} chore
- spec-set effect: {one clause per spec file any row touches, or `none`}
- read: {m} items in {m} sub-agents

## Questions:
```

`## Questions:` is always empty — extending the change table is the gate's question, not the step's.
The runner presents the gate from these lines plus the section just written. No prose outside the
block.

## Step: Sync Specs

Fold the confirmed change table into the four `_specs/` files — briefing, roles, surfaces, feature index — rewriting in place only what a row targets, so every later step resolves "what does this project ship, for whom, at what depth" against a current spec set.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook docs --step sync-specs`.

## Step: Targeting
# Plan the role × surface writes

You perform this step yourself, in the driving conversation: you own the plan you present at the
gate that follows, and that gate always fires.

You have the workdir (`{vault}/docs/`), the run record whose change table the user has just
extended and confirmed, and a spec set `sync-specs` has already folded those changes into. Read
the change table directly — each change's id, its type, what it touched. Hand the spec-set reads
to `booping:booping-researcher`, one brief covering `_specs/targets.md`, `_specs/roles.md` and
`_specs/features.md`, and ask for exactly what a row needs back: per surface its path, format,
audience, depth and whether this run seeds it or appends to it; per role its depth ceiling, its
voice and its withheld set; the feature groups that give the documentation its structure. The
three files never enter the driving context whole.

## The section to write

`{vault}/docs/{YYYYMMDDHHmm}-{title}.md` gains a `## Targeting plan`. Nothing else — no
destination document is opened or written here, and the spec set is read-only to you even where
the planning exposes a gap in it.

One table row per destination document:

| Column | Holds |
| --- | --- |
| **Destination** | the file's path — a concrete markdown file, never a directory |
| **Roles** | names taken from the roles file, never invented |
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
- A change is placed under the group it already belongs to in the feature index — never a home
  invented for it.
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
| `documentation/vault.md` | Playbook author, Plugin user | C2 | `_lessons/` holds flat files carrying `targets:`; describe the current shape only — no per-surface-file narration. | pending |

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
- [UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md — targeting plan, {n} destinations, {m} of {k} confirmed changes assigned

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
