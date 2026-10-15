# Input — answer-only

The project is `taskflow`; the current working directory is its vault root. Run date: **2026-10-15**. This run covers the `intake` step only; `work` takes the items up later.

This run has no shell, so the `booping` commands were run for you; their outputs:

- `booping items list` — one open item, `OI-0001` (below).
- `booping items answer OI-0001 C1 --text -` — cannot run here; edit the sidecar yourself the way it would: the stdin text becomes the body under C1's `**Answer:**` label, kept verbatim, and C1's heading's last segment flips from `open` to `answered`. Nothing else in the file changes.

## Dialogue

**Manager:** OI-0001 is waiting on you — one question in `open-items/questions/OI-0001.md#C1`: should the retry limit be three attempts for every job, or configurable per job type?

**User:** Make it configurable per job type, with three attempts as the default when a job type sets nothing.

## Context files

<file path="open-items/OI-0001.md">
---
id: OI-0001
title: "Retry failed jobs"
status: open
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
</file>

<file path="open-items/questions/OI-0001.md">
# Questions — OI-0001

## C1 — retry limit — open

**Asked:** 2026-10-14 — project-manager/work

**Question:** Should the retry limit be three attempts for every job, or configurable per job type?

**Options:**

- three attempts for every job
- configurable per job type

**Answer:**
</file>
