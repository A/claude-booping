# Input — record-adr-brief

The project is `taskflow`; the current working directory is its vault root, which lives inside the attached repo, so the project tier is `specs/`. Run date: **2026-10-15**. The session is supervised.

This run has no shell and no sub-agents, so the `booping` commands and the scorer were run for you; their outputs:

- Preamble tiers — `project` — `specs/`.
- `booping specs ls --tier project` — one record, `specs/value/0001-one-service-to-run.md`.
- `booping specs ls --tier project --type value --type rule --type adr --exclude adr/0001 --titles` — one line:

  ```
  value/0001  -  One service to run: Taskflow runs on one database and one app process; a new stateful service has to pay for its operational cost.
  ```

- The attached repo's `CLAUDE.md` names no commands or building blocks.
- `booping specs next adr --tier project` — `0001`.
- `booping specs check --tier project` — cannot run here; it checks each record against its type's mdcheck schema (the ADR one is given above) — check the ADR against it yourself.
- `booping:adr-scorer`, given the scorer prompt you assemble — its reply:

  ```
  {"route":"adr","route_why":"A real choice between three retry policies, with a reason the code does not show.","overlaps":[],"alt_score":2,"missing":["retries left to the job runner's existing retry setting, extended with a backoff list"]}
  ```

## Dialogue

**User:** Let's record the decision: job retries use a fixed exponential backoff — 10 s, 1 min, 10 min, then the job is marked failed. We weighed a per-job-type retry policy in the job table, but nobody needs it yet and it adds a column every job type must fill; we also weighed no retries at all, letting the user re-run a failed job by hand, which is the cheapest but loses jobs that fail on a short outage. Record it as an ADR.

## Context files

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

## Trade-off

Some workloads run slower on Postgres than on a dedicated store.
</file>
