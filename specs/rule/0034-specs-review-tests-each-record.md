---
type: rule
title: A specs review tests each record against its type
summary: A review of the specs puts every record to the type tests of the format guide and lists each failure — the type it fits or deletion — for the user to accept.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: accepted
targets: [specs]
brief: "On a review or audit of the specs, put every record to the tests in the format guide's \"When a record is worth writing\" (an ADR needs a real choice, a rule must change behaviour, nothing derivable from config or code, no value restated); list each failure as `{ref} → {type it fits | delete} — {one reason}` for the user to accept."
---

## Rule

A review or an audit of the specs puts every record to the tests in [the format guide](../../src/specs/README.md#when-a-record-is-worth-writing): an ADR needs a real choice with analysed options, a rule must change how the system behaves, nothing restates what config, code or a value already says. Each record that fails is listed as one line — the record, the type it fits or deletion, one reason — for the user to accept per [booping:rule/0033](0033-decisions-listed-for-acceptance.md); nothing is moved or deleted before that (owner, 2026-10-18).

## Follows from

- [Single source](../../vault/value/0003-single-source.md) — a record repeating config, code or a value is a second place to drift.
- [Specs live with the work](../../vault/value/0016-specs-live-with-the-work.md) — a review keeps the set to what earns its place, so it is read and applied.
