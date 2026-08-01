# Input — invalidating-correction

The plan below was refined by `decompose-work` and confirmed by the user at the decomposition
gate. Check every external reference it names against current upstream documentation, correct
what is wrong, and write the step's artifact into the run workdir.

## Run-time context

- project: `helpdesk` — a Django service managed with `uv` that ingests support tickets and
  renders them for agents
- run slug: `20260801-11-40_summarize-support-tickets`
- run workdir: `_runs/groom/20260801-11-40_summarize-support-tickets/`, relative to the current
  working directory
- plan file: `plans/20260801-11-40_summarize-support-tickets.md`, on disk and inlined below

## Inputs

- the confirmed, decomposed plan — the file at the path above; the pinned client appears in a task
  body and in the milestone's `Verify` command, and the task's DoD is written against the API that
  pin exposes
- the decomposition record for the run, with its confirmation stamp
- current upstream documentation for every external reference the plan names — the vendor's own
  docs, release notes, changelogs and package registries, read now rather than recalled

## Context files

<file path="plans/20260801-11-40_summarize-support-tickets.md">
---
title: Summarize long ticket threads for agents
type: feature
status: awaiting-plan-review
sp: 10
split_from: null
created: 2026-08-01
planned: 20260801 11:52
started: null
completed: null
retro: null
goal: null
summary: "Agents opening a long ticket see a short summary of the thread above the messages"
commit: e18a73c9f04b52d6a1c8035ef7b294d16ca07f5b
---

# Summarize long ticket threads for agents

## Context

**Current state** — a ticket page renders every message in order. Threads that ran through several
handovers are dozens of messages long, and an agent picking one up reads the whole history before
answering.

**Motivation** — first-response time on re-opened tickets is roughly double that of fresh ones,
and the agents' own explanation is the read-through.

**Scope** — a generated summary shown above the thread on the ticket page, refreshed when new
messages arrive. Not: summaries in the list view, in notifications, or in the customer-facing
portal.

## Decisions

- **Generation point**: a background job triggered when a thread passes ten messages and again on
  every fifth message after that — synchronous generation would put a network call on the page
  request.
- **Storage**: the summary is a column on the ticket row, replaced in place; no history of past
  summaries is kept.
- **Failure policy**: a generation failure leaves the previous summary in place and the page
  renders without one on the first attempt — the thread itself is never blocked.

## Milestones

### M1: Summary storage and trigger — 4 SP | pending

**Goal**: a ticket carries a summary column and the job that fills it is enqueued at the right
moments.

**Verify**: `just test tests/test_summary_trigger.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add the `summary` and `summary_generated_at` columns with their migration | `tickets/models.py`, `tickets/migrations/0031_ticket_summary.py` | 2 | pending |
| 1.2 | Enqueue the generation job when a thread passes ten messages and on every fifth message after | `tickets/signals.py`, `tickets/tasks.py` | 2 | pending |

#### Task 1.1 DoD

- [ ] The migration applies and reverses cleanly on a copy of the staging database.
- [ ] Both columns are nullable; an existing ticket loads unchanged.

#### Task 1.2 DoD

- [ ] A thread crossing the tenth message enqueues exactly one job.
- [ ] Messages eleven through fourteen enqueue nothing; the fifteenth enqueues one.
- [ ] `just test tests/test_summary_trigger.py` passes.

### M2: Generate the summary — 6 SP | pending

**Goal**: the job turns a thread into a stored summary, and the ticket page renders it.

**Verify**: `uv add openai==0.28.1 && just test tests/test_summarize.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Pin the vendor client at `openai==0.28.1` and call `POST /v1/chat/completions` through it from the generation job, storing the returned text on the ticket | `pyproject.toml`, `tickets/summarize.py` | 3 | pending |
| 2.2 | Render the stored summary above the thread, with the message count it was generated from | `tickets/templates/tickets/detail.html`, `tickets/views.py` | 3 | pending |

#### Task 2.1 DoD

- [ ] `openai.ChatCompletion.create(model=..., messages=[...])` is called once per job with the
      thread rendered as a single user message.
- [ ] The summary text is read off `response["choices"][0]["message"]["content"]` and written to
      the ticket row.
- [ ] `openai.error.RateLimitError` is caught and the job retries once with a backoff; a second
      failure leaves the previous summary in place.
- [ ] `just test tests/test_summarize.py` passes against a stubbed client.

#### Task 2.2 DoD

- [ ] A ticket with a stored summary renders it above the first message, with the message count
      beside it.
- [ ] A ticket without one renders exactly as today.

## Key Files Reference

| File | Role |
|------|------|
| `tickets/summarize.py` | the generation job: builds the prompt, calls the vendor, stores the text |
| `tickets/signals.py` | the message-count trigger |
| `tickets/templates/tickets/detail.html` | where the summary is rendered |

## Final Verification

- [ ] A thread past ten messages gets a summary within one job cycle, and it is visible on the
      ticket page.
- [ ] A vendor failure leaves the page renderable and the previous summary intact.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Summaries in the ticket list, in notifications and in the customer portal.
- Any history of past summaries.
</file>

<file path="_runs/groom/20260801-11-40_summarize-support-tickets/decomposition.md">
---
reviewed_at: 20260801 11:52
---
# Decomposition — 20260801-11-40_summarize-support-tickets

## Verdict

Skipped — no task sits at or over the 5 SP re-decompose threshold (the largest is 3 SP), and the
sprint totals 10 SP, well under the 35 SP split threshold. The plan file was not touched.
</file>
