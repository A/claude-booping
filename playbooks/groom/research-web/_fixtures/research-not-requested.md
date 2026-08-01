# Input — stale session cookie survives logout (web research not requested)

Intake recorded the user's web-research decision in the `### Web research` line of `## Framing`.
Read that line and execute it.

## Run-time context

- project: `northwind-shop` — a storefront web application on a mainstream web framework, using
  that framework's own session middleware and its server-side session store
- run slug: `20260801-stale-session-cookie`
- run workdir: the plan directory `plans/20260801-stale-session-cookie/`, relative to the
  current working directory — it already holds `index.md` and `plan.md`

## Inputs

- the run's `index.md`, on disk: `## Framing` with intake's web-research decision, and
  `## Blast radius` with the surfaces the codebase pass mapped and the calls it left open —
  including one open external question

## Context files

<file path="plans/20260801-stale-session-cookie/index.md">
---
status: researching
---
# Stale session cookie survives logout

## Framing

### Request

> After logging out, the back button still shows the account page until the tab is closed. The
> session cookie is still sitting there in the browser.

### Restated problem

Logout deletes the server-side session but the response never expires the session cookie, so the
browser keeps sending it and the framework's session middleware hands back a fresh empty session
instead of treating the caller as signed out; the account page, which carries no cache directives,
is then served from the browser's back-forward cache. The fix is to expire the cookie on the
logout response the way the framework's own logout helper does, and to mark authenticated
responses uncacheable.

### Task type

`bug` — documented behaviour (logging out ends the session everywhere in the tab) diverges from
what happens. No new capability, no structural change.

### Scope boundaries

**In scope**

- the logout handler's response: expiring the session cookie under the same name, path and domain
  the login response set it with
- cache directives on authenticated responses, so a back-navigation after logout cannot render a
  stored copy

**Out of scope**

- the session storage backend, the cookie flags set at login, and the remember-me path — all
  correct today and untouched by this fix

### Web research

Not requested — the request asks for no deep web research, and the user asked for none when the
scope questions came back.

### Scope challenge

- [x] Should logout revoke every session for the user, or only this one? — only this one; global
      revocation is a separate ask.
- [x] Does anything depend on the cookie surviving logout? — no.

## Blast radius

### Touched surfaces

| Surface           | Where                                          | Why it moves                                                      | Risk                                                        |
| ----------------- | ---------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------ |
| Logout handler    | `shop/accounts/views.py` (`logout_view`)       | the response must expire the session cookie it set at login       | medium — every customer logout goes through it               |
| Response headers  | `shop/accounts/middleware.py` (`after_request`)| authenticated responses need the no-store directives              | low — the same hook shape is already in use for billing      |

### Prior art

- `shop/staff/views.py` — the staff logout route already delegates to the framework's own logout
  helper, which expires the cookie correctly
- `shop/billing/middleware.py` — the billing area already sets `no-store` on its authenticated
  responses through a single after-request hook

### Conventions in play

- `CONTRIBUTING.md` requires a regression test that fails before the fix and passes after, for
  every bug plan
- `shop/settings.py` holds the single source of the session cookie's name, path and domain — the
  logout response must read them from there rather than restate them

### Unknowns for design

- whether the no-store directives go on the whole authenticated area or on the account pages
  alone
- open external question, for the user to escalate if they want it settled off the repo: whether
  the framework's own logout helper is still the recommended path on the version the project
  pins, or whether that changed in a later release
</file>
