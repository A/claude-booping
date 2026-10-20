---
type: rule
title: The ADR scorer judges its prompt alone
summary: The adr-scorer runs only its body render and judges a draft ADR from the pasted parts alone; nothing it was not shown exists for it.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: accepted
targets: [agent:adr-scorer]
brief: "Run no command but your body render and read no file — no codebase, vault or web. Judge from the pasted parts alone: an alternative, record or primitive they do not show does not exist."
---

## Rule

The only command the scorer runs is its body render. It reads no file, runs no other
command and consults no codebase, vault or web; it judges the draft ADR from the parts its
prompt pastes, and an alternative, record or primitive they do not show does not exist.
Its `tools:` Bash pattern exposes Bash without restricting the command, so this rule and
the eval's tools assert are the guard.

## Follows from

- [adr/0041](../../vault/adr/0041-adr-scorer-reads-the-guide-and-the-record-inventory.md) — the
  scorer is given exactly what it judges.
- [Proven to work](../../vault/value/0010-proven-to-work.md) — a score drawn from a fixed input
  is reproducible, so the eval measures the scorer and not what it happened to find.
- [Minimal effective context](../../vault/value/0002-minimal-effective-context.md) — the pasted
  parts are what the judgement needs.
