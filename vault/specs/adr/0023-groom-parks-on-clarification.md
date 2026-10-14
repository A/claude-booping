---
type: adr
title: A groom run with unanswerable questions parks itself in a sidecar
summary: Groom writes questions it cannot answer to clarifications.md, records where to return in return_to, and ends at awaiting-clarification; a later run resumes from the answered file.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [values/0001#plans-run-to-the-end, values/0001#effective-human-review]
rules: [rule/0004]
sources: [CHANGELOG.md, CLAUDE.md]
---

## Context

Grooming settles open questions with the user before a plan reaches
`ready-for-dev` ([rule/0004](../rule/0004-questions-settled-in-grooming.md)). Some
questions a run cannot answer itself, and a run that waits for them holds the
user in the conversation. With a task tracker attached,
the questions also need to reach the issue.

## Decision

Groom has an `awaiting-clarification` status, entered from `framing` and from
`drafting`. The run writes its questions to `clarifications.md` beside `index.md`,
one H2 per question with an id and an `open`/`answered` state, and ends. Each
entering edge stamps `return_to` with its own source status and each return edge
clears it, so the mapping is static per edge rather than computed. A later
invocation reads the answers from the sidecar and resumes; `tracker-comment` posts
the sidecar verbatim to the plan's issue.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Park in a sidecar](#park-in-a-sidecar) | accepted | low | high | The run ends; answers arrive on file |
| [Hold the user in the conversation](#hold-the-user-in-the-conversation) | rejected | low | high | The run waits as long as the question does |
| [A computed return target](#a-computed-return-target) | rejected | low | high | Reason not named in the source |

### Park in a sidecar

Questions go to a file; the run stops at a status that names the wait.

- **Pros:** the user leaves and comes back; the questions are a durable artifact the
  tracker mirror can post.
- **Cons:** a second session to finish grooming.
- **Complexity:** low.
- **Reversibility:** high.

### Hold the user in the conversation

The run asks and waits in the same session.

- **Pros:** no sidecar or extra status.
- **Cons:** the session stays open until the answer exists.
- **Complexity:** low.
- **Reversibility:** high.

### A computed return target

The resume point is worked out at runtime from history.

- **Pros:** not named in the source.
- **Cons:** [clarify] the source chooses a static per-edge `return_to` without naming
  why a computed one was worse.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- The clarifications format is documented in `docs/clarifications.md`.
- `tracker_provider`, `tracker_request` and `tracker_issue` on `index.md` are
  written only by hooks and the tracker CLI.
