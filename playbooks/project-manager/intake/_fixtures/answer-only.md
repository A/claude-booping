# Input — answer-only

The project is `taskflow`; the current working directory is its vault root. Run date: **2026-10-15**. This run covers the `intake` step only; `work` takes the items up later.

This run has no shell, so the `booping` commands were run for you; their outputs:

- `booping items list` — one item, `OI-0001`, in `clarify` (below).
- `booping playbook-transition specs open --state open_item --target open-items/OI-0001.md` — cannot run here; edit the item file yourself the way it would: its `status:` becomes `open`. Nothing else in the frontmatter changes.

## Dialogue

**Manager:** OI-0001 is waiting on you — its question is in `open-items/OI-0001.md`: should the retry limit be three attempts for every job, or configurable per job type?

**User:** Make it configurable per job type, with three attempts as the default when a job type sets nothing.

## Context files

<file path="open-items/OI-0001.md">
---
id: OI-0001
title: "Retry failed jobs"
status: clarify
direction: null
record: null
source: request
plan: null
created_at: 2026-10-14
closed_at: null
reason: null
---

# Retry failed jobs

Failed jobs should be retried automatically instead of staying failed until someone reruns them.

## Question

Should the retry limit be three attempts for every job, or configurable per job type?

- three attempts for every job
- configurable per job type
</file>
