---
type: rule
title: The manager delegates heavy reads
summary: The project manager never reviews an artefact, reads a long file or scans many files or logs itself; a subagent does it under a bounded return contract and the manager keeps only the verdict.
created_by: claude
created_at: 2026-10-20
updated_at: 2026-10-20
status: accepted
review: accepted
review_evidence: "owner, 2026-10-20: «Ты project manager, а не team lead или researcher, ты должен был это делегировать, очевидно, запиши… core правила, что project manager делегирует.»"
targets: [project-manager]
brief: "Never do a heavy read yourself — reviewing a worker's artefact (a mockup, a diff, a report file), reading a long file, scanning many files or logs: delegate it to a subagent (booping:booping-researcher or a general-purpose reviewer) with a bounded return contract and keep only the verdict; your own reads are short receipts, status outputs and small targeted lookups."
---

## Rule

The project manager does not do heavy reads in its own context. Reviewing a worker's artefact (a mockup, a diff, a report file), reading a long file, and scanning many files or logs go to a subagent — `booping:booping-researcher` or a general-purpose reviewer — with a bounded return contract (e.g. a verdict in at most five lines). The manager keeps only that verdict.

The manager's own reads are limited to short receipts, status outputs and small targeted lookups.

## Follows from

- [Minimal effective context](../../vault/value/0002-minimal-effective-context.md) — the manager's context carries the whole session; an artefact read into it crowds out the state it exists to hold; in another booping project the manager read a whole ~1.5k-line, ~110 KB HTML mockup into its own context to check it before publishing, where a subagent check returning at most five lines would have done (private note, not published).
- [Bounded agent return contract](0009-bounded-agent-return-contract.md) — the delegated read returns only what the manager needs.
