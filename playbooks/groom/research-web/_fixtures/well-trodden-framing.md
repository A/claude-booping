# Input — stale session cookie survives logout

The framing below was confirmed by the user at the end of `intake`. Research current external
practice for it and write the step's artifact into the run workdir.

## Run-time context

- project: `northwind-shop` — a storefront web application on a mainstream web framework, using
  that framework's own session middleware and its server-side session store
- run slug: `20260801-stale-session-cookie`
- run workdir: `_runs/groom/20260801-stale-session-cookie/`, relative to the current
  working directory — it already holds the confirmed framing

## Inputs

- the confirmed framing — `_runs/groom/20260801-stale-session-cookie/intake.md`, on disk;
  confirmed by the user, every scope-challenge question answered
- the uncertainty signals intake recorded: none — on the grounds the framing states, namely that
  the defect sits on the framework's own session middleware, the fix adds no dependency and no
  new surface, and the framing names two places in the repository where the correct shape is
  already in use

## Context files

<file path="_runs/groom/20260801-stale-session-cookie/intake.md">
---
reviewed_at: 20260801 11:48
---
# Intake — stale session cookie survives logout

## Request

> After logging out, the back button still shows the account page until the tab is closed. The
> session cookie is still sitting there in the browser.

## Restated problem

Logout deletes the server-side session but the response never expires the session cookie, so the
browser keeps sending it and the framework's session middleware hands back a fresh empty session
instead of treating the caller as signed out; the account page, which carries no cache directives,
is then served from the browser's back-forward cache. The fix is to expire the cookie on the
logout response the way the framework's own logout helper does, and to mark authenticated
responses uncacheable.

## Task type

`bug` — documented behaviour (logging out ends the session everywhere in the tab) diverges from
what happens. No new capability, no structural change.

## Scope boundaries

**In scope**

- the logout handler's response: expiring the session cookie under the same name, path and domain
  the login response set it with
- cache directives on authenticated responses, so a back-navigation after logout cannot render a
  stored copy

**Out of scope**

- the session storage backend, the cookie flags set at login, and the remember-me path — all
  correct today and untouched by this fix

## Prior art in the repository

- the staff logout route already delegates to the framework's own logout helper, which expires
  the cookie correctly; the customer-facing handler was written by hand and skipped that call
- the billing area already sets `no-store` on its authenticated responses through a single
  after-request hook — the same hook shape covers the account pages

## Scope challenge (answered)

- [x] Should logout revoke every session for the user, or only this one? — only this one; global
      revocation is a separate ask.
- [x] Does anything depend on the cookie surviving logout? — no.
</file>
