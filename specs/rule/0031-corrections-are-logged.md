---
type: rule
title: Corrections are logged as they happen
summary: When the user corrects the driver, it logs the correction verbatim as a file under the vault's corrections/, so retro starts from a ready list of what is not yet handled.
created_by: claude
created_at: 2026-10-15
updated_at: 2026-10-18
status: accepted
targets: [groom, develop, code-review]
brief: "When the user corrects you — rejects a proposal, rewrites an output, says it is wrong, answers a gate other than you suggested — run `booping create core.corrections.template {vault}/corrections --set name=$(date +%Y%m%d-%H%M%S)-{step} --set step={playbook}/{step} --set did=… --set said='{the user's words verbatim}' --set artifact={run artefact, vault-relative}`, with `--set why=…` when the user states it; a plain confirmation is not a correction."
---

## Rule

When the user corrects you — rejects a proposal, rewrites an output, says it is
wrong, answers a gate other than you suggested — run
`booping create core.corrections.template {vault}/corrections --set name=$(date +%Y%m%d-%H%M%S)-{step} --set step={playbook}/{step} --set did=… --set said='{the user's words verbatim}' --set artifact={run artefact, vault-relative}`.
Add `--set why=…` when the user states the reason. A plain confirmation is not a
correction.

One file per correction under `{vault}/corrections/`, its frontmatter stamped with the
session id and the time; fields: `core.corrections.template`.

## Follows from

- [Curated self-learning](../../vault/value/0001-curated-self-learning.md) — a correction is
  logged, not turned into a rule; it reaches a rule only through retro and learn with the user.
- [Analysable history](../../vault/value/0004-analysable-history.md) — the log is plain
  markdown in the vault, with the session it came from.
- [Corrections log](../../vault/adr/0026-corrections-log.md) — the decision to log
  corrections as they happen instead of mining transcripts at retro.
- [Journal entries are vault files](../../vault/adr/0037-journal-entries-are-vault-files.md) —
  one file per correction, written by `booping create`.
