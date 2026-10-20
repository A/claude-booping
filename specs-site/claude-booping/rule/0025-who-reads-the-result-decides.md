---
type: rule
title: Who reads the result decides prose or code
summary: A command, key or check exists when code reads its result or it supplies a fact the model cannot see; the rest is prose, the default when unsure.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-18
status: accepted
targets: [groom, specs, playbook-authoring, code-review]
brief: "Decide prose or code by who reads the result. Code reads it (a guard, a status report, another command, a slice of entries filled into a prompt at render time) or it is a fact outside the model's view (the time, the session id, a process, a transcript, many files at once) → a CLI, extending an existing one first. Only a model or a human reads it (instructions, a mode of behaviour, findings, a note someone reviews) → prose, with a format doc if the shape matters. Count only readers that exist today or that the request names, never code your own design would add. Exact transforms the model was measured to get wrong are the one exception. When unsure, prose with a fixed format; a CLI over it is a later optimisation."
sources: [vault/reference/0009-prose-or-code-probes-2026-10.md]
---

## Rule

Who reads the result decides where it is produced.

- Code reads it, or it is a fact outside the model's view → a CLI, extending or generalising an
  existing one first. Code reads it: a guard, a status report, another command, a slice of entries
  filled into a prompt at render time. Facts outside the model's view: the current time, the session
  id, a process, a transcript, many files at once.
- Only a model or a human reads it — instructions, a mode of behaviour, findings, a note someone
  reviews → prose, with a format doc if the shape matters.
- Count only readers that exist today or that the request names. Code the proposed design would add
  to read the result does not count: a config key read only by the template branch it was made for
  justifies neither.
- Exact transforms the model was measured to get wrong are the one exception (adr/0031).
- When unsure, choose prose with a fixed format. A CLI over that format is a later optimisation, taken
  when code starts to read it.

What code produces is trusted: a transition's printed mutation report is authoritative, and the
runner does not re-read frontmatter to verify it.

## Follows from

- [Deterministic where code reads it](../value/0015-deterministic-where-code-reads-it.md) — code
  produces what code reads; prose holds the rest.
- [Quality at a rational cost](../value/0012-quality-at-a-rational-cost.md) — every command and key is
  code to keep; a mechanism without a reader is cost without gain.
- [Prose or code probes](../reference/0009-prose-or-code-probes-2026-10.md) — the wording that held
  on every probe, and the old "whatever can be computed" wording that pushed prose tasks into code.
