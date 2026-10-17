---
type: adr
title: Journal entries are vault files built from existing primitives
summary: A correction or an agent decision is one vault file with frontmatter, made by scaffold, moved by frontmatter-update and sliced by query; an item's question is its clarify status; no journal command.
created_by: owner
created_at: 2026-10-18
updated_at: 2026-10-18
status: accepted
values: [value/0015, value/0012, value/0011]
rules: [rule/0025]
issues: []
sources: [vault/reference/0009-prose-or-code-probes-2026-10.md]
---

## Context

Three append-only journals had their own commands: `booping correction add|list` (a transcript lookup
proving the quote, a dialogue link), `booping defaults add` and `booping items ask|answer` (an
`open`/`answered` marker and a two-part answered test) — about 550 lines and 35 e2e cases. Code reads
two of them: retro's prompt is filled with the open corrections at render time, and the manager
reviews the open agent decisions. Each entry also needs the time and the session id, facts outside the
model's view (rule/0025). Item questions are read by `booping status` only to say an item waits on the
user; plan questions are read by the groom driver when it resumes and posted verbatim to the tracker.
Building nothing — retro mining transcripts — was rejected by adr/0026 for its token cost and loses the
review of agent decisions.

## Criteria

- What code reads comes from code; what only a model reads stays prose (rule/0025).
- No new command where an existing primitive does the job.

## Decision

A journal entry is one vault file with YAML frontmatter, built from primitives booping already has.
`booping scaffold core.<journal>.scaffold <dir> --set name=… --set …` writes it from a config template,
whose macros stamp the time and the session id; `booping frontmatter-update` moves its `state`;
`booping query` slices entries by frontmatter, at render time inside a template or on the command line.

- `corrections/` — `step`, `did`, `said`, `why`, `state: open | handled`; retro takes every open entry
  and marks what it handled.
- `agent-decisions/` (was `defaults`) — `step`, `asked`, `decision`, `why`, `state: open | reviewed`.
- An open item's question is its status: the item machine gains `clarify` (`open → clarify` when it
  asks, `clarify → open` when answered), moved by `booping playbook-transition --state open_item`; the
  question and the answer are prose in the item's body. `booping status` lists `clarify` items as
  waiting on the user.
- A plan's questions stay prose in its `clarifications.md` by the format doc; the plan's
  `awaiting-clarification` status is what waits on the user.

There is no journal command, no field DSL and no entry parser. Obsidian reads the entries as notes and
can table them with a Base, as it does plans.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Entries as files over existing primitives](#entries-as-files-over-existing-primitives) | accepted | low | high | No new code; every reader is an existing command |
| [One journal command](#one-journal-command) | rejected | medium | high | A second way to store records and a fragile parser |
| [Entries as open items](#entries-as-open-items) | rejected | low | high | Corrections would enter the work queue |
| [One prose file per journal](#one-prose-file-per-journal) | rejected | low | high | Code reads the slices; the model cannot stamp time and session |

### Entries as files over existing primitives

The decision above.

- **Pros:** no new code; `scaffold`, `frontmatter-update` and `query` are already tested; entries are
  native vault notes.
- **Cons:** many small files; an entry's id is its file name, given by the caller; fields are not
  validated.
- **Complexity:** low.
- **Reversibility:** high.

### One journal command

`booping journal add|set|list` over `core.journals.<name>` with typed fields, entries as H2 sections of
one file per journal; built and then discarded on 2026-10-18.

- **Pros:** one readable file per journal; short sequential ids; enum values checked.
- **Cons:** about 200 lines and a field DSL; an entry parser that breaks on `**Label:**` or `## `
  inside a text field; records stored differently from every other vault record.
- **Complexity:** medium.
- **Reversibility:** high.

### Entries as open items

A correction or a decision is an open item with a kind.

- **Pros:** id allocation, states and listing already exist.
- **Cons:** open items are the manager's work queue; excluding corrections and decisions from it is new
  code, and an item's lifecycle does not fit a log entry.
- **Complexity:** low.
- **Reversibility:** high.

### One prose file per journal

The driver appends entries by a format doc, with no command at all.

- **Pros:** nothing to build or keep.
- **Cons:** retro's render-time slice and the manager's review are read by code; the model does not
  know the time or its session id.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- `booping journal`, `core.journals` and `docs/journals.md` are removed with the commands they replaced;
  the vault-root `corrections.md` and `agent-decisions.md` give way to the two directories.
- The open item machine gains `clarify`; `open-items/questions/` goes.
- `clarifications.md` keeps its prose format doc; groom writes it by hand.
- The repo guide lists what each booping subcommand can do, not only its name: given names only, a
  fresh model generalised the old journal commands into a new one; told what `scaffold`, `query` and
  `frontmatter-update` do, it chose this decision every time (reference/0009).
