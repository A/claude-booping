---
type: value
title: Deterministic where code reads it
summary: What code reads, and every fact outside the model's view, is produced by code; what only a model or a human reads stays prose with a fixed format until code starts to read it.
kind: value
created_by: owner
created_at: 2026-10-15
updated_at: 2026-10-18
---

What code reads — a guard, a status report, another command, a slice filled into a prompt at render
time — and every fact outside the model's view — the time, the session id, a process, a transcript,
many files at once — is produced by code, so it is the same on every model and every run. What only a
model or a human reads — instructions, a mode of behaviour, findings, a note someone reviews — stays
prose, with a fixed format when its shape matters. Code over that format is an optimisation, taken
when a reader in code appears; a reader that only the proposed design would add does not count.

## In practice

Playbooks render by code, rules and config values are injected by code, state transitions and their
hooks run as code, and a transition's printed report is trusted without re-reading. Whether a run is
autonomous is prose (adr/0036); journal entries are vault files that rendered prompts slice through `query`
(adr/0037).

## Trade-off

Prose drifts from its format where no code checks it; a format fixed in `docs/` keeps the later move
to code cheap.
