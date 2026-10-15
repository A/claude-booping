Specs are typed records about why the project is the way it is; every type, its frontmatter and the principles behind the set are in [the specs format guide](${CLAUDE_PLUGIN_ROOT}/src/specs/README.md) — read it before writing a record.

Tiers (`core.specs.tiers`; every `booping specs` verb takes `--tier`, default `project`):

- `core` — `${CLAUDE_PLUGIN_ROOT}/specs`, namespace `booping`.
- `project` — `specs`.

Writing a record:

- Number it with `booping specs next {type}`.
- Set `created_by: claude`; never set `reviewed`.
- Run `booping specs check` after every write and fix what it reports.

The run keeps no state of its own. The `open_item` machine below tracks one open-item file each: its workdir is the vault, and only `booping specs open-items` moves it — never call `booping playbook-transition` for it, and never create a run workdir for it.




## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `guide` | — | Act on the user's specs request from the dialogue. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state specs --workdir <run workdir>
```

### State: open_item

- Referenced by: no graph scope — standalone, moved only by `--state open_item` calls
- Artifact: `open-items/{instance}.md` (relative to the run workdir)
- Initial status: `open`
- Advance: `booping playbook-transition specs <to> --state open_item --instance <slug> --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `open` | `planned` | `booping specs open-items plan` linked the item to a plan | `plan` names an existing plan file |
| `open` | `dropped` | `booping specs open-items close --dropped` closed the item without work | — |
| `planned` | `done` | `booping specs open-items close`, or the linked plan reached develop's `done` | — |
| `planned` | `dropped` | `booping specs open-items close --dropped` closed the item without work | — |
| `planned` | `open` | `booping specs open-items reopen`, or the linked plan failed or was cancelled | — |
| `done` | *(terminal)* | — | — |
| `dropped` | *(terminal)* | — | — |

## Step: Guide
Act on the user's request; the scenarios below orient, never restrict — never ask which one to run.
Flags and their allowed values come from `booping specs open-items {verb} --help`.

## Init

No project tier yet (the preamble lists none, or `booping specs ls` finds no specs): offer to
create it. Once the user agrees, run `booping specs init --tier project`, then walk the user
through [the alignment guide](${CLAUDE_PLUGIN_ROOT}/docs/specs-alignment.md).

## Alignment

The user refines the project's values: read the `value` records, then follow the alignment
guide's order — values first, then the boundaries that follow from them. Next:
`booping specs check` after each record written.

## Auto-review

Read the values, rules and ADRs. A contradiction the records settle becomes a `conflict` record; one
the user must settle becomes an item. Next: `booping specs open-items add --direction conflict`.

## Record

A decision → an ADR, only for one choice with a real alternative and a reason the code cannot
show. An idea → an idea record. A constraint on how the model works → a rule with `targets` and
`brief`. Next: an ADR with a `Confirmation:` line → `booping specs open-items add --record adr/NNNN`;
anything else → `booping specs check`.

## Sync specs and code

Compare the records with the code; each gap becomes one item with the direction it runs:
`booping specs open-items add --source sync`. Next: `booping specs open-items scan` for the marks
and check findings.

## Retro to rules

A retrospective awaits learning → hand it to learn. A lesson from this dialogue → a rule record,
written directly. Next: `/playbook learn`, or `booping specs check` after the rule.

## Open items

Show `booping specs open-items list`; the user picks. An item needing no work →
`booping specs open-items close {ids} --dropped --reason "…"`; a planned item whose plan was
cancelled outside develop → `booping specs open-items reopen --plan {plan}`. Next:
`/playbook groom` naming the picked ids — groom links them to the plan.
