# Input — fix stale session cookie

The plan below was written by `draft-plan` against the `backend` template and cross-reviewed in
place; the user has not read it yet. Refine it against the sizing thresholds and write the
decomposition artifact into the run workdir.

## Run-time context

- project: `atlas-web` — a Django + DRF application serving a browser client and a mobile app
- run slug: `20260801-16-05_fix-stale-session-cookie`
- run workdir: `_runs/groom/20260801-16-05_fix-stale-session-cookie/`, relative to the current
  working directory — it already holds the confirmed framing, the blast-radius map and the
  confirmed design
- plan file: `plans/20260801-16-05_fix-stale-session-cookie.md`, on disk, written and complete

## Inputs

- the written plan — `plans/20260801-16-05_fix-stale-session-cookie.md`, on disk: 3 milestones,
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

<file path="plans/20260801-16-05_fix-stale-session-cookie.md">
---
title: Fix stale session cookie surviving logout
type: bug
status: in-spec
sp: 9
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Logging out ends the session everywhere, so the next visitor on that browser starts signed out"
commit: null
---

# Fix stale session cookie surviving logout

## Context

**Current state** — `POST /auth/logout/` flushes the server-side session record but returns
without clearing the `sessionid` cookie. On a shared browser the stale cookie is sent on the next
request, and because the custom `SessionRefreshMiddleware` re-materialises a session record for any
cookie it recognises, the visitor lands back inside the previous account.

**Motivation** — reported twice from a shared kiosk build and once from a support agent's browser.
It is an authentication defect: signing out does not sign the user out.

**Scope** — the logout response and the middleware path that resurrects a flushed session. Not:
the session backend, token auth for the mobile app, or the session-expiry policy.

## Decisions

- **Fix at both ends**: clear the cookie in the logout view *and* stop the middleware from
  re-materialising a flushed session — either alone leaves a path back in.
- **Delete rather than expire**: the response deletes the cookie with the same domain and path
  attributes it was set with, since a mismatched delete is silently ignored by the browser.

## Architecture

`LogoutView.post()` in `atlas/auth/views.py` calls `django.contrib.auth.logout()` and then
`response.delete_cookie(settings.SESSION_COOKIE_NAME, domain=…, path=…)`.
`SessionRefreshMiddleware` in `atlas/auth/middleware.py` currently treats "no session record" as
"refresh it"; it changes to treat an unknown session key as anonymous and to drop the cookie on the
way out.

## Milestones

### M1: Reproduce and cover — 3 SP | pending

**Goal**: a failing test reproduces the resurrection path before anything is changed.

**Verify**: `just test atlas/auth/tests/test_logout.py` — the new test fails on `main`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Failing test: logout, then a request replaying the old cookie | `atlas/auth/tests/test_logout.py` | 2 | pending |
| 1.2 | Failing test: middleware re-materialises an unknown session key | `atlas/auth/tests/test_middleware.py` | 1 | pending |

#### Task 1.1 DoD

- [ ] The test logs in, logs out, replays the captured `sessionid`, and asserts the response is
      anonymous.
- [ ] It fails on `main` for the reported reason, not for a setup error.

**Verify**: `just test atlas/auth/tests/test_logout.py`

#### Task 1.2 DoD

- [ ] The test drives the middleware with a session key that has no record and asserts the request
      stays anonymous.
- [ ] It fails on `main`.

**Verify**: `just test atlas/auth/tests/test_middleware.py`

---

### M2: End the session on logout — 4 SP | pending

**Goal**: logging out clears the cookie and no later request can revive the session.

**Verify**: `just test atlas/auth/` — the M1 tests pass

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Stop the middleware resurrecting an unknown session key | `atlas/auth/middleware.py` | 3 | pending |
| 2.2 | Delete the cookie on the logout response with matching attributes | `atlas/auth/views.py` | 1 | pending |

#### Task 2.1 DoD

- [ ] An unknown session key yields an anonymous request instead of a fresh session record.
- [ ] A live session key still refreshes as before — the existing middleware tests pass unchanged.
- [ ] The response drops the cookie when the key was unknown.

**Verify**: `just test atlas/auth/tests/test_middleware.py`

#### Task 2.2 DoD

- [ ] `delete_cookie` is called with the configured `SESSION_COOKIE_DOMAIN` and
      `SESSION_COOKIE_PATH`.
- [ ] The logout response carries a `Set-Cookie` clearing `sessionid`.

**Verify**: `just test atlas/auth/tests/test_logout.py`

---

### M3: Guard the regression — 2 SP | pending

**Goal**: the shared-browser path is covered end to end and the behaviour is written down.

**Verify**: `just test && just lint`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | End-to-end test: second visitor on the same browser starts signed out | `atlas/auth/tests/test_logout.py` | 1 | pending |
| 3.2 | Note the logout contract in the auth README | `atlas/auth/README.md` | 1 | pending |

#### Task 3.1 DoD

- [ ] The test replays a full browser session across two users and asserts no cross-account leak.
- [ ] It passes with the fix and fails with either half reverted.

**Verify**: `just test atlas/auth/tests/test_logout.py`

#### Task 3.2 DoD

- [ ] The README states that logout clears the cookie and that an unknown key is anonymous.
- [ ] It names both files that enforce it.

**Verify**: `just lint`

## Key Files Reference

| File | Role |
|------|------|
| `atlas/auth/middleware.py` | the path that resurrects a flushed session |
| `atlas/auth/views.py` | the logout response that must clear the cookie |

## Final Verification

- [ ] Logging out and replaying the old cookie yields an anonymous response.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Token auth for the mobile app.
- Session-expiry and idle-timeout policy.
- The session backend itself.
</file>
