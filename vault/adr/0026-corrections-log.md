---
type: adr
title: Corrections are logged where they happen
summary: Each time the user corrects the model in groom, develop or code-review, a short entry with a link back to the dialogue goes into the run's corrections sidecar — the feed retro and learn read.
created_by: claude
created_at: 2026-10-15
updated_at: 2026-10-18
status: accepted
values: [value/0001, value/0004, value/0015]
---

## Context

Retro today digs the moments the user corrected the model out of session
transcripts. The owner proposed on 2026-10-15 to log them as they happen in groom,
develop, code-review and similar steps, so retro and learn get a ready feed.

## Decision

When the user corrects the model — rejects a proposal, rewrites an output, says it is
wrong, answers a gate other than the agent suggested — the agent records a short
entry, one file in the vault's `corrections/` ([adr/0037](0037-journal-entries-are-vault-files.md)):
the step, what the model did, the user's words verbatim, the reason when stated, the
artefact and the session id, so retro can pull the surrounding conversation. Retro
reads every open entry as its feed and marks what it handled; learn proposes rules
from it. A plain confirmation is not a correction.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Log as it happens](#log-as-it-happens) | accepted | medium | high | A ready feed with links |
| [Mine the transcripts at retro](#mine-the-transcripts-at-retro) | rejected | low | high | What retro does today |

### Log as it happens

A CLI call writes each correction with its session id.

- **Pros:** retro starts from a list; the format is held by code; cross-project history.
- **Cons:** relies on the agent noticing a correction.
- **Complexity:** medium.
- **Reversibility:** high.

### Mine the transcripts at retro

Retro reads whole sessions and finds corrections itself.

- **Pros:** nothing to do during the run.
- **Cons:** expensive in tokens; misses corrections across long sessions.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- Confirmation: a groom run where the user rejects a proposal leaves an open entry in the
  vault's `corrections/` with its session id, and retro lists it.
