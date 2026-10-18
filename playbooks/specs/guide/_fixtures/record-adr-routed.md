# Input — record-adr-routed

The project is `taskflow`; the current working directory is its vault root, which lives inside the attached repo, so the project tier is `specs/`. Run date: **2026-10-15**. The session is supervised.

This run has no shell and no sub-agents, so the `booping` commands and the scorer were run for you; their outputs:

- Preamble tiers — `project` — `specs/`.
- `booping specs ls --tier project` — one record, `specs/value/0001-one-service-to-run.md`.
- `booping specs next adr --tier project` — `0001`.
- `booping specs ls --tier project --type value --type rule --type adr --exclude adr/0001 --titles` — one line:

  ```
  value/0001  -  One service to run: Taskflow runs on one database and one app process; a new stateful service has to pay for its operational cost.
  ```

- The attached repo's `CLAUDE.md` names no commands or building blocks.
- `booping specs check --tier project` — cannot run here; it checks each record against its type's mdcheck schema (the ADR one is given above) — check a record against it yourself.
- `booping:adr-scorer`, given the scorer prompt you assemble — its reply:

  ```
  {"route":"rule","route_why":"A behaviour picked without weighing an alternative: every handler must return errors one way, a constraint, not a choice.","overlaps":[],"alt_score":0,"missing":[]}
  ```

## Dialogue

**User:** Record an ADR: every API handler returns errors as a JSON body with an `error` field and a matching HTTP status code. That is just how we do it — nothing else was on the table.

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
