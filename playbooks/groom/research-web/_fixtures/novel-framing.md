# Input — export admission control

The framing below was confirmed by the user at the end of `intake`. Research current external
practice for it and write the step's artifact into the run workdir.

## Run-time context

- project: `ledger-reporting` — an internal reporting service exposing an HTTP API, deployed as
  several identical processes behind a load balancer, with a shared cache tier already in the
  deployment
- run slug: `20260801-10-15_export-admission-control`
- run workdir: `_runs/groom/20260801-10-15_export-admission-control/`, relative to the current
  working directory — it already holds the confirmed framing

## Inputs

- the confirmed framing — `_runs/groom/20260801-10-15_export-admission-control/intake.md`, on
  disk; confirmed by the user, every scope-challenge question answered
- the uncertainty signals intake recorded:
  - the service has never taken an admission or rate-limiting dependency, and its shared cache
    tier has never been used for cross-process coordination — this would be the first of both
  - bounded admission itself has no prior art in the repository: every endpoint today accepts
    whatever arrives and runs it to completion, so there is no in-house shape to copy

## Context files

<file path="_runs/groom/20260801-10-15_export-admission-control/intake.md">
---
reviewed_at: 20260801 10:22
---
# Intake — export admission control

## Request

> Big CSV exports are taking the reporting API down. When four or five of them land at once,
> every other request times out. I want the export endpoint to admit only what the service can
> actually carry and tell the rest to come back later, instead of everything degrading together.

## Restated problem

The synchronous export endpoint runs unbounded: every accepted request holds a worker for the
whole render, so a handful of concurrent exports starves the pool that also serves ordinary
reads. The request is to put an admission decision in front of the endpoint — a bounded number
of exports in flight, a bounded wait for the rest, and an explicit refusal past that — so
overload is confined to the exports and stays visible to the caller instead of surfacing as
timeouts everywhere.

## Task type

`feature` — a new user-facing capability: callers gain a documented budget and a defined
refusal contract. Not a bug (the endpoint does what it was written to do; the writing is what is
wrong) and not a refactoring (request handling changes behaviour, not just structure).

## Scope boundaries

**In scope**

- the admission decision in front of the export endpoint: how many exports run at once, how long
  a waiting caller is held, and what a refused caller is told
- the shared state that decision needs across the service's processes
- the refusal response contract callers code against

**Out of scope**

- the CDN and the reverse proxy in front of the service — they belong to the platform team and
  cannot see the caller's plan tier or the cost of an export, so no admission logic is to live
  there
- making the export itself faster, and moving exports onto a background job queue — each is its
  own plan

## Scope challenge (answered)

- [x] Can a refused caller queue instead of being refused? — no; past the wait budget the
      refusal is immediate. Queueing belongs to the background-job plan.
- [x] Is the budget service-wide or per caller? — service-wide concurrency, plus a per-caller cap
      so one caller cannot take the whole budget.
- [x] Any dependency you already know this must not pull in? — none named; a new library is
      acceptable if it earns its place.
</file>
