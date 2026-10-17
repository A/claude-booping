---
type: adr
title: Open items are a stored index; closed ones are filtered out
summary: Every gap between specs and code, open question or conflict is an open item stored in the vault and listed by an explicit command; closed items stay and are filtered.
created_by: claude
created_at: 2026-10-15
updated_at: 2026-10-17
status: accepted
values: [value/0004, value/0007, value/0009]
---

## Context

Specs and code drift apart both ways: a record promises behaviour the code lacks, the
code does what no record says, a value conflict is open, a `[clarify]` waits for the
owner. The owner wants a log of these that a playbook can take and groom and build
on its own (2026-10-15), and preferred storing items as an index over computing them
on the fly, since creating an ADR already creates an item to confirm.

## Decision

An open item is a file in the vault, `open-items/OI-NNNN.md`, with a status (`open`, `planned`, `done`, `dropped`), the record it concerns (with anchor), its direction (code to spec, spec to code, conflict, clarify) and the plan that works it. Items are created when a record that needs code lands (an ADR with a confirmation line), by a specs sync, by `specs check` findings and from marks; closed items stay and are filtered. The command is explicit: `booping items list` lists the open ones (the index), with the `booping items` subcommands to add and close.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Stored index](#stored-index) | accepted | medium | high | One list a playbook can take |
| [Computed on the fly](#computed-on-the-fly) | rejected | low | high | Loses items no record shows |

### Stored index

Every item is a file; closed ones are filtered out.

- **Pros:** one list across every source; history kept; a playbook works it directly.
- **Cons:** an item can go stale against its record.
- **Complexity:** medium.
- **Reversibility:** high.

### Computed on the fly

Marks, open conflicts and check findings are collected at query time; nothing stored.

- **Pros:** never stale.
- **Cons:** a gap found by a sync or an ADR's pending confirmation has nowhere to live.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- A specs playbook run can take open items, groom them and build them in the
  autonomy mode the project sets ([adr/0027](0027-autonomy-modes.md)).
- Confirmation: creating an ADR with a confirmation line adds an open item; closing its plan closes the item; `booping items list` hides it afterwards.
- 2026-10-15: the store's command is `booping items`, and items include user requests
  filed verbatim (`source: request`/`backlog`) beside spec gaps
  ([adr/0028](0028-one-project-manager.md)).
