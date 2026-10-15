---
type: rule
title: Corrections are logged as they happen
summary: When the user corrects the driver, it logs the correction verbatim beside the run artefact, so retro starts from a ready list with links back into the dialogue.
created_by: claude
created_at: 2026-10-15
updated_at: 2026-10-15
status: accepted
targets: [groom, develop, code-review]
brief: "When the user corrects you — rejects a proposal, rewrites an output, says it is wrong, answers a gate other than you suggested — run `booping correction add --target {run artefact} --step {playbook}/{step} --did … --said '{the user's words verbatim}'`, with `--why` when the user states it and `--record {ref}` when the correction names a spec record; a plain confirmation is not a correction."
---

## Rule

When the user corrects you — rejects a proposal, rewrites an output, says it is
wrong, answers a gate other than you suggested — run
`booping correction add --target {run artefact} --step {playbook}/{step} --did … --said '{the user's words verbatim}'`.
Add `--why` when the user states the reason, and `--record {ref}` when the
correction names a spec record. A plain confirmation is not a correction.

The entry lands in `corrections.md` beside the run artefact: the plan directory for
groom and develop, the review's `codereviews/` directory for code-review. Format:
[docs/corrections.md](../../docs/corrections.md).

## Follows from

- [Curated self-learning](../../vault/value/0001-curated-self-learning.md) — a correction is
  logged, not turned into a rule; it reaches a rule only through retro and learn with the user.
- [Analysable history](../../vault/value/0004-analysable-history.md) — the log is plain
  markdown in the vault beside the artefact, with a link back to the dialogue.
- [Corrections log](../../vault/adr/0026-corrections-log.md) — the decision to log
  corrections as they happen instead of mining transcripts at retro.
