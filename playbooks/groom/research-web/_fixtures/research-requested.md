# Input — export admission control (web research requested)

Intake recorded the user's web-research decision in the `### Web research` line of `## Framing`.
Read that line and execute it.

## Run-time context

- project: `ledger-reporting` — an internal reporting service exposing an HTTP API, deployed as
  several identical processes behind a load balancer, with a shared cache tier already in the
  deployment
- run slug: `20260801-export-admission-control`
- run workdir: the plan directory `plans/20260801-export-admission-control/`, relative to the
  current working directory — it already holds `index.md` and `plan.md`

## Inputs

- the run's `index.md`, on disk: `## Framing` with intake's web-research decision, and
  `## Blast radius` with the surfaces the codebase pass mapped and the calls it left open

## Context files

<file path="plans/20260801-export-admission-control/index.md">
---
status: researching
---
# Export admission control

## Framing

### Request

> Big CSV exports are taking the reporting API down. When four or five of them land at once,
> every other request times out. I want the export endpoint to admit only what the service can
> actually carry and tell the rest to come back later, instead of everything degrading together.

### Restated problem

The synchronous export endpoint runs unbounded: every accepted request holds a worker for the
whole render, so a handful of concurrent exports starves the pool that also serves ordinary
reads. The request is to put an admission decision in front of the endpoint — a bounded number
of exports in flight, a bounded wait for the rest, and an explicit refusal past that — so
overload is confined to the exports and stays visible to the caller instead of surfacing as
timeouts everywhere.

### Task type

`feature` — a new user-facing capability: callers gain a documented budget and a defined
refusal contract. Not a bug (the endpoint does what it was written to do; the writing is what is
wrong) and not a refactoring (request handling changes behaviour, not just structure).

### Scope boundaries

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

### Web research

Requested — the user asked for the current practice on bounded admission before the design is
settled: "look at how this is actually done today, we have never built one of these".

### Scope challenge

- [x] Can a refused caller queue instead of being refused? — no; past the wait budget the
      refusal is immediate. Queueing belongs to the background-job plan.
- [x] Is the budget service-wide or per caller? — service-wide concurrency, plus a per-caller cap
      so one caller cannot take the whole budget.
- [x] Any dependency you already know this must not pull in? — none named; a new library is
      acceptable if it earns its place.

## Blast radius

### Touched surfaces

| Surface           | Where                                       | Why it moves                                                        | Risk                                                     |
| ----------------- | ------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------- |
| Export endpoint   | `app/api/exports.py` (`post_export`)        | the admission decision sits in front of it                          | high — every export caller goes through this handler      |
| Shared cache tier | `app/cache.py` (`get_client`)               | the only cross-process state the deployment already runs            | medium — never used for coordination, only for read cache |
| Error contract    | `app/api/errors.py` (`error_response`)      | the refusal needs a documented response shape callers code against  | medium — the shape is public to every API consumer        |

### Prior art

- no prior art in the repository: every endpoint accepts whatever arrives and runs it to
  completion, and the cache tier has never carried coordination state

### Conventions in play

- `docs/api-contract.md` requires every non-2xx response to carry the `error_response` envelope,
  so a refusal cannot invent its own body
- `pyproject.toml` pins runtime dependencies explicitly; a new library needs a stated reason in
  the plan's Decisions section

### Unknowns for design

- where the admission decision lives: in the handler, in middleware, or in front of the worker
  pool
- how the bounded wait is expressed to a caller that is eventually refused — a header, a body
  field, or both
</file>
