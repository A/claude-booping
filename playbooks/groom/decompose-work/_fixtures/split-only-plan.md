# Input — notification center

The plan below was written by `draft-plan` against the `backend` template and cross-reviewed in
place; the user has not read it yet. Refine it against the sizing thresholds and write the
`## Refinement` section of the run's `index.md`.

## Run-time context

- project: `helio` — a team-collaboration SaaS: a Django backend and a React web client in one
  repository
- run slug: `20260801-notification-center`
- run workdir: the plan directory `plans/20260801-notification-center/`, relative to the
  current working directory — its `index.md` already carries the framing, the blast radius
  and the confirmed design
- plan file: `plans/20260801-notification-center/plan.md`, on disk, written and complete

## Inputs

- the written plan — `plans/20260801-notification-center/plan.md`, on disk: 6 milestones,
  per-task and per-milestone story points, the sprint total mirrored in its `sp:` frontmatter
- the re-decompose threshold — **5 SP**: a task at or over it needs another pass before a single
  agent briefing can carry it
- the split threshold — **35 SP**: a sprint total past it should be proposed as two siblings
- the SP scale:
  - 1 — simple text/config change, no risk
  - 2 — simple task, predictable, no risk
  - 3 — medium task, minor risks but predictable overall
  - 4 — complex task, medium risk, may need small research but clear enough
  - 5 — research task: the developer would have to clarify and decompose it further before
    proceeding
- rework from the user: none — this is the run's first pass through decomposition

## Context files

<file path="plans/20260801-notification-center/index.md">
---
status: decomposing
---
# Notification center

## Framing

### Request

> Members get in-app and email notifications for the events they care about, on their own schedule

### Restated problem

**Current state** — three features send email directly from their own view code: mentions,
invitations and the weekly summary. Each builds its own message, each has its own opt-out column,
and nothing is recorded in-app. A member who misses an email has no way to see what happened.

**Motivation** — every new feature that wants to notify someone re-invents delivery, and support
cannot answer "was I notified?". The work is to put one pipeline behind all of them and give
members a place to read and tune their notifications.

**Scope** — an event → notification pipeline with in-app and email transports, and a preference
surface members control. Not: push notifications, SMS, or a notification API for third parties.

### Task type

`feature` — classified at intake and unchanged since.

### Scope boundaries

**In scope**

- M1: Event intake
- M2: Fan-out and dedupe
- M3: Transports and the in-app feed
- M4: Preference model and API
- M5: Preferences UI
- M6: Digest schedule

**Out of scope**

- Push and SMS transports.
- A third-party notification API.
- Per-workspace notification policy set by admins.

### Web research

Not requested — the request asks for no deep web research, and the user asked for none
when the scope questions came back.

### Scope challenge

- [x] Anything the request pulls in that it does not state? — answered at intake;
      the boundaries above are what the answers settled.

## Blast radius

### Touched surfaces

| Surface | Where | Why it moves | Risk |
| --- | --- | --- | --- |
| api.py | `helio/notifications/api.py` | the single entry point every producer calls | medium — the plan changes what it does |
| preferences.py | `helio/notifications/preferences.py` | defaults in M2, stored choices in M4 — one interface | medium — the plan changes what it does |
| fanout.py | `helio/notifications/fanout.py` | where an event becomes notifications | medium — the plan changes what it does |
| Preferences.tsx | `web/src/notifications/Preferences.tsx` | the member-facing control surface | medium — the plan changes what it does |

### Prior art

- `helio/notifications/api.py` — the closest existing shape this work follows

### Conventions in play

- the project's own lint / typecheck / test gate runs on every change under these
  surfaces, and the plan's Final Verification restates it

### Unknowns for design

- none left open: the design below settles every call the map raised

## Design

### Approach

Producers call `notify(event)` (`helio/notifications/api.py`), which writes a `NotificationEvent`
row and enqueues fan-out. The fan-out task (`helio/notifications/fanout.py`) expands an event into
one `Notification` per recipient per transport, consulting `PreferenceResolver` — which, until M4
lands, answers every question with the built-in default. Transports
(`helio/notifications/transports/`) render and deliver. The React client reads the in-app feed from
`/api/notifications/` and, from M5, edits preferences at `/api/notifications/preferences/`.

### Surface changes

- `helio/notifications/api.py` — the single entry point every producer calls
- `helio/notifications/preferences.py` — defaults in M2, stored choices in M4 — one interface
- `helio/notifications/fanout.py` — where an event becomes notifications
- `web/src/notifications/Preferences.tsx` — the member-facing control surface

### Alternatives

- none survived the blast radius: the approach above is the only one the mapped
  surfaces support

### Trade-offs

- **Events, not messages**: producers emit a typed domain event; rendering a message per transport
  is the pipeline's job, so a new transport needs no producer change.
- **Ship with defaults**: until a member changes anything, every notification type is on and
  delivered immediately — the pipeline is complete and useful before any preference exists.
- **Idempotency by event key**: fan-out dedupes on `(event_key, recipient, transport)` so a retried
  producer cannot double-notify.

### Risks

- the change lands across several call sites at once — mitigated by the plan's own
  Final Verification pass
</file>

<file path="plans/20260801-notification-center/plan.md">
---
title: Notification center
type: feature
status: in-spec
sp: 41
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Members get in-app and email notifications for the events they care about, on their own schedule"
commit: null
---

# Notification center

## Context

**Current state** — three features send email directly from their own view code: mentions,
invitations and the weekly summary. Each builds its own message, each has its own opt-out column,
and nothing is recorded in-app. A member who misses an email has no way to see what happened.

**Motivation** — every new feature that wants to notify someone re-invents delivery, and support
cannot answer "was I notified?". The work is to put one pipeline behind all of them and give
members a place to read and tune their notifications.

**Scope** — an event → notification pipeline with in-app and email transports, and a preference
surface members control. Not: push notifications, SMS, or a notification API for third parties.

## Decisions

- **Events, not messages**: producers emit a typed domain event; rendering a message per transport
  is the pipeline's job, so a new transport needs no producer change.
- **Ship with defaults**: until a member changes anything, every notification type is on and
  delivered immediately — the pipeline is complete and useful before any preference exists.
- **Idempotency by event key**: fan-out dedupes on `(event_key, recipient, transport)` so a retried
  producer cannot double-notify.

## Architecture

Producers call `notify(event)` (`helio/notifications/api.py`), which writes a `NotificationEvent`
row and enqueues fan-out. The fan-out task (`helio/notifications/fanout.py`) expands an event into
one `Notification` per recipient per transport, consulting `PreferenceResolver` — which, until M4
lands, answers every question with the built-in default. Transports
(`helio/notifications/transports/`) render and deliver. The React client reads the in-app feed from
`/api/notifications/` and, from M5, edits preferences at `/api/notifications/preferences/`.

## Milestones

### M1: Event intake — 8 SP | pending

**Goal**: producers emit typed events and every event is durably recorded.

**Verify**: `just test helio/notifications/tests/test_api.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `NotificationEvent` model, migration and the typed event registry | `helio/notifications/models.py`, `helio/notifications/events.py` | 4 | pending |
| 1.2 | `notify()` entry point and the three existing producers moved onto it | `helio/notifications/api.py`, `helio/mentions/views.py`, `helio/invites/views.py` | 4 | pending |

#### Task 1.1 DoD

- [ ] An event type declares its payload schema and its default transports in one place.
- [ ] An unknown event type is rejected at emit time with a message naming it.
- [ ] Migration applies and reverses cleanly.

**Verify**: `just test helio/notifications/tests/test_events.py`

#### Task 1.2 DoD

- [ ] `notify(event)` records the event and enqueues fan-out in one transaction.
- [ ] Mentions and invitations emit events instead of sending mail directly; their old send paths
      are deleted.
- [ ] The weekly summary keeps its own path until M6 and is untouched here.

**Verify**: `just test helio/notifications/tests/test_api.py`

---

### M2: Fan-out and dedupe — 7 SP | pending

**Goal**: one event becomes exactly one notification per recipient per transport, once.

**Verify**: `just test helio/notifications/tests/test_fanout.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Fan-out task: recipients, transports, `Notification` rows | `helio/notifications/fanout.py`, `helio/notifications/models.py` | 4 | pending |
| 2.2 | `PreferenceResolver` returning the built-in defaults | `helio/notifications/preferences.py` | 3 | pending |

#### Task 2.1 DoD

- [ ] A retried event produces no duplicate rows — unique on `(event_key, recipient, transport)`.
- [ ] A recipient who lost access between emit and fan-out is skipped.
- [ ] Fan-out for 500 recipients stays inside one task run.

**Verify**: `just test helio/notifications/tests/test_fanout.py`

#### Task 2.2 DoD

- [ ] `PreferenceResolver.allows(recipient, event_type, transport)` answers from the event
      registry's defaults.
- [ ] Its interface is the one M4 will back with stored preferences — no caller changes then.

**Verify**: `just test helio/notifications/tests/test_preferences.py`

---

### M3: Transports and the in-app feed — 7 SP | pending

**Goal**: notifications are delivered by email and readable in the app.

**Verify**: `just test helio/notifications/ && just test-web notifications`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Email transport: per-type templates, retry and failure recording | `helio/notifications/transports/email.py` | 4 | pending |
| 3.2 | In-app feed endpoint and the client's notification list | `helio/notifications/views.py`, `web/src/notifications/Feed.tsx` | 3 | pending |

#### Task 3.1 DoD

- [ ] Each event type renders a subject and body from its own template.
- [ ] A provider failure is retried with backoff and recorded on the notification row after the
      last attempt.
- [ ] No email is sent for a notification `PreferenceResolver` disallowed.

**Verify**: `just test helio/notifications/tests/test_email.py`

#### Task 3.2 DoD

- [ ] `GET /api/notifications/` returns the caller's notifications, newest first, paginated.
- [ ] Marking one read is reflected in the unread badge without a reload.
- [ ] The feed renders every event type through one component.

**Verify**: `just test-web notifications`

---

### M4: Preference model and API — 7 SP | pending

**Goal**: a member's stored choices override the defaults, everywhere.

**Verify**: `just test helio/notifications/tests/test_preferences.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `NotificationPreference` model, migration, and resolver precedence | `helio/notifications/models.py`, `helio/notifications/preferences.py` | 4 | pending |
| 4.2 | Preferences REST endpoint with per-type, per-transport writes | `helio/notifications/views.py`, `helio/notifications/serializers.py` | 3 | pending |

#### Task 4.1 DoD

- [ ] A stored preference wins over the event type's default; an absent one falls back to it.
- [ ] The three legacy opt-out columns are migrated into preference rows and dropped.
- [ ] Fan-out consults the resolver unchanged — no call-site edits.

**Verify**: `just test helio/notifications/tests/test_preferences.py`

#### Task 4.2 DoD

- [ ] `GET /api/notifications/preferences/` returns every type with its effective value and whether
      it is stored or default.
- [ ] `PATCH` writes one type/transport pair at a time and rejects unknown types.

**Verify**: `just test helio/notifications/tests/test_preferences_api.py`

---

### M5: Preferences UI — 6 SP | pending

**Goal**: members tune their notifications from settings.

**Verify**: `just test-web notifications-preferences`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Preferences screen: grouped types, per-transport toggles | `web/src/notifications/Preferences.tsx` | 3 | pending |
| 5.2 | Optimistic writes with rollback and an inline error state | `web/src/notifications/usePreferences.ts` | 3 | pending |

#### Task 5.1 DoD

- [ ] Every event type appears grouped by product area with its effective value.
- [ ] A default-valued row is visibly distinguished from a stored one.
- [ ] The screen is reachable from settings and keyboard-navigable.

**Verify**: `just test-web notifications-preferences`

#### Task 5.2 DoD

- [ ] A toggle applies immediately and rolls back with an inline error when the write fails.
- [ ] Two rapid toggles on the same row resolve to the last one.

**Verify**: `just test-web notifications-preferences`

---

### M6: Digest schedule — 6 SP | pending

**Goal**: members can batch notifications into a daily or weekly digest instead of immediate mail.

**Verify**: `just test helio/notifications/tests/test_digest.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Digest scheduling: hold, batch and send per member cadence | `helio/notifications/digest.py` | 3 | pending |
| 6.2 | Cadence control in the preferences screen; retire the weekly-summary path | `web/src/notifications/Preferences.tsx`, `helio/summary/tasks.py` | 3 | pending |

#### Task 6.1 DoD

- [ ] A member on a daily cadence receives one mail holding the day's notifications.
- [ ] Switching cadence flushes whatever is held.
- [ ] Immediate remains the default for members who never chose.

**Verify**: `just test helio/notifications/tests/test_digest.py`

#### Task 6.2 DoD

- [ ] Cadence is selectable per member in the preferences screen.
- [ ] The legacy weekly-summary task is deleted and its recipients land on the weekly cadence.

**Verify**: `just test helio/notifications/tests/test_digest.py && just test-web notifications-preferences`

## Implementation Order

```
M1 → M2 → M3
             ↓
           M4 → M5 → M6
```

M1–M3 deliver notifications end to end on the built-in defaults. M4 needs the resolver interface
M2 defines and the transports M3 delivers through; M5 needs M4's endpoint; M6 needs M5's screen and
M3's email transport.

## Key Files Reference

| File | Role |
|------|------|
| `helio/notifications/api.py` | the single entry point every producer calls |
| `helio/notifications/preferences.py` | defaults in M2, stored choices in M4 — one interface |
| `helio/notifications/fanout.py` | where an event becomes notifications |
| `web/src/notifications/Preferences.tsx` | the member-facing control surface |

## Final Verification

- [ ] A mention notifies its recipient in-app and by email, once.
- [ ] Turning a type off in settings stops the next one.
- [ ] `just test && just test-web` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Push and SMS transports.
- A third-party notification API.
- Per-workspace notification policy set by admins.
</file>
