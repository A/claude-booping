# Input — record-decision

The project is `taskflow`; the current working directory is its vault root, which lives inside the attached repo, so the project tier is `specs/`. Run date: **2026-10-15**.

This run has no shell, so the `booping` commands were run for you; their outputs:

- Preamble tiers — `project` — `specs/`.
- `booping specs ls --tier project` — one record, `specs/value/0001-one-service-to-run.md`.
- `booping specs ls --tier project --type value --type rule --type adr --exclude adr/0001 --titles` — one line:

  ```
  value/0001  -  One service to run: Taskflow runs on one database and one app process; a new stateful service has to pay for its operational cost.
  ```

- The attached repo's `CLAUDE.md` names no commands or building blocks.
- `booping specs next adr --tier project` — `0001`.
- `booping specs check --tier project` — cannot run here; it checks each record against its type's mdcheck schema (the ADR one is given above) — check the ADR against it yourself.
- `booping:adr-scorer`, given the scorer prompt you assemble — cannot run here (no sub-agents); its reply was `{"route":"adr","route_why":"A real choice between Postgres and Redis for the queue, with a reason the code does not show.","overlaps":["value/0001"],"alt_score":3,"missing":[]}`.
- `booping create core.specs.open_items.template open-items --set source=adr --set record=adr/0001 …` — cannot run here; write the file it would create yourself: `open-items/OI-0001.md`, frontmatter `id: OI-0001`, `title` (the ADR's `Confirmation:` text, first sentence), `status: open`, `direction: spec-to-code`, `record: adr/0001#consequences`, `source: adr`, `plan: null`, `created_at: 2026-10-15`, `closed_at: null`, `reason: null`, then `# {title}`.

## Dialogue

**User:** We decided to keep the job queue in Postgres, using `SELECT … FOR UPDATE SKIP LOCKED`, instead of adding Redis with a queue library. Redis would give us faster dequeues, but it is a second stateful service to run, back up and monitor, and our load is a few hundred jobs a minute — Postgres handles that. Confirmation: the worker package imports no Redis client and `docker-compose.yml` defines no Redis service.

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
