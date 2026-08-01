---
status: done
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:27
suite_reviewed_at: 20260731 19:47
---

[← index](../../index.md)

# research-web

## Contract

- **Delegation** — assisted: the runner renders and owns the step and decides what is
  researched; the configured researcher agent performs the web reads and returns the findings
  with their sources; the runner writes the artifact. The runner records the agent's id in
  `index.md` so a loopback resumes the same agent instead of spawning a fresh one.
- **Needs** —
  - the confirmed framing — the restated problem, the task type, and the scope boundaries the
    user confirmed
  - intake's web-research decision — `requested` or `not requested`
- **Value** — when the user asked for it, settles what current external practice says before the
  architecture is called, so design argues from dated sources rather than model memory. The
  decision is the user's, recorded at intake and executed here mechanically — the step never
  judges novelty itself. With no conditional edges in the framework the step always runs; on the
  not-requested path its whole work is one skip line, so `design` never has to work out whether
  research happened.
- **Output files** —
  - on the requested path: `[CREATED] plans/{slug}/research.md` — the candidate approaches with
    their trade-offs and fit, the pitfalls that constrain the design, and a source table
    carrying a URL and a retrieval date per claim. Research is sized to the open questions the
    framing carries — one primary source per question, stopping once the design call is
    constrained; facts answerable from local ground truth are not fetched.
  - on the not-requested path: `[UPDATED] plans/{slug}/index.md` — a one-line
    `Web research: not requested` note in the `## Framing` section; no `research.md` is created.
- **Step report** — `## Changed:` list, plus `## Notes:` carrying the recommendation and the
  pitfall count, or the skip line.
- **Review gate** —
  - none — the step never pauses the run; its findings reach the user through the design
    conversation

## Example artifact

`plans/20260731-rate-limit-public-api/research.md`, requested path:

```markdown
# research — rate-limit-public-api

## Approaches

### Token bucket in gateway middleware

Per-key bucket refilled at a fixed rate, checked before the handler runs.

- Fits: limits are per API key, which the gateway already resolves.
- Costs: bucket state must be shared across processes — needs the cache tier, which the
  deployment already runs.
- Retire cost: low — the middleware is one layer, removable without touching handlers.

### Sliding-window counter in the datastore

Counts requests per key per window directly in the primary datastore.

- Fits: no new infrastructure.
- Costs: a write per request on the hot path; the window boundary allows a 2x burst.

## Pitfalls

- Returning `429` without `Retry-After` makes well-behaved clients retry immediately; the header
  is expected, not optional.
- Counting on the cache tier without a failure policy turns a cache outage into a total outage —
  fail-open vs fail-closed is a design call, not an implementation detail.
- Per-process in-memory buckets silently multiply the effective limit by the process count.

## Sources

| Source                                                | Backs                            | Checked  |
| ----------------------------------------------------- | -------------------------------- | -------- |
| https://www.rfc-editor.org/rfc/rfc6585                | `429` + `Retry-After` semantics  | 20260731 |
| https://redis.io/docs/latest/develop/use-cases/rate-limiting/ | token bucket on a shared cache | 20260731 |
```

## Return Format

Requested path:

```markdown
## Changed:

- [CREATED] plans/20260731-rate-limit-public-api/research.md — 2 approaches, 2 sources

## Notes:

- recommended: token bucket in gateway middleware — lowest retire cost, keys on what the
  gateway already resolves
- 3 pitfall(s) the design must answer, one of them a fail-open vs fail-closed call
```

Not-requested path:

```markdown
## Changed:

- [UPDATED] plans/20260731-fix-stale-session-cookie/index.md — web research: not requested

## Notes:

- web research not requested at intake; open external questions, if any, are in the blast
  radius for the user to escalate
```
