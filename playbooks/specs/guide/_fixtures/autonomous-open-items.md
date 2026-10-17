# Input — autonomous-open-items

The project is `taskflow`; the current working directory is its vault root, which lives inside the attached repo, so the project tier is `specs/`. Run date: **2026-10-15**.

This run has no shell, so the `booping` commands were run for you; their outputs:

- Preamble tiers — `project` — `specs/`.
- `booping items list` — cannot run here; it prints the `open` and `planned` items under `open-items/` as a table — read them yourself.
- `/playbook` cannot run here either: name each `/playbook` invocation you run, with its arguments, in your reply.

## Dialogue

**User:** work the open items autonomously

## Context files

<file path="open-items/OI-0001.md">
---
id: OI-0001
title: "The worker package imports no Redis client"
status: open
direction: spec-to-code
record: adr/0001#consequences
source: adr
plan: null
created_at: 2026-10-12
closed_at: null
reason: null
---

# The worker package imports no Redis client
</file>

<file path="open-items/OI-0002.md">
---
id: OI-0002
title: "Retry limit: three attempts or configurable per job type?"
status: open
direction: clarify
record: value/0001#in-practice
source: mark
plan: null
created_at: 2026-10-13
closed_at: null
reason: null
---

# Retry limit: three attempts or configurable per job type?
</file>

<file path="specs/value/0001-one-service-to-run.md">
---
type: value
title: One service to run
summary: "Taskflow runs on one database and one app process; a new stateful service has to pay for its operational cost."
kind: value
created_by: owner
created_at: 2026-09-01
updated_at: 2026-09-01
---

Taskflow runs on one database and one app process; a new stateful service has to pay for
its operational cost before it is added.

## In practice

A feature that needs storage uses Postgres first; a second datastore needs a measured reason.
Retries stop after three attempts [clarify] or a per-job-type limit.

## Trade-off

Some workloads run slower on Postgres than on a dedicated store.
</file>
