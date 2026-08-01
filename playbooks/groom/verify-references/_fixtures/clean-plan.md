# Input — clean-plan

The plan below was refined by `decompose-work` and confirmed by the user at the decomposition
gate. Check every external reference it names against current upstream documentation, correct
what is wrong, and write the step's artifact into the run workdir.

## Run-time context

- project: `portal` — a Flask application behind a hosted OpenID Connect identity provider,
  managed with `uv`
- run slug: `20260731-16-05_fix-stale-session-cookie`
- run workdir: `_runs/groom/20260731-16-05_fix-stale-session-cookie/`, relative to the current
  working directory
- plan file: `plans/20260731-16-05_fix-stale-session-cookie.md`, on disk and inlined below

## Inputs

- the confirmed, decomposed plan — the file at the path above; it names three external
  references: a pinned dependency, a test-runner flag in a milestone `Verify` command, and a
  discovery endpoint with the payload key the fix reads from it
- the decomposition record for the run, with its confirmation stamp
- current upstream documentation for every external reference the plan names — the vendor's own
  docs, release notes, changelogs and package registries, read now rather than recalled

## Context files

<file path="plans/20260731-16-05_fix-stale-session-cookie.md">
---
title: Expire the session cookie when the identity provider ends the session
type: bug
status: awaiting-plan-review
sp: 6
split_from: null
created: 2026-07-31
planned: 20260731 16:21
started: null
completed: null
retro: null
goal: null
summary: "Signing out at the identity provider signs the user out of the portal in the same tab"
commit: 9b2e5f04a7c318d6ef05b91a2c4d7380fa6e1cb9
---

# Expire the session cookie when the identity provider ends the session

## Context

**Current state** — the portal's session cookie is signed with a timestamp but never re-checked
against the identity provider. After a user signs out at the provider, the browser keeps sending
the cookie and the portal keeps serving the account pages until the cookie's own lifetime runs
out.

**Motivation** — support has three reports of a shared machine still showing the previous user's
account page after they signed out centrally.

**Scope** — the portal's own session cookie and the provider round-trip that invalidates it. Not:
the provider's configuration, the login flow, or the remember-me path.

## Decisions

- **Signing**: keep the current signer and lean on its own max-age check rather than adding a
  second expiry of ours — one lifetime, one place to get wrong.
- **Logout coupling**: read the provider's logout endpoint out of its discovery document instead
  of configuring a second URL that can drift from the issuer.

## Architecture

`app/session.py` gains a single `load_session` entry point that verifies the signed cookie with an
explicit max age and drops the session when verification fails. `app/auth.py` fetches the
provider's discovery document once per process, caches it, and uses the logout endpoint it
advertises to build the redirect the sign-out route issues; a session dropped by either path
clears the cookie on the response.

## Milestones

### M1: Session cookie carries an enforced lifetime — 3 SP | pending

**Goal**: an expired or tampered session cookie is dropped and cleared instead of trusted.

**Verify**: `pytest --maxfail=1 tests/test_session.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Pin the signing dependency at `itsdangerous==2.2.0` and verify the session cookie with an explicit max age in `load_session` | `pyproject.toml`, `app/session.py` | 3 | pending |

#### Task 1.1 DoD

- [ ] A cookie older than the configured lifetime is rejected and cleared on the response.
- [ ] A cookie with a tampered payload is rejected without raising out of the request handler.
- [ ] `pytest --maxfail=1 tests/test_session.py` passes.

### M2: Sign-out follows the provider — 3 SP | pending

**Goal**: signing out at the portal ends the provider session too, and the local cookie goes with
it.

**Verify**: `just test && just lint`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Read the provider's `/.well-known/openid-configuration` document and redirect sign-out to the `end_session_endpoint` it advertises, clearing the local cookie on the way out | `app/auth.py` | 3 | pending |

#### Task 2.1 DoD

- [ ] The discovery document is fetched once per process and cached; `issuer` is checked against
      the configured issuer before anything from the document is used.
- [ ] Sign-out redirects to the `end_session_endpoint` value from that document — no second URL is
      configured anywhere in the portal.
- [ ] The response that issues the redirect also clears the session cookie.

## Key Files Reference

| File | Role |
|------|------|
| `app/session.py` | signs, verifies and clears the session cookie |
| `app/auth.py` | the provider round-trip: discovery, sign-in and sign-out |
| `tests/test_session.py` | cookie lifetime and tamper cases |

## Final Verification

- [ ] Signing out at the provider leaves no page in the portal reachable in the same tab.
- [ ] `just test` — all tests pass.
- [ ] `just lint` — clean.

## Out of scope

- The provider's own configuration and the login flow.
- The remember-me path, which issues a separate long-lived cookie.
</file>

<file path="_runs/groom/20260731-16-05_fix-stale-session-cookie/decomposition.md">
---
reviewed_at: 20260731 16:21
---
# Decomposition — 20260731-16-05_fix-stale-session-cookie

## Verdict

Skipped — no task sits at or over the 5 SP re-decompose threshold (the largest is 3 SP), and the
sprint totals 6 SP, well under the 35 SP split threshold. The plan file was not touched.
</file>
