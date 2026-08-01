# Input — verify signed partner webhooks

The framing below was confirmed by the user at the end of `intake`. Research current external
practice for it and write the step's artifact into the run workdir.

## Run-time context

- project: `settle-gateway` — a payments integration service that receives partner callbacks over
  HTTP and posts settlement records into the ledger
- run slug: `20260801-15-05_signed-partner-webhooks`
- run workdir: `_runs/groom/20260801-15-05_signed-partner-webhooks/`, relative to the current
  working directory — it already holds the confirmed framing
- the repository has never implemented HTTP Message Signatures, in any form, on any endpoint

## Inputs

- the confirmed framing — `_runs/groom/20260801-15-05_signed-partner-webhooks/intake.md`, on
  disk; confirmed by the user, every scope-challenge question answered
- the uncertainty signals intake recorded: none — the list came back empty

## Context files

<file path="_runs/groom/20260801-15-05_signed-partner-webhooks/intake.md">
---
reviewed_at: 20260801 15:12
---
# Intake — verify signed partner webhooks

## Request

> Our new settlement partner signs every webhook with HTTP Message Signatures and will not send
> us live traffic until we verify them. We need to accept their callbacks and reject anything
> whose signature does not check out.

## Restated problem

Partner callbacks are accepted today on a shared secret passed as a query parameter. The new
partner requires RFC 9421 HTTP Message Signatures: a `Signature-Input` header naming the covered
components and their parameters, a `Signature` header carrying the signature itself, and key
material resolved from the partner's published key set. The request is to verify those signatures
on the callback endpoint and refuse everything that fails, leaving what an accepted callback does
downstream unchanged.

## Task type

`feature` — a new capability on the callback endpoint, with its own acceptance and rejection
contract. Not a bug (nothing diverges from expected behaviour today) and not a refactoring (new
behaviour, not restructured behaviour).

## Scope boundaries

**In scope**

- verifying `Signature` and `Signature-Input` on the partner callback endpoint: which components
  must be covered for a signature to count, and how key material is resolved and refreshed
- the rejection contract — what an unverifiable callback is answered with, and what is recorded

**Out of scope**

- signing our own outbound requests to the partner
- retiring the shared-secret query parameter for the three older integrations still using it

## Scope challenge (answered)

- [x] Do the older integrations move to signatures too? — no, this partner only, for now.
- [x] Is replay protection part of this? — yes, to the extent the standard's own `created` and
      `nonce` parameters cover it; the partner sends both.
- [x] Is the partner's key set fetched live or pinned? — the partner publishes a key set at a URL
      and rotates it; whichever of the two the design lands on has to survive a rotation.
</file>
