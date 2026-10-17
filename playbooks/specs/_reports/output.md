Specs are typed records about why the project is the way it is; every type, its frontmatter and the principles behind the set are in [the specs format guide](${CLAUDE_PLUGIN_ROOT}/src/specs/README.md) — read it before writing a record.

Tiers (`core.specs.tiers`; every `booping specs` verb takes `--tier`, default `project`):

- `core` — `${CLAUDE_PLUGIN_ROOT}/specs`, namespace `booping`.
- `project` — `.`.

Mode: autonomous when the user told this session to work autonomously, or its launch prompt carries `AUTONOMOUS RUN`; otherwise supervised.

Writing a record:

- Number it with `booping specs next {type}`.
- Set `created_by: claude`; never set `reviewed`.
- Run `booping specs check` after every write and fix what it reports.

The run keeps no state of its own. The `open_item` machine below tracks one open-item file each: its workdir is the vault, `booping transition {item} {status}` moves it, the machine inferred from the path — never create a run workdir for it.




## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Rules

The following 1 rule(s) apply to this playbook. Never silently violate one; conflict → stop and flag. Read a rule's record when its brief is not enough.

- On a review or audit of the specs, put every record to the tests in the format guide's "When a record is worth writing" (an ADR needs a real choice, a rule must change behaviour, nothing derivable from config or code, no value restated); list each failure as `{ref} → {type it fits | delete} — {one reason}` for the user to accept. [booping:rule/0034](${CLAUDE_PLUGIN_ROOT}/specs/rule/0034-specs-review-tests-each-record.md)

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `guide` | — | Act on the user's specs request from the dialogue. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping state <run workdir>/open-items/<slug>.md --playbook specs
```

### State: open_item

- Referenced by: no graph scope — standalone, moved only by `--state open_item` calls
- Artifact: `open-items/{instance}.md` (relative to the run workdir)
- Initial status: `open`
- Advance: `booping transition <run workdir>/open-items/<slug>.md <to> --playbook specs --state open_item`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `open` | `planned` | `booping set {item} plan={plan index}` linked the item to a plan | `plan` names an existing plan file |
| `open` | `done` | an open item closed without a plan — a tiny fix, an answered question or a recorded decision closed without a plan | — |
| `open` | `dropped` | the item closed without work, `booping set {item} reason=…` first when there is one | — |
| `open` | `clarify` | the item asks the user a question, written in its body | — |
| `clarify` | `open` | the user answered, the answer written in the item's body | — |
| `planned` | `done` | the item closed by hand, or the linked plan reached develop's `done` | — |
| `planned` | `dropped` | the item closed without work, `booping set {item} reason=…` first when there is one | — |
| `planned` | `open` | the item reopened by hand, or the linked plan failed or was cancelled | — |
| `done` | *(terminal)* | — | — |
| `dropped` | *(terminal)* | — | — |

## Step: Guide
Act on the user's request; the scenarios below orient, never restrict — never ask which one to run.
An open item is filed with `booping create core.specs.open_items.template {vault}/open-items --set title=… --set source=… [--set direction=…] [--set record=…] [--set body=…]`;
`direction` is one of `code-to-spec`, `spec-to-code`, `conflict`, `clarify`.

## Handed over

Another playbook hands over a piece of spec material or a question instead of a dialogue. Material:
write it into the record it belongs to, new or existing — a value, or anything dropping or weakening
a rule, as an owner draft; anything else per the autonomy mode. A question: answer it from the records.
Reply in at most five lines: the refs written or found, one line each, then what needs the owner.

## Init

No project tier yet (the preamble lists none, or `booping specs ls` finds no specs): offer to
create it. Once the user agrees, run `booping specs init --tier project`, then walk the user
through [the alignment guide](${CLAUDE_PLUGIN_ROOT}/docs/specs-alignment.md).

## Import

The user brings specs written elsewhere: convert them per [the import guide](${CLAUDE_PLUGIN_ROOT}/docs/specs-import.md) —
English structural headings, area files split into `value` records. Next: `booping specs check`.

## Alignment

The user refines the project's values: read the `value` records, then follow the alignment
guide's order — values first, then the boundaries that follow from them. Next:
`booping specs check` after each record written.

## Auto-review

Read every record type in every tier the project reaches — values, rules, ADRs, conflicts, stories,
ideas, references, runbooks; stale records hide outside the first three. A fix that only makes a
record say what is already decided or true: apply it and report it. A contradiction the records
settle becomes a `conflict` record. Every finding the user must settle becomes an open item at once —
filed with `--set source=manual --set direction=conflict|clarify`, the question in its body, then
`booping transition {vault}/open-items/OI-NNNN.md clarify`;
the user's answer goes into the body and `… open` moves it back. Next: propose Sync specs and
code; do not run it.

## Site review

The user pastes the specs site's Outbox block (`## {ref} — {title}` groups). Per record, check each
comment against the record first: apply it, or skip it when the record already says so. A
`{ref} — reviewed {date}` line sets `reviewed: {date}` — the only case you set `reviewed`, never on
your own initiative. Next: `booping specs check`.

## Record

A decision → an ADR, only for one choice with a real alternative and a reason the code cannot
show. An idea → an idea record. A constraint on how the model works → a rule with `targets` and
`brief`. Next: an ADR with a `Confirmation:` line → file an item with `--set source=adr --set record=adr/NNNN
--set direction=spec-to-code --set title="{the Confirmation: line}"`;
anything else → `booping specs check`.

## Sync specs and code

Compare the records with the code; each gap becomes one item with the direction it runs:
filed with `--set source=sync --set direction=…`. Next: `booping specs scan` for the marks
and check findings.

## Retro to rules

A retrospective awaits learning → hand it to learn. A lesson from this dialogue → a rule record,
written directly. Next: `/playbook learn`, or `booping specs check` after the rule.

## Open items

Show `booping query --config core.specs.open_items.index --where status:in=open,planned`; the user picks. An item
needing no work → `booping set {item} reason="…"` then `booping transition {item} dropped`; a planned
item whose plan was cancelled outside develop → `booping transition {item} open`.
Supervised: next is `/playbook groom` naming the picked ids — groom links them to the plan and stops at its plan review.
Autonomous: run `/playbook groom` naming the picked ids — none picked, every `open` item — then `/playbook develop` on the plan it readies, in this session, without stopping; a groom that splits develops the first plan and reports the parked stubs.
